from pathlib import Path

import pytest

from app.batch_experiment_sweep_ensemble_v01550 import (
    BatchCampaignError,
    BatchExperimentCampaignManager,
    MANIFEST_SCHEMA,
    VERSION,
    generate_trials,
    normalize_campaign,
)


def manager(tmp_path: Path) -> BatchExperimentCampaignManager:
    return BatchExperimentCampaignManager(str(tmp_path / "batch.sqlite3"), True, 20, 500, 1000)


def sweep_payload():
    return {
        "title": "Response sweep",
        "objective": "Compare bounded parameter combinations.",
        "mode": "parameter-sweep",
        "method": "simulation.parameter_sweep",
        "parameters": [
            {"name": "rate", "path": "rate", "values": [0.1, 0.2, 0.3]},
            {"name": "capacity", "path": "capacity", "values": [50, 100]},
        ],
        "repeats": 2,
        "baseSeed": 42,
        "requestedOutputs": ["summary", "values"],
        "metrics": ["score"],
    }


def test_health_and_policy_boundary(tmp_path):
    m = manager(tmp_path)
    h = m.health()
    assert h["version"] == VERSION
    assert h["automaticDispatch"] is False
    assert h["arbitraryCodeExecution"] is False
    assert h["partialFailureRecovery"] is True
    assert "monte-carlo" in h["campaignModes"]
    assert m.policies()["executionAuthority"] == "Workspace/runtime fabric"


def test_grid_trials_are_deterministic_and_repeated():
    d = normalize_campaign(sweep_payload(), 500)
    a = generate_trials(d, 500)
    b = generate_trials(d, 500)
    assert len(a) == 12
    assert [x["seed"] for x in a] == [x["seed"] for x in b]
    assert [x["specHash"] for x in a] == [x["specHash"] for x in b]


def test_campaign_creation_and_execution_handoff(tmp_path):
    m = manager(tmp_path)
    out = m.create("project:test", sweep_payload(), "tester")
    cid = out["campaign"]["id"]
    assert out["totalTrials"] == 12
    handoffs = m.execution_batch(cid, 3)
    assert handoffs["count"] == 3
    assert handoffs["automaticDispatch"] is False
    assert all(h["schema"].endswith("/0.155.0") for h in handoffs["handoffs"])
    assert all(h["dispatchRequested"] is False for h in handoffs["handoffs"])


def test_partial_failure_retry_and_aggregation(tmp_path):
    m = manager(tmp_path)
    out = m.create("project:test", sweep_payload(), "tester")
    cid = out["campaign"]["id"]
    t1, t2 = out["trials"][:2]
    m.record_trial_state(cid, t1["id"], {"status": "succeeded", "executionRef": "run:1", "resultRef": "result:1", "metrics": {"score": 2.0}}, "tester")
    state = m.record_trial_state(cid, t2["id"], {"status": "failed", "executionRef": "run:2", "error": "worker error"}, "tester")
    assert state["campaign"]["status"] == "partial-failure"
    agg = m.aggregate(cid)
    assert agg["metrics"]["score"]["mean"] == 2.0
    retried = m.retry_failed(cid, "tester")
    assert retried["retryCount"] == 1
    assert m.trial(t2["id"])["attempt"] == 2
    assert m.trial(t2["id"])["status"] == "planned"


def test_manifest_digest_verification(tmp_path):
    m = manager(tmp_path)
    cid = m.create("project:test", sweep_payload(), "tester")["campaign"]["id"]
    manifest = m.manifest(cid)["manifest"]
    assert manifest["schema"] == MANIFEST_SCHEMA
    assert m.verify_manifest({"manifest": manifest})["ok"] is True
    bad = dict(manifest); bad["projectId"] = "project:other"
    assert m.verify_manifest({"manifest": bad})["ok"] is False


def test_monte_carlo_and_ensemble_modes(tmp_path):
    monte = normalize_campaign({
        "title": "Monte Carlo", "mode": "monte-carlo", "method": "simulation.run", "samples": 15,
        "parameters": [{"name": "x", "min": 0, "max": 1, "distribution": "uniform"}], "baseSeed": 7,
    }, 500)
    assert len(generate_trials(monte, 500)) == 15
    ensemble = normalize_campaign({
        "title": "Ensemble", "mode": "ensemble", "method": "model.predict", "repeats": 2,
        "members": [{"ref": "model:a", "weight": 0.4}, {"ref": "model:b", "weight": 0.6}],
    }, 500)
    assert len(generate_trials(ensemble, 500)) == 4


def test_invalid_modes_and_unbounded_campaigns_rejected():
    bad = sweep_payload(); bad["mode"] = "arbitrary-code"
    with pytest.raises(BatchCampaignError):
        normalize_campaign(bad, 500)
    huge = sweep_payload(); huge["parameters"] = [{"name": "a", "values": list(range(30))}, {"name": "b", "values": list(range(30))}]
    with pytest.raises(BatchCampaignError):
        generate_trials(normalize_campaign(huge, 500), 500)
