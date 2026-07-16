from __future__ import annotations

import importlib
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app.persistent_dispatch_queue import PersistentDistributedDispatcher


def worker() -> dict:
    return {
        "id": "ops-worker",
        "name": "Operations Worker",
        "workerType": "local-python",
        "capabilities": {
            "methods": ["simulation.parameter_sweep"],
            "packages": ["numpy"],
            "memoryMb": 2048,
            "checkpointing": True,
            "maxConcurrentJobs": 1,
        },
        "tags": ["trusted"],
    }


def workload(max_attempts: int = 3) -> dict:
    return {
        "method": "simulation.parameter_sweep",
        "projectId": "ops-project",
        "priority": 75,
        "requiredPackages": ["numpy"],
        "requiredTags": ["trusted"],
        "checkpointingRequired": True,
        "maxAttempts": max_attempts,
        "request": {"inputs": {"values": [1, 2, 3]}},
    }


def claimed(dispatcher: PersistentDistributedDispatcher, max_attempts: int = 3) -> dict:
    dispatcher.register(worker())
    dispatcher.enqueue(workload(max_attempts))
    return dispatcher.claim({"workerId": "ops-worker", "leaseSeconds": 120}, "secret")


def test_retryable_failure_enters_backoff_with_classification():
    with TemporaryDirectory() as td:
        d = PersistentDistributedDispatcher(str(Path(td) / "d.sqlite3"), retry_base_delay_seconds=5, retry_max_delay_seconds=30)
        c = claimed(d)
        d.acknowledge(c["contract"]["id"], "ops-worker")
        out = d.complete(c["contract"]["id"], {"ok": False, "error": "temporary worker dependency unavailable"}, "ops-worker")
        assert out["queueStatus"] == "retrying"
        item = d.queue_item(c["queueItem"]["id"])["queueItem"]
        assert item["failure"]["failureClass"] == "worker-transient"
        assert item["failure"]["retryable"] is True
        assert item["availableAt"] > item["updatedAt"]


def test_nonretryable_failure_dead_letters_and_operator_replays():
    with TemporaryDirectory() as td:
        d = PersistentDistributedDispatcher(str(Path(td) / "d.sqlite3"))
        c = claimed(d)
        d.acknowledge(c["contract"]["id"], "ops-worker")
        out = d.complete(c["contract"]["id"], {"ok": False, "error": "input validation failed: required field missing"}, "ops-worker")
        assert out["queueStatus"] == "dead-lettered"
        dead = d.dead_letters()
        assert dead["count"] == 1
        queue_id = dead["deadLetters"][0]["id"]
        replay = d.replay(queue_id, {"operatorId": "admin", "reason": "corrected input", "resetAttempts": True})
        assert replay["queueItem"]["status"] == "queued"
        assert replay["queueItem"]["attempts"] == 0
        timeline = d.timeline(queue_id)
        assert any(event["eventType"] == "operator-replayed" for event in timeline["timeline"])


def test_attempt_limit_moves_retryable_failure_to_dead_letter():
    with TemporaryDirectory() as td:
        d = PersistentDistributedDispatcher(str(Path(td) / "d.sqlite3"), max_attempts=1)
        c = claimed(d, 1)
        d.acknowledge(c["contract"]["id"], "ops-worker")
        out = d.complete(c["contract"]["id"], {"ok": False, "error": "temporary worker runtime failure"}, "ops-worker")
        assert out["queueStatus"] == "dead-lettered"
        assert out["failure"]["deadLetterReason"] == "attempt-limit-exhausted"


def test_operator_cancel_metrics_and_database_diagnostics():
    with TemporaryDirectory() as td:
        d = PersistentDistributedDispatcher(str(Path(td) / "d.sqlite3"))
        queued = d.enqueue(workload())["queueItem"]
        cancelled = d.cancel_queue_item(queued["id"], {"operatorId": "admin", "reason": "duplicate campaign"})
        assert cancelled["queueItem"]["status"] == "cancelled"
        metrics = d.operations_metrics()
        assert metrics["counts"]["cancelled"] == 1
        assert metrics["operatorActionCount"] == 1
        diagnostics = d.diagnostics()
        assert diagnostics["ok"] is True
        assert diagnostics["integrityCheck"] == "ok"
        health = d.operations_health()
        assert health["deadLetterRecovery"] is True and health["queueMetrics"] is True


def test_fastapi_dispatcher_operations_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "admin-key")
    monkeypatch.setenv("SC_LAB_COMPUTE_SIGNING_SECRET", "")
    import app.config
    import app.main
    importlib.reload(app.config)
    module = importlib.reload(app.main)
    client = TestClient(module.app)
    headers = {"X-SC-Lab-Key": "admin-key"}
    assert client.get("/v1/dispatcher/operations/health", headers=headers).status_code == 200
    assert client.get("/v1/dispatcher/operations/policies", headers=headers).json()["version"] == "0.31.4"
    assert client.get("/v1/dispatcher/operations/metrics", headers=headers).status_code == 200
    assert client.get("/v1/dispatcher/operations/diagnostics", headers=headers).json()["integrityCheck"] == "ok"
    assert client.get("/v1/dispatcher/dead-letters", headers=headers).status_code == 200


def test_v2_dispatcher_database_migrates_in_place(tmp_path: Path):
    import sqlite3
    db = tmp_path / "legacy-v2.sqlite3"
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE dispatcher_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    INSERT INTO dispatcher_meta(key,value) VALUES('schema_version','2');
    CREATE TABLE dispatcher_workers(
      id TEXT PRIMARY KEY, state TEXT NOT NULL, worker_type TEXT NOT NULL,
      capability_fingerprint TEXT NOT NULL, payload_json TEXT NOT NULL,
      registered_at TEXT NOT NULL, last_heartbeat_at TEXT NOT NULL, updated_at TEXT NOT NULL
    );
    CREATE TABLE dispatcher_queue(
      id TEXT PRIMARY KEY, workload_hash TEXT NOT NULL, project_id TEXT NOT NULL,
      method TEXT NOT NULL, priority INTEGER NOT NULL, status TEXT NOT NULL,
      payload_json TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
      max_attempts INTEGER NOT NULL, available_at TEXT NOT NULL,
      lease_id TEXT, worker_id TEXT, lease_expires_at TEXT,
      result_json TEXT, error_text TEXT,
      created_at TEXT NOT NULL, updated_at TEXT NOT NULL, completed_at TEXT
    );
    CREATE TABLE dispatcher_contracts(
      id TEXT PRIMARY KEY, lease_id TEXT UNIQUE NOT NULL, queue_id TEXT,
      worker_id TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL,
      expires_at TEXT NOT NULL, updated_at TEXT NOT NULL
    );
    CREATE TABLE dispatcher_events(
      id INTEGER PRIMARY KEY AUTOINCREMENT, schema_name TEXT NOT NULL,
      entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, event_type TEXT NOT NULL,
      payload_json TEXT NOT NULL, created_at TEXT NOT NULL
    );
    CREATE TABLE dispatcher_worker_credentials(
      worker_id TEXT PRIMARY KEY REFERENCES dispatcher_workers(id) ON DELETE CASCADE,
      credential_hash TEXT NOT NULL, issued_at TEXT NOT NULL, rotated_at TEXT,
      revoked_at TEXT, last_used_at TEXT
    );
    """)
    con.close()
    dispatcher = PersistentDistributedDispatcher(str(db))
    diagnostics = dispatcher.diagnostics()
    assert diagnostics["schemaVersion"] == 3
    con = sqlite3.connect(db)
    columns = {row[1] for row in con.execute("PRAGMA table_info(dispatcher_queue)")}
    assert {"failure_class", "failure_code", "retryable", "dead_lettered_at", "operator_note"}.issubset(columns)
    assert con.execute("SELECT value FROM dispatcher_meta WHERE key='schema_version'").fetchone()[0] == "3"
    assert con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispatcher_operator_actions'").fetchone()
    con.close()
