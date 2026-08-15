import math
import pytest

from app.probabilistic_analysis import (
    ProbabilisticAnalysisError,
    analyze,
    health,
    normalize_study,
    policies,
)


def decay_model():
    return {
        "family": "declarative-expression",
        "title": "Exponential decay",
        "definition": {"equation": "y = a * exp(-k*x)"},
        "variables": [
            {"symbol": "x", "label": "Time", "unit": "s", "role": "input"},
            {"symbol": "y", "label": "Concentration", "unit": "mg/L", "role": "response"},
        ],
        "parameters": [
            {"symbol": "a", "role": "estimated", "value": 10, "bounds": {"lower": 0, "upper": 20}},
            {"symbol": "k", "role": "estimated", "value": 0.3, "bounds": {"lower": 0.01, "upper": 1}},
        ],
        "constants": [],
        "datasetBindings": [],
    }


def study(method="latin-hypercube", samples=256, curve=False):
    payload = {
        "title": "Decay uncertainty",
        "model": decay_model(),
        "values": {"x": 5},
        "uncertainInputs": [
            {"symbol": "a", "distribution": "normal", "mean": 10, "stdDev": 0.5},
            {"symbol": "k", "distribution": "normal", "mean": 0.3, "stdDev": 0.02},
        ],
        "design": {"method": method, "samples": samples, "seed": 42},
        "analysis": {"confidence": 0.95, "thresholds": [2.0]},
    }
    if curve:
        payload["curve"] = {"xSymbol": "x", "start": 0, "stop": 10, "points": 17}
    return payload


def test_health_and_policy_contract():
    assert health()["version"] == "0.48.0"
    p = policies()
    assert "saltelli-sobol" in p["designs"]
    assert p["safeDeclarativeModels"] is True
    assert p["arbitraryCode"] is False
    assert p["registeredModelEnsembles"] == "ensemble-uncertainty-v0341"


def test_normalize_study_preserves_explicit_assumptions():
    normalized = normalize_study(study())
    assert normalized["schema"] == "sc-lab-probabilistic-study/0.48.0"
    assert normalized["design"]["evaluationCount"] == 256
    assert normalized["governance"]["independentInputs"] is True
    assert normalized["uncertainInputs"][0]["distribution"] == "normal"
    assert len(normalized["studyHash"]) == 64


def test_latin_hypercube_analysis_is_seeded_and_reproducible():
    first = analyze(study())["result"]
    second = analyze(study())["result"]
    assert first["summary"] == second["summary"]
    assert first["sensitivity"] == second["sensitivity"]
    assert first["summary"]["count"] == 256
    assert first["summary"]["centralInterval"]["lower"] < first["summary"]["median"] < first["summary"]["centralInterval"]["upper"]


def test_probability_thresholds_and_distribution_graphs_are_generated():
    result = analyze(study())["result"]
    probability = result["summary"]["thresholdProbabilities"][0]
    assert 0 <= probability["probabilityAbove"] <= 1
    assert math.isclose(probability["probabilityAbove"] + probability["probabilityBelowOrEqual"], 1.0)
    assert set(result["graphs"]) == {"distribution", "cdf", "sensitivity"}
    assert result["graphs"]["distribution"]["kind"] == "histogram"
    assert result["graphs"]["cdf"]["kind"] == "line"
    assert result["graphs"]["sensitivity"]["kind"] == "horizontal-bars"


def test_correlation_sensitivity_identifies_decay_rate_as_negative_driver():
    result = analyze(study(samples=512))["result"]
    rows = {row["symbol"]: row for row in result["sensitivity"]["variables"]}
    assert rows["k"]["pearson"] < -0.7
    assert rows["k"]["standardizedRegression"] < 0
    assert rows["a"]["standardizedRegression"] > 0


def test_saltelli_sobol_produces_first_and_total_order_indices():
    result = analyze(study(method="saltelli-sobol", samples=128))["result"]
    assert result["sensitivity"]["method"] == "saltelli-sobol"
    assert result["summary"]["count"] == 256  # A + B samples summarize the output distribution.
    assert len(result["sensitivity"]["variables"]) == 2
    for row in result["sensitivity"]["variables"]:
        assert math.isfinite(row["firstOrder"])
        assert math.isfinite(row["totalOrder"])


def test_uncertainty_curve_emits_confidence_ribbon_contract():
    result = analyze(study(samples=128, curve=True))["result"]
    graph = result["graphs"]["uncertaintyBand"]
    assert graph["kind"] == "line"
    points = graph["series"][0]["points"]
    assert len(points) == 17
    assert all(p["yLow"] <= p["y"] <= p["yHigh"] for p in points)
    assert result["curve"][0]["x"] == 0


def test_missing_deterministic_model_value_is_rejected_at_execution():
    payload = study()
    payload["values"] = {}
    with pytest.raises(ProbabilisticAnalysisError, match="Missing deterministic values"):
        analyze(payload)


def test_response_symbol_cannot_be_uncertain_input():
    payload = study()
    payload["uncertainInputs"] = [{"symbol": "y", "distribution": "normal", "mean": 1, "stdDev": 0.1}]
    with pytest.raises(ProbabilisticAnalysisError, match="not an eligible"):
        normalize_study(payload)


def test_curve_cannot_reuse_sampled_input_symbol():
    payload = study()
    payload["curve"] = {"xSymbol": "k", "start": 0.1, "stop": 0.5, "points": 10}
    with pytest.raises(ProbabilisticAnalysisError, match="not itself sampled"):
        normalize_study(payload)


def test_arbitrary_code_expression_remains_blocked_by_model_studio_parser():
    payload = study()
    payload["model"]["definition"]["equation"] = "y = __import__('os').system('id')"
    with pytest.raises(ProbabilisticAnalysisError):
        normalize_study(payload)
