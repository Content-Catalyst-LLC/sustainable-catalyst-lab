from __future__ import annotations

import importlib
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from fastapi.testclient import TestClient

from app.persistent_dispatch_queue import PersistentDistributedDispatcher
from app.workflow_orchestration import WorkflowError, WorkflowOrchestrator, normalize_workflow


def definition() -> dict:
    return {
        "id": "calibration-pipeline",
        "title": "Calibration pipeline",
        "projectId": "project-workflow",
        "nodes": [
            {
                "id": "prepare-a",
                "method": "dataset.profile",
                "request": {"inputs": {"dataset": "a"}},
                "requiredTags": ["workflow"],
            },
            {
                "id": "prepare-b",
                "method": "dataset.profile",
                "request": {"inputs": {"dataset": "b"}},
                "requiredTags": ["workflow"],
            },
            {
                "id": "calibrate",
                "method": "model.calibrate",
                "dependsOn": ["prepare-a", "prepare-b"],
                "bindings": [
                    {"fromNode": "prepare-a", "sourcePath": "result.profile.mean", "targetPath": "inputs.initialMean"}
                ],
                "request": {"inputs": {"model": "linear"}},
                "artifactOutputs": [{"kind": "result", "name": "calibration-result"}],
                "requiredTags": ["workflow"],
                "maxAttempts": 4,
            },
        ],
    }


def worker() -> dict:
    return {
        "id": "workflow-worker",
        "name": "Workflow Worker",
        "workerType": "local-python",
        "capabilities": {
            "methods": ["dataset.profile", "model.calibrate"],
            "packages": [],
            "memoryMb": 4096,
            "checkpointing": True,
            "maxConcurrentJobs": 4,
        },
        "tags": ["workflow"],
    }


def make(tmp: Path) -> tuple[PersistentDistributedDispatcher, WorkflowOrchestrator]:
    dispatcher = PersistentDistributedDispatcher(str(tmp / "dispatcher.sqlite3"))
    dispatcher.register(worker())
    orchestrator = WorkflowOrchestrator(str(tmp / "workflows.sqlite3"), dispatcher)
    orchestrator.save(definition())
    return dispatcher, orchestrator


def complete_claim(dispatcher: PersistentDistributedDispatcher, result: dict, ok: bool = True, error: str = "") -> dict:
    claim = dispatcher.claim({"workerId": "workflow-worker", "leaseSeconds": 120}, "secret")
    assert claim["claimed"] is True
    dispatcher.acknowledge(claim["contract"]["id"], "workflow-worker")
    dispatcher.complete(claim["contract"]["id"], {"ok": ok, "result": result, "error": error}, "workflow-worker")
    return claim


def test_workflow_validation_builds_topological_order_and_rejects_cycles():
    normalized = normalize_workflow(definition())
    assert normalized["entryNodes"] == ["prepare-a", "prepare-b"]
    assert normalized["terminalNodes"] == ["calibrate"]
    assert normalized["topologicalOrder"][-1] == "calibrate"
    assert len(normalized["definitionHash"]) == 64

    cyclic = definition()
    cyclic["nodes"][0]["dependsOn"] = ["calibrate"]
    with pytest.raises(WorkflowError, match="cycle"):
        normalize_workflow(cyclic)


def test_start_schedules_parallel_roots_then_dependency_with_binding_and_artifacts(tmp_path: Path):
    dispatcher, orchestrator = make(tmp_path)
    started = orchestrator.start_run("calibration-pipeline", {"inputs": {"campaign": "summer"}})["run"]
    assert started["status"] == "running"
    assert started["nodeCounts"]["queued"] == 2
    assert started["nodeCounts"]["waiting"] == 1

    first = complete_claim(dispatcher, {"profile": {"mean": 2.5}, "artifactIds": ["artifact-a"]})
    second = complete_claim(dispatcher, {"profile": {"mean": 3.5}, "artifactId": "artifact-b"})
    assert {first["queueItem"]["workload"]["id"].rsplit("-", 1)[-1], second["queueItem"]["workload"]["id"].rsplit("-", 1)[-1]} == {"a", "b"}

    reconciled = orchestrator.reconcile(started["id"])
    assert reconciled["run"]["nodeCounts"]["completed"] == 2
    assert reconciled["run"]["nodeCounts"]["queued"] == 1
    calibrate = next(node for node in reconciled["run"]["nodes"] if node["nodeId"] == "calibrate")
    queue_item = dispatcher.queue_item(calibrate["queueId"])["queueItem"]
    request = queue_item["workload"]["request"]
    assert request["inputs"]["initialMean"] == 2.5
    assert set(request["workflowContext"]["dependencyArtifactIds"]) == {"artifact-a", "artifact-b"}
    assert {item["artifactId"] for item in queue_item["workload"]["artifactInputs"]} == {"artifact-a", "artifact-b"}
    assert queue_item["maxAttempts"] == 4

    complete_claim(dispatcher, {"parameters": {"slope": 1.2}, "resultArtifactId": "artifact-final"})
    final = orchestrator.reconcile(started["id"])["run"]
    assert final["status"] == "completed"
    assert final["nodeCounts"]["completed"] == 3
    timeline = orchestrator.timeline(started["id"])["events"]
    assert any(event["eventType"] == "run-completed" for event in timeline)


def test_failed_node_stops_downstream_and_preserves_timeline(tmp_path: Path):
    dispatcher, orchestrator = make(tmp_path)
    run_id = orchestrator.start_run("calibration-pipeline")["run"]["id"]
    complete_claim(dispatcher, {}, ok=False, error="input validation failed: malformed dataset")
    complete_claim(dispatcher, {"profile": {"mean": 4.0}})
    failed = orchestrator.reconcile(run_id)["run"]
    assert failed["status"] == "failed"
    assert failed["nodeCounts"]["failed"] == 1
    assert failed["nodeCounts"]["skipped"] == 1
    assert failed["nodeCounts"]["completed"] == 1
    assert any(event["eventType"] == "run-failed" for event in orchestrator.timeline(run_id)["events"])


def test_workflow_database_persists_definitions_runs_and_node_queue_ids(tmp_path: Path):
    dispatcher, orchestrator = make(tmp_path)
    run_id = orchestrator.start_run("calibration-pipeline")["run"]["id"]
    reopened = WorkflowOrchestrator(str(tmp_path / "workflows.sqlite3"), dispatcher)
    restored = reopened.run(run_id, reconcile=False)["run"]
    assert restored["workflowId"] == "calibration-pipeline"
    assert restored["nodeCounts"]["queued"] == 2
    assert all(node["queueId"] for node in restored["nodes"] if node["status"] == "queued")
    health = reopened.health()
    assert health["integrityCheck"] == "ok"
    assert health["definitionCount"] == 1
    assert health["runCount"] == 1


def test_cancel_run_cancels_active_dispatch_items(tmp_path: Path):
    dispatcher, orchestrator = make(tmp_path)
    run_id = orchestrator.start_run("calibration-pipeline")["run"]["id"]
    cancelled = orchestrator.cancel(run_id, {"operatorId": "admin", "reason": "campaign withdrawn"})["run"]
    assert cancelled["status"] == "cancelled"
    assert cancelled["nodeCounts"]["cancelled"] == 3
    for node in cancelled["nodes"]:
        if node["queueId"]:
            assert dispatcher.queue_item(node["queueId"])["queueItem"]["status"] == "cancelled"


def test_fastapi_workflow_routes(monkeypatch, tmp_path: Path):
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

    health = client.get("/v1/workflows/health", headers=headers)
    assert health.status_code == 200
    assert health.json()["version"] == "0.32.0"
    assert client.get("/v1/workflows/policies", headers=headers).json()["execution"]["dependencyAwareScheduling"] is True
    assert client.post("/v1/workflows/validate", json=definition(), headers=headers).json()["valid"] is True
    saved = client.post("/v1/workflows", json=definition(), headers=headers)
    assert saved.status_code == 200
    run = client.post("/v1/workflows/calibration-pipeline/runs", json={}, headers=headers)
    assert run.status_code == 200
    run_id = run.json()["run"]["id"]
    assert client.get(f"/v1/workflow-runs/{run_id}?reconcile=false", headers=headers).status_code == 200
    assert client.get(f"/v1/workflow-runs/{run_id}/timeline", headers=headers).status_code == 200
    assert client.post(f"/v1/workflow-runs/{run_id}/cancel", json={"reason": "route test"}, headers=headers).status_code == 200
