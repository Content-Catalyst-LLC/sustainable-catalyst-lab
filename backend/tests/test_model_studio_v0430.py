from pathlib import Path

from app.model_studio import build_bundle, health, normalize_graph, normalize_model, policies


def base_model():
    return {
        "title": "Urban heat screening model",
        "family": "linear-multivariate",
        "variables": [
            {"symbol": "C", "label": "Tree canopy", "unit": "%", "role": "input"},
            {"symbol": "T", "label": "Surface temperature", "unit": "degC", "role": "response"},
        ],
        "parameters": [{"symbol": "b0", "role": "estimated"}, {"symbol": "b1", "role": "estimated"}],
        "datasetBindings": [
            {"column": "C", "symbol": "C", "role": "feature", "unit": "%"},
            {"column": "T", "symbol": "T", "role": "response", "unit": "degC"},
        ],
        "assumptions": ["Linear screening relationship."],
        "limitations": ["Not causal."],
        "provenance": {"projectId": "project-1"},
    }


def test_model_studio_advances_to_v0430_contracts():
    assert health()["version"] == "0.45.0"
    assert health()["status"] == "interactive-visualization-ready"
    model = normalize_model(base_model())
    assert model["schema"] == "sc-lab-model-studio-model/0.45.0"
    assert model["version"] == "0.45.0"
    assert policies()["boundaries"]["arbitraryCode"] is False


def test_shared_graph_contract_preserves_comparison_bars():
    graph = normalize_graph({
        "kind": "horizontal-bars",
        "title": "Model comparison",
        "bars": [{"label": "Linear", "value": 1.2}, {"label": "Polynomial", "value": 1.6}],
    })
    assert graph["schema"] == "sc-lab-scientific-graph/0.45.0"
    assert graph["bars"] == [{"label": "Linear", "value": 1.2}, {"label": "Polynomial", "value": 1.6}]


def test_bundle_adds_model_diagnostics_handoff():
    bundle = build_bundle({"model": base_model()})
    assert bundle["schema"] == "sc-lab-model-studio-bundle/0.45.0"
    assert "model-diagnostics" in bundle["handoffTargets"]


def test_fastapi_routes_expose_diagnostics_cv_and_comparison():
    text = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    for route in (
        "/v1/model-studio/diagnostics/health",
        "/v1/model-studio/diagnostics/run",
        "/v1/model-studio/cross-validation/run",
        "/v1/model-studio/comparison/run",
    ):
        assert route in text
