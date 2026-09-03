import pytest

from app.scientific_data_binding_v0750 import (
    ScientificDataBindingError,
    bind_visualization,
    build_figure,
    execute_pipeline,
    health,
    normalize_binding,
    normalize_dataset,
    normalize_pipeline,
    policies,
)


def dataset():
    return {
        "id": "dataset-observations",
        "title": "Observed response",
        "units": {"time": "s", "response": "mg", "lower": "mg", "upper": "mg"},
        "rows": [
            {"time": 1, "response": 2.0, "lower": 1.7, "upper": 2.3, "group": "A", "z": 0.2, "w": 0.0},
            {"time": 2, "response": 4.0, "lower": 3.5, "upper": 4.5, "group": "A", "z": 0.4, "w": 0.5},
            {"time": 3, "response": 6.0, "lower": 5.4, "upper": 6.6, "group": "B", "z": 0.7, "w": 1.0},
            {"time": 4, "response": 8.0, "lower": 7.3, "upper": 8.7, "group": "B", "z": 1.0, "w": 1.5},
        ],
        "provenance": {"sourceId": "experiment-12", "sourceType": "experiment", "license": "internal-research"},
    }


def test_health_and_policies_expose_binding_pipeline():
    h = health()
    assert h["ok"] is True
    assert h["version"] == "0.75.0"
    assert h["engineVersion"] == "2.2.0"
    assert h["realProjectData2d"] is True
    assert h["realProjectData4dPointProjection"] is True
    p = policies()
    assert "aggregate" in p["extendedTransforms"]
    assert "unit-convert" in p["transforms"]
    assert p["boundaries"]["arbitraryCode"] is False
    assert p["boundaries"]["surfaceInterpolation"] is False


def test_dataset_is_fingerprinted_and_unit_aware():
    d = normalize_dataset(dataset())
    assert d["schema"] == "sc-lab-scientific-dataset/0.75.0"
    assert d["rowCount"] == 4
    assert d["units"]["time"] == "s"
    assert d["columns"][0]["dataType"] in {"integer", "number"}
    assert len(d["fingerprint"]) == 64


def test_pipeline_reuses_v0550_and_adds_extended_lineage():
    result = execute_pipeline({
        "dataset": dataset(),
        "pipeline": {"id": "prep", "operations": [
            {"type": "filter", "column": "time", "operator": "gte", "value": 2},
            {"type": "scale", "column": "response", "target": "response_z", "method": "z-score"},
            {"type": "bin", "column": "time", "target": "time_bin", "count": 2},
            {"type": "sort", "by": [{"column": "time", "direction": "desc"}]},
        ]},
    })
    assert result["rowCount"] == 3
    assert result["rows"][0]["time"] == 4
    assert "response_z" in result["rows"][0]
    assert "time_bin" in result["rows"][0]
    assert len(result["lineage"]) == 4
    assert result["lineage"][0]["type"] == "filter"
    assert len(result["fingerprint"]) == 64



def test_structured_derive_is_safe_and_replayable():
    result = execute_pipeline({
        "dataset": dataset(),
        "pipeline": {"operations": [{"type": "derive", "name": "response_per_time", "unit": "mg/s", "expression": {"op": "divide", "args": [{"field": "response"}, {"field": "time"}]}}]},
    })
    assert result["rows"][0]["response_per_time"] == pytest.approx(2.0)
    assert result["units"]["response_per_time"] == "mg/s"
    assert result["lineage"][0]["details"]["structuredExpression"] is True

def test_aggregate_pipeline_is_reproducible():
    result = execute_pipeline({
        "dataset": dataset(),
        "pipeline": {"operations": [{"type": "aggregate", "groupBy": ["group"], "metrics": [{"column": "response", "op": "mean", "as": "mean_response"}, {"op": "count", "as": "n"}]}]},
    })
    assert result["rowCount"] == 2
    assert {row["group"] for row in result["rows"]} == {"A", "B"}
    assert {row["n"] for row in result["rows"]} == {2}
    assert result["units"]["mean_response"] == "mg"


def test_line_binding_maps_real_rows_and_provenance():
    bound = bind_visualization({
        "dataset": dataset(),
        "pipeline": {"operations": [{"type": "filter", "column": "time", "operator": "gte", "value": 2}]},
        "binding": {"kind": "confidence-band", "mappings": {"x": "time", "y": "response", "yLow": "lower", "yHigh": "upper", "group": "group"}},
        "figure": {"title": "Bound confidence interval", "axes": {"x": {"scale": "linear"}, "y": {"scale": "linear"}}},
    })
    s = bound["spec"]
    assert s["schema"] == "sc-lab-scientific-visualization/0.75.0"
    assert s["version"] == "0.75.0"
    assert s["visualizationEngine"] == "2.2.0"
    assert s["rendering"]["dataMode"] == "project-data-bound"
    assert len(s["series"]) == 2
    assert s["dataBinding"]["provenance"]["datasetId"] == "dataset-observations"
    assert s["dataBinding"]["transformationLineage"][0]["type"] == "filter"


def test_box_binding_uses_transformed_project_data():
    bound = bind_visualization({
        "dataset": dataset(),
        "binding": {"kind": "box", "mappings": {"x": "group", "y": "response"}},
        "figure": {"title": "Response by group"},
    })
    assert len(bound["spec"]["boxes"]) == 2
    assert bound["spec"]["axes"]["x"]["scale"] == "categorical"


def test_surface4d_binding_is_project_data_not_synthetic_surface():
    bound = bind_visualization({
        "dataset": dataset(),
        "binding": {"kind": "surface-4d", "mappings": {"x": "time", "y": "response", "z": "z", "w": "w", "label": "group"}},
        "figure": {"title": "4D project observations"},
    })
    s = bound["spec"]
    assert s["renderer"] == "canvas4d"
    assert s["profile"] == "project-data"
    assert s["rendering"]["dataMode"] == "project-data-bound"
    assert s["dataBinding"]["pointCount"] == 4
    assert s["surface"]["layers"]["surface"] is False
    assert "does not interpolate" in s["dataBoundary"]


def test_figure_carries_dataset_pipeline_binding_fingerprints():
    built = build_figure({
        "dataset": dataset(),
        "pipeline": {"id": "identity", "operations": []},
        "binding": {"id": "response-binding", "kind": "line", "mappings": {"x": "time", "y": "response"}},
        "figure": {"title": "Bound figure"},
    })["figure"]
    assert built["recordType"] == "scientific-figure-v0750"
    assert built["dataset"]["id"] == "dataset-observations"
    assert built["binding"]["id"] == "response-binding"
    assert len(built["fingerprint"]) == 64


def test_missing_mapped_column_is_rejected():
    with pytest.raises(ScientificDataBindingError):
        bind_visualization({"dataset": dataset(), "binding": {"kind": "line", "mappings": {"x": "time", "y": "missing"}}})


def test_pipeline_and_binding_normalizers_are_stable():
    p = normalize_pipeline({"operations": []})
    b = normalize_binding({"kind": "line", "mappings": {"x": "time", "y": "response"}})
    assert p["schema"] == "sc-lab-data-transformation-pipeline/0.75.0"
    assert b["schema"] == "sc-lab-visualization-data-binding/0.75.0"
    assert len(p["fingerprint"]) == 64
    assert len(b["fingerprint"]) == 64
