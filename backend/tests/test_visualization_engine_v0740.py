import pytest

from app.visualization_engine_v0740 import (
    ADVANCED_2D_KINDS,
    VisualizationGrammarError,
    build_workspace,
    health,
    normalize_figure,
    normalize_spec,
    policies,
)


def advanced_spec(kind="confidence-band"):
    return {
        "kind": kind,
        "title": "Advanced scientific plot",
        "axes": {
            "x": {"label": "Time", "unit": "s", "scale": "log", "tickFormat": "scientific"},
            "y": {"label": "Response", "unit": "mg/L", "scale": "linear", "tickFormat": "si"},
        },
        "series": [
            {
                "id": "fit",
                "label": "Estimate",
                "points": [
                    {"x": 1, "y": 2.0, "yLow": 1.5, "yHigh": 2.5},
                    {"x": 10, "y": 4.0, "yLow": 3.2, "yHigh": 4.8},
                ],
            }
        ],
        "publication": {"caption": "Test figure", "source": "Unit test"},
    }


def test_health_exposes_advanced_grammar():
    h = health()
    assert h["ok"] is True
    assert h["version"] == "0.74.0"
    assert h["engineVersion"] == "2.1.0"
    assert "box" in h["advanced2dKinds"]
    assert "contour" in h["advanced2dKinds"]
    assert "symlog" in h["axisScales"]
    assert h["legacy2dCompatibility"] is True
    assert h["canvas4dCompatibility"] is True


def test_policies_keep_cartesian_boundaries_explicit():
    p = policies()
    assert p["plotGrammar"] == "sc-lab-advanced-2d-plot-grammar/0.74.0"
    assert p["boundaries"]["polarRadar"] is False
    assert p["boundaries"]["dualAxis"] is False
    assert p["boundaries"]["rawDataTransformationPipeline"] == "v0.75.0"
    assert p["renderers"]["svg2d"]["version"] == "0.74.0"


@pytest.mark.parametrize("kind", sorted(ADVANCED_2D_KINDS))
def test_every_advanced_kind_normalizes(kind):
    s = normalize_spec(advanced_spec(kind))
    assert s["schema"] == "sc-lab-scientific-visualization/0.74.0"
    assert s["grammar"] == "sc-lab-advanced-2d-plot-grammar/0.74.0"
    assert s["kind"] == kind
    assert s["renderer"] == "svg2d"
    assert s["rendererVersion"] == "0.74.0"
    assert s["axes"]["x"]["scale"] == "log"
    assert s["axes"]["x"]["unit"] == "s"
    assert s["axes"]["y"]["tickFormat"] == "si"


def test_legacy_line_upgrades_without_losing_contract():
    s = normalize_spec({
        "kind": "line",
        "title": "Legacy-compatible line",
        "xLabel": "x",
        "yLabel": "y",
        "series": [{"label": "Observed", "points": [{"x": 0, "y": 1}, {"x": 1, "y": 2}]}],
    })
    assert s["kind"] == "line"
    assert s["renderer"] == "svg2d"
    assert s["version"] == "0.74.0"
    assert s["axes"]["x"]["scale"] == "linear"


def test_surface4d_is_carried_forward_through_v0730_adapter():
    s = normalize_spec({"kind": "surface-4d", "profile": "biodiversity", "title": "Biodiversity surface"})
    assert s["renderer"] == "canvas4d"
    assert s["version"] == "0.74.0"
    assert s["visualizationEngine"] == "2.1.0"
    assert s["compatibility"]["sourceSchema"] == "sc-lab-scientific-visualization/0.73.0"
    assert s["dataBoundary"]


def test_figure_and_workspace_use_v0740_contracts():
    fig = normalize_figure({"title": "Figure", "graph": advanced_spec("box"), "provenance": {"datasetId": "dataset-1"}})
    assert fig["schema"] == "sc-lab-scientific-figure/0.74.0"
    assert fig["recordType"] == "scientific-figure-v0740"
    assert fig["provenance"]["visualizationEngine"] == "2.1.0"
    assert len(fig["fingerprint"]) == 64
    ws = build_workspace({"projectId": "project-1", "figures": [fig]})["workspace"]
    assert ws["schema"] == "sc-lab-figure-workspace/0.74.0"
    assert ws["figureCount"] == 1


def test_invalid_axis_scale_is_rejected():
    bad = advanced_spec("line")
    bad["axes"]["x"]["scale"] = "magic"
    with pytest.raises(VisualizationGrammarError):
        normalize_spec(bad)


def test_duplicate_or_unbounded_code_not_part_of_contract():
    p = policies()
    assert p["boundaries"]["arbitraryCode"] is False
    assert p["boundaries"]["remoteImageFetch"] is False
