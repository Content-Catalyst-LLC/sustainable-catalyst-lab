import pytest

from app.graph_studio import GraphStudioError, build_workspace, health, normalize_figure, normalize_graph, policies


def example_graph(kind="line-scatter"):
    return {
        "kind": kind,
        "title": "Observed and fitted response",
        "xLabel": "Time (s)",
        "yLabel": "Response (mg/L)",
        "series": [
            {"label": "Observed", "mode": "points", "points": [{"x": 0, "y": 10.1}, {"x": 1, "y": 7.2}]},
            {"label": "Fitted", "mode": "line", "points": [{"x": 0, "y": 10}, {"x": 1, "y": 7.05}]},
        ],
        "publication": {"aspectRatio": "16:9", "source": "Dataset D-1", "method": "Model Studio fit"},
    }


def test_health_and_policy_contracts():
    assert health()["version"] == "0.47.0"
    p = policies()
    assert p["figureSchema"] == "sc-lab-scientific-figure/0.47.0"
    assert p["sharedVisualizationEngine"] == "0.44.0"
    assert p["boundaries"]["arbitraryCode"] is False


def test_normalize_graph_retains_interactive_publication_contract():
    graph = normalize_graph(example_graph())
    assert graph["schema"] == "sc-lab-scientific-graph/0.46.0"
    assert graph["interaction"]["zoom"] is True
    assert graph["interaction"]["pan"] is True
    assert graph["publication"]["source"] == "Dataset D-1"
    assert graph["exports"] == ["svg", "png", "csv", "json"]


def test_normalize_figure_wraps_governed_graph_and_fingerprint():
    figure = normalize_figure({"title": "Figure 1", "graph": example_graph(), "sourceContext": "model-studio", "provenance": {"projectId": "p-1"}})
    assert figure["version"] == "0.47.0"
    assert figure["recordType"] == "scientific-figure-v0470"
    assert figure["graph"]["kind"] == "line-scatter"
    assert len(figure["fingerprint"]) == 64


def test_workspace_normalizes_multiple_figures():
    result = build_workspace({"projectId": "project-1", "figures": [{"graph": example_graph()}, {"graph": example_graph("scatter")}]})
    assert result["ok"] is True
    assert result["workspace"]["figureCount"] == 2
    assert result["workspace"]["schema"] == "sc-lab-figure-workspace/0.47.0"


def test_rejects_unsupported_kind_and_nonfinite_points():
    with pytest.raises(GraphStudioError):
        normalize_graph({"kind": "3d-volume", "title": "Bad"})
    bad = example_graph()
    bad["series"][0]["points"][0]["y"] = float("nan")
    with pytest.raises(GraphStudioError):
        normalize_graph(bad)


def test_heatmap_contract():
    graph = normalize_graph({
        "kind": "heatmap", "title": "Response surface", "xLabel": "T", "yLabel": "P",
        "xValues": [20, 50], "yValues": [1, 5],
        "cells": [
            {"xIndex": 0, "yIndex": 0, "x": 20, "y": 1, "z": 88},
            {"xIndex": 1, "yIndex": 0, "x": 50, "y": 1, "z": 96},
            {"xIndex": 0, "yIndex": 1, "x": 20, "y": 5, "z": 92},
            {"xIndex": 1, "yIndex": 1, "x": 50, "y": 5, "z": 100},
        ]
    })
    assert graph["kind"] == "heatmap"
    assert len(graph["cells"]) == 4
