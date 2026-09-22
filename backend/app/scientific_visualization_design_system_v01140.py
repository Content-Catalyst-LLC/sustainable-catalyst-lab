from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

from .visualization_engine_v0740 import normalize_spec as normalize_v0740_spec, VisualizationGrammarError
from .provenance_aware_figures_v0830 import attach_provenance, build_export_manifest
from .gpu_renderer_architecture_v0840 import renderer_registry as gpu_renderer_registry
from .platform_core_v3_visual_scene_v01090 import build_core_visual_binding

VERSION = "0.114.0"
ENGINE_VERSION = "3.0.0"
SCHEMA = "sc-lab-scientific-visualization-design-system/0.114.0"
FIGURE_SCHEMA = "sc-lab-publication-grade-figure/0.114.0"
EXPORT_SCHEMA = "sc-lab-publication-render-plan/0.114.0"
AUDIT_SCHEMA = "sc-lab-publication-figure-audit/0.114.0"
CORE_VISUAL_CONTRACT = "sc.visual-runtime.scene.v1"

PROFILES = {
    "journal-single": {"width_mm": 89, "height_mm": 67, "dpi": 600, "font_scale": 0.90, "target": "journal", "vector_first": True},
    "journal-double": {"width_mm": 183, "height_mm": 112, "dpi": 600, "font_scale": 1.00, "target": "journal", "vector_first": True},
    "report-wide": {"width_mm": 178, "height_mm": 100, "dpi": 450, "font_scale": 1.00, "target": "report", "vector_first": True},
    "web-responsive": {"width_px": 1440, "height_px": 810, "dpi": 144, "font_scale": 1.00, "target": "web", "vector_first": True},
    "slide-wide": {"width_px": 1920, "height_px": 1080, "dpi": 144, "font_scale": 1.18, "target": "presentation", "vector_first": True},
    "poster": {"width_mm": 420, "height_mm": 297, "dpi": 300, "font_scale": 1.35, "target": "poster", "vector_first": True},
}

SEMANTIC_ROLES = {
    "observed": {"color": "#111827", "stroke": "solid", "marker": "circle", "priority": 100},
    "model": {"color": "#2563EB", "stroke": "solid", "marker": "none", "priority": 90},
    "forecast": {"color": "#7C3AED", "stroke": "dash", "marker": "none", "priority": 85},
    "comparison": {"color": "#0F766E", "stroke": "solid", "marker": "square", "priority": 80},
    "reference": {"color": "#6B7280", "stroke": "dot", "marker": "none", "priority": 45},
    "threshold": {"color": "#991B1B", "stroke": "dash", "marker": "none", "priority": 95},
    "anomaly": {"color": "#B45309", "stroke": "solid", "marker": "diamond", "priority": 100},
    "positive": {"color": "#047857", "stroke": "solid", "marker": "circle", "priority": 80},
    "negative": {"color": "#B91C1C", "stroke": "solid", "marker": "triangle", "priority": 80},
    "muted": {"color": "#9CA3AF", "stroke": "solid", "marker": "none", "priority": 20},
}

UNCERTAINTY_STYLES = {
    "confidence": {"fill_opacity": 0.16, "boundary_opacity": 0.72, "boundary_style": "solid", "pattern": "none"},
    "credible": {"fill_opacity": 0.18, "boundary_opacity": 0.78, "boundary_style": "solid", "pattern": "none"},
    "prediction": {"fill_opacity": 0.12, "boundary_opacity": 0.65, "boundary_style": "dash", "pattern": "none"},
    "ensemble": {"fill_opacity": 0.10, "boundary_opacity": 0.58, "boundary_style": "dot", "pattern": "none"},
    "sensitivity": {"fill_opacity": 0.12, "boundary_opacity": 0.72, "boundary_style": "solid", "pattern": "diagonal"},
}

ANNOTATION_TYPES = {"callout", "event", "threshold", "reference-line", "interval", "band", "label", "finding", "method-note"}
EXPORT_FORMATS = {"svg", "pdf", "png", "tiff", "json", "csv"}

class VisualizationDesignSystemError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()

def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None: return {}
    if not isinstance(value, dict): raise VisualizationDesignSystemError(f"{label} must be an object.")
    return copy.deepcopy(value)

def _list(value: Any, label: str, maximum: int=5000) -> list[Any]:
    if value is None: return []
    if not isinstance(value, list): raise VisualizationDesignSystemError(f"{label} must be an array.")
    if len(value)>maximum: raise VisualizationDesignSystemError(f"{label} exceeds {maximum} entries.")
    return copy.deepcopy(value)

def _text(value: Any, label: str, maximum: int=1200, required: bool=False) -> str:
    s=str(value or '').strip()
    if required and not s: raise VisualizationDesignSystemError(f"{label} is required.")
    if len(s)>maximum: raise VisualizationDesignSystemError(f"{label} exceeds {maximum} characters.")
    return s

def design_tokens() -> dict[str, Any]:
    return {
        "ok": True, "schema": SCHEMA, "version": VERSION, "engine_version": ENGINE_VERSION,
        "typography": {
            "font_family": "Inter, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            "mono_family": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
            "title_px": 18, "subtitle_px": 12, "axis_title_px": 11, "tick_px": 10, "legend_px": 10,
            "annotation_px": 10, "caption_px": 10, "source_px": 9, "line_height": 1.35,
        },
        "layout": {"outer_margin_px": 20, "plot_padding_px": 14, "panel_gap_px": 18, "legend_gap_px": 10, "caption_gap_px": 10},
        "geometry": {"axis_stroke_px": 1.0, "grid_stroke_px": 0.75, "series_stroke_px": 2.0, "focus_stroke_px": 3.0, "marker_px": 5.0},
        "palette": {
            "paper": "#FFFFFF", "ink": "#111827", "subtle_ink": "#4B5563", "grid": "#E5E7EB", "axis": "#9CA3AF",
            "brand_accent": "#A31822", "observed": "#111827", "model": "#2563EB", "forecast": "#7C3AED",
            "comparison": "#0F766E", "warning": "#B45309", "negative": "#B91C1C", "positive": "#047857",
        },
        "principles": [
            "data-first", "vector-first", "semantic-encoding", "uncertainty-first", "annotation-with-evidence",
            "small-multiple-consistency", "responsive-composition", "accessible-without-color", "provenance-visible", "publication-exportable",
        ],
    }

def catalog() -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"profiles":copy.deepcopy(PROFILES),"semantic_roles":copy.deepcopy(SEMANTIC_ROLES),"uncertainty_styles":copy.deepcopy(UNCERTAINTY_STYLES),"annotation_types":sorted(ANNOTATION_TYPES),"export_formats":sorted(EXPORT_FORMATS)}

def normalize_figure(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise VisualizationDesignSystemError("figure request must be an object.")
    raw=payload.get("spec") if isinstance(payload.get("spec"),dict) else payload.get("figure") if isinstance(payload.get("figure"),dict) else payload
    try: spec=normalize_v0740_spec(raw)
    except VisualizationGrammarError as exc: raise VisualizationDesignSystemError(str(exc),422) from exc
    profile_name=_text(payload.get("profile") or raw.get("profile") or "web-responsive","profile",80,True)
    if profile_name not in PROFILES: raise VisualizationDesignSystemError(f"Unsupported profile: {profile_name}")
    semantic=[]
    raw_series=raw.get("series") if isinstance(raw.get("series"),list) else []
    for i,s in enumerate(spec.get("series") or []):
        source_role=raw_series[i] if i < len(raw_series) and isinstance(raw_series[i],dict) else {}
        role=_text(source_role.get("semantic_role") or source_role.get("semanticRole") or (s or {}).get("semantic_role") or (s or {}).get("semanticRole") or ("observed" if i==0 else "comparison"),"semantic role",40,True)
        if role not in SEMANTIC_ROLES: raise VisualizationDesignSystemError(f"Unsupported semantic role: {role}")
        semantic.append({"series_id":s.get("id") or f"series-{i+1}","role":role,"style":copy.deepcopy(SEMANTIC_ROLES[role])})
    figure={
        "schema":FIGURE_SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,"profile":profile_name,"profile_spec":copy.deepcopy(PROFILES[profile_name]),
        "spec":spec,"semantic_series":semantic,"annotations":[],"uncertainty_layers":[],"accessibility":{},"publication":copy.deepcopy(spec.get("publication") or {}),
        "rendering": {"vector_first":True,"preferred_renderer":"svg2d" if spec.get("kind")!="surface-4d" else "webgpu","core_renderer_neutral":True},
        "boundaries": {"automatic_claim_inference":False,"automatic_uncertainty_inference":False,"automatic_source_inference":False,"automatic_scientific_certification":False},
    }
    figure["fingerprint"]=_hash({k:v for k,v in figure.items() if k!="fingerprint"})
    return {"ok":True,"figure":figure}

def apply_profile(payload: dict[str, Any]) -> dict[str, Any]:
    figure=_dict(payload.get("figure"),"figure")
    if not figure: figure=normalize_figure(payload)["figure"]
    name=_text(payload.get("profile") or figure.get("profile") or "web-responsive","profile",80,True)
    if name not in PROFILES: raise VisualizationDesignSystemError(f"Unsupported profile: {name}")
    out=copy.deepcopy(figure); out["profile"]=name; out["profile_spec"]=copy.deepcopy(PROFILES[name]); out["design_tokens"]=design_tokens(); out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"})
    return {"ok":True,"figure":out}

def build_annotation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    items=_list(payload.get("annotations"),"annotations",500); out=[]
    for i,item in enumerate(items):
        if not isinstance(item,dict): raise VisualizationDesignSystemError(f"annotations[{i}] must be an object.")
        kind=_text(item.get("type") or "callout","annotation type",40,True)
        if kind not in ANNOTATION_TYPES: raise VisualizationDesignSystemError(f"Unsupported annotation type: {kind}")
        text=_text(item.get("text") or item.get("label"),"annotation text",800,True)
        out.append({"id":_text(item.get("id") or f"annotation-{i+1}","annotation id",120,True),"type":kind,"text":text,"x":item.get("x"),"y":item.get("y"),"x2":item.get("x2"),"y2":item.get("y2"),"source_ref":item.get("source_ref") or item.get("sourceRef"),"evidence_ref":item.get("evidence_ref") or item.get("evidenceRef"),"priority":int(item.get("priority",50)),"collision_policy":"avoid-data-and-labels","leader_line":kind in {"callout","finding","method-note"}})
    out.sort(key=lambda x:(-x["priority"],x["id"]))
    return {"ok":True,"schema":f"{SCHEMA}/annotations","annotations":out,"automatic_finding_generation":False,"automatic_evidence_linking":False}

def style_uncertainty(payload: dict[str, Any]) -> dict[str, Any]:
    layers=_list(payload.get("layers") or payload.get("uncertainty_layers"),"layers",500); out=[]
    for i,item in enumerate(layers):
        if not isinstance(item,dict): raise VisualizationDesignSystemError(f"layers[{i}] must be an object.")
        kind=_text(item.get("kind") or item.get("type") or "confidence","uncertainty kind",40,True)
        if kind not in UNCERTAINTY_STYLES: raise VisualizationDesignSystemError(f"Unsupported uncertainty kind: {kind}")
        level=item.get("level")
        if level is not None:
            level=float(level)
            if not 0 < level < 1: raise VisualizationDesignSystemError("uncertainty level must be between 0 and 1.")
        out.append({"id":_text(item.get("id") or f"uncertainty-{i+1}","uncertainty id",120,True),"kind":kind,"level":level,"lower_ref":item.get("lower_ref"),"upper_ref":item.get("upper_ref"),"source_ref":item.get("source_ref"),"style":copy.deepcopy(UNCERTAINTY_STYLES[kind]),"legend_label":_text(item.get("legend_label") or item.get("label") or kind.title(),"legend label",160,True)})
    return {"ok":True,"schema":f"{SCHEMA}/uncertainty","layers":out,"automatic_uncertainty_inference":False,"color_alone_is_not_required":True}

def compose_small_multiples(payload: dict[str, Any]) -> dict[str, Any]:
    panels=_list(payload.get("panels"),"panels",64)
    if not panels: raise VisualizationDesignSystemError("At least one panel is required.")
    cols=int(payload.get("columns") or min(3,len(panels))); cols=max(1,min(cols,6)); rows=math.ceil(len(panels)/cols)
    normalized=[]
    for i,p in enumerate(panels):
        if not isinstance(p,dict): raise VisualizationDesignSystemError(f"panels[{i}] must be an object.")
        letter=chr(65+i) if i<26 else str(i+1)
        normalized.append({"panel_id":_text(p.get("panel_id") or p.get("id") or f"panel-{i+1}","panel id",120,True),"label":_text(p.get("label") or letter,"panel label",20,True),"title":_text(p.get("title"),"panel title",240),"figure_ref":p.get("figure_ref") or p.get("figureRef"),"spec":copy.deepcopy(p.get("spec")) if isinstance(p.get("spec"),dict) else None})
    return {"ok":True,"schema":f"{SCHEMA}/small-multiples","layout":{"rows":rows,"columns":cols,"panel_gap_px":18,"shared_x":bool(payload.get("shared_x",False)),"shared_y":bool(payload.get("shared_y",False)),"consistent_semantic_roles":True},"panels":normalized,"responsive":{"desktop_columns":cols,"tablet_columns":min(cols,2),"mobile_columns":1}}

def accessibility_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    figure=_dict(payload.get("figure"),"figure"); alt=_text(payload.get("alt_text") or payload.get("altText"),"alt text",1200)
    long_desc=_text(payload.get("long_description") or payload.get("longDescription"),"long description",5000)
    table_ref=_text(payload.get("table_ref") or payload.get("tableRef"),"table ref",1200)
    meta={"alt_text":alt,"long_description":long_desc,"table_ref":table_ref or None,"keyboard_navigation":True,"focus_visible":True,"color_only_encoding":False,"patterns_and_markers_available":True,"minimum_text_px":9,"target_contrast_ratio":4.5,"reduced_motion_supported":True,"screen_reader_title":_text((figure.get("spec") or {}).get("title"),"screen reader title",300) if figure else ""}
    return {"ok":True,"schema":f"{SCHEMA}/accessibility","accessibility":meta,"automatic_alt_text_inference":False}

def renderer_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figure=_dict(payload.get("figure"),"figure")
    if not figure: figure=normalize_figure(payload)["figure"]
    spec=figure.get("spec") or {}; kind=str(spec.get("kind") or '')
    point_count=sum(len(s.get("points") or []) for s in spec.get("series") or [])
    publication=bool(payload.get("publication",True)); interactive=bool(payload.get("interactive",False))
    if kind=="surface-4d": preferred="webgpu"
    elif point_count>150000 and interactive: preferred="webgl2"
    else: preferred="svg2d"
    fallback=["svg2d"] if preferred=="svg2d" else (["webgl2","canvas4d","svg2d"] if preferred=="webgpu" else ["canvas4d","svg2d"])
    registry=gpu_renderer_registry()
    return {"ok":True,"schema":f"{SCHEMA}/renderer-plan","preferred_renderer":preferred,"fallback_renderers":fallback,"publication_renderer":"svg2d" if kind!="surface-4d" else "rasterized-gpu-export","vector_first":publication and kind!="surface-4d","point_count":point_count,"gpu_registry_version":registry.get("version"),"automatic_gpu_execution":False}

def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figure=_dict(payload.get("figure"),"figure")
    if not figure: figure=normalize_figure(payload)["figure"]
    formats=[str(x).lower() for x in (payload.get("formats") or ["svg","pdf","png","json"])]
    bad=[f for f in formats if f not in EXPORT_FORMATS]
    if bad: raise VisualizationDesignSystemError("Unsupported export format(s): "+", ".join(bad))
    profile=PROFILES.get(figure.get("profile"),PROFILES["web-responsive"])
    vector=[f for f in formats if f in {"svg","pdf"}]; raster=[f for f in formats if f in {"png","tiff"}]
    provenance_plan=None
    try: provenance_plan=build_export_manifest({"figure":figure,"format":"json"})
    except Exception: provenance_plan={"ok":False,"reason":"figure does not yet carry v0.83 provenance envelope"}
    return {"ok":True,"schema":EXPORT_SCHEMA,"version":VERSION,"profile":figure.get("profile"),"formats":formats,"vector_formats":vector,"raster_formats":raster,"dpi":profile.get("dpi",300),"embed_fonts":True,"outline_fonts_for_archive":False,"preserve_live_text_in_svg_pdf":True,"background":"transparent" if bool(payload.get("transparent",False)) else "paper","include_caption":True,"include_source_note":True,"include_method_note":True,"include_provenance_id":True,"renderer_plan":renderer_plan({"figure":figure,"publication":True}),"provenance_export_manifest":provenance_plan,"automatic_file_write":False}

def audit_figure(payload: dict[str, Any]) -> dict[str, Any]:
    figure=_dict(payload.get("figure"),"figure")
    if not figure: figure=normalize_figure(payload)["figure"]
    spec=figure.get("spec") or {}; pub=figure.get("publication") or spec.get("publication") or {}
    checks=[]
    def add(key,ok,severity,msg): checks.append({"check":key,"ok":bool(ok),"severity":severity,"message":msg})
    add("title",bool(_text(spec.get("title"),"title",300)),"error","Figure has a concise title.")
    axes=spec.get("axes") or {}; add("axis-labels",bool((axes.get("x") or {}).get("label") and (axes.get("y") or {}).get("label")),"error","Both axes carry labels.")
    units_ok=all("unit" in (axes.get(k) or {}) for k in ("x","y")); add("axis-units-declared",units_ok,"warning","Axis unit fields are explicitly present, including unitless axes.")
    add("caption",bool(_text(pub.get("caption"),"caption",1600)),"warning","Publication caption is present.")
    add("source",bool(_text(pub.get("source"),"source",1000)),"warning","Source/provenance note is present.")
    add("semantic-series",bool(figure.get("semantic_series")) or not spec.get("series"),"warning","Series use semantic visual roles.")
    acc=figure.get("accessibility") or {}; add("accessibility",bool(acc.get("alt_text") or acc.get("long_description") or acc.get("table_ref")),"warning","Accessibility description or data-table fallback is attached.")
    add("vector-first",bool((figure.get("rendering") or {}).get("vector_first")),"warning","Publication workflow prefers vector output where applicable.")
    add("provenance",bool(figure.get("figureProvenance") or figure.get("provenance") or spec.get("provenance")),"warning","Figure carries provenance metadata.")
    blockers=[c for c in checks if c["severity"]=="error" and not c["ok"]]; warnings=[c for c in checks if c["severity"]=="warning" and not c["ok"]]
    return {"ok":True,"schema":AUDIT_SCHEMA,"version":VERSION,"publication_ready":not blockers,"blocker_count":len(blockers),"warning_count":len(warnings),"checks":checks,"scientific_validity_certified":False,"visual_truth_inferred":False}

def build_publication_figure(payload: dict[str, Any]) -> dict[str, Any]:
    figure=normalize_figure(payload)["figure"] if not isinstance(payload.get("figure"),dict) else copy.deepcopy(payload["figure"])
    if payload.get("profile"): figure=apply_profile({"figure":figure,"profile":payload["profile"]})["figure"]
    if payload.get("annotations") is not None: figure["annotations"]=build_annotation_plan({"annotations":payload.get("annotations")})["annotations"]
    if payload.get("uncertainty_layers") is not None: figure["uncertainty_layers"]=style_uncertainty({"layers":payload.get("uncertainty_layers")})["layers"]
    if any(k in payload for k in ("alt_text","altText","long_description","longDescription","table_ref","tableRef")): figure["accessibility"]=accessibility_metadata({"figure":figure,**payload})["accessibility"]
    figure["renderer_plan"]=renderer_plan({"figure":figure,"publication":True})
    figure["fingerprint"]=_hash({k:v for k,v in figure.items() if k!="fingerprint"})
    return {"ok":True,"figure":figure,"audit":audit_figure({"figure":figure}),"export_plan":build_export_plan({"figure":figure,"formats":payload.get("formats") or ["svg","pdf","png","json"]})}

def core_visual_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figure=_dict(payload.get("figure"),"figure")
    if not figure: figure=build_publication_figure(payload)["figure"]
    spec=figure.get("spec") or {}
    core_request={"context":payload.get("context") or payload,"visual":{"id":payload.get("id") or f"figure-{figure.get('fingerprint','')[:20]}","visual_type":"scientific-figure","title":spec.get("title") or "Scientific figure","source_refs":payload.get("source_refs") or [],"renderer":(figure.get("renderer_plan") or {}).get("preferred_renderer"),"metadata":{"lab_design_system_version":VERSION,"figure_fingerprint":figure.get("fingerprint"),"profile":figure.get("profile"),"publication_ready":audit_figure({"figure":figure})["publication_ready"]}}}
    try: plan=build_core_visual_binding(core_request)
    except Exception as exc: raise VisualizationDesignSystemError(f"Core visual binding plan could not be built: {exc}",422) from exc
    plan["automatic_submission"]=False; plan["publication_figure_remains_authoritative_in_lab"]=True
    return plan

def manifest() -> dict[str, Any]:
    return {"ok":True,"status":"scientific-visualization-design-system-ready","version":VERSION,"engine_version":ENGINE_VERSION,"profile_count":len(PROFILES),"semantic_role_count":len(SEMANTIC_ROLES),"uncertainty_style_count":len(UNCERTAINTY_STYLES),"annotation_type_count":len(ANNOTATION_TYPES),"publication_grade_rendering":True,"vector_first_exports":True,"responsive_composition":True,"accessible_non_color_encodings":True,"small_multiples":True,"core_visual_bridge_compatible":"0.109.0","boundaries":{"automatic_core_submission":False,"automatic_scientific_validity_certification":False,"automatic_claim_inference":False,"automatic_uncertainty_inference":False,"automatic_source_inference":False,"automatic_truth_determination":False}}

def health() -> dict[str, Any]:
    m=manifest(); return {**m,"schema":SCHEMA,"core_visual_contract":CORE_VISUAL_CONTRACT,"legacy_visualization_engine":"0.74.0","provenance_figures":"0.83.0","gpu_renderer_registry":"0.84.0"}
