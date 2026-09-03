from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

from .graph_studio import GraphStudioError, normalize_graph as normalize_legacy_graph

VERSION = "0.73.0"
ENGINE_VERSION = "2.0.0"
SPEC_SCHEMA = "sc-lab-scientific-visualization/0.73.0"
FIGURE_SCHEMA = "sc-lab-scientific-figure/0.73.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.73.0"
LEGACY_GRAPH_CONTRACT = "sc-lab-scientific-graph/0.46.0"
LEGACY_KINDS = {"line", "scatter", "line-scatter", "histogram", "horizontal-bars", "heatmap"}
SURFACE_KINDS = {"surface-4d"}
GRAPH_KINDS = LEGACY_KINDS | SURFACE_KINDS
RENDERERS = {
    "svg2d": {"kinds": sorted(LEGACY_KINDS), "exports": ["svg", "png", "csv", "json"]},
    "canvas4d": {"kinds": sorted(SURFACE_KINDS), "exports": ["png", "json"]},
}
ASPECT_RATIOS = {"16:9", "3:2", "4:3", "1:1"}
PROFILES = {"generic", "biodiversity"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")


class VisualizationEngineError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, name: str, max_len: int = 500, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise VisualizationEngineError(f"{name} is required.")
    if len(text) > max_len:
        raise VisualizationEngineError(f"{name} exceeds {max_len} characters.")
    return text


def _finite(value: Any, name: str, *, minimum: float | None = None, maximum: float | None = None) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise VisualizationEngineError(f"{name} must be numeric.") from exc
    if not math.isfinite(number):
        raise VisualizationEngineError(f"{name} must be finite.")
    if minimum is not None and number < minimum:
        raise VisualizationEngineError(f"{name} must be at least {minimum}.")
    if maximum is not None and number > maximum:
        raise VisualizationEngineError(f"{name} must be at most {maximum}.")
    return number


def _publication(src: dict[str, Any], exports: list[str]) -> dict[str, Any]:
    pub = src.get("publication") if isinstance(src.get("publication"), dict) else {}
    aspect = _text(pub.get("aspectRatio") or "16:9", "publication aspect ratio", 20, True)
    if aspect not in ASPECT_RATIOS:
        raise VisualizationEngineError("Unsupported publication aspect ratio.")
    return {
        "aspectRatio": aspect,
        "caption": _text(pub.get("caption"), "caption", 1500),
        "source": _text(pub.get("source"), "source", 800),
        "method": _text(pub.get("method"), "method", 1200),
        "notes": _text(pub.get("notes"), "notes", 1200),
        "showGrid": bool(pub.get("showGrid", True)),
        "showLegend": bool(pub.get("showLegend", True)),
        "background": _text(pub.get("background") or "white", "background", 40, True),
        "exports": list(exports),
    }


def _dimensions(values: Any, *, required_count: int | None = None) -> list[dict[str, str]]:
    if values in (None, ""):
        values = []
    if not isinstance(values, list):
        raise VisualizationEngineError("dimensions must be an array.")
    if len(values) > 4:
        raise VisualizationEngineError("At most four visualization dimensions are supported in v0.73.0.")
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, row in enumerate(values):
        if not isinstance(row, dict):
            raise VisualizationEngineError(f"dimensions[{index}] must be an object.")
        key = _text(row.get("key"), f"dimensions[{index}].key", 80, True)
        if key in seen:
            raise VisualizationEngineError("Visualization dimension keys must be unique.")
        seen.add(key)
        out.append({
            "key": key,
            "label": _text(row.get("label") or key, f"dimensions[{index}].label", 120, True),
            "role": _text(row.get("role") or ("w" if index == 3 else ("xyz"[index] if index < 3 else "dimension")), f"dimensions[{index}].role", 40, True),
            "unit": _text(row.get("unit"), f"dimensions[{index}].unit", 80),
        })
    if required_count is not None and len(out) != required_count:
        raise VisualizationEngineError(f"This visualization requires exactly {required_count} dimensions.")
    return out


def _normalize_legacy(src: dict[str, Any]) -> dict[str, Any]:
    try:
        legacy = normalize_legacy_graph(src)
    except GraphStudioError as exc:
        raise VisualizationEngineError(str(exc)) from exc
    kind = legacy["kind"]
    exports = RENDERERS["svg2d"]["exports"]
    legacy["legacySchema"] = legacy.get("schema") or LEGACY_GRAPH_CONTRACT
    legacy["legacyVersion"] = legacy.get("version") or "0.46.0"
    legacy["schema"] = SPEC_SCHEMA
    legacy["version"] = VERSION
    legacy["recordType"] = "scientific-visualization-spec"
    legacy["renderer"] = "svg2d"
    legacy["rendererVersion"] = "0.44.0"
    legacy["visualizationEngine"] = ENGINE_VERSION
    legacy["dimensions"] = _dimensions(src.get("dimensions") or [
        {"key": "x", "label": legacy.get("xLabel") or "x", "role": "x", "unit": ""},
        {"key": "y", "label": legacy.get("yLabel") or "y", "role": "y", "unit": ""},
    ])
    legacy["visualEncoding"] = deepcopy(src.get("visualEncoding") or {"x": "x", "y": "y"})
    legacy["publication"] = _publication(legacy, exports)
    legacy["exports"] = list(exports)
    legacy["rendering"] = {
        "renderer": "svg2d",
        "adapter": "scientific-visualization-engine-v0440",
        "dataMode": "inline-declarative",
        "interactive": True,
    }
    return legacy


def _normalize_surface_4d(src: dict[str, Any]) -> dict[str, Any]:
    profile = _text(src.get("profile") or (src.get("surface") or {}).get("profile") or "generic", "surface profile", 40, True)
    if profile not in PROFILES:
        raise VisualizationEngineError(f"Unsupported surface profile: {profile}.")
    default_dimensions = (
        [
            {"key": "habitat_quality", "label": "Habitat quality", "role": "x", "unit": "relative"},
            {"key": "climate_stress", "label": "Climate stress", "role": "y", "unit": "relative"},
            {"key": "biodiversity_response", "label": "Biodiversity response", "role": "z", "unit": "relative"},
            {"key": "time", "label": "Time / disturbance progression", "role": "w", "unit": "relative"},
        ] if profile == "biodiversity" else [
            {"key": "x", "label": "Descriptor 1", "role": "x", "unit": ""},
            {"key": "y", "label": "Descriptor 2", "role": "y", "unit": ""},
            {"key": "z", "label": "Response", "role": "z", "unit": ""},
            {"key": "w", "label": "Fourth dimension", "role": "w", "unit": ""},
        ]
    )
    dimensions = _dimensions(src.get("dimensions") or default_dimensions, required_count=4)
    surface = src.get("surface") if isinstance(src.get("surface"), dict) else {}
    rotation = surface.get("rotation") if isinstance(surface.get("rotation"), dict) else {}
    layers = surface.get("layers") if isinstance(surface.get("layers"), dict) else {}
    profile_range = (0.0, 1.0) if profile == "biodiversity" else (-1.0, 1.0)
    exports = RENDERERS["canvas4d"]["exports"]
    data_boundary_default = (
        "Deterministic synthetic biodiversity illustration only; not observations, estimates, forecasts, or conservation conclusions."
        if profile == "biodiversity" else
        "Deterministic synthetic visualization profile only; not measured or model-derived project data."
    )
    out = {
        "schema": SPEC_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-visualization-spec",
        "kind": "surface-4d",
        "title": _text(src.get("title") or "Four-dimensional scientific response surface", "title", 180, True),
        "subtitle": _text(src.get("subtitle"), "subtitle", 240),
        "renderer": "canvas4d",
        "rendererVersion": "0.71.0",
        "visualizationEngine": ENGINE_VERSION,
        "profile": profile,
        "dimensions": dimensions,
        "visualEncoding": deepcopy(src.get("visualEncoding") or {
            "x": dimensions[0]["key"], "y": dimensions[1]["key"], "z": dimensions[2]["key"], "w": dimensions[3]["key"]
        }),
        "surface": {
            "profile": profile,
            "slice": _finite(surface.get("slice", 0.60 if profile == "biodiversity" else 0.37), "surface.slice", minimum=profile_range[0], maximum=profile_range[1]),
            "range": list(profile_range),
            "rotation": {
                "xw": _finite(rotation.get("xw", 0.34), "surface.rotation.xw", minimum=-1.4, maximum=1.4),
                "yw": _finite(rotation.get("yw", -0.22), "surface.rotation.yw", minimum=-1.4, maximum=1.4),
                "zw": _finite(rotation.get("zw", 0.12), "surface.rotation.zw", minimum=-1.4, maximum=1.4),
            },
            "layers": {
                "surface": True,
                "vector": bool(layers.get("vector", True)),
                "uncertainty": bool(layers.get("uncertainty", True)),
                "contours": bool(layers.get("contours", True)),
                "projection4d": bool(layers.get("projection4d", True)),
            },
            "animation": {"enabled": bool((surface.get("animation") or {}).get("enabled", False)) if isinstance(surface.get("animation"), dict) else False},
        },
        "publication": _publication(src, exports),
        "interaction": {
            "tooltip": True,
            "hyperslice": True,
            "rotation4d": True,
            "animation": True,
            "layerToggle": True,
        },
        "exports": list(exports),
        "rendering": {
            "renderer": "canvas4d",
            "adapter": "advanced-visualization-front-door-v0710",
            "dataMode": "synthetic-profile" if profile in PROFILES else "unknown",
            "interactive": True,
        },
        "dataBoundary": _text(src.get("dataBoundary") or data_boundary_default, "dataBoundary", 1200, True),
    }
    return out


def normalize_spec(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise VisualizationEngineError("Visualization specification must be an object.")
    src = deepcopy(payload)
    kind = _text(src.get("kind") or src.get("type"), "visualization kind", 40, True)
    if kind not in GRAPH_KINDS:
        raise VisualizationEngineError(f"Unsupported visualization kind: {kind}.")
    if kind in LEGACY_KINDS:
        return _normalize_legacy(src)
    return _normalize_surface_4d(src)


def normalize_figure(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise VisualizationEngineError("Figure definition must be an object.")
    src = deepcopy(payload)
    spec = normalize_spec(src.get("graph") or src.get("spec") or src.get("visualization") or {})
    raw_id = _text(src.get("id") or f"figure-{_digest(src)[:16]}", "figure id", 160, True)
    if not ID_RE.fullmatch(raw_id):
        raise VisualizationEngineError("Figure id contains unsupported characters.")
    provenance = src.get("provenance") if isinstance(src.get("provenance"), dict) else {}
    figure = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-figure-v0730",
        "id": raw_id,
        "title": _text(src.get("title") or spec["title"], "figure title", 180, True),
        "status": _text(src.get("status") or "draft", "status", 40, True),
        "graph": spec,
        "sourceContext": _text(src.get("sourceContext") or "graph-studio", "sourceContext", 120, True),
        "tags": [_text(v, "tag", 80, True) for v in (src.get("tags") or [])][:30],
        "provenance": {
            "projectId": _text(provenance.get("projectId"), "projectId", 160),
            "sourceRecordId": _text(provenance.get("sourceRecordId"), "sourceRecordId", 160),
            "datasetId": _text(provenance.get("datasetId"), "datasetId", 160),
            "modelRunId": _text(provenance.get("modelRunId"), "modelRunId", 160),
            "createdAt": _text(provenance.get("createdAt") or _now(), "createdAt", 80, True),
            "updatedAt": _now(),
            "visualizationEngine": ENGINE_VERSION,
            "renderer": spec["renderer"],
        },
    }
    figure["fingerprint"] = _digest({k: v for k, v in figure.items() if k != "fingerprint"})
    return figure


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise VisualizationEngineError("Figure workspace payload must be an object.")
    figures = [normalize_figure(row) for row in (payload.get("figures") or [])]
    return {
        "ok": True,
        "workspace": {
            "schema": WORKSPACE_SCHEMA,
            "version": VERSION,
            "projectId": _text(payload.get("projectId"), "projectId", 160),
            "figureCount": len(figures),
            "figures": figures,
            "createdAt": _now(),
        },
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "specSchema": SPEC_SCHEMA,
        "figureSchema": FIGURE_SCHEMA,
        "workspaceSchema": WORKSPACE_SCHEMA,
        "supportedKinds": sorted(GRAPH_KINDS),
        "renderers": deepcopy(RENDERERS),
        "compatibility": {"legacyGraphContract": LEGACY_GRAPH_CONTRACT, "legacySvgRenderer": "0.44.0", "advancedCanvasRenderer": "0.71.0"},
        "boundaries": {
            "arbitraryCode": False,
            "remoteImageFetch": False,
            "surface4dProjectDataBinding": False,
            "surface4dSyntheticProfilesOnly": True,
            "publicationMetadata": True,
            "rendererSelectionExplicit": True,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-visualization-engine-v2-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "rendererCount": len(RENDERERS),
        "renderers": sorted(RENDERERS),
        "supportedKinds": sorted(GRAPH_KINDS),
        "legacy2dCompatibility": True,
        "surface4dFirstClassFigure": True,
        "saved4dState": True,
        "projectDataSurfaceBinding": False,
        "arbitraryCode": False,
    }
