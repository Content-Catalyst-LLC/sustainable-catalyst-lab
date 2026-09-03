from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any

VERSION = "0.81.0"
ENGINE_VERSION = "2.8.0"
RENDERER_OVERLAY = "scientific-markup"
ANNOTATION_SCHEMA = "sc-lab-scientific-annotation/0.81.0"
MEASUREMENT_SCHEMA = "sc-lab-scientific-measurement/0.81.0"
LAYER_SCHEMA = "sc-lab-scientific-markup-layer/0.81.0"
FIGURE_SCHEMA = "sc-lab-marked-scientific-figure/0.81.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.81.0"
MAX_ANNOTATIONS = 2_000
MAX_MEASUREMENTS = 2_000
MAX_MARKUP_LAYERS = 32
MAX_POINTS_PER_MARK = 2_000


class ScientificMarkupError(ValueError):
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
        raise ScientificMarkupError(f"{label} must be numeric")
    if not math.isfinite(out):
        raise ScientificMarkupError(f"{label} must be finite")
    return out


def _identifier(value: Any, fallback: str) -> str:
    text = str(value or fallback).strip()
    if not text:
        raise ScientificMarkupError("identifier must not be empty")
    return text[:160]


def _point(value: Any, label: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or not 2 <= len(value) <= 4:
        raise ScientificMarkupError(f"{label} must contain 2–4 coordinates")
    return [_finite(v, f"{label}[{i}]") for i, v in enumerate(value)]


def _points(value: Any, label: str, minimum: int = 1) -> list[list[float]]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ScientificMarkupError(f"{label} must contain at least {minimum} point(s)")
    if len(value) > MAX_POINTS_PER_MARK:
        raise ScientificMarkupError(f"{label} exceeds {MAX_POINTS_PER_MARK} points", 413)
    out = [_point(v, f"{label}[{i}]") for i, v in enumerate(value)]
    dims = {len(p) for p in out}
    if len(dims) != 1:
        raise ScientificMarkupError(f"{label} points must use the same dimensionality")
    return out


def _coordinate_context(payload: dict[str, Any]) -> dict[str, Any]:
    space = str(payload.get("coordinateSpace") or "data-2d").strip().lower()
    if space not in {"screen-normalized", "data-2d", "data-3d", "state-4d", "projected", "geographic"}:
        raise ScientificMarkupError("unsupported coordinateSpace")
    units = str(payload.get("units") or "unitless").strip()[:80]
    crs = payload.get("crs")
    if crs is not None and not isinstance(crs, dict):
        raise ScientificMarkupError("crs must be an object when supplied")
    return {
        "coordinateSpace": space,
        "units": units,
        "crs": deepcopy(crs) if isinstance(crs, dict) else None,
    }


ANNOTATION_TYPES = {"point", "label", "arrow", "line", "polyline", "region", "threshold-x", "threshold-y"}


def normalize_annotation(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificMarkupError("annotation must be an object")
    kind = str(payload.get("type") or payload.get("kind") or "label").strip().lower()
    if kind not in ANNOTATION_TYPES:
        raise ScientificMarkupError("unsupported annotation type")
    context = _coordinate_context(payload)
    raw_points = payload.get("points")
    if raw_points is None and payload.get("point") is not None:
        raw_points = [payload.get("point")]
    if raw_points is None and payload.get("position") is not None:
        raw_points = [payload.get("position")]
    minimum = 2 if kind in {"arrow", "line", "polyline", "region"} else 1
    pts = _points(raw_points, "annotation.points", minimum=minimum)
    if kind == "region" and len(pts) < 3:
        raise ScientificMarkupError("region annotation requires at least 3 points")
    if kind in {"threshold-x", "threshold-y"} and len(pts) != 1:
        raise ScientificMarkupError("threshold annotation requires one anchor point")
    out = {
        "schema": ANNOTATION_SCHEMA,
        "version": VERSION,
        "id": _identifier(payload.get("id"), "annotation"),
        "type": kind,
        **context,
        "points": pts,
        "text": str(payload.get("text") or "")[:2_000],
        "style": deepcopy(payload.get("style") or {}),
        "provenance": deepcopy(payload.get("provenance") or {}),
        "scientificRole": "annotation",
        "isObservation": False,
        "isDerivedScientificDatum": False,
        "boundaries": {
            "automaticObservationCreation": False,
            "automaticScientificInterpretation": False,
            "automaticGeometrySnapping": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def _euclidean(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def compute_measurement(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificMarkupError("measurement must be an object")
    kind = str(payload.get("type") or payload.get("kind") or "distance").strip().lower()
    if kind not in {"coordinate", "distance", "polyline-length", "angle", "area"}:
        raise ScientificMarkupError("unsupported measurement type")
    context = _coordinate_context(payload)
    minimum = {"coordinate": 1, "distance": 2, "polyline-length": 2, "angle": 3, "area": 3}[kind]
    pts = _points(payload.get("points"), "measurement.points", minimum=minimum)
    if kind in {"distance", "angle"} and len(pts) != minimum:
        raise ScientificMarkupError(f"{kind} measurement requires exactly {minimum} points")
    if context["coordinateSpace"] == "geographic" and kind in {"distance", "polyline-length", "area"}:
        raise ScientificMarkupError("geographic distance/area requires governed geodesy; v0.81 does not approximate geodesic measurement")
    dims = len(pts[0])
    value: Any
    output_units = context["units"]
    method: str
    if kind == "coordinate":
        value = pts[0]
        method = "declared-coordinate-readout"
    elif kind == "distance":
        value = _euclidean(pts[0], pts[1])
        method = "euclidean-coordinate-space"
    elif kind == "polyline-length":
        value = sum(_euclidean(a, b) for a, b in zip(pts, pts[1:]))
        method = "euclidean-polyline-coordinate-space"
    elif kind == "angle":
        a, vertex, b = pts
        u = [x - y for x, y in zip(a, vertex)]
        v = [x - y for x, y in zip(b, vertex)]
        nu = math.sqrt(sum(x*x for x in u)); nv = math.sqrt(sum(x*x for x in v))
        if nu == 0 or nv == 0:
            raise ScientificMarkupError("angle measurement requires non-zero rays")
        cosine = max(-1.0, min(1.0, sum(x*y for x, y in zip(u, v)) / (nu * nv)))
        value = math.degrees(math.acos(cosine))
        output_units = "degrees"
        method = "vector-angle"
    else:
        if dims != 2:
            raise ScientificMarkupError("area measurement requires 2D coordinates")
        ring = pts if pts[0] == pts[-1] else pts + [pts[0]]
        value = abs(sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(ring, ring[1:]))) / 2.0
        output_units = f"{context['units']}^2" if context["units"] != "unitless" else "unitless^2"
        method = "shoelace-coordinate-space"
    out = {
        "schema": MEASUREMENT_SCHEMA,
        "version": VERSION,
        "id": _identifier(payload.get("id"), "measurement"),
        "type": kind,
        **context,
        "points": pts,
        "value": value,
        "outputUnits": output_units,
        "method": method,
        "precision": max(0, min(15, int(payload.get("precision", 6)))),
        "provenance": deepcopy(payload.get("provenance") or {}),
        "scientificRole": "measurement",
        "isObservation": False,
        "derivedFromExplicitMarkupCoordinates": True,
        "boundaries": {
            "automaticUnitConversion": False,
            "automaticGeodesicMeasurement": False,
            "automaticUncertaintyInference": False,
            "automaticGeometrySnapping": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def normalize_markup_layer(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificMarkupError("markup layer must be an object")
    raw_annotations = payload.get("annotations") or []
    raw_measurements = payload.get("measurements") or []
    if not isinstance(raw_annotations, list) or not isinstance(raw_measurements, list):
        raise ScientificMarkupError("annotations and measurements must be arrays")
    if len(raw_annotations) > MAX_ANNOTATIONS or len(raw_measurements) > MAX_MEASUREMENTS:
        raise ScientificMarkupError("markup layer exceeds annotation/measurement limits", 413)
    annotations = [normalize_annotation(x) for x in raw_annotations]
    measurements = [compute_measurement(x) for x in raw_measurements]
    out = {
        "schema": LAYER_SCHEMA,
        "version": VERSION,
        "id": _identifier(payload.get("id"), "markup-layer"),
        "title": str(payload.get("title") or "Scientific markup")[:240],
        "visible": bool(payload.get("visible", True)),
        "annotations": annotations,
        "measurements": measurements,
        "annotationCount": len(annotations),
        "measurementCount": len(measurements),
        "provenance": deepcopy(payload.get("provenance") or {}),
        "scientificRole": "markup-overlay",
        "boundaries": {
            "annotationIsObservation": False,
            "automaticObservationCreation": False,
            "automaticScientificInterpretation": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def attach_markup(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificMarkupError("figure markup request must be an object")
    base = payload.get("baseFigure") or payload.get("figure")
    if not isinstance(base, dict) or not base:
        raise ScientificMarkupError("baseFigure is required")
    raw_layers = payload.get("markupLayers") or payload.get("layers") or []
    if not isinstance(raw_layers, list) or not raw_layers:
        raise ScientificMarkupError("at least one markup layer is required")
    if len(raw_layers) > MAX_MARKUP_LAYERS:
        raise ScientificMarkupError(f"markup figure exceeds {MAX_MARKUP_LAYERS} layers", 413)
    layers = [normalize_markup_layer(x) for x in raw_layers]
    base_copy = deepcopy(base)
    base_fp = str(base.get("fingerprint") or _hash(base))
    out = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "rendererOverlay": RENDERER_OVERLAY,
        "id": _identifier(payload.get("id"), "marked-scientific-figure"),
        "title": str(payload.get("title") or base.get("title") or "Marked scientific figure")[:240],
        "baseFigure": base_copy,
        "baseFigureFingerprint": base_fp,
        "baseRenderer": base.get("renderer"),
        "markupLayers": layers,
        "markupLayerCount": len(layers),
        "provenance": deepcopy(payload.get("provenance") or {}),
        "boundaries": {
            "baseFigureMutation": False,
            "annotationIsObservation": False,
            "automaticObservationCreation": False,
            "automaticScientificInterpretation": False,
            "automaticUnitConversion": False,
            "automaticGeodesicMeasurement": False,
        },
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return {"ok": True, "figure": out}


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    figure = attach_markup(payload.get("figure") or payload)["figure"]
    workspace = {
        "schema": WORKSPACE_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "rendererRegistry": ["svg2d", "canvas3d", "canvas4d", "canvas-spatial"],
        "overlayRegistry": [RENDERER_OVERLAY],
        "figure": figure,
        "provenance": deepcopy(payload.get("provenance") or {}),
        "compatibility": {
            "v0800Spatial": True,
            "v0790LinkedViews": True,
            "v0780TimeParameter": True,
            "v0770Scene3d": True,
            "v0760AdaptiveRendering": True,
            "v0750DataBinding": True,
        },
    }
    workspace["fingerprint"] = _hash({k: v for k, v in workspace.items() if k != "fingerprint"})
    return {"ok": True, "workspace": workspace}


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "annotation-measurement-scientific-markup-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "rendererOverlay": RENDERER_OVERLAY,
        "scientificAnnotation": True,
        "scientificMeasurement": True,
        "scientificMarkupLayers": True,
        "pointAnnotation": True,
        "lineAnnotation": True,
        "regionAnnotation": True,
        "thresholdAnnotation": True,
        "coordinateMeasurement": True,
        "distanceMeasurement": True,
        "polylineLengthMeasurement": True,
        "angleMeasurement": True,
        "areaMeasurement": True,
        "declaredUnits": True,
        "annotationProvenance": True,
        "baseFigurePreservation": True,
        "v0800SpatialCompatibility": True,
        "v0790LinkedViewsCompatibility": True,
        "v0780TimeParameterCompatibility": True,
        "v0770SceneCompatibility": True,
        "v0760AdaptiveCompatibility": True,
        "v0750DataBindingCompatibility": True,
        "annotationIsObservation": False,
        "automaticObservationCreation": False,
        "automaticScientificInterpretation": False,
        "automaticUnitConversion": False,
        "automaticGeodesicMeasurement": False,
        "automaticGeometrySnapping": False,
        "automaticUncertaintyInference": False,
        "arbitraryCode": False,
        "limits": {
            "annotationsPerLayer": MAX_ANNOTATIONS,
            "measurementsPerLayer": MAX_MEASUREMENTS,
            "markupLayers": MAX_MARKUP_LAYERS,
            "pointsPerMark": MAX_POINTS_PER_MARK,
        },
    }


def policies() -> dict[str, Any]:
    return health()
