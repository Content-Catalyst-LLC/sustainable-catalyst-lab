import pytest

from app.visualization_engine_v0730 import (
    VisualizationEngineError,
    build_workspace,
    health,
    normalize_figure,
    normalize_spec,
    policies,
)


def legacy_graph():
    return {
        "kind": "line-scatter",
        "title": "Observed and fitted response",
        "xLabel": "Time (s)",
        "yLabel": "Response (mg/L)",
        "series": [
            {"label": "Observed", "mode": "points", "points": [{"x": 0, "y": 10.1}, {"x": 1, "y": 7.2}]},
            {"label": "Fitted", "mode": "line", "points": [{"x": 0, "y": 10}, {"x": 1, "y": 7.05}]},
        ],
        "publication": {"aspectRatio": "16:9", "source": "Dataset D-1", "method": "Model Studio fit"},
    }


def surface_graph():
    return {
        "kind": "surface-4d",
        "profile": "biodiversity",
        "title": "Biodiversity response through time",
        "dimensions": [
            {"key": "habitat", "label": "Habitat quality", "role": "x", "unit": "relative"},
            {"key": "climate", "label": "Climate stress", "role": "y", "unit": "relative"},
            {"key": "response", "label": "Biodiversity response", "role": "z", "unit": "relative"},
            {"key": "time", "label": "Time / disturbance", "role": "w", "unit": "relative"},
        ],
        "surface": {"slice": 0.63, "rotation": {"xw": 0.2, "yw": -0.1}, "layers": {"vector": True, "uncertainty": True, "contours": True}},
        "publication": {"source": "Synthetic interface profile", "method": "Deterministic v0.71 biodiversity field"},
    }


def test_health_and_policy_expose_two_renderer_architecture():
    h = health()
    assert h["version"] == "0.73.0"
    assert h["engineVersion"] == "2.0.0"
    assert h["surface4dFirstClassFigure"] is True
    p = policies()
    assert p["renderers"]["svg2d"]["exports"] == ["svg", "png", "csv", "json"]
    assert p["renderers"]["canvas4d"]["exports"] == ["png", "json"]
    assert p["boundaries"]["surface4dProjectDataBinding"] is False


def test_legacy_graph_is_upgraded_without_losing_old_renderer_contract():
    spec = normalize_spec(legacy_graph())
    assert spec["schema"] == "sc-lab-scientific-visualization/0.73.0"
    assert spec["renderer"] == "svg2d"
    assert spec["legacySchema"] == "sc-lab-scientific-graph/0.46.0"
    assert spec["series"][0]["points"][0]["y"] == pytest.approx(10.1)
    assert spec["publication"]["source"] == "Dataset D-1"


def test_surface_4d_is_governed_first_class_saved_spec():
    spec = normalize_spec(surface_graph())
    assert spec["kind"] == "surface-4d"
    assert spec["renderer"] == "canvas4d"
    assert len(spec["dimensions"]) == 4
    assert spec["surface"]["slice"] == pytest.approx(0.63)
    assert spec["surface"]["layers"]["uncertainty"] is True
    assert spec["exports"] == ["png", "json"]
    assert "synthetic" in spec["dataBoundary"].lower()


def test_surface_4d_rejects_bad_dimension_and_slice_state():
    bad = surface_graph()
    bad["dimensions"] = bad["dimensions"][:3]
    with pytest.raises(VisualizationEngineError):
        normalize_spec(bad)
    bad = surface_graph()
    bad["surface"]["slice"] = 1.5
    with pytest.raises(VisualizationEngineError):
        normalize_spec(bad)


def test_figure_and_workspace_preserve_renderer_provenance():
    figure = normalize_figure({"title": "Figure 4D", "graph": surface_graph(), "provenance": {"projectId": "p-1"}})
    assert figure["recordType"] == "scientific-figure-v0730"
    assert figure["provenance"]["renderer"] == "canvas4d"
    assert len(figure["fingerprint"]) == 64
    result = build_workspace({"projectId": "p-1", "figures": [{"graph": legacy_graph()}, {"graph": surface_graph()}]})
    assert result["workspace"]["figureCount"] == 2
    assert result["workspace"]["schema"] == "sc-lab-figure-workspace/0.73.0"
