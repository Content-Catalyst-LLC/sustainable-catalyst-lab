from __future__ import annotations

import copy
import importlib
from pathlib import Path

import pytest

from app.experiment_campaigns import ExperimentCampaignError, ExperimentCampaignManager, normalize_campaign


class StubWorkflows:
    def __init__(self):
        self.definitions = {"campaign-workflow": {"id": "campaign-workflow"}}
        self.runs = {}
        self.counter = 0

    def get(self, workflow_id):
        if workflow_id not in self.definitions:
            raise Exception("workflow missing")
        return {"ok": True, "workflow": self.definitions[workflow_id]}

    def start_run(self, workflow_id, payload):
        self.get(workflow_id)
        self.counter += 1
        run_id = payload.get("id") or f"run-{self.counter}"
        self.runs[run_id] = {
            "id": run_id,
            "workflowId": workflow_id,
            "status": "running",
            "inputs": copy.deepcopy(payload.get("inputs", {})),
            "context": copy.deepcopy(payload.get("context", {})),
            "nodes": [{"nodeId": "evaluate", "status": "running", "result": None}],
            "error": None,
        }
        return {"ok": True, "run": copy.deepcopy(self.runs[run_id])}

    def run(self, run_id, reconcile=True):
        del reconcile
        return {"ok": True, "run": copy.deepcopy(self.runs[run_id])}

    def complete(self, run_id, objective):
        self.runs[run_id]["status"] = "completed"
        self.runs[run_id]["nodes"] = [{"nodeId": "evaluate", "status": "completed", "result": {"metrics": {"score": objective}}}]

    def fail(self, run_id):
        self.runs[run_id]["status"] = "failed"
        self.runs[run_id]["error"] = "simulated failure"

    def cancel(self, run_id, payload):
        del payload
        self.runs[run_id]["status"] = "cancelled"
        return {"ok": True, "run": copy.deepcopy(self.runs[run_id])}


def campaign_payload(**changes):
    payload = {
        "id": "adaptive-calibration",
        "workflowId": "campaign-workflow",
        "projectId": "test",
        "parameterSpace": {
            "learningRate": {"type": "continuous", "min": 0.001, "max": 0.1, "precision": 6},
            "iterations": {"type": "integer", "min": 10, "max": 50, "step": 10},
            "solver": {"type": "categorical", "values": ["a", "b"]},
        },
        "objective": {"path": "nodes.evaluate.result.metrics.score", "goal": "minimize"},
        "strategy": {"type": "adaptive-explore-exploit", "initialRandomTrials": 1, "explorationRate": 0.0, "neighborhoodScale": 0.1, "randomSeed": 44},
        "budget": {"maxTrials": 5, "maxFailures": 2, "maxConcurrentTrials": 1},
        "stopping": {"patience": 4, "minImprovement": 0.001},
        "run": {"parameterInputPath": "study.parameters", "autoAdvance": True},
    }
    payload.update(changes)
    return payload


def test_normalize_campaign_contract_and_rejections():
    record = normalize_campaign(campaign_payload())
    assert record["schema"].endswith("0.33.0")
    assert record["budget"]["maxConcurrentTrials"] == 1
    assert record["definitionHash"]
    with pytest.raises(ExperimentCampaignError):
        normalize_campaign({**campaign_payload(), "parameterSpace": {}})
    with pytest.raises(ExperimentCampaignError):
        normalize_campaign({**campaign_payload(), "objective": {"path": "unsafe.value", "goal": "minimize"}})


def test_start_complete_and_adaptive_advance(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows, poll_seconds=60)
    manager.save(campaign_payload())
    started = manager.start_campaign("adaptive-calibration")
    assert started["launchedCount"] == 1
    first = started["campaign"]["trials"][0]
    assert first["status"] == "running"
    assert workflows.runs[first["workflowRunId"]]["inputs"]["study"]["parameters"] == first["parameters"]
    workflows.complete(first["workflowRunId"], 10.0)
    reconciled = manager.reconcile("adaptive-calibration", auto_advance=True)
    trials = reconciled["campaign"]["trials"]
    assert trials[0]["objectiveValue"] == 10.0
    assert reconciled["campaign"]["bestTrialId"] == first["id"]
    assert len(trials) == 2
    assert trials[1]["proposal"]["source"] == "exploit-best-neighborhood"
    assert trials[1]["parametersHash"] != trials[0]["parametersHash"]


def test_target_stopping_prevents_more_trials(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    payload = campaign_payload(stopping={"patience": 4, "minImprovement": 0.0, "target": 2.0})
    manager.save(payload)
    started = manager.start_campaign("adaptive-calibration")
    trial = started["campaign"]["trials"][0]
    workflows.complete(trial["workflowRunId"], 1.5)
    result = manager.reconcile("adaptive-calibration", auto_advance=True)
    assert result["campaign"]["status"] == "completed"
    assert result["campaign"]["stopReason"] == "target-objective-reached"
    assert len(result["campaign"]["trials"]) == 1


def test_manual_observation_updates_best_and_deduplicates(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    manager.save(campaign_payload())
    observed = manager.observe("adaptive-calibration", {"parameters": {"learningRate": 0.01, "iterations": 20, "solver": "a"}, "objectiveValue": 4.0, "source": "bench test"})
    assert observed["campaign"]["bestObjective"] == 4.0
    assert observed["trial"]["proposal"]["strategy"] == "manual-observation"
    with pytest.raises(ExperimentCampaignError):
        manager.observe("adaptive-calibration", {"parameters": {"learningRate": 0.01, "iterations": 20, "solver": "a"}, "objectiveValue": 3.0})


def test_pause_resume_cancel_and_persistence(tmp_path: Path):
    workflows = StubWorkflows()
    db = str(tmp_path / "campaigns.sqlite3")
    manager = ExperimentCampaignManager(db, workflows)
    manager.save(campaign_payload())
    started = manager.start_campaign("adaptive-calibration")
    paused = manager.pause("adaptive-calibration", "inspect instrumentation")
    assert paused["campaign"]["status"] == "paused"
    resumed = manager.resume("adaptive-calibration")
    assert resumed["campaign"]["status"] == "running"
    cancelled = manager.cancel("adaptive-calibration", "stop study")
    assert cancelled["campaign"]["status"] == "cancelled"
    assert all(trial["status"] == "cancelled" for trial in cancelled["campaign"]["trials"])
    reopened = ExperimentCampaignManager(db, workflows)
    assert reopened.get("adaptive-calibration")["campaign"]["stopReason"] == "stop study"
    assert started["campaign"]["trials"][0]["workflowRunId"] in workflows.runs


def test_grid_proposals_are_deterministic_and_unique(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    manager.save(campaign_payload(strategy={"type": "grid", "gridLevels": 3, "randomSeed": 9}, budget={"maxTrials": 4, "maxFailures": 2, "maxConcurrentTrials": 2}))
    result = manager.start_campaign("adaptive-calibration")
    assert result["launchedCount"] == 2
    hashes = [trial["parametersHash"] for trial in result["campaign"]["trials"]]
    assert len(hashes) == len(set(hashes))


def test_fastapi_campaign_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_DB_PATH", str(tmp_path / "workflows.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_SCHEDULE_DB_PATH", str(tmp_path / "schedules.sqlite3"))
    monkeypatch.setenv("SC_LAB_EXPERIMENT_CAMPAIGN_DB_PATH", str(tmp_path / "campaigns.sqlite3"))
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(tmp_path / "jobs.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "campaign-key")
    import app.config as config
    import app.main as main
    importlib.reload(config)
    importlib.reload(main)
    from fastapi.testclient import TestClient
    headers = {"X-SC-Lab-Key": "campaign-key"}
    workflow = {"id": "campaign-workflow", "projectId": "test", "nodes": [{"id": "evaluate", "method": "dataset.profile", "request": {"inputs": {"records": []}}}]}
    with TestClient(main.app) as client:
        assert client.post("/v1/workflows", json=workflow, headers=headers).status_code == 200
        assert client.post("/v1/experiment-campaigns/validate", json=campaign_payload(), headers=headers).status_code == 200
        saved = client.post("/v1/experiment-campaigns", json=campaign_payload(), headers=headers)
        assert saved.status_code == 200
        started = client.post("/v1/experiment-campaigns/adaptive-calibration/start", headers=headers)
        assert started.status_code == 200
        assert started.json()["launchedCount"] == 1
        assert client.get("/v1/experiment-campaigns", headers=headers).json()["count"] == 1
        health = client.get("/v1/experiment-campaigns/health", headers=headers).json()
        assert health["version"] == "0.33.0"
        assert health["serviceVersion"] == "0.33.0"
