from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

from .scientific_data_binding_v0750 import execute_pipeline as execute_pipeline_v0750, normalize_dataset as normalize_dataset_v0750
from .large_data_visualization_v0760 import adapt_dataset as adapt_dataset_v0760, normalize_large_dataset as normalize_large_dataset_v0760

VERSION = "0.78.0"
ENGINE_VERSION = "2.5.0"
RENDERER = "canvas4d"
RENDERER_VERSION = "0.78.0"
STATE_SPACE_SCHEMA = "sc-lab-4d-state-space/0.78.0"
AXIS_SCHEMA = "sc-lab-state-axis/0.78.0"
PROJECTION_SCHEMA = "sc-lab-4d-projection/0.78.0"
SPEC_SCHEMA = "sc-lab-scientific-visualization/0.78.0"
FIGURE_SCHEMA = "sc-lab-scientific-figure/0.78.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.78.0"

MODES = {"4d-points", "time-sequence", "parameter-sweep"}
AXIS_KINDS = {"time", "parameter", "dimension"}
TIME_SCALES = {"index", "elapsed", "timestamp"}
PROJECTION_PLANES = {"xw", "yw", "zw"}
MAX_SOURCE_ROWS = 250_000
MAX_RENDER_POINTS = 5_000
DEFAULT_RENDER_POINTS = 2_000
MAX_FRAMES = 2_000
MAX_PARAMETERS = 256


class TimeParameterSpaceError(ValueError):
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
        raise TimeParameterSpaceError(f"{name} is required.")
    if len(text) > limit:
        raise TimeParameterSpaceError(f"{name} exceeds {limit} characters.")
    return text


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise TimeParameterSpaceError(f"{name} must be numeric.")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise TimeParameterSpaceError(f"{name} must be numeric.") from exc
    if not math.isfinite(out):
        raise TimeParameterSpaceError(f"{name} must be finite.")
    return out


def _timestamp(value: Any, name: str) -> str:
    text = _text(value, name, 80, True)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TimeParameterSpaceError(f"{name} must be ISO-8601.") from exc
    if parsed.tzinfo is None:
        raise TimeParameterSpaceError(f"{name} must include a timezone offset.")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_axis(value: Any, *, default_kind: str = "dimension", default_label: str = "w") -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    kind = str(raw.get("kind") or default_kind).strip().lower()
    if kind not in AXIS_KINDS:
        raise TimeParameterSpaceError("axis.kind must be time, parameter, or dimension.")
    scale = str(raw.get("scale") or ("index" if kind == "time" else "numeric")).strip().lower()
    if kind == "time" and scale not in TIME_SCALES:
        raise TimeParameterSpaceError("time axis scale must be index, elapsed, or timestamp.")
    if kind != "time" and scale not in {"numeric", "categorical"}:
        raise TimeParameterSpaceError("parameter/dimension axis scale must be numeric or categorical.")
    label = _text(raw.get("label") or default_label, "axis.label", 80, True)
    unit = _text(raw.get("unit"), "axis.unit", 32)
    field = _text(raw.get("field"), "axis.field", 120)
    values = raw.get("values") if isinstance(raw.get("values"), list) else []
    normalized_values: list[Any] = []
    if kind == "time" and scale == "timestamp":
        normalized_values = [_timestamp(v, f"axis.values[{i}]") for i, v in enumerate(values)]
    elif scale == "numeric" or (kind == "time" and scale in {"index", "elapsed"}):
        normalized_values = [_finite(v, f"axis.values[{i}]") for i, v in enumerate(values)]
    else:
        normalized_values = [_text(v, f"axis.values[{i}]", 120, True) for i, v in enumerate(values)]
    if len(normalized_values) > MAX_FRAMES:
        raise TimeParameterSpaceError(f"axis.values exceeds {MAX_FRAMES} entries.")
    return {
        "schema": AXIS_SCHEMA,
        "kind": kind,
        "scale": scale,
        "label": label,
        "unit": unit,
        "field": field,
        "values": normalized_values,
        "valueCount": len(normalized_values),
    }


def normalize_projection(value: Any) -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    rotations = raw.get("rotations") if isinstance(raw.get("rotations"), dict) else {}
    out_rotations = {}
    for plane in sorted(PROJECTION_PLANES):
        angle = _finite(rotations.get(plane, 0.0), f"projection.rotations.{plane}")
        if abs(angle) > 3600:
            raise TimeParameterSpaceError("4D rotation angles must remain within ±3600 degrees.")
        out_rotations[plane] = angle
    hyperslice = raw.get("hyperslice") if isinstance(raw.get("hyperslice"), dict) else {}
    enabled = bool(hyperslice.get("enabled", False))
    center = _finite(hyperslice.get("center", 0.0), "projection.hyperslice.center")
    tolerance = _finite(hyperslice.get("tolerance", 0.0), "projection.hyperslice.tolerance")
    if tolerance < 0:
        raise TimeParameterSpaceError("hyperslice tolerance cannot be negative.")
    return {
        "schema": PROJECTION_SCHEMA,
        "rotations": out_rotations,
        "hyperslice": {"enabled": enabled, "center": center, "tolerance": tolerance},
        "normalizeForProjection": bool(raw.get("normalizeForProjection", True)),
        "preserveOriginalCoordinates": True,
    }


def _point(row: dict[str, Any], bindings: dict[str, str], index: int) -> dict[str, Any]:
    coords = {}
    for axis in ("x", "y", "z", "w"):
        field = bindings.get(axis)
        if not field:
            raise TimeParameterSpaceError(f"binding.{axis} is required.")
        coords[axis] = _finite(row.get(field), f"row[{index}].{field}")
    out: dict[str, Any] = {"index": index, **coords}
    for key in ("time", "parameter", "value", "label", "group"):
        field = bindings.get(key)
        if field and field in row:
            value = row.get(field)
            if key in {"value", "parameter"} and value not in (None, ""):
                try:
                    value = _finite(value, f"row[{index}].{field}")
                except TimeParameterSpaceError:
                    if key == "parameter":
                        value = _text(value, f"row[{index}].{field}", 120, True)
                    else:
                        raise
            elif key == "label" or key == "group":
                value = _text(value, f"row[{index}].{field}", 160)
            out[key] = value
    return out


def _axis_value(point: dict[str, Any], axis: dict[str, Any]) -> Any:
    if axis["kind"] == "time":
        return point.get("time", point.get("w"))
    if axis["kind"] == "parameter":
        return point.get("parameter", point.get("w"))
    return point.get("w")


def _sort_key(value: Any, axis: dict[str, Any]) -> tuple[int, Any]:
    if value is None:
        return (1, 0)
    if axis["kind"] == "time" and axis["scale"] == "timestamp":
        try:
            return (0, datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp())
        except ValueError:
            return (0, str(value))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (0, float(value))
    return (0, str(value))


def _frame_index(points: list[dict[str, Any]], axis: dict[str, Any]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for point in points:
        value = _axis_value(point, axis)
        key = _canonical(value)
        bucket = buckets.setdefault(key, {"value": value, "pointIndexes": []})
        bucket["pointIndexes"].append(point["index"])
    frames = sorted(buckets.values(), key=lambda item: _sort_key(item["value"], axis))
    if len(frames) > MAX_FRAMES:
        raise TimeParameterSpaceError(f"state sequence exceeds {MAX_FRAMES} observed states.")
    for i, frame in enumerate(frames):
        frame["index"] = i
        frame["pointCount"] = len(frame["pointIndexes"])
    return frames


def normalize_state_space(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TimeParameterSpaceError("state space must be an object.")
    mode = str(value.get("mode") or "4d-points").strip().lower()
    if mode not in MODES:
        raise TimeParameterSpaceError("mode must be 4d-points, time-sequence, or parameter-sweep.")
    axis_default = "time" if mode == "time-sequence" else "parameter" if mode == "parameter-sweep" else "dimension"
    axis = normalize_axis(value.get("axis"), default_kind=axis_default, default_label="time" if axis_default == "time" else "parameter" if axis_default == "parameter" else "w")
    if mode == "time-sequence" and axis["kind"] != "time":
        raise TimeParameterSpaceError("time-sequence requires a time axis.")
    if mode == "parameter-sweep" and axis["kind"] != "parameter":
        raise TimeParameterSpaceError("parameter-sweep requires a parameter axis.")
    projection = normalize_projection(value.get("projection"))
    points_raw = value.get("points")
    if not isinstance(points_raw, list):
        raise TimeParameterSpaceError("stateSpace.points must be an array.")
    if len(points_raw) > MAX_RENDER_POINTS:
        raise TimeParameterSpaceError(f"stateSpace.points exceeds the render limit of {MAX_RENDER_POINTS}.")
    points: list[dict[str, Any]] = []
    for i, item in enumerate(points_raw):
        if not isinstance(item, dict):
            raise TimeParameterSpaceError(f"points[{i}] must be an object.")
        point = {"index": i}
        for dim in ("x", "y", "z", "w"):
            point[dim] = _finite(item.get(dim), f"points[{i}].{dim}")
        for optional in ("time", "parameter", "value", "label", "group"):
            if optional in item:
                point[optional] = deepcopy(item.get(optional))
        points.append(point)
    frames = _frame_index(points, axis) if mode != "4d-points" else []
    playback = value.get("playback") if isinstance(value.get("playback"), dict) else {}
    playback_out = {
        "enabled": mode == "time-sequence" and bool(playback.get("enabled", True)),
        "loop": bool(playback.get("loop", True)),
        "framesPerSecond": max(0.25, min(30.0, _finite(playback.get("framesPerSecond", 4.0), "playback.framesPerSecond"))),
        "interpolate": False,
    }
    out = {
        "schema": STATE_SPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "mode": mode,
        "title": _text(value.get("title") or "4D scientific state space", "stateSpace.title", 180, True),
        "axis": axis,
        "projection": projection,
        "points": points,
        "pointCount": len(points),
        "frames": frames,
        "frameCount": len(frames),
        "playback": playback_out,
        "dataBoundary": _text(value.get("dataBoundary") or "Observed states only; no temporal or parameter interpolation is performed.", "stateSpace.dataBoundary", 400, True),
        "boundaries": {
            "syntheticFrames": False,
            "temporalInterpolation": False,
            "parameterInterpolation": False,
            "surfaceInterpolation": False,
            "forecasting": False,
            "arbitraryCode": False,
        },
    }
    out["fingerprint"] = _digest({k: out[k] for k in out if k != "fingerprint"})
    return out


def state_space_from_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TimeParameterSpaceError("payload must be an object.")
    mode = str(payload.get("mode") or "4d-points").strip().lower()
    if mode not in MODES:
        raise TimeParameterSpaceError("mode must be 4d-points, time-sequence, or parameter-sweep.")
    dataset_input = payload.get("dataset") or {}
    if not isinstance(dataset_input, dict):
        raise TimeParameterSpaceError("dataset must be an object.")
    raw_rows = dataset_input.get("rows")
    if not isinstance(raw_rows, list):
        raise TimeParameterSpaceError("dataset.rows must be an array.")
    source_rows = len(raw_rows)
    if source_rows > MAX_SOURCE_ROWS:
        raise TimeParameterSpaceError(f"dataset exceeds the {MAX_SOURCE_ROWS} row source limit.")
    render_budget = int(payload.get("renderPointBudget") or DEFAULT_RENDER_POINTS)
    render_budget = max(100, min(MAX_RENDER_POINTS, render_budget))

    bindings_raw = payload.get("binding") if isinstance(payload.get("binding"), dict) else {}
    bindings = {key: _text(bindings_raw.get(key), f"binding.{key}", 120) for key in ("x", "y", "z", "w", "time", "parameter", "value", "label", "group")}
    for required in ("x", "y", "z", "w"):
        if not bindings[required]:
            raise TimeParameterSpaceError(f"binding.{required} is required.")

    pipeline_input = payload.get("pipeline") if isinstance(payload.get("pipeline"), dict) else {"operations": []}
    operations = pipeline_input.get("operations") if isinstance(pipeline_input.get("operations"), list) else []
    adaptation = None
    pipeline_result = None
    if source_rows > MAX_RENDER_POINTS:
        if operations:
            raise TimeParameterSpaceError("v0.78 does not transform after adaptive sampling. Pre-transform or aggregate large datasets upstream, then submit an identity pipeline.")
        large_dataset = normalize_large_dataset_v0760(dataset_input)
        adaptation = adapt_dataset_v0760({
            "dataset": large_dataset,
            "binding": {"kind": "surface-4d", "mappings": {k: bindings[k] for k in ("x", "y", "z", "w")}},
            "renderPlan": {"strategy": "stride", "pointBudget": render_budget, "progressive": False},
        })
        rows = adaptation.get("rows") or []
        authoritative_fingerprint = large_dataset.get("fingerprint") or large_dataset.get("datasetFingerprint")
        representation = "adaptive-stride"
    else:
        dataset = normalize_dataset_v0750(dataset_input)
        authoritative_fingerprint = dataset.get("fingerprint") or dataset.get("datasetFingerprint")
        pipeline_result = execute_pipeline_v0750({"dataset": dataset, "pipeline": pipeline_input})
        rows = pipeline_result.get("rows") or []
        representation = "full-transformed" if operations else "full"
    points = [_point(row, bindings, i) for i, row in enumerate(rows)]
    axis_default = "time" if mode == "time-sequence" else "parameter" if mode == "parameter-sweep" else "dimension"
    axis_input = deepcopy(payload.get("axis") if isinstance(payload.get("axis"), dict) else {})
    axis_input.setdefault("kind", axis_default)
    if axis_default == "time" and bindings.get("time"):
        axis_input.setdefault("field", bindings["time"])
    elif axis_default == "parameter" and bindings.get("parameter"):
        axis_input.setdefault("field", bindings["parameter"])
    axis = normalize_axis(axis_input, default_kind=axis_default, default_label=axis_default)

    state = normalize_state_space({
        "mode": mode,
        "title": payload.get("title") or "4D scientific state space",
        "axis": axis,
        "projection": payload.get("projection") or {},
        "points": points,
        "playback": payload.get("playback") or {},
        "dataBoundary": payload.get("dataBoundary") or "Observed source rows remain authoritative; any render reduction changes only the displayed representation.",
    })
    state["source"] = {
        "sourceRows": source_rows,
        "renderedRows": len(points),
        "representation": representation,
        "authoritativeDatasetFingerprint": authoritative_fingerprint,
        "adaptiveReduction": adaptation is not None,
        "strategy": "stride" if adaptation is not None else "full",
        "renderPointBudget": render_budget,
        "transformAfterSampling": False,
        "pipelineFingerprint": pipeline_result.get("pipelineFingerprint") if pipeline_result else None,
        "transformedRows": pipeline_result.get("rowCount") if pipeline_result else source_rows,
    }
    state["binding"] = bindings
    state["fingerprint"] = _digest({k: state[k] for k in state if k != "fingerprint"})
    return {"ok": True, "stateSpace": state}


def slice_state_space(payload: dict[str, Any]) -> dict[str, Any]:
    state = normalize_state_space(payload.get("stateSpace") or payload.get("state") or payload)
    selector = payload.get("selector") if isinstance(payload.get("selector"), dict) else {}
    axis = state["axis"]
    target_index = selector.get("frameIndex")
    target_value = selector.get("value")
    if state["mode"] == "4d-points":
        center = _finite(selector.get("w", target_value if target_value is not None else 0.0), "selector.w")
        tolerance = _finite(selector.get("tolerance", 0.0), "selector.tolerance")
        points = [p for p in state["points"] if abs(p["w"] - center) <= tolerance]
        selection = {"kind": "hyperslice", "w": center, "tolerance": tolerance}
    else:
        frames = state["frames"]
        if target_index is not None:
            idx = int(target_index)
            if idx < 0 or idx >= len(frames):
                raise TimeParameterSpaceError("selector.frameIndex is out of range.")
            frame = frames[idx]
        elif target_value is not None:
            matches = [f for f in frames if _canonical(f["value"]) == _canonical(target_value)]
            if not matches:
                raise TimeParameterSpaceError("selector.value is not an observed state.")
            frame = matches[0]
        elif frames:
            frame = frames[0]
        else:
            frame = {"index": 0, "value": None, "pointIndexes": []}
        indexes = set(frame["pointIndexes"])
        points = [p for p in state["points"] if p["index"] in indexes]
        selection = {"kind": axis["kind"], "frameIndex": frame["index"], "value": frame["value"]}
    return {
        "ok": True,
        "schema": "sc-lab-state-slice/0.78.0",
        "version": VERSION,
        "selection": selection,
        "points": points,
        "pointCount": len(points),
        "interpolated": False,
        "forecast": False,
    }


def build_figure(payload: dict[str, Any]) -> dict[str, Any]:
    state_result = state_space_from_dataset(payload) if "dataset" in payload else {"ok": True, "stateSpace": normalize_state_space(payload.get("stateSpace") or payload)}
    state = state_result["stateSpace"]
    figure = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "title": _text(payload.get("title") or state["title"], "figure.title", 180, True),
        "stateSpace": state,
        "provenance": {
            "stateSpaceFingerprint": state["fingerprint"],
            "authoritativeDatasetFingerprint": state.get("source", {}).get("authoritativeDatasetFingerprint"),
            "renderRepresentation": state.get("source", {}).get("representation", "explicit"),
        },
        "createdAt": _now(),
    }
    figure["fingerprint"] = _digest({k: figure[k] for k in figure if k not in {"fingerprint", "createdAt"}})
    return {"ok": True, "figure": figure}


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    figure_result = build_figure(payload)
    figure = figure_result["figure"]
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "title": _text(payload.get("workspaceTitle") or figure["title"], "workspace.title", 180, True),
        "figures": [figure],
        "controls": {
            "timeScrubber": figure["stateSpace"]["mode"] == "time-sequence",
            "parameterScrubber": figure["stateSpace"]["mode"] == "parameter-sweep",
            "hyperslice": True,
            "rotationPlanes": sorted(PROJECTION_PLANES),
            "discretePlaybackOnly": True,
        },
        "createdAt": _now(),
    }
    workspace["fingerprint"] = _digest({k: workspace[k] for k in workspace if k not in {"fingerprint", "createdAt"}})
    return {"ok": True, "workspace": workspace}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "modes": sorted(MODES),
        "axisKinds": sorted(AXIS_KINDS),
        "timeScales": sorted(TIME_SCALES),
        "projectionPlanes": sorted(PROJECTION_PLANES),
        "limits": {
            "sourceRows": MAX_SOURCE_ROWS,
            "renderPoints": MAX_RENDER_POINTS,
            "defaultRenderPoints": DEFAULT_RENDER_POINTS,
            "observedStates": MAX_FRAMES,
            "parameterDefinitions": MAX_PARAMETERS,
        },
        "capabilities": {
            "fourDimensionalProjection": True,
            "timeStatePlayback": True,
            "parameterSweep": True,
            "hyperslicing": True,
            "xwRotation": True,
            "ywRotation": True,
            "zwRotation": True,
            "discreteScrubbing": True,
            "observedStatePlayback": True,
            "v0770SceneCompatibility": True,
            "v0760AdaptiveCompatibility": True,
            "v0750DataBindingCompatibility": True,
        },
        "boundaries": {
            "syntheticFrames": False,
            "temporalInterpolation": False,
            "parameterInterpolation": False,
            "automaticTrajectories": False,
            "surfaceInterpolation": False,
            "forecasting": False,
            "arbitraryCode": False,
        },
    }


def health() -> dict[str, Any]:
    p = policies()
    return {
        "ok": True,
        "status": "4d-time-parameter-space-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "rendererVersion": RENDERER_VERSION,
        "fourDimensionalProjection": True,
        "timeStatePlayback": True,
        "parameterSweep": True,
        "hyperslicing": True,
        "discreteScrubbing": True,
        "observedStatePlayback": True,
        "v0770SceneCompatibility": True,
        "v0760AdaptiveCompatibility": True,
        "v0750DataBindingCompatibility": True,
        "svg2dCompatibility": True,
        "canvas3dCompatibility": True,
        "syntheticFrames": False,
        "temporalInterpolation": False,
        "parameterInterpolation": False,
        "surfaceInterpolation": False,
        "forecasting": False,
        "arbitraryCode": False,
        "limits": p["limits"],
    }
