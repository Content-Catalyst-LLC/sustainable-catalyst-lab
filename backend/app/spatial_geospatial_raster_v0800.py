from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any, Iterable

VERSION = "0.80.0"
ENGINE_VERSION = "2.7.0"
RENDERER = "canvas-spatial"
CRS_SCHEMA = "sc-lab-spatial-crs/0.80.0"
VECTOR_SCHEMA = "sc-lab-spatial-vector-layer/0.80.0"
RASTER_SCHEMA = "sc-lab-spatial-raster/0.80.0"
VIEWPORT_SCHEMA = "sc-lab-spatial-viewport/0.80.0"
FIGURE_SCHEMA = "sc-lab-spatial-figure/0.80.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.80.0"
MAX_FEATURES = 50_000
MAX_COORDINATES = 500_000
MAX_RASTER_CELLS = 1_048_576
MAX_LAYERS = 32


class SpatialVisualizationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise SpatialVisualizationError(f"{label} must be numeric")
    if not math.isfinite(out):
        raise SpatialVisualizationError(f"{label} must be finite")
    return out


def _identifier(value: Any, fallback: str) -> str:
    text = str(value or fallback).strip()
    if not text:
        raise SpatialVisualizationError("identifier must not be empty")
    return text[:160]


def normalize_crs(payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = payload or {}
    if not isinstance(payload, dict):
        raise SpatialVisualizationError("crs must be an object")
    identifier = str(payload.get("id") or payload.get("identifier") or "LOCAL:UNSPECIFIED").strip()
    if not identifier:
        raise SpatialVisualizationError("crs.id is required")
    axis_order = str(payload.get("axisOrder") or "xy").lower()
    if axis_order not in {"xy", "yx"}:
        raise SpatialVisualizationError("crs.axisOrder must be xy or yx")
    units = str(payload.get("units") or "unknown").strip().lower()
    geographic = bool(payload.get("geographic", identifier.upper() in {"EPSG:4326", "CRS84", "OGC:CRS84"}))
    out = {
        "schema": CRS_SCHEMA,
        "version": VERSION,
        "id": identifier[:160],
        "name": str(payload.get("name") or identifier)[:240],
        "axisOrder": axis_order,
        "units": units[:80],
        "geographic": geographic,
        "authority": str(payload.get("authority") or "declared")[:80],
        "wkt": str(payload.get("wkt") or "")[:20_000] or None,
        "boundaries": {
            "automaticCRSInference": False,
            "automaticReprojection": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_bounds(value: Any, label: str = "bounds") -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise SpatialVisualizationError(f"{label} must be [minX,minY,maxX,maxY]")
    bounds = [_finite(v, f"{label}[{i}]") for i, v in enumerate(value)]
    if not bounds[0] < bounds[2] or not bounds[1] < bounds[3]:
        raise SpatialVisualizationError(f"{label} must have min < max on both axes")
    return bounds


def normalize_viewport(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SpatialVisualizationError("viewport must be an object")
    bounds = normalize_bounds(payload.get("bounds"), "viewport.bounds")
    out = {
        "schema": VIEWPORT_SCHEMA,
        "version": VERSION,
        "bounds": bounds,
        "crs": normalize_crs(payload.get("crs") or {}),
        "width": max(64, min(8192, int(payload.get("width") or 960))),
        "height": max(64, min(8192, int(payload.get("height") or 540))),
        "preserveAspect": bool(payload.get("preserveAspect", True)),
        "clipToBounds": bool(payload.get("clipToBounds", True)),
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def _coord_pair(value: Any, label: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        raise SpatialVisualizationError(f"{label} must contain x and y")
    return [_finite(value[0], f"{label}.x"), _finite(value[1], f"{label}.y")]


def _normalize_coordinate_tree(value: Any, depth: int, label: str) -> tuple[Any, int, list[float]]:
    if depth == 0:
        pair = _coord_pair(value, label)
        return pair, 1, [pair[0], pair[1], pair[0], pair[1]]
    if not isinstance(value, list) or not value:
        raise SpatialVisualizationError(f"{label} must be a non-empty coordinate array")
    normalized = []
    count = 0
    bounds = [math.inf, math.inf, -math.inf, -math.inf]
    for i, item in enumerate(value):
        child, child_count, child_bounds = _normalize_coordinate_tree(item, depth - 1, f"{label}[{i}]")
        normalized.append(child)
        count += child_count
        bounds[0] = min(bounds[0], child_bounds[0])
        bounds[1] = min(bounds[1], child_bounds[1])
        bounds[2] = max(bounds[2], child_bounds[2])
        bounds[3] = max(bounds[3], child_bounds[3])
    return normalized, count, bounds


_GEOMETRY_DEPTH = {
    "Point": 0,
    "MultiPoint": 1,
    "LineString": 1,
    "MultiLineString": 2,
    "Polygon": 2,
    "MultiPolygon": 3,
}


def normalize_geometry(payload: dict[str, Any]) -> tuple[dict[str, Any], int, list[float]]:
    if not isinstance(payload, dict):
        raise SpatialVisualizationError("geometry must be an object")
    geometry_type = str(payload.get("type") or "")
    if geometry_type not in _GEOMETRY_DEPTH:
        raise SpatialVisualizationError("unsupported geometry type")
    coords, count, bounds = _normalize_coordinate_tree(payload.get("coordinates"), _GEOMETRY_DEPTH[geometry_type], "geometry.coordinates")
    if count > MAX_COORDINATES:
        raise SpatialVisualizationError(f"geometry exceeds {MAX_COORDINATES} coordinate pairs", 413)
    return {"type": geometry_type, "coordinates": coords}, count, bounds


def _merge_bounds(items: Iterable[list[float]]) -> list[float] | None:
    result = [math.inf, math.inf, -math.inf, -math.inf]
    found = False
    for bounds in items:
        found = True
        result[0] = min(result[0], bounds[0])
        result[1] = min(result[1], bounds[1])
        result[2] = max(result[2], bounds[2])
        result[3] = max(result[3], bounds[3])
    return result if found else None


def normalize_vector_layer(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SpatialVisualizationError("vector layer must be an object")
    if payload.get("type") == "FeatureCollection":
        raw_features = payload.get("features") or []
        metadata = {}
    else:
        raw_features = payload.get("features") or []
        metadata = payload
    if not isinstance(raw_features, list):
        raise SpatialVisualizationError("vector features must be an array")
    if len(raw_features) > MAX_FEATURES:
        raise SpatialVisualizationError(f"vector layer exceeds {MAX_FEATURES} features", 413)
    features = []
    coordinate_count = 0
    feature_bounds: list[list[float]] = []
    for i, raw in enumerate(raw_features):
        if not isinstance(raw, dict):
            raise SpatialVisualizationError(f"feature {i} must be an object")
        geometry_payload = raw.get("geometry") if raw.get("type") == "Feature" else raw.get("geometry") or raw
        geometry, count, bounds = normalize_geometry(geometry_payload)
        coordinate_count += count
        if coordinate_count > MAX_COORDINATES:
            raise SpatialVisualizationError(f"vector layer exceeds {MAX_COORDINATES} coordinate pairs", 413)
        props = raw.get("properties") if raw.get("type") == "Feature" else raw.get("properties") or {}
        if props is None:
            props = {}
        if not isinstance(props, dict):
            raise SpatialVisualizationError(f"feature {i} properties must be an object")
        feature = {
            "type": "Feature",
            "id": str(raw.get("id") if raw.get("id") is not None else f"feature-{i+1}"),
            "geometry": geometry,
            "properties": deepcopy(props),
            "bounds": bounds,
            "sourceIndex": i,
        }
        features.append(feature)
        feature_bounds.append(bounds)
    extent = _merge_bounds(feature_bounds)
    out = {
        "schema": VECTOR_SCHEMA,
        "version": VERSION,
        "id": _identifier(metadata.get("id"), "vector-layer"),
        "title": str(metadata.get("title") or "Spatial vector layer")[:240],
        "crs": normalize_crs(metadata.get("crs") or {}),
        "features": features,
        "featureCount": len(features),
        "coordinateCount": coordinate_count,
        "bounds": extent,
        "style": deepcopy(metadata.get("style") or {}),
        "provenance": deepcopy(metadata.get("provenance") or {}),
        "boundaries": {
            "topologyRepair": False,
            "geometryInference": False,
            "automaticReprojection": False,
            "automaticSpatialJoin": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_raster(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SpatialVisualizationError("raster must be an object")
    values = payload.get("values")
    if not isinstance(values, list) or not values:
        raise SpatialVisualizationError("raster.values must be a non-empty array")
    if all(isinstance(row, list) for row in values):
        height = len(values)
        width = len(values[0]) if values else 0
        if width <= 0 or any(len(row) != width for row in values):
            raise SpatialVisualizationError("raster rows must have equal non-zero width")
        grid = deepcopy(values)
    else:
        width = int(payload.get("width") or 0)
        height = int(payload.get("height") or 0)
        if width <= 0 or height <= 0 or width * height != len(values):
            raise SpatialVisualizationError("flat raster values require matching width and height")
        grid = [values[r * width:(r + 1) * width] for r in range(height)]
    cell_count = width * height
    if cell_count > MAX_RASTER_CELLS:
        raise SpatialVisualizationError(f"raster exceeds {MAX_RASTER_CELLS} cells", 413)
    bounds = normalize_bounds(payload.get("bounds"), "raster.bounds")
    nodata = payload.get("nodata")
    finite_values: list[float] = []
    normalized_grid: list[list[float | None]] = []
    nodata_count = 0
    for y, row in enumerate(grid):
        norm_row = []
        for x, raw in enumerate(row):
            is_nodata = raw is None or (nodata is not None and raw == nodata)
            if is_nodata:
                norm_row.append(None)
                nodata_count += 1
                continue
            value = _finite(raw, f"raster.values[{y}][{x}]")
            norm_row.append(value)
            finite_values.append(value)
        normalized_grid.append(norm_row)
    stats = {
        "min": min(finite_values) if finite_values else None,
        "max": max(finite_values) if finite_values else None,
        "validCellCount": len(finite_values),
        "nodataCellCount": nodata_count,
    }
    out = {
        "schema": RASTER_SCHEMA,
        "version": VERSION,
        "id": _identifier(payload.get("id"), "raster-layer"),
        "title": str(payload.get("title") or "Spatial raster layer")[:240],
        "crs": normalize_crs(payload.get("crs") or {}),
        "width": width,
        "height": height,
        "cellCount": cell_count,
        "bounds": bounds,
        "cellSize": [(bounds[2] - bounds[0]) / width, (bounds[3] - bounds[1]) / height],
        "values": normalized_grid,
        "nodata": nodata,
        "statistics": stats,
        "style": deepcopy(payload.get("style") or {}),
        "provenance": deepcopy(payload.get("provenance") or {}),
        "boundaries": {
            "rasterInterpolation": False,
            "rasterResampling": False,
            "nodataImputation": False,
            "automaticReprojection": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def _layer_crs(layer: dict[str, Any]) -> str:
    return str((layer.get("crs") or {}).get("id") or "")


def _auto_extent(layers: list[dict[str, Any]]) -> list[float]:
    extents = [layer.get("bounds") for layer in layers if layer.get("bounds")]
    bounds = _merge_bounds(extents)
    if not bounds:
        raise SpatialVisualizationError("a spatial figure requires explicit layer bounds or viewport bounds")
    if bounds[0] == bounds[2]:
        bounds[0] -= 0.5
        bounds[2] += 0.5
    if bounds[1] == bounds[3]:
        bounds[1] -= 0.5
        bounds[3] += 0.5
    return bounds


def build_spatial_figure(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SpatialVisualizationError("figure must be an object")
    raw_layers = payload.get("layers") or []
    if not isinstance(raw_layers, list) or not raw_layers:
        raise SpatialVisualizationError("spatial figure requires at least one layer")
    if len(raw_layers) > MAX_LAYERS:
        raise SpatialVisualizationError(f"spatial figure supports at most {MAX_LAYERS} layers")
    layers = []
    for i, raw in enumerate(raw_layers):
        if not isinstance(raw, dict):
            raise SpatialVisualizationError(f"layer {i} must be an object")
        kind = str(raw.get("kind") or raw.get("layerType") or "vector")
        if kind == "vector":
            layer = normalize_vector_layer(raw)
        elif kind == "raster":
            layer = normalize_raster(raw)
        else:
            raise SpatialVisualizationError("layer kind must be vector or raster")
        layer["kind"] = kind
        layers.append(layer)
    crs_ids = {c for c in (_layer_crs(layer) for layer in layers) if c}
    if len(crs_ids) > 1:
        raise SpatialVisualizationError("all layers must already use the same declared CRS; automatic reprojection is disabled")
    declared_crs = normalize_crs(payload.get("crs") or (layers[0].get("crs") if layers else {}))
    if crs_ids and declared_crs["id"] not in crs_ids:
        raise SpatialVisualizationError("figure CRS must match layer CRS because automatic reprojection is disabled")
    viewport_payload = payload.get("viewport")
    if viewport_payload:
        viewport = normalize_viewport({**viewport_payload, "crs": viewport_payload.get("crs") or declared_crs})
        if viewport["crs"]["id"] != declared_crs["id"]:
            raise SpatialVisualizationError("viewport CRS must match figure CRS")
    else:
        viewport = normalize_viewport({"bounds": _auto_extent(layers), "crs": declared_crs})
    out = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "id": _identifier(payload.get("id"), "spatial-figure"),
        "title": str(payload.get("title") or "Spatial scientific figure")[:240],
        "subtitle": str(payload.get("subtitle") or "")[:1000],
        "crs": declared_crs,
        "viewport": viewport,
        "layers": layers,
        "layerCount": len(layers),
        "publication": deepcopy(payload.get("publication") or {}),
        "provenance": deepcopy(payload.get("provenance") or {}),
        "boundaries": {
            "automaticCRSInference": False,
            "automaticReprojection": False,
            "automaticGeocoding": False,
            "automaticSpatialJoin": False,
            "topologyRepair": False,
            "rasterInterpolation": False,
            "rasterResampling": False,
            "nodataImputation": False,
            "networkBasemaps": False,
            "arbitraryCode": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return {"ok": True, "figure": out}


def _bbox_intersects(a: list[float], b: list[float]) -> bool:
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def bbox_select(payload: dict[str, Any]) -> dict[str, Any]:
    layer = normalize_vector_layer(payload.get("layer") or payload.get("vectorLayer") or {})
    bbox = normalize_bounds(payload.get("bounds") or payload.get("bbox"), "selection.bounds")
    selected = [feature["id"] for feature in layer["features"] if _bbox_intersects(feature["bounds"], bbox)]
    indexes = [feature["sourceIndex"] for feature in layer["features"] if _bbox_intersects(feature["bounds"], bbox)]
    return {
        "ok": True,
        "version": VERSION,
        "layerId": layer["id"],
        "bounds": bbox,
        "featureIds": selected,
        "sourceIndexes": indexes,
        "selectionCount": len(selected),
        "selectionMode": "explicit-bounding-box-intersection",
        "fingerprint": _hash({"layer": layer["fingerprint"], "bounds": bbox, "ids": selected}),
    }


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    figure_result = build_spatial_figure(payload.get("figure") or payload)
    figure = figure_result["figure"]
    linked = deepcopy(payload.get("linkedComposition") or payload.get("composition"))
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "rendererRegistry": ["svg2d", "canvas3d", "canvas4d", RENDERER],
        "spatialFigure": figure,
        "linkedComposition": linked,
        "controls": {
            "viewport": True,
            "bboxSelection": True,
            "vectorLayers": True,
            "rasterLayers": True,
            "linkedViewsCompatibility": True,
        },
        "provenance": deepcopy(payload.get("provenance") or {}),
    }
    workspace["fingerprint"] = _hash({k: v for k, v in workspace.items() if k != "fingerprint"})
    return {"ok": True, "workspace": workspace}


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "spatial-geospatial-raster-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "renderer": RENDERER,
        "spatialVisualization": True,
        "geospatialVisualization": True,
        "vectorGeometry": True,
        "rasterVisualization": True,
        "coordinateReferenceMetadata": True,
        "explicitViewport": True,
        "bboxSelection": True,
        "mixedRendererComposition": True,
        "v0790LinkedViewsCompatibility": True,
        "v0780TimeParameterCompatibility": True,
        "v0770SceneCompatibility": True,
        "v0760AdaptiveCompatibility": True,
        "v0750DataBindingCompatibility": True,
        "automaticCRSInference": False,
        "automaticReprojection": False,
        "automaticGeocoding": False,
        "automaticSpatialJoin": False,
        "topologyRepair": False,
        "rasterInterpolation": False,
        "rasterResampling": False,
        "nodataImputation": False,
        "networkBasemaps": False,
        "webgl": False,
        "arbitraryCode": False,
        "limits": {
            "features": MAX_FEATURES,
            "coordinatePairs": MAX_COORDINATES,
            "rasterCells": MAX_RASTER_CELLS,
            "layers": MAX_LAYERS,
        },
    }


def policies() -> dict[str, Any]:
    return health()
