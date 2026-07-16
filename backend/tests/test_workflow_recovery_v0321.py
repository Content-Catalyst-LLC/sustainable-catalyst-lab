from __future__ import annotations

import importlib
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from app.persistent_dispatch_queue import PersistentDistributedDispatcher
from app.workflow_orchestration import WorkflowOrchestrator, normalize_workflow


def worker() -> dict:
    return {
        "id": "recovery-worker",
        "name": "Recovery Worker",
        "workerType": "local-python",
        "capabilities": {
            "methods": ["dataset.profile", "model.calibrate", "report.build"],
            "packages": [],
            "memoryMb": 4096,
            "checkpointing": True,
            "maxConcurrentJobs": 4,
        },
        "tags": ["workflow"],
    }


def definition() -> dict:
    return {
        "id": "conditional-recovery",
        "title": "Conditional recovery",
        "nodes": [
            {"id": "profile", "method": "dataset.profile", "request": {"inputs": {}}, "requiredTags": ["workflow"]},
            {
                "id": "calibrate",
                "method": "model.calibrate",
                "dependsOn": ["profile"],
                "condition": {"source": "run.inputs.enableCalibration", "operator": "equals", "value": True},
                "request": {"inputs": {}},
                "checkpointingRequired": True,
                "requiredTags": ["workflow"],
            },
            {
                "id": "report",
                "method": "report.build",
                "dependsOn": ["calibrate"],
                "request": {"inputs": {}},
                "requiredTags": ["workflow"],
            },
        ],
    }


def make(tmp: Path) -> tuple[PersistentDistributedDispatcher, WorkflowOrchestrator]:
    dispatcher = PersistentDistributedDispatcher(str(tmp / "dispatcher.sqlite3"))
    dispatcher.register(worker())
    orchestrator = WorkflowOrchestrator(str(tmp / "workflows.sqlite3"), dispatcher)
    orchestrator.save(definition())
    return dispatcher, orchestrator


def complete(dispatcher: PersistentDistributedDispatcher, result: dict, ok: bool = True, error: str = "") -> dict:
    claim = dispatcher.claim({"workerId": "recovery-worker", "leaseSeconds": 120}, "secret")
    assert claim["claimed"] is True
    dispatcher.acknowledge(claim["contract"]["id"], "recovery-worker")
    dispatcher.complete(claim["contract"]["id"], {"ok": ok, "result": result, "error": error}, "recovery-worker")
    return claim


def test_condition_false_skips_node_and_allows_downstream(tmp_path: Path):
    dispatcher, orchestrator = make(tmp_path)
    run = orchestrator.start_run("conditional-recovery", {"inputs": {"enableCalibration": False}})["run"]
    complete(dispatcher, {"profile": {"rows": 10}})
    mid = orchestrator.reconcile(run["id"])["run"]
    calibrate = next(node for node in mid["nodes"] if node["nodeId"] == "calibrate")
    assert calibrate["status"] == "skipped"
    assert calibrate["skipReason"] == "condition-false"
    assert mid["nodeCounts"]["queued"] == 1
    complete(dispatcher, {"report": "done"})
    final = orchestrator.reconcile(run["id"])["run"]
    assert final["status"] == "completed"
    assert final["nodeCounts"]["skipped"] == 1


def test_manual_checkpoint_history_is_deduplicated(tmp_path: Path):
    _, orchestrator = make(tmp_path)
    run_id = orchestrator.start_run("conditional-recovery", {"inputs": {"enableCalibration": True}})["run"]["id"]
    first = orchestrator.record_checkpoint(run_id, "profile", {"artifactId": "artifact-checkpoint-1", "state": {"offset": 20}, "progress": 0.4})
    second = orchestrator.record_checkpoint(run_id, "profile", {"artifactId": "artifact-checkpoint-1", "state": {"offset": 20}, "progress": 0.4})
    assert first["checkpoint"]["sequence"] == 1
    assert second["checkpoint"]["id"] == first["checkpoint"]["id"]
    history = orchestrator.checkpoints(run_id, "profile")
    assert history["count"] == 1
    assert history["checkpoints"][0]["artifactId"] == "artifact-checkpoint-1"


def test_failed_branch_recovery_reuses_completed_nodes_and_checkpoint(tmp_path: Path):
    dispatcher, orchestrator = make(tmp_path)
    run_id = orchestrator.start_run("conditional-recovery", {"inputs": {"enableCalibration": True}})["run"]["id"]
    complete(dispatcher, {"profile": {"rows": 10}})
    orchestrator.reconcile(run_id)
    complete(dispatcher, {"checkpointArtifactId": "checkpoint-calibrate", "checkpoint": {"iteration": 4}}, ok=False, error="input validation failed: solver state invalid")
    failed = orchestrator.reconcile(run_id)["run"]
    assert failed["status"] == "failed"
    assert failed["nodeCounts"]["failed"] == 1
    assert failed["nodeCounts"]["skipped"] == 1

    plan = orchestrator.recovery_plan(run_id)["plan"]
    assert plan["restartNodes"] == ["calibrate", "report"]
    assert plan["reuseNodes"] == ["profile"]
    assert plan["checkpointCandidates"][0]["nodeId"] == "calibrate"

    recovered = orchestrator.recover(run_id, {"operatorId": "admin", "reason": "retry solver"})["run"]
    assert recovered["recoveryOfRunId"] == run_id
    assert recovered["recoveryGeneration"] == 1
    profile = next(node for node in recovered["nodes"] if node["nodeId"] == "profile")
    calibrate = next(node for node in recovered["nodes"] if node["nodeId"] == "calibrate")
    assert profile["status"] == "reused"
    assert calibrate["status"] == "queued"
    queue_item = dispatcher.queue_item(calibrate["queueId"])["queueItem"]
    context = queue_item["workload"]["request"]["workflowContext"]
    assert context["resumeCheckpoint"]["artifactId"] == "checkpoint-calibrate"
    assert any(item.get("role") == "workflow-checkpoint" for item in queue_item["workload"]["artifactInputs"])


def test_operator_can_restart_completed_branch(tmp_path: Path):
    dispatcher, orchestrator = make(tmp_path)
    run_id = orchestrator.start_run("conditional-recovery", {"inputs": {"enableCalibration": False}})["run"]["id"]
    complete(dispatcher, {"profile": {"rows": 10}})
    orchestrator.reconcile(run_id)
    complete(dispatcher, {"report": "done"})
    assert orchestrator.reconcile(run_id)["run"]["status"] == "completed"
    restarted = orchestrator.restart_node(run_id, "report", {"operatorId": "admin"})["run"]
    assert restarted["nodeCounts"]["reused"] == 1
    assert restarted["nodeCounts"]["skipped"] == 1
    assert restarted["nodeCounts"]["queued"] == 1


def test_v0320_database_migrates_in_place(tmp_path: Path):
    db = tmp_path / "workflows.sqlite3"
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE workflow_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    INSERT INTO workflow_meta VALUES('schema_version','1');
    CREATE TABLE workflow_definitions(id TEXT PRIMARY KEY, definition_hash TEXT NOT NULL, project_id TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE TABLE workflow_runs(id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, definition_hash TEXT NOT NULL, project_id TEXT NOT NULL, status TEXT NOT NULL, definition_json TEXT NOT NULL, inputs_json TEXT NOT NULL, context_json TEXT NOT NULL, error_text TEXT, created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL);
    CREATE TABLE workflow_node_runs(run_id TEXT NOT NULL, node_id TEXT NOT NULL, status TEXT NOT NULL, queue_id TEXT, payload_json TEXT NOT NULL, result_json TEXT, error_text TEXT, created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL, PRIMARY KEY(run_id,node_id));
    CREATE TABLE workflow_events(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, node_id TEXT, event_type TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL);
    """)
    con.close()
    dispatcher = PersistentDistributedDispatcher(str(tmp_path / "dispatcher.sqlite3"))
    orchestrator = WorkflowOrchestrator(str(db), dispatcher)
    health = orchestrator.health()
    assert health["schemaVersion"] == 2
    assert health["checkpointHistory"] is True
    with sqlite3.connect(db) as check:
        columns = {row[1] for row in check.execute("PRAGMA table_info(workflow_node_runs)")}
        assert {"skip_reason", "checkpoint_json", "recovery_source_run_id"}.issubset(columns)


def test_fastapi_recovery_and_checkpoint_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_DB_PATH", str(tmp_path / "workflows.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(tmp_path / "jobs.sqlite3"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "workflow-key")
    monkeypatch.setenv("SC_LAB_COMPUTE_SIGNING_SECRET", "")
    import app.config
    import app.main
    importlib.reload(app.config)
    module = importlib.reload(app.main)
    client = TestClient(module.app)
    headers = {"X-SC-Lab-Key": "workflow-key"}
    client.post("/v1/workflows", json=definition(), headers=headers)
    run = client.post("/v1/workflows/conditional-recovery/runs", json={"inputs": {"enableCalibration": True}}, headers=headers).json()["run"]
    checkpoint = client.post(f"/v1/workflow-runs/{run['id']}/nodes/profile/checkpoints", json={"state": {"offset": 5}}, headers=headers)
    assert checkpoint.status_code == 200
    assert client.get(f"/v1/workflow-runs/{run['id']}/nodes/profile/checkpoints", headers=headers).json()["count"] == 1
    # Recovery planning is correctly rejected until the run reaches a terminal state or nodes are selected.
    plan = client.post(f"/v1/workflow-runs/{run['id']}/recovery-plan", json={"restartNodes": ["profile"]}, headers=headers)
    assert plan.status_code == 200
    assert plan.json()["plan"]["restartNodes"] == ["profile", "calibrate", "report"]


def test_condition_normalization_is_declarative_only():
    normalized = normalize_workflow(definition())
    condition = next(node for node in normalized["nodes"] if node["id"] == "calibrate")["condition"]
    assert condition == {"source": "run.inputs.enableCalibration", "operator": "equals", "value": True}
