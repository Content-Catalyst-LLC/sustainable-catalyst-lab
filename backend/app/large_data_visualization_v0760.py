from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

from .scientific_data_binding_v0750 import (
    ScientificDataBindingError,
    bind_visualization as bind_visualization_v0750,
    normalize_binding as normalize_binding_v0750,
)

VERSION = "0.76.0"
ENGINE_VERSION = "2.3.0"
PLAN_SCHEMA = "sc-lab-adaptive-render-plan/0.76.0"
RESULT_SCHEMA = "sc-lab-adaptive-render-result/0.76.0"
SPEC_SCHEMA = "sc-lab-scientific-visualization/0.76.0"
FIGURE_SCHEMA = "sc-lab-scientific-figure/0.76.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.76.0"
MAX_SOURCE_ROWS = 250_000
MAX_COLUMNS = 200
MAX_RENDER_POINTS = 5_000
DEFAULT_RENDER_POINTS = 2_000
MIN_RENDER_POINTS = 100
MAX_PROGRESSIVE_LEVELS = 3
STRATEGIES = {"auto", "full", "stride", "lttb", "grid", "quantile"}
LINE_KINDS = {"line", "line-scatter", "step", "area", "stacked-area", "confidence-band", "error-bar", "residual"}
DISTRIBUTION_KINDS = {"histogram", "density", "box", "violin", "ecdf", "qq"}
GRID_KINDS = {"scatter", "heatmap", "hexbin", "contour", "surface-4d"}


class LargeDataVisualizationError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, name: str, limit: int = 240, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise LargeDataVisualizationError(f"{name} is required.")
    if len(text) > limit:
        raise LargeDataVisualizationError(f"{name} exceeds {limit} characters.")
    return text


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise LargeDataVisualizationError(f"{name} must be numeric.")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise LargeDataVisualizationError(f"{name} must be numeric.") from exc
    if not math.isfinite(out):
        raise LargeDataVisualizationError(f"{name} must be finite.")
    return out


def _clean_rows(rows: Any) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(rows, list):
        raise LargeDataVisualizationError("dataset.rows must be an array of row objects.")
    if not rows:
        raise LargeDataVisualizationError("dataset requires at least one row.")
    if len(rows) > MAX_SOURCE_ROWS:
        raise LargeDataVisualizationError(f"dataset exceeds the {MAX_SOURCE_ROWS}-row v0.76 adaptive-rendering limit.")
    out: list[dict[str, Any]] = []
    columns: list[str] = []
    for i, raw in enumerate(rows):
        if not isinstance(raw, dict):
            raise LargeDataVisualizationError(f"dataset.rows[{i}] must be an object.")
        row: dict[str, Any] = {}
        for key, value in raw.items():
            name = _text(key, "column name", 240, True)
            if isinstance(value, (dict, list, tuple, set)):
                raise LargeDataVisualizationError(f"nested values are not supported in adaptive rendering rows ({name}).")
            if isinstance(value, float) and not math.isfinite(value):
                raise LargeDataVisualizationError(f"non-finite value in {name} at row {i + 1}.")
            row[name] = value
            if name not in columns:
                columns.append(name)
        out.append(row)
    if len(columns) > MAX_COLUMNS:
        raise LargeDataVisualizationError(f"dataset exceeds the {MAX_COLUMNS}-column limit.")
    return out, columns


def normalize_large_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise LargeDataVisualizationError("dataset definition must be an object.")
    rows, columns = _clean_rows(payload.get("rows") or [])
    units = payload.get("units") if isinstance(payload.get("units"), dict) else {}
    dataset = {
        "schema": "sc-lab-large-scientific-dataset/0.76.0",
        "version": VERSION,
        "recordType": "large-scientific-dataset-v0760",
        "id": _text(payload.get("id") or payload.get("datasetId") or f"dataset-{_digest(rows)[:16]}", "dataset id", 160, True),
        "title": _text(payload.get("title") or "Large scientific dataset", "dataset title", 240, True),
        "rowCount": len(rows),
        "columnCount": len(columns),
        "columns": columns,
        "units": {str(k): _text(v, f"unit {k}", 120) for k, v in units.items()},
        "rows": rows,
        "provenance": deepcopy(payload.get("provenance") or {}),
    }
    dataset["fingerprint"] = _digest({"id": dataset["id"], "rows": rows, "units": dataset["units"], "provenance": dataset["provenance"]})
    return dataset


def _strategy_for(kind: str, requested: str) -> str:
    if requested != "auto":
        return requested
    if kind in LINE_KINDS:
        return "lttb"
    if kind in DISTRIBUTION_KINDS:
        return "quantile"
    if kind in GRID_KINDS:
        return "grid"
    return "stride"


def normalize_plan(payload: dict[str, Any] | None, *, kind: str = "line-scatter", row_count: int = 0) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    strategy = _text(source.get("strategy") or "auto", "adaptive strategy", 30, True).lower()
    if strategy not in STRATEGIES:
        raise LargeDataVisualizationError(f"unsupported adaptive strategy: {strategy}.")
    budget = int(source.get("pointBudget") or source.get("maxPoints") or DEFAULT_RENDER_POINTS)
    if budget < MIN_RENDER_POINTS or budget > MAX_RENDER_POINTS:
        raise LargeDataVisualizationError(f"pointBudget must be between {MIN_RENDER_POINTS} and {MAX_RENDER_POINTS}.")
    progressive = source.get("progressive") is not False
    selected = _strategy_for(kind, strategy)
    if row_count and row_count <= budget:
        selected = "full"
    plan = {
        "schema": PLAN_SCHEMA,
        "version": VERSION,
        "recordType": "adaptive-render-plan-v0760",
        "strategyRequested": strategy,
        "strategy": selected,
        "pointBudget": budget,
        "progressive": progressive,
        "levels": [],
        "deterministic": True,
        "preserveSourceDataset": True,
        "silentMutation": False,
    }
    if progressive:
        for name, count in (("preview", min(500, budget)), ("interactive", min(2000, budget)), ("detail", budget)):
            if not plan["levels"] or count != plan["levels"][-1]["pointBudget"]:
                plan["levels"].append({"name": name, "pointBudget": count})
    else:
        plan["levels"] = [{"name": "detail", "pointBudget": budget}]
    plan["fingerprint"] = _digest({k: v for k, v in plan.items() if k != "fingerprint"})
    return plan


def _stride(rows: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    if len(rows) <= budget:
        return deepcopy(rows)
    step = len(rows) / budget
    indices = sorted({min(len(rows) - 1, int(i * step)) for i in range(budget)} | {0, len(rows) - 1})
    if len(indices) > budget:
        indices = indices[: budget - 1] + [len(rows) - 1]
    return [deepcopy(rows[i]) for i in indices]


def _quantile(rows: list[dict[str, Any]], budget: int, y_key: str | None) -> list[dict[str, Any]]:
    if len(rows) <= budget:
        return deepcopy(rows)
    if not y_key:
        return _stride(rows, budget)
    observed: list[tuple[float, int]] = []
    for i, row in enumerate(rows):
        try:
            observed.append((_finite(row.get(y_key), y_key), i))
        except LargeDataVisualizationError:
            continue
    if len(observed) < 2:
        return _stride(rows, budget)
    observed.sort(key=lambda item: (item[0], item[1]))
    picks = []
    for j in range(budget):
        pos = round(j * (len(observed) - 1) / max(1, budget - 1))
        picks.append(observed[pos][1])
    return [deepcopy(rows[i]) for i in sorted(set(picks))]


def _lttb(rows: list[dict[str, Any]], budget: int, x_key: str | None, y_key: str | None) -> list[dict[str, Any]]:
    if len(rows) <= budget or budget < 3 or not x_key or not y_key:
        return _stride(rows, budget)
    points: list[tuple[float, float, int]] = []
    for i, row in enumerate(rows):
        try:
            points.append((_finite(row.get(x_key), x_key), _finite(row.get(y_key), y_key), i))
        except LargeDataVisualizationError:
            continue
    if len(points) <= budget:
        return [deepcopy(rows[i]) for _, _, i in points]
    every = (len(points) - 2) / (budget - 2)
    sampled = [points[0]]
    a = 0
    for i in range(budget - 2):
        avg_start = int(math.floor((i + 1) * every)) + 1
        avg_end = min(int(math.floor((i + 2) * every)) + 1, len(points))
        avg_range = points[avg_start:avg_end] or [points[min(avg_start, len(points) - 1)]]
        avg_x = sum(p[0] for p in avg_range) / len(avg_range)
        avg_y = sum(p[1] for p in avg_range) / len(avg_range)
        range_start = int(math.floor(i * every)) + 1
        range_end = min(int(math.floor((i + 1) * every)) + 1, len(points) - 1)
        ax, ay, _ = points[a]
        best = None
        best_area = -1.0
        for idx in range(range_start, max(range_start + 1, range_end)):
            px, py, _ = points[idx]
            area = abs((ax - avg_x) * (py - ay) - (ax - px) * (avg_y - ay)) * 0.5
            if area > best_area:
                best_area = area
                best = idx
        a = best if best is not None else range_start
        sampled.append(points[a])
    sampled.append(points[-1])
    return [deepcopy(rows[i]) for _, _, i in sampled]


def _grid(rows: list[dict[str, Any]], budget: int, x_key: str | None, y_key: str | None) -> list[dict[str, Any]]:
    if len(rows) <= budget or not x_key or not y_key:
        return _stride(rows, budget)
    coords: list[tuple[float, float, int]] = []
    for i, row in enumerate(rows):
        try:
            coords.append((_finite(row.get(x_key), x_key), _finite(row.get(y_key), y_key), i))
        except LargeDataVisualizationError:
            continue
    if len(coords) <= budget:
        return [deepcopy(rows[i]) for _, _, i in coords]
    xs = [x for x, _, _ in coords]; ys = [y for _, y, _ in coords]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    side = max(1, int(math.sqrt(budget)))
    cells: dict[tuple[int, int], list[tuple[float, float, int]]] = {}
    for x, y, i in coords:
        gx = 0 if xmax == xmin else min(side - 1, int((x - xmin) / (xmax - xmin) * side))
        gy = 0 if ymax == ymin else min(side - 1, int((y - ymin) / (ymax - ymin) * side))
        cells.setdefault((gx, gy), []).append((x, y, i))
    picks: list[int] = []
    for key in sorted(cells):
        members = cells[key]
        cx = sum(p[0] for p in members) / len(members); cy = sum(p[1] for p in members) / len(members)
        chosen = min(members, key=lambda p: ((p[0] - cx) ** 2 + (p[1] - cy) ** 2, p[2]))
        picks.append(chosen[2])
        if len(picks) >= budget:
            break
    if len(picks) < min(budget, len(coords)):
        remaining = [i for _, _, i in coords if i not in set(picks)]
        picks.extend(i for i in [r for r in remaining] if len(picks) < budget)
    return [deepcopy(rows[i]) for i in sorted(picks[:budget])]


def _adapt(rows: list[dict[str, Any]], plan: dict[str, Any], binding: dict[str, Any], budget: int) -> list[dict[str, Any]]:
    strategy = plan["strategy"]
    mappings = binding.get("mappings") or {}
    if strategy == "full": return deepcopy(rows[:budget]) if len(rows) > budget else deepcopy(rows)
    if strategy == "lttb": return _lttb(rows, budget, mappings.get("x"), mappings.get("y"))
    if strategy == "grid": return _grid(rows, budget, mappings.get("x"), mappings.get("y"))
    if strategy == "quantile": return _quantile(rows, budget, mappings.get("y") or mappings.get("value"))
    return _stride(rows, budget)


def adapt_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise LargeDataVisualizationError("adaptive dataset request must be an object.")
    dataset = normalize_large_dataset(payload.get("dataset") or payload.get("data") or {})
    try:
        binding = normalize_binding_v0750(payload.get("binding") or {})
    except ScientificDataBindingError as exc:
        raise LargeDataVisualizationError(str(exc)) from exc
    kind = binding["kind"]
    plan = normalize_plan(payload.get("renderPlan") or payload.get("plan"), kind=kind, row_count=dataset["rowCount"])
    representations = []
    for level in plan["levels"]:
        adapted = _adapt(dataset["rows"], plan, binding, level["pointBudget"])
        representations.append({
            "level": level["name"],
            "pointBudget": level["pointBudget"],
            "rowCount": len(adapted),
            "rows": adapted,
            "fingerprint": _digest(adapted),
        })
    detail = representations[-1]
    result = {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "recordType": "adaptive-render-result-v0760",
        "dataset": {"id": dataset["id"], "title": dataset["title"], "fingerprint": dataset["fingerprint"], "rowCount": dataset["rowCount"], "units": dataset["units"], "provenance": dataset["provenance"]},
        "binding": binding,
        "renderPlan": plan,
        "sourceRowCount": dataset["rowCount"],
        "renderedRowCount": detail["rowCount"],
        "omittedRowCount": max(0, dataset["rowCount"] - detail["rowCount"]),
        "representations": representations,
        "rows": detail["rows"],
        "units": dataset["units"],
        "fidelity": {
            "deterministic": True,
            "sourceDatasetPreserved": True,
            "adaptiveRepresentationOnly": True,
            "interpolation": False,
            "forecasting": False,
            "uncertaintyInvented": False,
        },
        "generatedAt": _now(),
    }
    result["fingerprint"] = _digest({k: v for k, v in result.items() if k not in {"generatedAt", "fingerprint"}})
    return result


def bind_visualization(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise LargeDataVisualizationError("adaptive visualization request must be an object.")
    source_dataset = payload.get("dataset") or payload.get("data") or {}
    source_rows = source_dataset.get("rows") if isinstance(source_dataset, dict) else None
    if not isinstance(source_rows, list):
        raise LargeDataVisualizationError("dataset.rows must be supplied.")
    pipeline = payload.get("pipeline") or {"operations": []}
    operations = pipeline.get("operations") if isinstance(pipeline, dict) else None
    if len(source_rows) > 5000 and operations:
        raise LargeDataVisualizationError("v0.76 adaptive rendering does not apply scientific transformations after sampling. Pre-transform or aggregate the dataset before large-data rendering, then submit an identity pipeline.")
    if len(source_rows) <= 5000:
        try:
            result = bind_visualization_v0750(payload)
        except ScientificDataBindingError as exc:
            raise LargeDataVisualizationError(str(exc)) from exc
        result["version"] = VERSION
        result["spec"]["schema"] = SPEC_SCHEMA
        result["spec"]["version"] = VERSION
        result["spec"]["visualizationEngine"] = ENGINE_VERSION
        result["adaptiveRendering"] = {"active": False, "sourceRowCount": len(source_rows), "renderedRowCount": len(source_rows), "strategy": "full"}
        return result
    adaptive = adapt_dataset({"dataset": source_dataset, "binding": payload.get("binding") or {}, "renderPlan": payload.get("renderPlan") or payload.get("plan")})
    adapted_dataset = {
        "id": f"{adaptive['dataset']['id']}-adaptive-{adaptive['renderPlan']['fingerprint'][:10]}",
        "title": f"{adaptive['dataset']['title']} — adaptive representation",
        "rows": adaptive["rows"],
        "units": adaptive["units"],
        "provenance": {**adaptive["dataset"].get("provenance", {}), "sourceId": adaptive["dataset"]["id"], "sourceType": "adaptive-render-representation", "notes": f"v0.76 adaptive representation from source fingerprint {adaptive['dataset']['fingerprint']}."},
    }
    request = deepcopy(payload)
    request["dataset"] = adapted_dataset
    request["pipeline"] = {"operations": []}
    request.pop("data", None)
    try:
        bound = bind_visualization_v0750(request)
    except ScientificDataBindingError as exc:
        raise LargeDataVisualizationError(str(exc)) from exc
    bound["version"] = VERSION
    bound["spec"]["schema"] = SPEC_SCHEMA
    bound["spec"]["version"] = VERSION
    bound["spec"]["visualizationEngine"] = ENGINE_VERSION
    bound["spec"].setdefault("rendering", {})["adaptive"] = {
        "active": True,
        "strategy": adaptive["renderPlan"]["strategy"],
        "sourceRowCount": adaptive["sourceRowCount"],
        "renderedRowCount": adaptive["renderedRowCount"],
        "pointBudget": adaptive["renderPlan"]["pointBudget"],
        "planFingerprint": adaptive["renderPlan"]["fingerprint"],
    }
    bound["adaptiveRendering"] = adaptive
    bound.setdefault("provenance", {})["sourceDatasetFingerprint"] = adaptive["dataset"]["fingerprint"]
    bound["provenance"]["adaptiveRenderFingerprint"] = adaptive["fingerprint"]
    return bound


def build_figure(payload: dict[str, Any]) -> dict[str, Any]:
    result = bind_visualization(payload)
    figure = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-figure-v0760",
        "id": _text((payload.get("figure") or {}).get("id") if isinstance(payload.get("figure"), dict) else "", "figure id", 160) or f"figure-{_digest(result['spec'])[:16]}",
        "title": _text((payload.get("figure") or {}).get("title") if isinstance(payload.get("figure"), dict) else result["spec"].get("title"), "figure title", 240, True),
        "graph": result["spec"],
        "adaptiveRendering": result.get("adaptiveRendering"),
        "provenance": result.get("provenance", {}),
        "generatedAt": _now(),
    }
    figure["fingerprint"] = _digest({k: v for k, v in figure.items() if k not in {"generatedAt", "fingerprint"}})
    return {"ok": True, "figure": figure, "result": result}


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    built = build_figure(payload)
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "recordType": "figure-workspace-v0760",
        "id": _text(payload.get("workspaceId") or f"workspace-{built['figure']['fingerprint'][:16]}", "workspace id", 160, True),
        "figure": built["figure"],
        "adaptiveRendering": built["result"].get("adaptiveRendering"),
        "generatedAt": _now(),
    }
    workspace["fingerprint"] = _digest({k: v for k, v in workspace.items() if k not in {"generatedAt", "fingerprint"}})
    return {"ok": True, "workspace": workspace}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "sourceRowLimit": MAX_SOURCE_ROWS,
        "renderPointLimit": MAX_RENDER_POINTS,
        "defaultPointBudget": DEFAULT_RENDER_POINTS,
        "strategies": sorted(STRATEGIES),
        "progressiveLevels": ["preview", "interactive", "detail"],
        "deterministic": True,
        "silentDataMutation": False,
        "transformAfterSampling": False,
        "streaming": False,
        "serverSideTiles": False,
        "webgl": False,
        "arbitraryCode": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "large-data-adaptive-rendering-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "largeDataVisualization": True,
        "adaptiveRendering": True,
        "progressiveRendering": True,
        "deterministicReduction": True,
        "sourceRowLimit": MAX_SOURCE_ROWS,
        "renderPointLimit": MAX_RENDER_POINTS,
        "strategies": sorted(STRATEGIES),
        "v0750DataBindingCompatibility": True,
        "v0740Advanced2dCompatibility": True,
        "canvas4dCompatibility": True,
        "silentDataMutation": False,
        "streaming": False,
        "webgl": False,
        "arbitraryCode": False,
    }
