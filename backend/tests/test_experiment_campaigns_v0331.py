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

    def complete(self, run_id, objective, cost=None):
        self.runs[run_id]["status"] = "completed"
        metrics = {"score": objective}
        if cost is not None:
            metrics["cost"] = cost
        self.runs[run_id]["nodes"] = [{"nodeId": "evaluate", "status": "completed", "result": {"metrics": metrics}}]

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
    assert record["schema"].endswith("0.33.1")
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
        assert health["version"] == "0.33.1"
        assert health["serviceVersion"] == "0.38.2"



def bayesian_payload(strategy_type="bayesian-optimization", **changes):
    payload = campaign_payload(
        id="bayesian-calibration",
        strategy={
            "type": strategy_type,
            "initialRandomTrials": 3,
            "candidatePoolSize": 128,
            "kernel": "matern52",
            "acquisition": "max-variance" if strategy_type == "active-learning" else "expected-improvement",
            "randomSeed": 331,
            "costExponent": 1.0,
        },
        budget={"maxTrials": 12, "maxFailures": 3, "maxConcurrentTrials": 1},
        resourceModel={
            "enabled": strategy_type == "resource-aware-bayesian",
            "baseCost": 1.0,
            "parameterWeights": {"iterations": 5.0},
            "categoricalCosts": {"solver": {"b": 3.0}},
            "resultCostPath": "nodes.evaluate.result.metrics.cost",
            "maxEstimatedCostPerTrial": 10.0,
            "maxTotalCost": 50.0,
        },
    )
    payload.update(changes)
    return payload


def test_bayesian_normalization_and_policy_catalog():
    record = normalize_campaign(bayesian_payload())
    assert record["version"] == "0.33.1"
    assert record["strategy"]["kernel"] == "matern52"
    assert record["strategy"]["acquisition"] == "expected-improvement"
    assert record["resourceModel"]["parameterWeights"]["iterations"] == 5.0
    with pytest.raises(ExperimentCampaignError):
        normalize_campaign(bayesian_payload(strategy={"type": "bayesian-optimization", "acquisition": "unsafe-eval"}))


def test_surrogate_preview_after_manual_observations(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    manager.save(bayesian_payload())
    observations = [
        ({"learningRate": 0.005, "iterations": 10, "solver": "a"}, 8.5),
        ({"learningRate": 0.02, "iterations": 20, "solver": "a"}, 5.2),
        ({"learningRate": 0.04, "iterations": 30, "solver": "b"}, 4.1),
        ({"learningRate": 0.08, "iterations": 40, "solver": "a"}, 6.7),
    ]
    for parameters, objective in observations:
        manager.observe("bayesian-calibration", {"parameters": parameters, "objectiveValue": objective, "costValue": 1.5})
    preview = manager.preview_proposal("bayesian-calibration")
    assert preview["surrogate"]["trained"] is True
    assert preview["proposal"]["source"] == "surrogate-acquisition"
    assert preview["proposal"]["prediction"]["standardDeviation"] > 0
    assert preview["proposal"]["acquisition"]["policy"] == "expected-improvement"
    assert preview["parametersHash"] not in {trial["parametersHash"] for trial in manager.get("bayesian-calibration")["campaign"]["trials"]}


def test_active_learning_uses_predictive_variance(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    manager.save(bayesian_payload("active-learning"))
    for parameters, objective in [
        ({"learningRate": 0.001, "iterations": 10, "solver": "a"}, 8.0),
        ({"learningRate": 0.05, "iterations": 30, "solver": "b"}, 4.0),
        ({"learningRate": 0.1, "iterations": 50, "solver": "a"}, 7.0),
    ]:
        manager.observe("bayesian-calibration", {"parameters": parameters, "objectiveValue": objective})
    preview = manager.preview_proposal("bayesian-calibration")
    assert preview["proposal"]["acquisition"]["policy"] == "max-variance"
    assert preview["proposal"]["acquisition"]["rawValue"] == pytest.approx(preview["proposal"]["prediction"]["standardDeviation"])


def test_resource_aware_trial_records_estimated_and_observed_cost(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    manager.save(bayesian_payload("resource-aware-bayesian"))
    started = manager.start_campaign("bayesian-calibration")
    trial = started["campaign"]["trials"][0]
    assert trial["estimatedCost"] > 0
    workflows.complete(trial["workflowRunId"], 3.0, cost=2.75)
    result = manager.reconcile("bayesian-calibration", auto_advance=False)
    completed = result["campaign"]["trials"][0]
    assert completed["observedCost"] == 2.75
    assert result["campaign"]["cumulativeCost"] == 2.75
    assert completed["resource"]["source"] == "workflow-result"


def test_campaign_database_v1_migrates_to_v2(tmp_path: Path):
    import sqlite3
    db = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(db) as con:
        con.executescript("""
        CREATE TABLE experiment_campaign_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE experiment_campaigns(id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, project_id TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, definition_hash TEXT NOT NULL, definition_json TEXT NOT NULL, best_trial_id TEXT, best_objective REAL, no_improvement_count INTEGER NOT NULL DEFAULT 0, stop_reason TEXT, created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL);
        CREATE TABLE experiment_trials(id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL, sequence_no INTEGER NOT NULL, status TEXT NOT NULL, parameters_hash TEXT NOT NULL, parameters_json TEXT NOT NULL, proposal_json TEXT NOT NULL, workflow_run_id TEXT, objective_value REAL, objective_json TEXT, result_json TEXT, error_text TEXT, created_at TEXT NOT NULL, started_at TEXT, completed_at TEXT, updated_at TEXT NOT NULL, UNIQUE(campaign_id, sequence_no), UNIQUE(campaign_id, parameters_hash));
        CREATE TABLE experiment_campaign_events(id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id TEXT NOT NULL, trial_id TEXT, event_type TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL);
        INSERT INTO experiment_campaign_meta(key,value) VALUES('schema_version','1');
        """)
    manager = ExperimentCampaignManager(str(db), StubWorkflows())
    health = manager.health()
    assert health["schemaVersion"] == 2
    with sqlite3.connect(db) as con:
        campaign_columns = {row[1] for row in con.execute("PRAGMA table_info(experiment_campaigns)")}
        trial_columns = {row[1] for row in con.execute("PRAGMA table_info(experiment_trials)")}
    assert {"cumulative_cost", "model_json"} <= campaign_columns
    assert {"predicted_mean", "predicted_std", "acquisition_value", "estimated_cost", "observed_cost"} <= trial_columns


def test_fastapi_bayesian_preview_and_surrogate_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher-bayes.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_DB_PATH", str(tmp_path / "workflows-bayes.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_SCHEDULE_DB_PATH", str(tmp_path / "schedules-bayes.sqlite3"))
    monkeypatch.setenv("SC_LAB_EXPERIMENT_CAMPAIGN_DB_PATH", str(tmp_path / "campaigns-bayes.sqlite3"))
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(tmp_path / "jobs-bayes.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts-bayes"))
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
        assert client.post("/v1/experiment-campaigns", json=bayesian_payload(), headers=headers).status_code == 200
        for parameters, objective in [
            ({"learningRate": 0.005, "iterations": 10, "solver": "a"}, 8.5),
            ({"learningRate": 0.02, "iterations": 20, "solver": "a"}, 5.2),
            ({"learningRate": 0.04, "iterations": 30, "solver": "b"}, 4.1),
        ]:
            response = client.post("/v1/experiment-campaigns/bayesian-calibration/observations", json={"parameters": parameters, "objectiveValue": objective}, headers=headers)
            assert response.status_code == 200
        preview = client.post("/v1/experiment-campaigns/bayesian-calibration/proposal-preview", headers=headers)
        assert preview.status_code == 200
        assert preview.json()["surrogate"]["trained"] is True
        surrogate = client.get("/v1/experiment-campaigns/bayesian-calibration/surrogate", headers=headers)
        assert surrogate.status_code == 200
        assert surrogate.json()["observationCount"] == 3


def test_initial_bayesian_design_respects_per_trial_cost_limit(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    payload = bayesian_payload(
        "resource-aware-bayesian",
        resourceModel={
            "enabled": True,
            "baseCost": 1.0,
            "parameterWeights": {"iterations": 20.0},
            "categoricalCosts": {"solver": {"b": 50.0}},
            "resultCostPath": "nodes.evaluate.result.metrics.cost",
            "maxEstimatedCostPerTrial": 8.0,
            "maxTotalCost": 30.0,
        },
    )
    manager.save(payload)
    preview = manager.preview_proposal("bayesian-calibration")
    assert preview["proposal"]["estimatedCost"] <= 8.0


def test_resource_budget_reserves_active_trial_costs(tmp_path: Path):
    workflows = StubWorkflows()
    manager = ExperimentCampaignManager(str(tmp_path / "campaigns.sqlite3"), workflows)
    payload = bayesian_payload(
        "resource-aware-bayesian",
        budget={"maxTrials": 5, "maxFailures": 2, "maxConcurrentTrials": 2},
        resourceModel={
            "enabled": True,
            "baseCost": 6.0,
            "parameterWeights": {},
            "categoricalCosts": {},
            "resultCostPath": "nodes.evaluate.result.metrics.cost",
            "maxEstimatedCostPerTrial": 10.0,
            "maxTotalCost": 10.0,
        },
    )
    manager.save(payload)
    started = manager.start_campaign("bayesian-calibration")
    assert started["launchedCount"] == 1
    assert len(started["campaign"]["trials"]) == 1
    blocked = manager.advance("bayesian-calibration", 1)
    assert blocked["launchedCount"] == 0
    assert blocked["campaign"]["status"] == "running"
