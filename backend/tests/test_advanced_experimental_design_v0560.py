from __future__ import annotations

import pytest

from app.advanced_experimental_design import (
    AdvancedExperimentalDesignError,
    design_diagnostics,
    generate_optimal_design,
    health,
    normalize_spec,
    sequential_plan,
    verify_record,
)


def factors():
    return [
        {"name": "temperature", "type": "continuous", "low": 10, "high": 30, "unit": "degC"},
        {"name": "pressure", "type": "continuous", "low": 1, "high": 3, "unit": "bar"},
    ]


def test_health_declares_proposal_only_safety():
    h = health()
    assert h["version"] == "0.56.0"
    assert h["capabilities"]["automaticExperimentExecution"] is False
    assert h["capabilities"]["automaticStopping"] is False


def test_normalize_spec_is_bounded_and_hashed():
    spec = normalize_spec({"factors": factors(), "criterion": "d-optimal", "modelOrder": "linear", "runBudget": 8, "candidatePoolSize": 100})
    assert spec["runBudget"] == 8
    assert spec["candidatePoolSize"] == 100
    assert len(spec["specHash"]) == 64


def test_d_optimal_design_is_reproducible_and_full_rank_linear():
    payload = {"title": "Thermal pressure design", "factors": factors(), "criterion": "d-optimal", "modelOrder": "linear", "runBudget": 8, "candidatePoolSize": 120, "seed": 11}
    first = generate_optimal_design(payload)["design"]
    second = generate_optimal_design(payload)["design"]
    assert first["designHash"] == second["designHash"]
    assert first["runCount"] == 8
    assert first["diagnostics"]["fullRank"] is True


def test_blocking_and_center_replication_are_recorded():
    design = generate_optimal_design({"factors": factors(), "modelOrder": "linear", "runBudget": 8, "blockCount": 2, "centerReplicates": 2, "randomizeRunOrder": False})["design"]
    assert set(r["block"] for r in design["rows"]) == {1, 2}
    centers = [r for r in design["rows"] if all(abs(v) < 0.05 for v in r["codedVector"])]
    assert len(centers) >= 2


def test_maximin_design_spreads_points():
    design = generate_optimal_design({"factors": factors(), "criterion": "maximin", "modelOrder": "linear", "runBudget": 6, "candidatePoolSize": 100})["design"]
    assert design["diagnostics"]["minPairwiseDistance"] is not None
    assert design["diagnostics"]["minPairwiseDistance"] > 0


def test_information_gain_sequential_plan_proposes_unused_points():
    design = generate_optimal_design({"factors": factors(), "modelOrder": "linear", "runBudget": 6, "candidatePoolSize": 100, "randomizeRunOrder": False})["design"]
    existing = design["rows"][:4]
    out = sequential_plan({"spec": {"factors": factors(), "modelOrder": "linear", "runBudget": 10, "candidatePoolSize": 120, "randomizeRunOrder": False}, "existingRows": existing, "strategy": "information-gain", "batchSize": 3, "maxTotalRuns": 10})["plan"]
    assert out["proposedRunCount"] == 3
    existing_vectors = {tuple(round(v, 8) for v in r["codedVector"]) for r in existing}
    assert all(tuple(round(v, 8) for v in r["codedVector"]) not in existing_vectors for r in out["proposedRows"])
    assert out["automaticExecutionAuthorized"] is False


def test_response_guided_plan_requires_enough_completed_responses():
    design = generate_optimal_design({"factors": factors(), "modelOrder": "linear", "runBudget": 5, "randomizeRunOrder": False})["design"]
    existing = design["rows"][:2]
    existing[0]["response"] = 1.0
    with pytest.raises(AdvancedExperimentalDesignError):
        sequential_plan({"spec": {"factors": factors(), "modelOrder": "linear", "runBudget": 10}, "existingRows": existing, "strategy": "response-guided", "batchSize": 2})


def test_response_guided_plan_records_predictions_and_warning():
    design = generate_optimal_design({"factors": factors(), "modelOrder": "linear", "runBudget": 7, "candidatePoolSize": 120, "randomizeRunOrder": False})["design"]
    existing = design["rows"][:5]
    for row in existing:
        t, p = row["codedVector"]
        row["response"] = 2.0 + 1.5 * t - 0.5 * p
    plan = sequential_plan({"spec": {"factors": factors(), "modelOrder": "linear", "objective": "maximize", "runBudget": 10, "candidatePoolSize": 140}, "existingRows": existing, "strategy": "response-guided", "batchSize": 2})["plan"]
    assert plan["proposedRunCount"] == 2
    assert "predictedResponse" in plan["proposedRows"][0]
    assert plan["warnings"]


def test_budget_reached_returns_stop_proposal():
    design = generate_optimal_design({"factors": factors(), "modelOrder": "linear", "runBudget": 4, "randomizeRunOrder": False})["design"]
    plan = sequential_plan({"spec": {"factors": factors(), "modelOrder": "linear", "runBudget": 4}, "existingRows": design["rows"], "maxTotalRuns": 4})["plan"]
    assert plan["recommendation"] == "stop"
    assert plan["proposedRows"] == []


def test_verify_detects_tampering():
    design = generate_optimal_design({"factors": factors(), "modelOrder": "linear", "runBudget": 6})["design"]
    assert verify_record({"record": design})["ok"] is True
    design["rows"][0]["block"] = 99
    assert verify_record({"record": design})["ok"] is False


def test_diagnostics_warn_rank_deficiency():
    rows = [{"codedVector": [0.0, 0.0]}, {"codedVector": [0.0, 0.0]}]
    diagnostics = design_diagnostics(rows, "quadratic")
    assert diagnostics["fullRank"] is False
    assert diagnostics["warnings"]
