from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

from .scientific_data_binding_v0750 import (
    ScientificDataBindingError,
    execute_pipeline as execute_pipeline_v0750,
    normalize_dataset as normalize_dataset_v0750,
)
from .large_data_visualization_v0760 import (
    LargeDataVisualizationError,
    adapt_dataset as adapt_dataset_v0760,
    normalize_large_dataset as normalize_large_dataset_v0760,
)

VERSION = "0.77.0"
ENGINE_VERSION = "2.4.0"
RENDERER = "canvas3d"
RENDERER_VERSION = "0.77.0"
SCENE_SCHEMA = "sc-lab-scientific-scene/0.77.0"
CAMERA_SCHEMA = "sc-lab-scientific-scene-camera/0.77.0"
OBJECT_SCHEMA = "sc-lab-scientific-scene-object/0.77.0"
SPEC_SCHEMA = "sc-lab-scientific-visualization/0.77.0"
FIGURE_SCHEMA = "sc-lab-scientific-figure/0.77.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.77.0"
MAX_SCENE_OBJECTS = 32
MAX_VERTICES_PER_OBJECT = 20_000
MAX_TOTAL_VERTICES = 25_000
MAX_TRIANGLES_PER_MESH = 30_000
MAX_DATASET_RENDER_ROWS = 5_000
OBJECT_TYPES = {"point-cloud", "polyline", "line-segments", "mesh", "vectors"}
PROJECTIONS = {"perspective", "orthographic"}
ID_RE = re.compile(r"^[A-Za-z0-9._:-]+$")


class ScientificSceneError(ValueError):
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
        raise ScientificSceneError(f"{name} is required.")
    if len(text) > limit:
        raise ScientificSceneError(f"{name} exceeds {limit} characters.")
    return text


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ScientificSceneError(f"{name} must be numeric.")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ScientificSceneError(f"{name} must be numeric.") from exc
    if not math.isfinite(out):
        raise ScientificSceneError(f"{name} must be finite.")
    return out


def _vec3(value: Any, name: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ScientificSceneError(f"{name} must contain exactly three numeric coordinates.")
    return [_finite(value[i], f"{name}[{i}]") for i in range(3)]


def _norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [a[i] - b[i] for i in range(3)]


def normalize_camera(payload: dict[str, Any] | None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    projection = _text(source.get("projection") or "perspective", "camera projection", 30, True).lower()
    if projection not in PROJECTIONS:
        raise ScientificSceneError(f"unsupported camera projection: {projection}.")
    position = _vec3(source.get("position") or [3.2, 2.4, 4.4], "camera.position")
    target = _vec3(source.get("target") or [0, 0, 0], "camera.target")
    up = _vec3(source.get("up") or [0, 1, 0], "camera.up")
    if _norm(_sub(position, target)) < 1e-9:
        raise ScientificSceneError("camera.position must differ from camera.target.")
    if _norm(up) < 1e-9:
        raise ScientificSceneError("camera.up must be non-zero.")
    fov = _finite(source.get("fovDegrees", 45), "camera.fovDegrees")
    if fov < 10 or fov > 120:
        raise ScientificSceneError("camera.fovDegrees must be between 10 and 120.")
    near = _finite(source.get("near", 0.01), "camera.near")
    far = _finite(source.get("far", 1000), "camera.far")
    if near <= 0 or far <= near:
        raise ScientificSceneError("camera near/far clipping planes are invalid.")
    ortho_scale = _finite(source.get("orthographicScale", 2.4), "camera.orthographicScale")
    if ortho_scale <= 0:
        raise ScientificSceneError("camera.orthographicScale must be positive.")
    camera = {
        "schema": CAMERA_SCHEMA,
        "version": VERSION,
        "projection": projection,
        "position": position,
        "target": target,
        "up": up,
        "fovDegrees": fov,
        "near": near,
        "far": far,
        "orthographicScale": ortho_scale,
        "interaction": {
            "orbit": bool((source.get("interaction") or {}).get("orbit", True)) if isinstance(source.get("interaction"), dict) else True,
            "pan": bool((source.get("interaction") or {}).get("pan", False)) if isinstance(source.get("interaction"), dict) else False,
            "zoom": bool((source.get("interaction") or {}).get("zoom", True)) if isinstance(source.get("interaction"), dict) else True,
        },
    }
    camera["fingerprint"] = _digest({k: v for k, v in camera.items() if k != "fingerprint"})
    return camera


def _normalize_vertices(value: Any, name: str) -> list[list[float]]:
    if not isinstance(value, list) or not value:
        raise ScientificSceneError(f"{name} requires a non-empty array of 3D vertices.")
    if len(value) > MAX_VERTICES_PER_OBJECT:
        raise ScientificSceneError(f"{name} exceeds the {MAX_VERTICES_PER_OBJECT}-vertex object limit.")
    return [_vec3(vertex, f"{name}[{i}]") for i, vertex in enumerate(value)]


def normalize_object(payload: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificSceneError("scene objects must be objects.")
    kind = _text(payload.get("type") or payload.get("kind"), "scene object type", 40, True).lower()
    if kind not in OBJECT_TYPES:
        raise ScientificSceneError(f"unsupported scene object type: {kind}.")
    raw_id = _text(payload.get("id") or f"object-{index + 1}", "scene object id", 160, True)
    if not ID_RE.fullmatch(raw_id):
        raise ScientificSceneError("scene object id contains unsupported characters.")
    obj: dict[str, Any] = {
        "schema": OBJECT_SCHEMA,
        "version": VERSION,
        "id": raw_id,
        "type": kind,
        "title": _text(payload.get("title") or raw_id, "scene object title", 240, True),
        "visible": payload.get("visible") is not False,
        "opacity": max(0.0, min(1.0, _finite(payload.get("opacity", 1.0), "scene object opacity"))),
        "style": deepcopy(payload.get("style") or {}),
        "provenance": deepcopy(payload.get("provenance") or {}),
    }
    if kind in {"point-cloud", "polyline", "line-segments", "mesh"}:
        obj["vertices"] = _normalize_vertices(payload.get("vertices"), f"scene.objects[{index}].vertices")
    if kind == "point-cloud":
        labels = payload.get("labels") or []
        values = payload.get("values") or []
        if labels and (not isinstance(labels, list) or len(labels) != len(obj["vertices"])):
            raise ScientificSceneError("point-cloud labels must align one-to-one with vertices.")
        if values and (not isinstance(values, list) or len(values) != len(obj["vertices"])):
            raise ScientificSceneError("point-cloud values must align one-to-one with vertices.")
        obj["labels"] = [_text(v, "point label", 240) for v in labels]
        obj["values"] = [None if v is None else _finite(v, "point scalar value") for v in values]
        obj["pointSize"] = max(1.0, min(18.0, _finite(payload.get("pointSize", 4), "pointSize")))
    elif kind == "polyline":
        obj["closed"] = bool(payload.get("closed", False))
        obj["lineWidth"] = max(0.5, min(8.0, _finite(payload.get("lineWidth", 1.5), "lineWidth")))
    elif kind == "line-segments":
        if len(obj["vertices"]) % 2:
            raise ScientificSceneError("line-segments requires an even number of vertices.")
        obj["lineWidth"] = max(0.5, min(8.0, _finite(payload.get("lineWidth", 1.5), "lineWidth")))
    elif kind == "mesh":
        triangles = payload.get("triangles") or payload.get("faces")
        if not isinstance(triangles, list) or not triangles:
            raise ScientificSceneError("mesh requires explicit triangle topology; automatic triangulation is disabled.")
        if len(triangles) > MAX_TRIANGLES_PER_MESH:
            raise ScientificSceneError(f"mesh exceeds the {MAX_TRIANGLES_PER_MESH}-triangle limit.")
        out_faces: list[list[int]] = []
        vertex_count = len(obj["vertices"])
        for face_i, face in enumerate(triangles):
            if not isinstance(face, (list, tuple)) or len(face) != 3:
                raise ScientificSceneError(f"mesh triangle {face_i} must contain exactly three vertex indexes.")
            indexes = []
            for j, raw in enumerate(face):
                if isinstance(raw, bool):
                    raise ScientificSceneError("mesh triangle indexes must be integers.")
                try:
                    idx = int(raw)
                except (TypeError, ValueError) as exc:
                    raise ScientificSceneError("mesh triangle indexes must be integers.") from exc
                if idx < 0 or idx >= vertex_count:
                    raise ScientificSceneError(f"mesh triangle index {idx} is outside the vertex array.")
                indexes.append(idx)
            if len(set(indexes)) != 3:
                raise ScientificSceneError("mesh triangles must reference three distinct vertices.")
            out_faces.append(indexes)
        obj["triangles"] = out_faces
        obj["wireframe"] = bool(payload.get("wireframe", False))
        obj["twoSided"] = bool(payload.get("twoSided", True))
    elif kind == "vectors":
        origins = _normalize_vertices(payload.get("origins"), f"scene.objects[{index}].origins")
        vectors = _normalize_vertices(payload.get("vectors"), f"scene.objects[{index}].vectors")
        if len(origins) != len(vectors):
            raise ScientificSceneError("vector origins and vectors must have the same length.")
        obj["origins"] = origins
        obj["vectors"] = vectors
        obj["scale"] = _finite(payload.get("scale", 1.0), "vector scale")
        obj["lineWidth"] = max(0.5, min(8.0, _finite(payload.get("lineWidth", 1.25), "lineWidth")))
    obj["fingerprint"] = _digest({k: v for k, v in obj.items() if k != "fingerprint"})
    return obj


def _object_points(obj: dict[str, Any]) -> list[list[float]]:
    if obj["type"] == "vectors":
        points = list(obj["origins"])
        for origin, vector in zip(obj["origins"], obj["vectors"]):
            points.append([origin[i] + vector[i] * obj["scale"] for i in range(3)])
        return points
    return list(obj.get("vertices") or [])


def _bounds(objects: list[dict[str, Any]]) -> dict[str, Any]:
    points = [point for obj in objects if obj.get("visible", True) for point in _object_points(obj)]
    if not points:
        points = [point for obj in objects for point in _object_points(obj)]
    if not points:
        raise ScientificSceneError("scene contains no drawable 3D coordinates.")
    minima = [min(p[i] for p in points) for i in range(3)]
    maxima = [max(p[i] for p in points) for i in range(3)]
    center = [(minima[i] + maxima[i]) / 2 for i in range(3)]
    extent = [maxima[i] - minima[i] for i in range(3)]
    radius = max(1e-12, math.sqrt(sum((extent[i] / 2) ** 2 for i in range(3))))
    return {"min": minima, "max": maxima, "center": center, "extent": extent, "radius": radius}


def normalize_scene(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificSceneError("scene definition must be an object.")
    raw_objects = payload.get("objects") or []
    if not isinstance(raw_objects, list) or not raw_objects:
        raise ScientificSceneError("scene requires at least one object.")
    if len(raw_objects) > MAX_SCENE_OBJECTS:
        raise ScientificSceneError(f"scene exceeds the {MAX_SCENE_OBJECTS}-object limit.")
    objects = [normalize_object(obj, i) for i, obj in enumerate(raw_objects)]
    total_vertices = sum(len(_object_points(obj)) for obj in objects)
    if total_vertices > MAX_TOTAL_VERTICES:
        raise ScientificSceneError(f"scene exceeds the {MAX_TOTAL_VERTICES}-coordinate limit.")
    scene_bounds = _bounds(objects)
    axes_src = payload.get("axes") if isinstance(payload.get("axes"), dict) else {}
    labels_src = axes_src.get("labels") if isinstance(axes_src.get("labels"), dict) else {}
    units_src = axes_src.get("units") if isinstance(axes_src.get("units"), dict) else {}
    clip_src = payload.get("clipping") if isinstance(payload.get("clipping"), dict) else {}
    clipping = {"enabled": bool(clip_src.get("enabled", False)), "bounds": deepcopy(clip_src.get("bounds") or {})}
    if clipping["enabled"]:
        for axis in ("x", "y", "z"):
            if axis in clipping["bounds"]:
                interval = clipping["bounds"][axis]
                if not isinstance(interval, (list, tuple)) or len(interval) != 2:
                    raise ScientificSceneError(f"clipping.bounds.{axis} must contain [min,max].")
                lo, hi = _finite(interval[0], f"clipping {axis} min"), _finite(interval[1], f"clipping {axis} max")
                if hi < lo:
                    raise ScientificSceneError(f"clipping.bounds.{axis} max must be >= min.")
                clipping["bounds"][axis] = [lo, hi]
    scene = {
        "schema": SCENE_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-scene-v0770",
        "id": _text(payload.get("id") or f"scene-{_digest(raw_objects)[:16]}", "scene id", 160, True),
        "title": _text(payload.get("title") or "3D scientific scene", "scene title", 240, True),
        "renderer": RENDERER,
        "rendererVersion": RENDERER_VERSION,
        "camera": normalize_camera(payload.get("camera")),
        "axes": {
            "visible": axes_src.get("visible") is not False,
            "grid": axes_src.get("grid") is not False,
            "labels": {axis: _text(labels_src.get(axis) or axis.upper(), f"{axis} axis label", 120, True) for axis in ("x", "y", "z")},
            "units": {axis: _text(units_src.get(axis), f"{axis} axis unit", 120) for axis in ("x", "y", "z")},
        },
        "clipping": clipping,
        "objects": objects,
        "objectCount": len(objects),
        "coordinateCount": total_vertices,
        "bounds": scene_bounds,
        "lighting": {"mode": "directional-lambert", "direction": [0.45, 0.75, 0.8], "ambient": 0.28},
        "rendering": {
            "depthSort": "painter",
            "depthBuffer": False,
            "webgl": False,
            "hardwareAccelerationRequired": False,
            "interactive": True,
        },
        "dataBoundary": _text(payload.get("dataBoundary") or "Three-dimensional coordinates and explicit geometry only. No interpolation, topology inference, hidden-surface guarantees, or invented scientific values.", "data boundary", 600, True),
        "provenance": deepcopy(payload.get("provenance") or {}),
    }
    scene["fingerprint"] = _digest({k: v for k, v in scene.items() if k != "fingerprint"})
    return scene


def _mapping(payload: dict[str, Any]) -> dict[str, str]:
    source = payload if isinstance(payload, dict) else {}
    out = {}
    for role in ("x", "y", "z", "label", "value", "dx", "dy", "dz"):
        value = _text(source.get(role), f"mapping {role}", 160)
        if value:
            out[role] = value
    for role in ("x", "y", "z"):
        if role not in out:
            raise ScientificSceneError(f"3D dataset binding requires an explicit {role} mapping.")
    return out


def _numeric_rows(rows: list[dict[str, Any]], mapping: dict[str, str], *, vector_mode: bool = False) -> tuple[list[list[float]], list[str], list[float | None], list[list[float]]]:
    vertices: list[list[float]] = []
    labels: list[str] = []
    values: list[float | None] = []
    vectors: list[list[float]] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ScientificSceneError(f"dataset row {i + 1} must be an object.")
        try:
            point = [_finite(row.get(mapping[axis]), f"row {i + 1} {axis}") for axis in ("x", "y", "z")]
        except ScientificSceneError as exc:
            raise ScientificSceneError(f"3D binding failed: {exc}") from exc
        vertices.append(point)
        labels.append(_text(row.get(mapping["label"]), "point label", 240) if mapping.get("label") else "")
        values.append(_finite(row.get(mapping["value"]), f"row {i + 1} value") if mapping.get("value") and row.get(mapping["value"]) is not None else None)
        if vector_mode:
            for role in ("dx", "dy", "dz"):
                if role not in mapping:
                    raise ScientificSceneError("3D vector binding requires dx, dy, and dz mappings.")
            vectors.append([_finite(row.get(mapping[role]), f"row {i + 1} {role}") for role in ("dx", "dy", "dz")])
    return vertices, labels, values, vectors


def scene_from_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificSceneError("3D dataset scene request must be an object.")
    dataset_src = payload.get("dataset") or payload.get("data") or {}
    if not isinstance(dataset_src, dict):
        raise ScientificSceneError("dataset must be an object.")
    rows = dataset_src.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ScientificSceneError("dataset.rows must be a non-empty array.")
    mapping = _mapping(payload.get("mapping") or payload.get("mappings") or {})
    pipeline = payload.get("pipeline") if isinstance(payload.get("pipeline"), dict) else {"operations": []}
    operations = pipeline.get("operations") if isinstance(pipeline, dict) and isinstance(pipeline.get("operations"), list) else []
    source_dataset = normalize_large_dataset_v0760(dataset_src) if len(rows) > MAX_DATASET_RENDER_ROWS else normalize_dataset_v0750(dataset_src)
    adaptive = None
    if len(rows) > MAX_DATASET_RENDER_ROWS:
        if operations:
            raise ScientificSceneError("3D large-data scenes never transform after adaptive reduction. Pre-transform or aggregate upstream, then submit an identity pipeline.")
        try:
            adaptive = adapt_dataset_v0760({
                "dataset": dataset_src,
                "binding": {"id": "scene3d-adaptive-binding", "kind": "scatter", "mappings": {"x": mapping["x"], "y": mapping["y"]}},
                "renderPlan": {"strategy": "stride", "pointBudget": min(MAX_DATASET_RENDER_ROWS, int((payload.get("renderPlan") or {}).get("pointBudget", MAX_DATASET_RENDER_ROWS))), "progressive": False},
            })
        except (LargeDataVisualizationError, ScientificDataBindingError) as exc:
            raise ScientificSceneError(str(exc)) from exc
        transformed_rows = adaptive["rows"]
        transformed_units = dict(adaptive.get("units") or source_dataset.get("units") or {})
        lineage = []
        pipeline_fingerprint = _digest({"operations": []})
        pipeline_result_fingerprint = adaptive["fingerprint"]
    else:
        try:
            pipeline_result = execute_pipeline_v0750({"dataset": dataset_src, "pipeline": pipeline})
        except ScientificDataBindingError as exc:
            raise ScientificSceneError(str(exc)) from exc
        transformed_rows = pipeline_result["rows"]
        transformed_units = pipeline_result["units"]
        lineage = pipeline_result["lineage"]
        pipeline_fingerprint = pipeline_result["pipelineFingerprint"]
        pipeline_result_fingerprint = pipeline_result["fingerprint"]
    geometry = _text(payload.get("geometry") or "point-cloud", "3D geometry", 40, True).lower()
    if geometry not in {"point-cloud", "polyline", "vectors"}:
        raise ScientificSceneError("dataset-bound 3D geometry supports point-cloud, polyline, or vectors. Meshes require explicit vertices and triangle topology.")
    vertices, labels, values, vectors = _numeric_rows(transformed_rows, mapping, vector_mode=geometry == "vectors")
    obj: dict[str, Any]
    if geometry == "vectors":
        obj = {"id": "dataset-vectors", "type": "vectors", "title": payload.get("objectTitle") or "Dataset vectors", "origins": vertices, "vectors": vectors, "scale": (payload.get("style") or {}).get("vectorScale", 1.0), "style": deepcopy(payload.get("style") or {})}
    elif geometry == "polyline":
        obj = {"id": "dataset-polyline", "type": "polyline", "title": payload.get("objectTitle") or "Dataset trajectory", "vertices": vertices, "lineWidth": (payload.get("style") or {}).get("lineWidth", 1.5), "style": deepcopy(payload.get("style") or {})}
    else:
        obj = {"id": "dataset-points", "type": "point-cloud", "title": payload.get("objectTitle") or "Dataset observations", "vertices": vertices, "labels": labels, "values": values, "pointSize": (payload.get("style") or {}).get("pointSize", 4), "style": deepcopy(payload.get("style") or {})}
    units = {axis: _text(transformed_units.get(mapping[axis]), f"{axis} unit", 120) for axis in ("x", "y", "z")}
    labels_map = payload.get("axisLabels") if isinstance(payload.get("axisLabels"), dict) else {}
    scene_payload = {
        "id": payload.get("sceneId") or f"scene-{source_dataset['id']}",
        "title": payload.get("title") or "3D scientific scene",
        "objects": [obj],
        "camera": payload.get("camera") or {},
        "axes": {"labels": {axis: labels_map.get(axis) or mapping[axis] for axis in ("x", "y", "z")}, "units": units, "grid": payload.get("showGrid") is not False},
        "clipping": payload.get("clipping") or {},
        "dataBoundary": "Dataset-bound 3D coordinates with explicit row order and mappings. No interpolation, inferred topology, forecasting, or invented observations.",
        "provenance": {
            "datasetId": source_dataset["id"],
            "datasetFingerprint": source_dataset["fingerprint"],
            "sourceRowCount": source_dataset["rowCount"],
            "renderedRowCount": len(transformed_rows),
            "pipelineFingerprint": pipeline_fingerprint,
            "pipelineResultFingerprint": pipeline_result_fingerprint,
            "transformationLineage": lineage,
            "adaptiveRenderFingerprint": adaptive["fingerprint"] if adaptive else None,
            "adaptiveRenderStrategy": adaptive["renderPlan"]["strategy"] if adaptive else "full",
            "mapping": mapping,
        },
    }
    scene = normalize_scene(scene_payload)
    spec = {
        "schema": SPEC_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-visualization-spec",
        "visualizationEngine": ENGINE_VERSION,
        "kind": f"{geometry}-3d",
        "renderer": RENDERER,
        "rendererVersion": RENDERER_VERSION,
        "title": scene["title"],
        "scene": scene,
        "publication": deepcopy(payload.get("publication") or {}),
        "rendering": {"renderer": RENDERER, "dataMode": "project-data-bound-3d", "interactive": True, "depthSort": "painter", "webgl": False},
        "exports": ["png", "json"],
        "dataBoundary": scene["dataBoundary"],
        "provenance": deepcopy(scene["provenance"]),
    }
    spec["fingerprint"] = _digest({k: v for k, v in spec.items() if k != "fingerprint"})
    return {"ok": True, "version": VERSION, "scene": scene, "spec": spec, "adaptiveRendering": adaptive, "dataset": source_dataset}


def build_figure(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificSceneError("3D figure request must be an object.")
    if payload.get("scene") and not payload.get("dataset") and not payload.get("data"):
        scene = normalize_scene(payload["scene"])
        spec = {
            "schema": SPEC_SCHEMA,
            "version": VERSION,
            "recordType": "scientific-visualization-spec",
            "visualizationEngine": ENGINE_VERSION,
            "kind": "scene-3d",
            "renderer": RENDERER,
            "rendererVersion": RENDERER_VERSION,
            "title": scene["title"],
            "scene": scene,
            "publication": deepcopy(payload.get("publication") or {}),
            "rendering": {"renderer": RENDERER, "dataMode": "explicit-scene", "interactive": True, "depthSort": "painter", "webgl": False},
            "exports": ["png", "json"],
            "dataBoundary": scene["dataBoundary"],
            "provenance": deepcopy(scene["provenance"]),
        }
        spec["fingerprint"] = _digest({k: v for k, v in spec.items() if k != "fingerprint"})
        result = {"ok": True, "scene": scene, "spec": spec, "adaptiveRendering": None, "dataset": None}
    else:
        result = scene_from_dataset(payload)
    figure_src = payload.get("figure") if isinstance(payload.get("figure"), dict) else {}
    figure = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-figure-v0770",
        "id": _text(figure_src.get("id") or f"figure-{result['spec']['fingerprint'][:16]}", "figure id", 160, True),
        "title": _text(figure_src.get("title") or result["spec"].get("title"), "figure title", 240, True),
        "status": _text(figure_src.get("status") or "draft", "figure status", 40, True),
        "graph": result["spec"],
        "scene": result["scene"],
        "adaptiveRendering": result.get("adaptiveRendering"),
        "provenance": {**deepcopy(result["spec"].get("provenance") or {}), "createdAt": _now(), "updatedAt": _now()},
    }
    if not ID_RE.fullmatch(figure["id"]):
        raise ScientificSceneError("figure id contains unsupported characters.")
    figure["fingerprint"] = _digest({k: v for k, v in figure.items() if k != "fingerprint"})
    return {"ok": True, "figure": figure, "result": result}


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    built = build_figure(payload)
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "recordType": "figure-workspace-v0770",
        "id": _text(payload.get("workspaceId") or f"workspace-{built['figure']['fingerprint'][:16]}", "workspace id", 160, True),
        "figure": built["figure"],
        "scene": built["figure"]["scene"],
        "generatedAt": _now(),
    }
    workspace["fingerprint"] = _digest({k: v for k, v in workspace.items() if k not in {"generatedAt", "fingerprint"}})
    return {"ok": True, "workspace": workspace}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "rendererVersion": RENDERER_VERSION,
        "objectTypes": sorted(OBJECT_TYPES),
        "cameraProjections": sorted(PROJECTIONS),
        "maxSceneObjects": MAX_SCENE_OBJECTS,
        "maxVerticesPerObject": MAX_VERTICES_PER_OBJECT,
        "maxTotalCoordinates": MAX_TOTAL_VERTICES,
        "maxTrianglesPerMesh": MAX_TRIANGLES_PER_MESH,
        "datasetRenderRowLimit": MAX_DATASET_RENDER_ROWS,
        "explicitMeshTopologyRequired": True,
        "v0760AdaptiveCompatibility": True,
        "v0750TransformationCompatibility": True,
        "webgl": False,
        "depthBuffer": False,
        "automaticTriangulation": False,
        "surfaceInterpolation": False,
        "hiddenSurfaceGuarantee": False,
        "arbitraryCode": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-3d-scene-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "rendererVersion": RENDERER_VERSION,
        "scientificScene3d": True,
        "pointCloud3d": True,
        "polyline3d": True,
        "mesh3d": True,
        "vectorField3d": True,
        "perspectiveCamera": True,
        "orthographicCamera": True,
        "orbitInteraction": True,
        "depthSorting": True,
        "clippingIntent": True,
        "v0760AdaptiveCompatibility": True,
        "v0750DataBindingCompatibility": True,
        "svg2dCompatibility": True,
        "canvas4dCompatibility": True,
        "webgl": False,
        "automaticTriangulation": False,
        "surfaceInterpolation": False,
        "arbitraryCode": False,
    }
