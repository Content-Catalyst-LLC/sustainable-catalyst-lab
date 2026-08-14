import pytest

from app.model_studio import ModelStudioError, build_bundle, health, normalize_graph, policies, preview_equation_model


def expression_model():
    return {
        "title": "Decay publication figure",
        "family": "declarative-expression",
        "definition": {"equation": "y = a * exp(-k*x)"},
        "variables": [{"symbol": "x", "unit": "h", "role": "input"}, {"symbol": "y", "unit": "mg/L", "role": "response"}],
        "parameters": [{"symbol": "a", "value": 10, "role": "estimated"}, {"symbol": "k", "value": 0.3, "role": "estimated"}],
        "datasetBindings": [{"column": "x", "symbol": "x", "role": "feature", "unit": "h"}, {"column": "y", "symbol": "y", "role": "response", "unit": "mg/L"}],
        "provenance": {"projectId": "p-1"},
    }


def test_v0440_health_and_visualization_policy():
    h = health()
    assert h["version"] == "0.44.0"
    assert h["status"] == "interactive-visualization-ready"
    assert h["interactiveVisualization"] is True
    assert h["publicationGraphics"] is True
    p = policies()["visualizationEngine"]
    assert p["version"] == "0.44.0"
    assert "zoom" in p["interactions"]
    assert "confidence-ribbons" in p["uncertainty"]
    assert p["publicationExports"] == ["svg", "png", "csv", "json"]


def test_graph_contract_preserves_uncertainty_and_publication_metadata():
    graph = normalize_graph({
        "kind": "line-scatter",
        "title": "Observed and fitted response",
        "xLabel": "Time (h)",
        "yLabel": "Concentration (mg/L)",
        "series": [{"id": "fit", "label": "Fit", "mode": "line-scatter", "points": [
            {"x": 0, "y": 10, "yLow": 9.2, "yHigh": 10.8, "label": "baseline"},
            {"x": 1, "y": 7.4, "yLow": 6.8, "yHigh": 8.1},
        ]}],
        "publication": {"subtitle": "95% model interval", "caption": "Illustrative fit.", "source": "Lab dataset", "method": "Governed equation preview", "aspectRatio": "3:2", "showGrid": True, "showLegend": True},
    })
    assert graph["schema"] == "sc-lab-scientific-graph/0.44.0"
    assert graph["series"][0]["points"][0]["yLow"] == 9.2
    assert graph["series"][0]["points"][0]["label"] == "baseline"
    assert graph["interaction"]["zoom"] is True
    assert graph["interaction"]["pan"] is True
    assert graph["interaction"]["crosshair"] is True
    assert graph["publication"]["aspectRatio"] == "3:2"
    assert graph["exports"] == ["svg", "png", "csv", "json"]


def test_invalid_publication_ratio_rejected():
    with pytest.raises(ModelStudioError, match="aspect ratio"):
        normalize_graph({"kind": "scatter", "title": "Bad ratio", "publication": {"aspectRatio": "5:4"}})


def test_equation_preview_uses_interactive_graph_contract():
    result = preview_equation_model({"model": expression_model(), "rows": [{"x": 0}, {"x": 1}, {"x": 2}, {"x": 3}]})
    graph = result["graph"]
    assert graph["version"] == "0.44.0"
    assert graph["interaction"]["zoom"] is True
    assert graph["accessibility"]["keyboardNavigation"] is True


def test_bundle_advances_to_v0440_without_changing_safety_boundary():
    bundle = build_bundle({"model": expression_model()})
    assert bundle["schema"] == "sc-lab-model-studio-bundle/0.44.0"
    assert bundle["boundaries"]["arbitraryCode"] is False
    assert "workbench" in bundle["handoffTargets"]
