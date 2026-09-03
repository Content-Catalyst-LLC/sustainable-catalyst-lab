from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json, math, re
from typing import Any

from .visualization_engine_v0730 import (
    VisualizationEngineError as V0730Error,
    normalize_spec as normalize_v0730_spec,
)

VERSION = "0.74.0"
ENGINE_VERSION = "2.1.0"
SPEC_SCHEMA = "sc-lab-scientific-visualization/0.74.0"
FIGURE_SCHEMA = "sc-lab-scientific-figure/0.74.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.74.0"
PLOT_GRAMMAR = "sc-lab-advanced-2d-plot-grammar/0.74.0"
LEGACY_GRAPH_CONTRACT = "sc-lab-scientific-graph/0.46.0"

BASE_2D_KINDS = {"line", "scatter", "line-scatter", "histogram", "horizontal-bars", "heatmap"}
ADVANCED_2D_KINDS = {
    "step", "area", "stacked-area", "bar", "grouped-bar", "stacked-bar",
    "density", "box", "violin", "error-bar", "confidence-band", "contour",
    "hexbin", "ecdf", "qq", "residual", "waterfall", "pareto",
}
SURFACE_KINDS = {"surface-4d"}
GRAPH_KINDS = BASE_2D_KINDS | ADVANCED_2D_KINDS | SURFACE_KINDS
AXIS_SCALES = {"linear", "log", "symlog", "probability", "datetime", "categorical"}
TICK_FORMATS = {"auto", "scientific", "si", "plain", "percent"}
ASPECT_RATIOS = {"16:9", "3:2", "4:3", "1:1"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
RENDERERS = {
    "svg2d": {"version": VERSION, "kinds": sorted(BASE_2D_KINDS | ADVANCED_2D_KINDS), "exports": ["svg", "png", "csv", "json"]},
    "canvas4d": {"version": "0.71.0", "kinds": ["surface-4d"], "exports": ["png", "json"]},
}

class VisualizationGrammarError(ValueError):
    pass

def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode()).hexdigest()

def _text(value: Any, name: str, max_len: int = 500, required: bool = False) -> str:
    s = str(value or "").strip()
    if required and not s:
        raise VisualizationGrammarError(f"{name} is required.")
    if len(s) > max_len:
        raise VisualizationGrammarError(f"{name} exceeds {max_len} characters.")
    return s

def _finite_or_value(value: Any, name: str) -> float | str:
    if isinstance(value, bool):
        raise VisualizationGrammarError(f"{name} must be numeric or a category/date value.")
    try:
        n = float(value)
        if math.isfinite(n):
            return n
    except (TypeError, ValueError):
        pass
    s = _text(value, name, 160, True)
    return s

def _axis(value: Any, label: str) -> dict[str, Any]:
    src = value if isinstance(value, dict) else {}
    scale = _text(src.get("scale") or "linear", f"{label}.scale", 20, True)
    if scale not in AXIS_SCALES:
        raise VisualizationGrammarError(f"Unsupported {label} scale: {scale}.")
    tick = _text(src.get("tickFormat") or "auto", f"{label}.tickFormat", 20, True)
    if tick not in TICK_FORMATS:
        raise VisualizationGrammarError(f"Unsupported {label} tick format: {tick}.")
    domain = src.get("domain")
    if domain is not None:
        if not isinstance(domain, list) or len(domain) != 2:
            raise VisualizationGrammarError(f"{label}.domain must contain exactly two values.")
        domain = [_finite_or_value(domain[0], f"{label}.domain[0]"), _finite_or_value(domain[1], f"{label}.domain[1]")]
    return {
        "scale": scale,
        "label": _text(src.get("label") or label.upper(), f"{label}.label", 120, True),
        "unit": _text(src.get("unit"), f"{label}.unit", 80),
        "tickFormat": tick,
        "inverted": bool(src.get("inverted", False)),
        "domain": domain,
        "categories": [_text(v, f"{label}.categories item", 120, True) for v in (src.get("categories") or [])][:500],
        "linthresh": float(src.get("linthresh", 1.0)) if scale == "symlog" else None,
    }

def _publication(src: dict[str, Any], exports: list[str]) -> dict[str, Any]:
    pub = src.get("publication") if isinstance(src.get("publication"), dict) else {}
    aspect = _text(pub.get("aspectRatio") or "16:9", "publication.aspectRatio", 20, True)
    if aspect not in ASPECT_RATIOS:
        raise VisualizationGrammarError("Unsupported publication aspect ratio.")
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

def _series(src: Any) -> list[dict[str, Any]]:
    if src in (None, ""):
        return []
    if not isinstance(src, list):
        raise VisualizationGrammarError("series must be an array.")
    out=[]
    for si,row in enumerate(src[:64]):
        if not isinstance(row, dict):
            raise VisualizationGrammarError(f"series[{si}] must be an object.")
        pts=[]
        for pi,p in enumerate((row.get("points") or [])[:100000]):
            if not isinstance(p,dict):
                raise VisualizationGrammarError(f"series[{si}].points[{pi}] must be an object.")
            point={}
            for k in ("x","y","yLow","yHigh","xLow","xHigh","size","weight"):
                if k in p and p[k] is not None:
                    point[k]=_finite_or_value(p[k],f"series[{si}].points[{pi}].{k}")
            if "x" not in point or "y" not in point:
                raise VisualizationGrammarError(f"series[{si}].points[{pi}] requires x and y.")
            if p.get("label") is not None: point["label"]=_text(p.get("label"),"point label",160)
            pts.append(point)
        out.append({
            "id": _text(row.get("id") or f"series-{si+1}", "series id", 80, True),
            "label": _text(row.get("label") or f"Series {si+1}", "series label", 120, True),
            "mode": _text(row.get("mode") or "auto", "series mode", 30, True),
            "stack": _text(row.get("stack"), "series stack", 80),
            "points": pts,
        })
    return out

def _records(values: Any, name: str, max_items: int = 100000) -> list[dict[str, Any]]:
    if values in (None, ""):
        return []
    if not isinstance(values, list):
        raise VisualizationGrammarError(f"{name} must be an array.")
    out=[]
    for i,row in enumerate(values[:max_items]):
        if not isinstance(row,dict):
            raise VisualizationGrammarError(f"{name}[{i}] must be an object.")
        out.append(deepcopy(row))
    return out

def _normalize_2d(src: dict[str, Any], kind: str) -> dict[str, Any]:
    exports=RENDERERS["svg2d"]["exports"]
    axes = src.get("axes") if isinstance(src.get("axes"),dict) else {}
    xaxis=_axis(axes.get("x") or {"label":src.get("xLabel") or "X"},"x")
    yaxis=_axis(axes.get("y") or {"label":src.get("yLabel") or "Y"},"y")
    out={
        "schema":SPEC_SCHEMA,"version":VERSION,"recordType":"scientific-visualization-spec",
        "grammar":PLOT_GRAMMAR,"kind":kind,"renderer":"svg2d","rendererVersion":VERSION,
        "visualizationEngine":ENGINE_VERSION,
        "title":_text(src.get("title") or "Scientific figure","title",180,True),
        "subtitle":_text(src.get("subtitle"),"subtitle",240),
        "xLabel":xaxis["label"],"yLabel":yaxis["label"],"axes":{"x":xaxis,"y":yaxis},
        "series":_series(src.get("series")),
        "bars":_records(src.get("bars"),"bars",50000),
        "boxes":_records(src.get("boxes"),"boxes",5000),
        "violins":_records(src.get("violins"),"violins",5000),
        "cells":_records(src.get("cells"),"cells",100000),
        "contours":_records(src.get("contours"),"contours",50000),
        "bins":_records(src.get("bins"),"bins",100000),
        "annotations":_records(src.get("annotations"),"annotations",500),
        "xValues":deepcopy(src.get("xValues") or []),"yValues":deepcopy(src.get("yValues") or []),
        "table":deepcopy(src.get("table") or {}),
        "publication":_publication(src,exports),
        "interaction":deepcopy(src.get("interaction") or {"tooltip":True,"focusablePoints":True,"zoom":True,"pan":True,"crosshair":True,"seriesToggle":True}),
        "exports":list(exports),
        "rendering":{"renderer":"svg2d","adapter":"scientific-visualization-engine-v0740","coordinateSystem":"cartesian-2d","interactive":True},
        "warnings":[],
    }
    if (xaxis["scale"] in {"log","probability"} or yaxis["scale"] in {"log","probability"}) and kind in {"stacked-bar","stacked-area"}:
        out["warnings"].append("Stacked marks on nonlinear axes can be difficult to interpret; verify the scientific meaning before publication.")
    if xaxis["scale"]=="categorical" and not xaxis["categories"]:
        out["warnings"].append("Categorical x-axis categories will be inferred from plotted values in encounter order.")
    if kind in {"qq","residual"}:
        out["publication"]["showGrid"] = bool(out["publication"].get("showGrid",True))
    return out

def normalize_spec(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict):
        raise VisualizationGrammarError("Visualization specification must be an object.")
    src=deepcopy(payload)
    kind=_text(src.get("kind") or src.get("type"),"visualization kind",40,True)
    if kind not in GRAPH_KINDS:
        raise VisualizationGrammarError(f"Unsupported visualization kind: {kind}.")
    if kind=="surface-4d":
        try: old=normalize_v0730_spec(src)
        except V0730Error as exc: raise VisualizationGrammarError(str(exc)) from exc
        old.update({"schema":SPEC_SCHEMA,"version":VERSION,"visualizationEngine":ENGINE_VERSION})
        old["compatibility"]={"sourceSchema":"sc-lab-scientific-visualization/0.73.0","renderer":"canvas4d"}
        return old
    return _normalize_2d(src,kind)

def normalize_figure(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise VisualizationGrammarError("Figure definition must be an object.")
    src=deepcopy(payload); spec=normalize_spec(src.get("graph") or src.get("spec") or src.get("visualization") or {})
    raw_id=_text(src.get("id") or f"figure-{_digest(src)[:16]}","figure id",160,True)
    if not ID_RE.fullmatch(raw_id): raise VisualizationGrammarError("Figure id contains unsupported characters.")
    p=src.get("provenance") if isinstance(src.get("provenance"),dict) else {}
    fig={"schema":FIGURE_SCHEMA,"version":VERSION,"recordType":"scientific-figure-v0740","id":raw_id,"title":_text(src.get("title") or spec["title"],"figure title",180,True),"status":_text(src.get("status") or "draft","status",40,True),"graph":spec,"sourceContext":_text(src.get("sourceContext") or "graph-studio","sourceContext",120,True),"tags":[_text(v,"tag",80,True) for v in (src.get("tags") or [])][:30],"provenance":{"projectId":_text(p.get("projectId"),"projectId",160),"sourceRecordId":_text(p.get("sourceRecordId"),"sourceRecordId",160),"datasetId":_text(p.get("datasetId"),"datasetId",160),"modelRunId":_text(p.get("modelRunId"),"modelRunId",160),"createdAt":_text(p.get("createdAt") or _now(),"createdAt",80,True),"updatedAt":_now(),"visualizationEngine":ENGINE_VERSION,"renderer":spec["renderer"]}}
    fig["fingerprint"]=_digest({k:v for k,v in fig.items() if k!="fingerprint"}); return fig

def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise VisualizationGrammarError("Figure workspace payload must be an object.")
    figs=[normalize_figure(v) for v in (payload.get("figures") or [])]
    return {"ok":True,"workspace":{"schema":WORKSPACE_SCHEMA,"version":VERSION,"projectId":_text(payload.get("projectId"),"projectId",160),"figureCount":len(figs),"figures":figs,"createdAt":_now()}}

def policies() -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"engineVersion":ENGINE_VERSION,"plotGrammar":PLOT_GRAMMAR,"specSchema":SPEC_SCHEMA,"figureSchema":FIGURE_SCHEMA,"workspaceSchema":WORKSPACE_SCHEMA,"supportedKinds":sorted(GRAPH_KINDS),"axisScales":sorted(AXIS_SCALES),"tickFormats":sorted(TICK_FORMATS),"renderers":deepcopy(RENDERERS),"compatibility":{"legacyGraphContract":LEGACY_GRAPH_CONTRACT,"legacySvgRenderer":"0.44.0","visualizationEngineV0730":"0.73.0","canvas4d":"0.71.0"},"boundaries":{"arbitraryCode":False,"remoteImageFetch":False,"polarRadar":False,"dualAxis":False,"surface4dProjectDataBinding":False,"rawDataTransformationPipeline":"v0.75.0","publicationMetadata":True,"unitAwareAxisMetadata":True}}

def health() -> dict[str, Any]:
    return {"ok":True,"status":"advanced-2d-plot-grammar-ready","version":VERSION,"engineVersion":ENGINE_VERSION,"rendererCount":len(RENDERERS),"renderers":sorted(RENDERERS),"advanced2dKinds":sorted(ADVANCED_2D_KINDS),"supportedKinds":sorted(GRAPH_KINDS),"axisScales":sorted(AXIS_SCALES),"tickFormats":sorted(TICK_FORMATS),"legacy2dCompatibility":True,"canvas4dCompatibility":True,"polarRadarDeferred":True,"dualAxisDeferred":True,"projectDataSurfaceBinding":False,"arbitraryCode":False}
