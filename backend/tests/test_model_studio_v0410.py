import pytest
from app.model_studio import ModelStudioError, build_bundle, health, normalize_graph, normalize_model, policies


def base_model():
    return {
        "title": "Urban heat screening model",
        "family": "linear-multivariate",
        "variables": [
            {"symbol": "C", "label": "Tree canopy", "unit": "%", "role": "input"},
            {"symbol": "T", "label": "Surface temperature", "unit": "degC", "role": "response"},
        ],
        "parameters": [
            {"symbol": "b0", "role": "estimated"},
            {"symbol": "b1", "role": "estimated", "bounds": {"lower": -20, "upper": 20}},
        ],
        "dataset": {"datasetId": "urban-heat-2026"},
        "datasetBindings": [
            {"column": "canopy", "symbol": "C", "role": "feature", "unit": "%"},
            {"column": "temperature", "symbol": "T", "role": "response", "unit": "degC"},
        ],
        "assumptions": ["Linear screening relationship."],
        "limitations": ["Not causal."],
        "provenance": {"projectId": "project-1", "sourceIds": ["source-1"]},
    }


def test_health_and_policy_boundary():
    assert health()["status"] == "model-studio-foundation-ready"
    policy = policies()
    assert policy["boundaries"]["arbitraryCode"] is False
    assert policy["boundaries"]["arbitraryFormulaExecution"] is False
    assert policy["boundaries"]["declarativeExpressionDefinition"] is True


def test_normalize_model_is_stable_and_binds_units():
    model = normalize_model(base_model())
    assert model["schema"] == "sc-lab-model-studio-model/0.41.0"
    assert model["family"] == "linear-multivariate"
    assert model["dataset"]["bindings"][0]["unit"] == "%"
    assert len(model["modelHash"]) == 64


def test_declarative_expression_is_definition_only():
    payload = base_model()
    payload["family"] = "declarative-expression"
    payload["definition"] = {"equation": "T = b0 + b1*C"}
    model = normalize_model(payload)
    assert model["definition"]["equation"] == "T = b0 + b1*C"
    assert model["definition"]["executable"] is False


def test_rejects_unsafe_symbol_and_bad_bounds():
    payload = base_model()
    payload["parameters"][0]["symbol"] = "__import__('os')"
    with pytest.raises(ModelStudioError):
        normalize_model(payload)
    payload = base_model()
    payload["parameters"][0]["bounds"] = {"lower": 2, "upper": 1}
    with pytest.raises(ModelStudioError):
        normalize_model(payload)


def test_normalize_true_scatter_graph():
    graph = normalize_graph({
        "kind": "scatter",
        "title": "Observed vs predicted",
        "xLabel": "Observed",
        "yLabel": "Predicted",
        "series": [{"id": "observed", "label": "Observations", "mode": "scatter", "points": [{"x": 1, "y": 1.1}, {"x": 2, "y": 1.9}]}],
    })
    assert graph["kind"] == "scatter"
    assert graph["series"][0]["mode"] == "scatter"
    assert graph["interaction"]["tooltip"] is True


def test_bundle_connects_existing_research_surfaces():
    bundle = build_bundle({"model": base_model(), "graphs": [{"kind": "scatter", "series": [{"points": [{"x": 1, "y": 2}, {"x": 2, "y": 3}]}]}]})
    assert "model-calibration" in bundle["handoffTargets"]
    assert "model-registry" in bundle["handoffTargets"]
    assert len(bundle["bundleHash"]) == 64


def test_fastapi_model_studio_routes_are_wired_without_runtime_side_effects():
    from pathlib import Path
    text = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    for route in (
        "/v1/model-studio/health",
        "/v1/model-studio/policies",
        "/v1/model-studio/models/normalize",
        "/v1/model-studio/graphs/normalize",
        "/v1/model-studio/bundles/build",
    ):
        assert route in text
