import math
import pytest

from app.large_data_visualization_v0760 import (
    LargeDataVisualizationError,
    adapt_dataset,
    bind_visualization,
    health,
    normalize_large_dataset,
    normalize_plan,
    policies,
)


def rows(n=12000):
    return [{"x": i, "y": math.sin(i / 31), "z": math.cos(i / 47), "w": i / max(1, n - 1), "group": "a" if i % 2 else "b"} for i in range(n)]


def binding(kind="line"):
    return {"id": "b", "kind": kind, "mappings": {"x": "x", "y": "y", "z": "z", "w": "w", "group": "group"}}


def test_health_and_policies():
    h = health(); p = policies()
    assert h["status"] == "large-data-adaptive-rendering-ready"
    assert h["engineVersion"] == "2.3.0"
    assert p["sourceRowLimit"] == 250000
    assert p["renderPointLimit"] == 5000
    assert p["silentDataMutation"] is False


def test_large_dataset_normalization_and_fingerprint():
    d = normalize_large_dataset({"id": "large", "rows": rows(6000), "units": {"x": "s"}})
    assert d["rowCount"] == 6000
    assert d["units"]["x"] == "s"
    assert len(d["fingerprint"]) == 64


def test_large_dataset_limit():
    with pytest.raises(LargeDataVisualizationError):
        normalize_large_dataset({"id": "too-large", "rows": [{"x": 1}] * 250001})


def test_auto_line_uses_lttb():
    p = normalize_plan({"strategy": "auto", "pointBudget": 1000}, kind="line", row_count=12000)
    assert p["strategy"] == "lttb"
    assert p["levels"][-1]["pointBudget"] == 1000


def test_auto_scatter_uses_grid():
    assert normalize_plan({"strategy": "auto"}, kind="scatter", row_count=12000)["strategy"] == "grid"


def test_auto_distribution_uses_quantile():
    assert normalize_plan({"strategy": "auto"}, kind="density", row_count=12000)["strategy"] == "quantile"


def test_adaptive_line_is_deterministic_and_bounded():
    req = {"dataset": {"id": "large", "title": "Large", "rows": rows()}, "binding": binding("line"), "renderPlan": {"strategy": "auto", "pointBudget": 1200}}
    a = adapt_dataset(req); b = adapt_dataset(req)
    assert a["renderedRowCount"] <= 1200
    assert a["rows"] == b["rows"]
    assert a["renderPlan"]["strategy"] == "lttb"
    assert a["sourceRowCount"] == 12000
    assert a["omittedRowCount"] > 0


def test_adaptive_grid_is_bounded():
    r = adapt_dataset({"dataset": {"id": "s", "rows": rows()}, "binding": binding("scatter"), "renderPlan": {"pointBudget": 900}})
    assert r["renderPlan"]["strategy"] == "grid"
    assert r["renderedRowCount"] <= 900


def test_progressive_levels_are_ordered():
    r = adapt_dataset({"dataset": {"id": "s", "rows": rows()}, "binding": binding("scatter"), "renderPlan": {"pointBudget": 3000, "progressive": True}})
    counts = [x["pointBudget"] for x in r["representations"]]
    assert counts == [500, 2000, 3000]


def test_small_dataset_delegates_full_v0750_binding():
    result = bind_visualization({"dataset": {"id": "small", "rows": rows(100)}, "pipeline": {"operations": []}, "binding": binding("line"), "figure": {"title": "Small"}})
    assert result["adaptiveRendering"]["active"] is False
    assert result["spec"]["version"] == "0.76.0"


def test_large_binding_reduces_before_v0750_renderer():
    result = bind_visualization({"dataset": {"id": "large", "rows": rows()}, "pipeline": {"operations": []}, "binding": binding("line"), "renderPlan": {"pointBudget": 1500}, "figure": {"title": "Large"}})
    assert result["adaptiveRendering"]["renderedRowCount"] <= 1500
    assert result["adaptiveRendering"]["sourceRowCount"] == 12000
    assert result["spec"]["rendering"]["adaptive"]["active"] is True
    assert result["provenance"]["sourceDatasetFingerprint"]


def test_large_transform_after_sampling_is_forbidden():
    with pytest.raises(LargeDataVisualizationError, match="does not apply scientific transformations after sampling"):
        bind_visualization({"dataset": {"id": "large", "rows": rows()}, "pipeline": {"operations": [{"type": "filter", "column": "x", "operator": "gt", "value": 0}]}, "binding": binding("line"), "figure": {"title": "Large"}})


def test_full_strategy_is_selected_when_under_budget():
    p = normalize_plan({"strategy": "stride", "pointBudget": 500}, kind="scatter", row_count=100)
    assert p["strategy"] == "full"


def test_invalid_budget_rejected():
    with pytest.raises(LargeDataVisualizationError):
        normalize_plan({"pointBudget": 20}, kind="line", row_count=10000)
