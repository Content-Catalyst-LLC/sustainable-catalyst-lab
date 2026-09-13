from copy import deepcopy

import pytest

from app.energy_modeling_uncertainty import (
    ANALYSIS_SCHEMA,
    EnergyModelingError,
    framework,
    plan,
    analyze,
    validate_result,
)


def _request(samples=16):
    return {
        "study_id": "energy-uncertainty-test",
        "question": "How does capacity-factor uncertainty propagate into annual generation?",
        "calculation_request": {
            "section": "energy_balance",
            "operation": "capacity-factor-generation",
            "inputs": {"capacity_kw": 100, "capacity_factor_pct": 50, "hours": 8760},
            "source_refs": ["test-source"],
            "assumptions": ["capacity fixed for test"],
        },
        "uncertainty": {
            "variables": [{"name": "capacity_factor_pct", "distribution": "triangular", "low": 40, "mode": 50, "high": 60, "unit": "%"}],
            "design": {"method": "latin-hypercube", "samples": samples, "seed": 2026},
        },
        "output": {"result_path": "generation_kwh", "unit": "kWh", "confidence": 0.95, "thresholds": [438000]},
        "provenance": [{"source_ref": "test-source"}],
        "review": {"human_review_required": True},
    }


def _fake_workbench(p):
    results = []
    for item in p["evaluation_map"]:
        cf = item["sampled_inputs"]["capacity_factor_pct"]
        results.append({
            "schema": "sc-energy-workbench-execution-result/1.0",
            "result_id": "ewr-test-" + item["request_id"],
            "request_id": item["request_id"],
            "operation": "capacity-factor-generation",
            "output": {"generation_kwh": str(100 * 8760 * cf / 100)},
        })
    return {
        "ok": True,
        "schema": "sc-energy-workbench-result-packet/1.0",
        "version": "1.3.0",
        "workbench_version": "6.2.0",
        "result_packet_id": "ewb-test-packet",
        "results": results,
        "provenance": [{"source_ref": "test-source"}],
    }


def test_framework_declares_safe_boundary():
    f = framework()
    assert f["lab_version"] == "0.102.0"
    assert f["version"] == "1.4.0"
    assert f["capabilities"]["automatic_workbench_execution"] is False
    assert f["capabilities"]["technology_ranking"] is False


def test_plan_is_deterministic_and_workbench_compatible():
    a = plan(_request())
    b = plan(_request())
    assert a["plan_id"] == b["plan_id"]
    assert a["evaluation_map"] == b["evaluation_map"]
    assert a["evaluation_count"] == 16
    handoff = a["workbench"]["handoff"]
    assert handoff["schema"] == "sc-energy-runtime-handoff/1.0"
    requests = handoff["packet"]["payload"]["energy_balance"]["calculation_requests"]
    assert len(requests) == 16
    assert handoff["packet"]["target"]["key"] == "workbench"
    assert a["workbench"]["execution_performed"] is False


def test_plan_requires_explicit_seed_and_distribution():
    body = _request()
    del body["uncertainty"]["design"]["seed"]
    with pytest.raises(EnergyModelingError):
        plan(body)
    body = _request()
    del body["uncertainty"]["variables"][0]["distribution"]
    with pytest.raises(EnergyModelingError):
        plan(body)


def test_analysis_summarizes_workbench_results_and_validates():
    p = plan(_request(32))
    result = analyze({"plan": p, "workbench_result": _fake_workbench(p)})
    assert result["schema"] == ANALYSIS_SCHEMA
    assert result["summary"]["count"] == 32
    assert result["summary"]["minimum"] < result["summary"]["maximum"]
    assert len(result["sensitivity"]["variables"]) == 1
    assert result["sensitivity"]["ranking_semantics"] == "input influence only; not technology ranking"
    assert result["persistence"]["performed"] is False
    assert result["recommendation"]["performed"] is False
    v = validate_result(result)
    assert v["ok"] is True
    assert v["valid"] is True


def test_analysis_rejects_incomplete_workbench_results():
    p = plan(_request())
    wb = _fake_workbench(p)
    wb["results"] = wb["results"][:-1]
    with pytest.raises(EnergyModelingError):
        analyze({"plan": p, "workbench_result": wb})
