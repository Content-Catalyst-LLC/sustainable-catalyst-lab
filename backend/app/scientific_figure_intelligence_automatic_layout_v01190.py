from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

from .scientific_visualization_design_system_v01140 import PROFILES, design_tokens
from .platform_core_v3_visual_scene_v01090 import build_core_visual_binding

VERSION = "0.119.0"
ENGINE_VERSION = "3.5.0"
SCHEMA = "sc-lab-scientific-figure-intelligence-automatic-layout/0.119.0"
PLAN_SCHEMA = "sc-lab-scientific-figure-layout-plan/0.119.0"
SNAPSHOT_SCHEMA = "sc-lab-scientific-figure-layout-snapshot/0.119.0"
MAX_PANELS = 64
MAX_ANNOTATIONS = 1000
MAX_LEGEND_ENTRIES = 256

LAYOUT_MODES = {
    "single", "two-column", "grid", "vertical-strip", "horizontal-strip", "focus-context", "small-multiples"
}
LEGEND_POSITIONS = {"inside-top-right", "inside-top-left", "outside-right", "below", "above", "none"}
LABEL_STRATEGIES = {"horizontal", "rotate-30", "rotate-45", "wrap", "stagger", "outside", "declared"}
COLLISION_POLICIES = {"displace", "leader-line", "stack", "preserve-and-report"}
QUALITY_SEVERITIES = {"info", "warning", "error"}

class FigureLayoutIntelligenceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()

def _text(value: Any, label: str, maximum: int = 1200, required: bool = False) -> str:
    s=str(value or "").strip()
    if required and not s: raise FigureLayoutIntelligenceError(f"{label} is required.")
    if len(s)>maximum: raise FigureLayoutIntelligenceError(f"{label} exceeds {maximum} characters.")
    return s

def _list(value: Any, label: str, maximum: int = 1000) -> list[Any]:
    if value is None: return []
    if not isinstance(value,list): raise FigureLayoutIntelligenceError(f"{label} must be an array.")
    if len(value)>maximum: raise FigureLayoutIntelligenceError(f"{label} exceeds {maximum} entries.",413)
    return copy.deepcopy(value)

def _dict(value: Any, label: str) -> dict[str,Any]:
    if value is None: return {}
    if not isinstance(value,dict): raise FigureLayoutIntelligenceError(f"{label} must be an object.")
    return copy.deepcopy(value)

def _bounded_int(value: Any, label: str, lo: int, hi: int, default: int) -> int:
    try: n=int(value if value is not None else default)
    except (TypeError,ValueError): raise FigureLayoutIntelligenceError(f"{label} must be an integer.")
    if not lo<=n<=hi: raise FigureLayoutIntelligenceError(f"{label} must be between {lo} and {hi}.")
    return n

def _finite(value: Any, label: str, default: float=0.0) -> float:
    try: n=float(value if value is not None else default)
    except (TypeError,ValueError): raise FigureLayoutIntelligenceError(f"{label} must be numeric.")
    if not math.isfinite(n): raise FigureLayoutIntelligenceError(f"{label} must be finite.")
    return n

def _profile(name: str) -> dict[str,Any]:
    if name not in PROFILES: raise FigureLayoutIntelligenceError(f"unsupported publication profile: {name}")
    return copy.deepcopy(PROFILES[name])

def schema_info() -> dict[str,Any]:
    return {"ok":True,"schema":SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,"plan_schema":PLAN_SCHEMA,"snapshot_schema":SNAPSHOT_SCHEMA,"panel_limit":MAX_PANELS,"annotation_limit":MAX_ANNOTATIONS}

def catalog() -> dict[str,Any]:
    return {"ok":True,"version":VERSION,"layout_modes":sorted(LAYOUT_MODES),"legend_positions":sorted(LEGEND_POSITIONS),"label_strategies":sorted(LABEL_STRATEGIES),"collision_policies":sorted(COLLISION_POLICIES),"publication_profiles":sorted(PROFILES)}

def normalize_figure_context(payload: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(payload,dict): raise FigureLayoutIntelligenceError("figure context must be an object.")
    raw = payload.get("figure") if isinstance(payload.get("figure"),dict) else payload
    profile_name=_text(raw.get("publication_profile") or raw.get("publicationProfile") or raw.get("profile") or "web-responsive","publication_profile",80,True)
    profile=_profile(profile_name)
    width=_bounded_int(raw.get("width_px") or raw.get("widthPx") or profile.get("width_px") or 1200,"width_px",240,12000,1200)
    height=_bounded_int(raw.get("height_px") or raw.get("heightPx") or profile.get("height_px") or 800,"height_px",180,12000,800)
    axes=_dict(raw.get("axes"),"axes")
    def axis(name: str) -> dict[str,Any]:
        a=_dict(axes.get(name),f"axes.{name}")
        labels=_list(a.get("labels"),f"axes.{name}.labels",500)
        count=_bounded_int(a.get("label_count") or a.get("labelCount") or len(labels),f"axes.{name}.label_count",0,500,len(labels))
        max_chars=_bounded_int(a.get("max_label_chars") or a.get("maxLabelChars") or max([len(str(x)) for x in labels] or [0]),f"axes.{name}.max_label_chars",0,500,max([len(str(x)) for x in labels] or [0]))
        return {"title":_text(a.get("title"),f"axes.{name}.title",300) or None,"unit":_text(a.get("unit"),f"axes.{name}.unit",120) or None,"label_count":count,"max_label_chars":max_chars,"domain_declared":bool(a.get("domain_declared") or a.get("domainDeclared") or (a.get("domain") is not None)),"scale_declared":bool(a.get("scale_declared") or a.get("scaleDeclared") or a.get("scale"))}
    panels=_list(raw.get("panels"),"panels",MAX_PANELS)
    legend=_dict(raw.get("legend"),"legend")
    entries=_list(legend.get("entries"),"legend.entries",MAX_LEGEND_ENTRIES)
    annotations=_list(raw.get("annotations"),"annotations",MAX_ANNOTATIONS)
    out={
        "schema":SCHEMA,"version":VERSION,"id":_text(raw.get("id") or raw.get("figure_id") or "figure","figure id",180,True),
        "figure_ref":_text(raw.get("figure_ref") or raw.get("figureRef") or "lab:figure:unbound","figure_ref",1200,True),
        "title":_text(raw.get("title"),"title",800) or None,"subtitle":_text(raw.get("subtitle"),"subtitle",1200) or None,
        "caption_present":bool(_text(raw.get("caption"),"caption",8000)),"source_note_present":bool(_text(raw.get("source_note") or raw.get("sourceNote"),"source note",5000)),
        "publication_profile":profile_name,"profile_spec":profile,"canvas":{"width_px":width,"height_px":height,"aspect_ratio":round(width/height,4)},
        "axes":{"x":axis("x"),"y":axis("y")},
        "legend":{"entry_count":len(entries) if entries else _bounded_int(legend.get("entry_count") or legend.get("entryCount"),"legend.entry_count",0,MAX_LEGEND_ENTRIES,0),"max_label_chars":max([len(str(x.get("label",""))) for x in entries if isinstance(x,dict)] or [int(legend.get("max_label_chars") or 0)]),"preferred_position":_text(legend.get("preferred_position") or legend.get("preferredPosition"),"legend.preferred_position",80) or None},
        "panel_count":len(panels) if panels else _bounded_int(raw.get("panel_count") or raw.get("panelCount"),"panel_count",1,MAX_PANELS,1),
        "annotations":copy.deepcopy(annotations),"annotation_count":len(annotations),
        "data_region_count":_bounded_int(raw.get("data_region_count") or raw.get("dataRegionCount"),"data_region_count",1,256,1),
        "declared_shared_x":bool(raw.get("shared_x") or raw.get("sharedX")),"declared_shared_y":bool(raw.get("shared_y") or raw.get("sharedY")),
        "alt_text_present":bool(_text(raw.get("alt_text") or raw.get("altText"),"alt_text",5000)),
        "scientific_encoding_locked":True,
    }
    out["context_hash"]=_hash({k:v for k,v in out.items() if k!="context_hash"})
    return out

def analyze_figure(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload)
    x=f["axes"]["x"]; y=f["axes"]["y"]; legend=f["legend"]
    crowding=(x["label_count"]*max(x["max_label_chars"],1)+y["label_count"]*0.45*max(y["max_label_chars"],1)+legend["entry_count"]*max(legend["max_label_chars"],8)+f["annotation_count"]*16)/max(f["canvas"]["width_px"],1)
    panel_density=f["panel_count"]/(max(f["canvas"]["width_px"]*f["canvas"]["height_px"],1)/250000)
    flags=[]
    if crowding>1.25: flags.append("high-label-density")
    elif crowding>0.75: flags.append("moderate-label-density")
    if f["annotation_count"]>12: flags.append("annotation-dense")
    if legend["entry_count"]>8: flags.append("legend-dense")
    if f["panel_count"]>9: flags.append("many-panels")
    if not x["domain_declared"] or not y["domain_declared"]: flags.append("domain-not-declared")
    return {"ok":True,"schema":f"{SCHEMA}/analysis","figure":f,"metrics":{"crowding_index":round(crowding,3),"panel_density":round(panel_density,3),"aspect_ratio":f["canvas"]["aspect_ratio"]},"flags":flags,"automatic_data_inspection":False,"automatic_scientific_inference":False}

def plan_axes(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload)
    plans={}
    for name in ("x","y"):
        a=f["axes"][name]; count=a["label_count"]; chars=a["max_label_chars"]
        strategy="horizontal"
        if name=="x":
            if count>=18 or chars>=22: strategy="rotate-45"
            elif count>=10 or chars>=14: strategy="rotate-30"
            elif chars>=10: strategy="wrap"
        else:
            if chars>=24: strategy="wrap"
        plans[name]={"label_strategy":strategy,"title_reserved_px":24 if a["title"] else 8,"unit_reserved_px":14 if a["unit"] else 0,"domain_preserved":True,"scale_preserved":True,"tick_count_preserved":True,"reason":f"declared label_count={count}, max_label_chars={chars}"}
    return {"ok":True,"schema":f"{PLAN_SCHEMA}/axes","axes":plans,"automatic_domain_changes":False,"automatic_scale_changes":False,"automatic_tick_thinning":False}

def plan_legend(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); l=f["legend"]
    preferred=l.get("preferred_position")
    if preferred:
        if preferred not in LEGEND_POSITIONS: raise FigureLayoutIntelligenceError(f"unsupported legend position: {preferred}")
        pos=preferred; reason="declared preference"
    elif l["entry_count"]==0: pos="none"; reason="no declared legend entries"
    elif l["entry_count"]<=4 and l["max_label_chars"]<=18: pos="inside-top-right"; reason="compact legend"
    elif l["entry_count"]<=8: pos="below"; reason="moderate legend density"
    else: pos="outside-right"; reason="dense legend"
    reserve={"right_px":220 if pos=="outside-right" else 0,"bottom_px":60 if pos=="below" else 0,"top_px":52 if pos=="above" else 0}
    return {"ok":True,"schema":f"{PLAN_SCHEMA}/legend","legend":{"position":pos,"reserve":reserve,"entry_count":l["entry_count"],"reason":reason},"automatic_series_reordering":False,"automatic_legend_entry_dropping":False}

def plan_panels(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); n=f["panel_count"]; aspect=f["canvas"]["aspect_ratio"]
    requested=payload.get("columns")
    if requested is not None: cols=_bounded_int(requested,"columns",1,8,min(n,4)); reason="declared columns"
    else:
        cols=min(n, max(1, min(6, round(math.sqrt(n*max(aspect,0.5)))))); reason="deterministic aspect-aware packing"
    rows=math.ceil(n/cols)
    if n==1: mode="single"
    elif rows==1: mode="horizontal-strip"
    elif cols==1: mode="vertical-strip"
    else: mode="small-multiples"
    return {"ok":True,"schema":f"{PLAN_SCHEMA}/panels","panels":{"count":n,"rows":rows,"columns":cols,"mode":mode,"gap_px":18,"shared_x":f["declared_shared_x"],"shared_y":f["declared_shared_y"],"reason":reason},"automatic_panel_reordering":False,"automatic_panel_omission":False}

def _boxes_overlap(a: dict[str,float], b: dict[str,float]) -> bool:
    return not (a["x"]+a["w"]<=b["x"] or b["x"]+b["w"]<=a["x"] or a["y"]+a["h"]<=b["y"] or b["y"]+b["h"]<=a["y"])

def plan_annotations(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); used=[]; placed=[]; unresolved=[]
    offsets=[(12,-12),(12,12),(-132,-12),(-132,12),(18,-42),(-132,-42),(18,30),(-132,30)]
    for i,item in enumerate(f["annotations"]):
        if not isinstance(item,dict): raise FigureLayoutIntelligenceError(f"annotations[{i}] must be an object.")
        aid=_text(item.get("id") or f"annotation-{i+1}","annotation id",160,True)
        ax=_finite(item.get("anchor_x") or item.get("x"),f"annotations[{i}].anchor_x",0.5)
        ay=_finite(item.get("anchor_y") or item.get("y"),f"annotations[{i}].anchor_y",0.5)
        # normalized 0..1 anchors are mapped to canvas; explicit pixel anchors >1 are kept
        px=ax*f["canvas"]["width_px"] if 0<=ax<=1 else ax; py=ay*f["canvas"]["height_px"] if 0<=ay<=1 else ay
        w=_bounded_int(item.get("width_px") or item.get("widthPx"),f"annotations[{i}].width_px",40,800,120)
        h=_bounded_int(item.get("height_px") or item.get("heightPx"),f"annotations[{i}].height_px",20,400,34)
        chosen=None
        for dx,dy in offsets:
            box={"x":max(0,min(f["canvas"]["width_px"]-w,px+dx)),"y":max(0,min(f["canvas"]["height_px"]-h,py+dy)),"w":w,"h":h}
            if not any(_boxes_overlap(box,u) for u in used): chosen=box; break
        if chosen is None:
            chosen={"x":max(0,min(f["canvas"]["width_px"]-w,px+12)),"y":max(0,min(f["canvas"]["height_px"]-h,py+12)),"w":w,"h":h}; unresolved.append(aid)
        used.append(chosen); placed.append({"id":aid,"anchor":{"x":px,"y":py},"box":chosen,"leader_line":True,"text_preserved":True})
    return {"ok":True,"schema":f"{PLAN_SCHEMA}/annotations","annotations":placed,"unresolved_collisions":unresolved,"collision_policy":"displace-then-report","automatic_annotation_deletion":False,"automatic_evidence_weighting":False}

def collision_audit(payload: dict[str,Any]) -> dict[str,Any]:
    p=plan_annotations(payload); return {"ok":True,"schema":f"{SCHEMA}/collision-audit","annotation_count":len(p["annotations"]),"unresolved_collision_count":len(p["unresolved_collisions"]),"unresolved_collisions":p["unresolved_collisions"],"passes":len(p["unresolved_collisions"])==0}

def plan_responsive(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); panels=plan_panels(payload)["panels"]
    desktop=panels["columns"]; tablet=min(desktop,2); mobile=1
    return {"ok":True,"schema":f"{PLAN_SCHEMA}/responsive","breakpoints":[{"min_width":1200,"columns":desktop,"legend":"outside-right" if f["legend"]["entry_count"]>8 else "inside-top-right"},{"min_width":720,"columns":tablet,"legend":"below"},{"min_width":0,"columns":mobile,"legend":"below"}],"preserve_panel_order":True,"preserve_scales":True,"automatic_scientific_encoding_changes":False}

def plan_print(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); profile=f["profile_spec"]
    return {"ok":True,"schema":f"{PLAN_SCHEMA}/print","profile":f["publication_profile"],"dimensions":profile,"vector_first":bool(profile.get("vector_first",True)),"minimum_font_pt":7.0,"line_weight_pt":0.5,"grayscale_safe":True,"print_safe_margins_mm":6,"automatic_content_removal":False}

def plan_layout(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); axes=plan_axes(payload)["axes"]; legend=plan_legend(payload)["legend"]; panels=plan_panels(payload)["panels"]
    left=58 + (16 if f["axes"]["y"]["title"] else 0) + min(60,max(0,f["axes"]["y"]["max_label_chars"]-8)*3)
    bottom=52 + (18 if f["axes"]["x"]["title"] else 0) + (26 if axes["x"]["label_strategy"].startswith("rotate") else 0)
    top=44 + (24 if f["subtitle"] else 0); right=30+legend["reserve"]["right_px"]; bottom+=legend["reserve"]["bottom_px"]; top+=legend["reserve"]["top_px"]
    plot_w=max(80,f["canvas"]["width_px"]-left-right); plot_h=max(80,f["canvas"]["height_px"]-top-bottom)
    out={"schema":PLAN_SCHEMA,"version":VERSION,"figure_ref":f["figure_ref"],"canvas":f["canvas"],"margins_px":{"left":left,"right":right,"top":top,"bottom":bottom},"plot_region_px":{"x":left,"y":top,"width":plot_w,"height":plot_h},"axes":axes,"legend":legend,"panels":panels,"responsive":plan_responsive(payload)["breakpoints"],"scientific_encoding_locked":True,"data_domain_locked":True,"scale_semantics_locked":True,"layout_algorithm":"deterministic-declared-metadata-v1"}
    out["layout_hash"]=_hash(out)
    return {"ok":True,"layout":out,"automatic_data_transformation":False,"automatic_scientific_encoding_changes":False}

def quality_audit(payload: dict[str,Any]) -> dict[str,Any]:
    a=analyze_figure(payload); f=a["figure"]; issues=[]
    def issue(code,severity,message): issues.append({"code":code,"severity":severity,"message":message})
    if "high-label-density" in a["flags"]: issue("label-density","warning","Declared labels are likely crowded at this canvas size.")
    if "legend-dense" in a["flags"]: issue("legend-density","warning","Legend is dense; outside placement is recommended.")
    if "domain-not-declared" in a["flags"]: issue("domain-declaration","info","One or more axis domains are not explicitly declared; layout will not infer them.")
    if not f["alt_text_present"]: issue("alt-text","warning","Alt text is not declared.")
    if not f["caption_present"]: issue("caption","info","Caption is not declared.")
    if f["canvas"]["width_px"]<480: issue("small-canvas","warning","Canvas width is constrained for publication-grade figure composition.")
    score=max(0,100-sum(15 if x["severity"]=="warning" else 5 for x in issues))
    return {"ok":True,"schema":f"{SCHEMA}/quality-audit","score":score,"issues":issues,"publication_layout_ready":not any(x["severity"]=="error" for x in issues),"scientific_validity_certified":False}

def accessibility_audit(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); issues=[]
    if not f["alt_text_present"]: issues.append("alt-text-missing")
    if f["legend"]["entry_count"]>0 and f["legend"]["max_label_chars"]>60: issues.append("legend-labels-long")
    if f["axes"]["x"]["title"] is None and f["axes"]["x"]["unit"] is not None: issues.append("x-axis-title-missing")
    if f["axes"]["y"]["title"] is None and f["axes"]["y"]["unit"] is not None: issues.append("y-axis-title-missing")
    return {"ok":True,"schema":f"{SCHEMA}/accessibility","accessible":len(issues)==0,"issues":issues,"keyboard_navigation_preserved":True,"non_color_encoding_required":True,"automatic_alt_text_inference":False}

def explain_layout(payload: dict[str,Any]) -> dict[str,Any]:
    a=analyze_figure(payload); l=plan_layout(payload)["layout"]
    reasons=[f"Canvas {l['canvas']['width_px']}×{l['canvas']['height_px']} px with aspect ratio {l['canvas']['aspect_ratio']}.",f"X-axis label strategy is {l['axes']['x']['label_strategy']} from declared label density.",f"Legend position is {l['legend']['position']} because {l['legend']['reason']}.",f"Panels use {l['panels']['rows']} rows × {l['panels']['columns']} columns ({l['panels']['reason']})."]
    if a["flags"]: reasons.append("Detected layout flags: "+", ".join(a["flags"])+".")
    return {"ok":True,"schema":f"{SCHEMA}/explanation","reasons":reasons,"explanation_is_layout_only":True,"automatic_scientific_interpretation":False}

def build_figure_intelligence(payload: dict[str,Any]) -> dict[str,Any]:
    a=analyze_figure(payload); l=plan_layout(payload); ann=plan_annotations(payload); q=quality_audit(payload); acc=accessibility_audit(payload)
    result={"schema":f"{SCHEMA}/figure-intelligence","version":VERSION,"figure":a["figure"],"analysis":a["metrics"],"flags":a["flags"],"layout":l["layout"],"annotations":ann,"quality":q,"accessibility":acc,"boundaries":{"automatic_data_transformation":False,"automatic_domain_inference":False,"automatic_scale_inference":False,"automatic_scientific_encoding_changes":False,"automatic_claim_inference":False,"automatic_evidence_weighting":False,"scientific_validity_certified":False}}
    result["intelligence_hash"]=_hash(result)
    return {"ok":True,"figure_intelligence":result}

def build_export_plan(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); formats=[_text(x,"format",20,True).lower() for x in _list(payload.get("formats") or ["svg","pdf","png","json"],"formats",20)]
    supported={"svg","pdf","png","tiff","json"}; bad=sorted(set(formats)-supported)
    if bad: raise FigureLayoutIntelligenceError("unsupported export formats: "+", ".join(bad))
    return {"ok":True,"schema":f"{SCHEMA}/export-plan","figure_ref":f["figure_ref"],"formats":formats,"layout":plan_layout(payload)["layout"],"print":plan_print(payload)["profile"],"embed_layout_hash":True,"embed_context_hash":True,"automatic_file_write":False,"automatic_publication":False}

def build_snapshot(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); layout=plan_layout(payload)["layout"]
    snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"figure_ref":f["figure_ref"],"context_hash":f["context_hash"],"layout_hash":layout["layout_hash"],"publication_profile":f["publication_profile"],"layout":layout,"locked_scientific_encoding":True}
    snap["snapshot_hash"]=_hash(snap)
    return {"ok":True,"snapshot":snap,"automatic_persistence":False}

def build_core_visual_plan(payload: dict[str,Any]) -> dict[str,Any]:
    f=normalize_figure_context(payload); session_id=_text(payload.get("session_id") or payload.get("sessionId"),"session_id",300,True)
    visual={"session_id":session_id,"visual_ref":f["figure_ref"],"visual_type":"scientific-figure-layout","scene_ref":None,"view_ref":f"layout:{f['id']}:0.119.0","source_refs":[]}
    # Preserve Core reference-first semantics; richer layout stays namespaced metadata.
    try: core=build_core_visual_binding(visual)
    except Exception:
        core={"automatic_submission":False,"data":visual}
    return {"ok":True,"schema":f"{SCHEMA}/core-visual-plan","core_visual_binding":core,"layout_snapshot":build_snapshot(payload)["snapshot"],"automatic_core_submission":False,"core_changes_scientific_encoding":False,"core_renders_figure":False}

def manifest() -> dict[str,Any]:
    return {"ok":True,"status":"scientific-figure-intelligence-automatic-layout-ready","version":VERSION,"engine_version":ENGINE_VERSION,"deterministic_layout_planning":True,"axis_label_strategy":True,"legend_placement":True,"annotation_collision_avoidance":True,"panel_grid_planning":True,"responsive_reflow":True,"print_layout":True,"quality_audit":True,"accessibility_audit":True,"layout_snapshots":True,"core_visual_bridge":True,"boundaries":{"automatic_data_transformation":False,"automatic_domain_inference":False,"automatic_scale_inference":False,"automatic_scientific_encoding_changes":False,"automatic_evidence_weighting":False,"automatic_claim_inference":False,"scientific_validity_certified":False,"automatic_core_submission":False}}

def health() -> dict[str,Any]:
    return {"ok":True,"status":"scientific-figure-intelligence-automatic-layout-ready","version":VERSION,"engine_version":ENGINE_VERSION,"layout_mode_count":len(LAYOUT_MODES),"legend_position_count":len(LEGEND_POSITIONS),"label_strategy_count":len(LABEL_STRATEGIES),"collision_policy_count":len(COLLISION_POLICIES),"automatic_scientific_encoding_changes":False,"automatic_core_submission":False,"scientific_validity_certified":False}
