from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

VERSION = "0.47.0"
FIGURE_SCHEMA = "sc-lab-scientific-figure/0.47.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.47.0"
GRAPH_CONTRACT = "sc-lab-scientific-graph/0.46.0"
GRAPH_ENGINE = "0.44.0"
GRAPH_TYPES = {"line", "scatter", "line-scatter", "histogram", "horizontal-bars", "heatmap"}
ASPECT_RATIOS = {"16:9", "3:2", "4:3", "1:1"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")


class GraphStudioError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, name: str, max_len: int = 500, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise GraphStudioError(f"{name} is required.")
    if len(text) > max_len:
        raise GraphStudioError(f"{name} exceeds {max_len} characters.")
    return text


def _finite(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise GraphStudioError(f"{name} must be numeric.") from exc
    if not math.isfinite(number):
        raise GraphStudioError(f"{name} must be finite.")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "figureSchema": FIGURE_SCHEMA,
        "workspaceSchema": WORKSPACE_SCHEMA,
        "graphContract": GRAPH_CONTRACT,
        "sharedVisualizationEngine": GRAPH_ENGINE,
        "graphTypes": sorted(GRAPH_TYPES),
        "aspectRatios": sorted(ASPECT_RATIOS),
        "exports": ["svg", "png", "csv", "json"],
        "handoffs": ["model-studio", "numerical-visualization", "report-studio", "notebook"],
        "boundaries": {
            "arbitraryCode": False,
            "remoteImageFetch": False,
            "browserLocalProjectFigures": True,
            "sourceAndMethodMetadata": True,
            "scientificGraphContractRequired": True,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "graph-studio-ready",
        "version": VERSION,
        "figureWorkspace": True,
        "largeScientificCanvas": True,
        "figureLibrary": True,
        "interactiveInspection": True,
        "publicationMetadata": True,
        "publicationExports": ["svg", "png", "csv", "json"],
        "sharedVisualizationEngine": GRAPH_ENGINE,
        "graphContract": GRAPH_CONTRACT,
        "arbitraryCode": False,
    }


def normalize_graph(graph: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(graph, dict):
        raise GraphStudioError("graph must be an object.")
    src = deepcopy(graph)
    kind = _text(src.get("kind") or src.get("type"), "graph kind", 40, True)
    if kind not in GRAPH_TYPES:
        raise GraphStudioError(f"Unsupported graph kind: {kind}.")

    series = []
    for si, row in enumerate(src.get("series") or []):
        if not isinstance(row, dict):
            raise GraphStudioError("series must contain objects.")
        points = []
        for pi, point in enumerate(row.get("points") or []):
            if not isinstance(point, dict):
                raise GraphStudioError("series points must be objects.")
            points.append({"x": _finite(point.get("x"), f"series[{si}].points[{pi}].x"), "y": _finite(point.get("y"), f"series[{si}].points[{pi}].y")})
        series.append({
            "label": _text(row.get("label") or f"Series {si + 1}", "series label", 120, True),
            "mode": _text(row.get("mode") or ("points" if kind == "scatter" else "line"), "series mode", 30, True),
            "points": points,
        })

    bars = []
    for bi, row in enumerate(src.get("bars") or []):
        if not isinstance(row, dict):
            raise GraphStudioError("bars must contain objects.")
        bars.append({"label": _text(row.get("label") or str(bi + 1), "bar label", 120, True), "value": _finite(row.get("value"), f"bars[{bi}].value")})

    cells = []
    for ci, row in enumerate(src.get("cells") or []):
        if not isinstance(row, dict):
            raise GraphStudioError("cells must contain objects.")
        cells.append({
            "xIndex": int(_finite(row.get("xIndex"), f"cells[{ci}].xIndex")),
            "yIndex": int(_finite(row.get("yIndex"), f"cells[{ci}].yIndex")),
            "x": _finite(row.get("x"), f"cells[{ci}].x"),
            "y": _finite(row.get("y"), f"cells[{ci}].y"),
            "z": _finite(row.get("z"), f"cells[{ci}].z"),
        })

    pub = src.get("publication") if isinstance(src.get("publication"), dict) else {}
    aspect = _text(pub.get("aspectRatio") or "16:9", "publication aspect ratio", 20, True)
    if aspect not in ASPECT_RATIOS:
        raise GraphStudioError("Unsupported publication aspect ratio.")

    interaction = src.get("interaction") if isinstance(src.get("interaction"), dict) else {}
    graph_out = {
        **{k: v for k, v in src.items() if k not in {"series", "bars", "cells", "publication", "interaction"}},
        "schema": GRAPH_CONTRACT,
        "version": "0.46.0",
        "kind": kind,
        "title": _text(src.get("title") or "Scientific figure", "graph title", 180, True),
        "subtitle": _text(src.get("subtitle"), "graph subtitle", 240),
        "xLabel": _text(src.get("xLabel") or "x", "x label", 120, True),
        "yLabel": _text(src.get("yLabel") or "y", "y label", 120, True),
        "series": series,
        "bars": bars,
        "cells": cells,
        "xValues": [_finite(v, "xValues item") for v in (src.get("xValues") or [])],
        "yValues": [_finite(v, "yValues item") for v in (src.get("yValues") or [])],
        "publication": {
            "aspectRatio": aspect,
            "caption": _text(pub.get("caption"), "caption", 1500),
            "source": _text(pub.get("source"), "source", 800),
            "method": _text(pub.get("method"), "method", 1200),
            "notes": _text(pub.get("notes"), "notes", 1200),
            "showGrid": bool(pub.get("showGrid", True)),
            "showLegend": bool(pub.get("showLegend", True)),
            "background": "white",
        },
        "interaction": {
            "tooltip": bool(interaction.get("tooltip", True)),
            "focusablePoints": bool(interaction.get("focusablePoints", True)),
            "zoom": bool(interaction.get("zoom", True)),
            "pan": bool(interaction.get("pan", True)),
            "crosshair": bool(interaction.get("crosshair", True)),
            "seriesToggle": bool(interaction.get("seriesToggle", True)),
        },
        "exports": ["svg", "png", "csv", "json"],
    }
    if isinstance(src.get("table"), dict):
        graph_out["table"] = deepcopy(src["table"])
    if isinstance(src.get("domain"), dict):
        graph_out["domain"] = deepcopy(src["domain"])
    if isinstance(src.get("annotations"), list):
        graph_out["annotations"] = deepcopy(src["annotations"][:100])
    return graph_out


def normalize_figure(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GraphStudioError("Figure definition must be an object.")
    src = deepcopy(payload)
    graph = normalize_graph(src.get("graph") or src.get("spec") or {})
    raw_id = _text(src.get("id") or f"figure-{_digest(src)[:16]}", "figure id", 160, True)
    if not ID_RE.fullmatch(raw_id):
        raise GraphStudioError("Figure id contains unsupported characters.")
    provenance = src.get("provenance") if isinstance(src.get("provenance"), dict) else {}
    figure = {
        "schema": FIGURE_SCHEMA,
        "version": VERSION,
        "recordType": "scientific-figure-v0470",
        "id": raw_id,
        "title": _text(src.get("title") or graph["title"], "figure title", 180, True),
        "status": _text(src.get("status") or "draft", "status", 40, True),
        "graph": graph,
        "sourceContext": _text(src.get("sourceContext") or "graph-studio", "sourceContext", 120, True),
        "tags": [_text(v, "tag", 80, True) for v in (src.get("tags") or [])][:30],
        "provenance": {
            "projectId": _text(provenance.get("projectId"), "projectId", 160),
            "sourceRecordId": _text(provenance.get("sourceRecordId"), "sourceRecordId", 160),
            "createdAt": _text(provenance.get("createdAt") or _now(), "createdAt", 80, True),
            "updatedAt": _now(),
        },
    }
    figure["fingerprint"] = _digest({k: v for k, v in figure.items() if k != "fingerprint"})
    return figure


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GraphStudioError("Figure workspace payload must be an object.")
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
