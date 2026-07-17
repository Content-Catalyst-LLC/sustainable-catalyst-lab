from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import hmac
import importlib
import json
from pathlib import Path

import pytest

from app.persistent_dispatch_queue import PersistentDistributedDispatcher
from app.workflow_orchestration import WorkflowOrchestrator
from app.workflow_scheduling import WorkflowScheduleError, WorkflowScheduler, next_cron_after, normalize_schedule, verify_event_signature


def workflow_definition():
    return {"id": "scheduled-pipeline", "title": "Scheduled pipeline", "projectId": "test", "nodes": [{"id": "profile", "method": "dataset.profile", "request": {"inputs": {"records": []}}}]}


def scheduler(tmp_path: Path):
    dispatcher = PersistentDistributedDispatcher(str(tmp_path / "dispatcher.sqlite3"))
    workflows = WorkflowOrchestrator(str(tmp_path / "workflows.sqlite3"), dispatcher)
    workflows.save(workflow_definition())
    return WorkflowScheduler(str(tmp_path / "schedules.sqlite3"), workflows, poll_seconds=60, max_catch_up_runs=5), workflows


def interval_schedule(**changes):
    payload = {"id": "hourly-profile", "workflowId": "scheduled-pipeline", "trigger": {"type": "interval", "everySeconds": 60, "anchorAt": "2026-07-16T00:00:00+00:00"}, "run": {"misfirePolicy": "catch-up-one", "concurrencyPolicy": "allow", "maxConcurrentRuns": 5}}
    payload.update(changes)
    return payload


def test_normalize_schedule_and_cron_validation():
    record = normalize_schedule(interval_schedule())
    assert record["schema"].endswith("0.32.2")
    assert record["trigger"]["everySeconds"] == 60
    assert next_cron_after("*/15 * * * *", datetime(2026, 7, 16, 12, 1, tzinfo=timezone.utc)).minute == 15
    with pytest.raises(WorkflowScheduleError):
        normalize_schedule({"workflowId": "scheduled-pipeline", "trigger": {"type": "cron", "expression": "bad cron"}})


def test_schedule_save_tick_and_persisted_firing(tmp_path: Path):
    engine, workflows = scheduler(tmp_path)
    saved = engine.save(interval_schedule())
    assert saved["schedule"]["id"] == "hourly-profile"
    first_due = datetime.fromisoformat(saved["schedule"]["nextFireAt"])
    tick = engine.tick(first_due + timedelta(minutes=3, seconds=5))
    assert tick["firingCount"] == 4
    firing = [item for item in tick["firings"] if item["status"] == "started"][0]
    assert len([item for item in tick["firings"] if item["status"] == "skipped"]) == 3
    run = workflows.run(firing["workflowRunId"], reconcile=False)["run"]
    assert run["context"]["automation"]["scheduleId"] == "hourly-profile"
    reopened = WorkflowScheduler(str(tmp_path / "schedules.sqlite3"), workflows)
    assert reopened.firings()["count"] == 4


def test_misfire_skip_records_skipped_occurrences(tmp_path: Path):
    engine, _ = scheduler(tmp_path)
    payload = interval_schedule(run={"misfirePolicy": "skip", "misfireGraceSeconds": 5, "concurrencyPolicy": "allow", "maxConcurrentRuns": 10})
    saved = engine.save(payload)
    first_due = datetime.fromisoformat(saved["schedule"]["nextFireAt"])
    tick = engine.tick(first_due + timedelta(minutes=3, seconds=30))
    assert tick["firingCount"] >= 3
    assert all(item["status"] == "skipped" for item in tick["firings"])


def test_forbid_concurrency_skips_second_manual_trigger(tmp_path: Path):
    engine, _ = scheduler(tmp_path)
    payload = interval_schedule(run={"misfirePolicy": "catch-up-one", "concurrencyPolicy": "forbid", "maxConcurrentRuns": 1})
    engine.save(payload)
    first = engine.trigger("hourly-profile")["firing"]
    second = engine.trigger("hourly-profile")["firing"]
    assert first["status"] == "started"
    assert second["status"] == "skipped"
    assert second["reason"] == "concurrency-forbid"


def test_event_filters_deduplication_and_run_context(tmp_path: Path):
    engine, workflows = scheduler(tmp_path)
    engine.save({"id": "dataset-arrived", "workflowId": "scheduled-pipeline", "trigger": {"type": "event", "eventType": "dataset.created", "filters": {"payload.projectId": "alpha"}}, "run": {"concurrencyPolicy": "allow", "maxConcurrentRuns": 10}})
    payload = {"id": "evt-1", "type": "dataset.created", "payload": {"projectId": "alpha", "datasetId": "ds-1"}}
    result = engine.ingest_event(payload)
    assert result["matchedSchedules"] == 1
    firing = result["firings"][0]
    run = workflows.run(firing["workflowRunId"], reconcile=False)["run"]
    assert run["inputs"]["event"]["payload"]["datasetId"] == "ds-1"
    duplicate = engine.ingest_event(payload)
    assert duplicate["duplicate"] is True
    assert engine.firings()["count"] == 1


def test_event_signature_verification():
    payload = {"id": "evt-2", "type": "instrument.sample", "payload": {"value": 12}}
    timestamp = "2026-07-16T12:00:00+00:00"
    signature = hmac.new(b"secret", f"{timestamp}.{json.dumps(payload,sort_keys=True,separators=(',',':'))}".encode(), sha256).hexdigest()
    now = datetime(2026, 7, 16, 12, 1, tzinfo=timezone.utc)
    assert verify_event_signature(payload, timestamp, signature, "secret", now=now)
    assert not verify_event_signature(payload, timestamp, "bad", "secret", now=now)


def test_enable_disable_delete_and_health(tmp_path: Path):
    engine, _ = scheduler(tmp_path)
    engine.save(interval_schedule())
    assert engine.set_enabled("hourly-profile", False)["schedule"]["enabled"] is False
    assert engine.health()["enabledSchedules"] == 0
    engine.set_enabled("hourly-profile", True)
    assert engine.list(enabled=True)["count"] == 1
    assert engine.delete("hourly-profile")["deleted"] == "hourly-profile"


def test_fastapi_workflow_automation_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_DB_PATH", str(tmp_path / "workflows.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_SCHEDULE_DB_PATH", str(tmp_path / "schedules.sqlite3"))
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(tmp_path / "jobs.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "automation-key")
    import app.config as config
    import app.main as main
    importlib.reload(config)
    importlib.reload(main)
    from fastapi.testclient import TestClient
    headers = {"X-SC-Lab-Key": "automation-key"}
    with TestClient(main.app) as client:
        assert client.post("/v1/workflows", json=workflow_definition(), headers=headers).status_code == 200
        schedule = interval_schedule()
        assert client.post("/v1/workflow-automation/schedules/validate", json=schedule, headers=headers).status_code == 200
        saved = client.post("/v1/workflow-automation/schedules", json=schedule, headers=headers)
        assert saved.status_code == 200
        assert client.get("/v1/workflow-automation/schedules", headers=headers).json()["count"] == 1
        triggered = client.post("/v1/workflow-automation/schedules/hourly-profile/trigger", json={}, headers=headers)
        assert triggered.status_code == 200
        event_schedule = {"id": "api-event", "workflowId": "scheduled-pipeline", "trigger": {"type": "event", "eventType": "dataset.created"}, "run": {"concurrencyPolicy": "allow", "maxConcurrentRuns": 10}}
        client.post("/v1/workflow-automation/schedules", json=event_schedule, headers=headers)
        event = client.post("/v1/workflow-automation/events", json={"id": "api-event-1", "type": "dataset.created", "payload": {}}, headers=headers)
        assert event.status_code == 200
        assert event.json()["matchedSchedules"] == 1
        assert client.get("/v1/workflow-automation/health", headers=headers).json()["version"] == "0.32.2"


def test_scheduler_migrates_legacy_firing_table_and_enforces_dedupe(tmp_path: Path):
    import sqlite3

    db = tmp_path / "schedules.sqlite3"
    with sqlite3.connect(db) as con:
        con.executescript("""
        CREATE TABLE workflow_schedule_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE workflow_schedules(
          id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, trigger_type TEXT NOT NULL,
          enabled INTEGER NOT NULL, definition_hash TEXT NOT NULL, definition_json TEXT NOT NULL,
          next_fire_at TEXT, last_fire_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE workflow_schedule_firings(
          id TEXT PRIMARY KEY, schedule_id TEXT NOT NULL,
          occurrence_at TEXT NOT NULL, source TEXT NOT NULL, event_id TEXT, workflow_run_id TEXT,
          status TEXT NOT NULL, reason TEXT, payload_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          UNIQUE(schedule_id,occurrence_at,source,event_id)
        );
        CREATE TABLE workflow_trigger_events(
          event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, payload_hash TEXT NOT NULL,
          payload_json TEXT NOT NULL, received_at TEXT NOT NULL, processed_at TEXT,
          status TEXT NOT NULL, result_json TEXT
        );
        """)
    dispatcher = PersistentDistributedDispatcher(str(tmp_path / "dispatcher.sqlite3"))
    workflows = WorkflowOrchestrator(str(tmp_path / "workflows.sqlite3"), dispatcher)
    workflows.save(workflow_definition())
    engine = WorkflowScheduler(str(db), workflows)
    engine.save(interval_schedule())
    firing = engine.trigger("hourly-profile")["firing"]
    with sqlite3.connect(db) as con:
        columns = {row[1] for row in con.execute("PRAGMA table_info(workflow_schedule_firings)")}
        schema_version = con.execute("SELECT value FROM workflow_schedule_meta WHERE key='schema_version'").fetchone()[0]
        dedupe_key = con.execute("SELECT dedupe_key FROM workflow_schedule_firings WHERE id=?", (firing["id"],)).fetchone()[0]
    assert "dedupe_key" in columns
    assert schema_version == "2"
    assert dedupe_key.startswith("hourly-profile|")


def test_reenable_missed_once_schedule_preserves_occurrence_for_misfire_policy(tmp_path: Path):
    engine, _ = scheduler(tmp_path)
    at = datetime.now(timezone.utc) - timedelta(minutes=5)
    engine.save({
        "id": "missed-once",
        "workflowId": "scheduled-pipeline",
        "enabled": False,
        "trigger": {"type": "once", "at": at.isoformat()},
        "run": {"misfirePolicy": "catch-up-one", "concurrencyPolicy": "allow", "maxConcurrentRuns": 1},
    })
    enabled = engine.set_enabled("missed-once", True)["schedule"]
    assert enabled["nextFireAt"] == at.isoformat()
    tick = engine.tick(datetime.now(timezone.utc))
    assert any(item["scheduleId"] == "missed-once" and item["status"] == "started" for item in tick["firings"])
