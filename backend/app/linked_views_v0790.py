from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

VERSION = "0.79.0"
ENGINE_VERSION = "2.6.0"
COMPOSITION_SCHEMA = "sc-lab-linked-figure-composition/0.79.0"
VIEW_SCHEMA = "sc-lab-linked-view/0.79.0"
FACET_SCHEMA = "sc-lab-facet-spec/0.79.0"
LINK_SCHEMA = "sc-lab-view-link/0.79.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.79.0"
MAX_VIEWS = 24
MAX_FACETS = 64
MAX_LINKS = 128
MAX_ROWS = 250000

class LinkedViewsError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _hash(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()).hexdigest()

def _id(value: Any, fallback: str) -> str:
    s=str(value or fallback).strip()
    if not s: raise LinkedViewsError("identifier must not be empty")
    return s[:120]

def _renderer(value: Any) -> str:
    v=str(value or "svg2d")
    if v not in {"svg2d","canvas3d","canvas4d"}: raise LinkedViewsError("renderer must be svg2d, canvas3d, or canvas4d")
    return v

def normalize_view(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict): raise LinkedViewsError("view must be an object")
    out={
      "schema": VIEW_SCHEMA,
      "version": VERSION,
      "engineVersion": ENGINE_VERSION,
      "id": _id(payload.get("id"), "view"),
      "title": str(payload.get("title") or "Scientific view")[:240],
      "renderer": _renderer(payload.get("renderer")),
      "figureKind": str(payload.get("figureKind") or payload.get("kind") or "scatter")[:80],
      "datasetId": str(payload.get("datasetId") or "")[:160] or None,
      "binding": deepcopy(payload.get("binding") or {}),
      "stateAxis": deepcopy(payload.get("stateAxis") or {}),
      "provenance": deepcopy(payload.get("provenance") or {}),
    }
    if "rowIndexes" in payload:
      rows=payload.get("rowIndexes") or []
      if not isinstance(rows,list): raise LinkedViewsError("rowIndexes must be an array")
      out["rowIndexes"]=sorted({int(i) for i in rows if int(i)>=0})
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"})
    return out

def normalize_link(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict): raise LinkedViewsError("link must be an object")
    channel=str(payload.get("channel") or "selection")
    if channel not in {"selection","filter","state-axis"}: raise LinkedViewsError("link channel must be selection, filter, or state-axis")
    source=_id(payload.get("sourceViewId"), "")
    targets=payload.get("targetViewIds") or []
    if isinstance(targets,str): targets=[targets]
    if not isinstance(targets,list) or not targets: raise LinkedViewsError("targetViewIds must contain at least one view")
    targets=[_id(v,"") for v in targets if str(v).strip()]
    key=str(payload.get("key") or "").strip()
    if channel in {"selection","filter"} and not key: raise LinkedViewsError("selection/filter links require an explicit key")
    out={"schema":LINK_SCHEMA,"version":VERSION,"sourceViewId":source,"targetViewIds":targets,"channel":channel,"key":key or None,"enabled":bool(payload.get("enabled",True)),"direction":str(payload.get("direction") or "forward")}
    if out["direction"] not in {"forward","bidirectional"}: raise LinkedViewsError("direction must be forward or bidirectional")
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"})
    return out

def normalize_facet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise LinkedViewsError("facet spec must be an object")
    field=str(payload.get("field") or "").strip()
    if not field: raise LinkedViewsError("facet field is required")
    order=str(payload.get("order") or "ascending")
    if order not in {"ascending","descending","source"}: raise LinkedViewsError("facet order must be ascending, descending, or source")
    columns=max(1,min(8,int(payload.get("columns") or 3)))
    limit=max(1,min(MAX_FACETS,int(payload.get("limit") or 24)))
    out={"schema":FACET_SCHEMA,"version":VERSION,"field":field,"order":order,"columns":columns,"limit":limit,"includeMissing":bool(payload.get("includeMissing",False)),"shareX":bool(payload.get("shareX",True)),"shareY":bool(payload.get("shareY",True))}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"})
    return out

def facet_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    dataset=payload.get("dataset") or {}; rows=dataset.get("rows") or []
    if not isinstance(rows,list): raise LinkedViewsError("dataset.rows must be an array")
    if len(rows)>MAX_ROWS: raise LinkedViewsError(f"dataset exceeds {MAX_ROWS} rows",413)
    facet=normalize_facet(payload.get("facet") or payload.get("facetSpec") or {})
    groups={}; encounter=[]
    for idx,row in enumerate(rows):
      if not isinstance(row,dict): continue
      value=row.get(facet["field"])
      if value is None and not facet["includeMissing"]: continue
      key="__missing__" if value is None else str(value)
      if key not in groups: groups[key]=[]; encounter.append(key)
      groups[key].append(idx)
    keys=encounter
    if facet["order"]!="source": keys=sorted(keys, reverse=facet["order"]=="descending")
    truncated=len(keys)>facet["limit"]; keys=keys[:facet["limit"]]
    facets=[{"id":f"facet-{i+1}","value":None if k=="__missing__" else k,"label":"Missing" if k=="__missing__" else k,"rowIndexes":groups[k],"rowCount":len(groups[k])} for i,k in enumerate(keys)]
    return {"ok":True,"version":VERSION,"facet":facet,"datasetId":dataset.get("id"),"sourceRowCount":len(rows),"facetCount":len(facets),"truncated":truncated,"facets":facets,"sourceFingerprint":dataset.get("fingerprint") or _hash(rows),"fingerprint":_hash({"facet":facet,"facets":facets})}

def normalize_composition(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise LinkedViewsError("composition must be an object")
    raw_views=payload.get("views") or []
    if not isinstance(raw_views,list) or not raw_views: raise LinkedViewsError("composition requires at least one view")
    if len(raw_views)>MAX_VIEWS: raise LinkedViewsError(f"composition supports at most {MAX_VIEWS} views")
    views=[normalize_view(v) for v in raw_views]
    ids=[v["id"] for v in views]
    if len(ids)!=len(set(ids)): raise LinkedViewsError("view ids must be unique")
    raw_links=payload.get("links") or []
    if not isinstance(raw_links,list) or len(raw_links)>MAX_LINKS: raise LinkedViewsError(f"composition supports at most {MAX_LINKS} links")
    links=[normalize_link(v) for v in raw_links]
    known=set(ids)
    for link in links:
      if link["sourceViewId"] not in known or any(t not in known for t in link["targetViewIds"]): raise LinkedViewsError("link references an unknown view")
    layout=deepcopy(payload.get("layout") or {})
    layout_type=str(layout.get("type") or "grid")
    if layout_type not in {"grid","rows","columns","freeform"}: raise LinkedViewsError("layout type must be grid, rows, columns, or freeform")
    layout={"type":layout_type,"columns":max(1,min(8,int(layout.get("columns") or min(3,len(views))))),"gap":str(layout.get("gap") or "normal")}
    out={"schema":COMPOSITION_SCHEMA,"version":VERSION,"engineVersion":ENGINE_VERSION,"title":str(payload.get("title") or "Scientific figure composition")[:240],"views":views,"links":links,"layout":layout,"caption":str(payload.get("caption") or "")[:4000],"provenance":deepcopy(payload.get("provenance") or {}),"boundaries":{"automaticLinkInference":False,"crossDatasetJoin":False,"statisticalCouplingInference":False,"dataDuplicationRequired":False,"syntheticPanels":False,"arbitraryCode":False}}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"})
    return out

def apply_link_event(payload: dict[str, Any]) -> dict[str, Any]:
    comp=normalize_composition(payload.get("composition") or {})
    event=payload.get("event") or {}; source=_id(event.get("sourceViewId"),"")
    channel=str(event.get("channel") or "selection")
    if channel not in {"selection","filter","state-axis"}: raise LinkedViewsError("unsupported event channel")
    if source not in {v["id"] for v in comp["views"]}: raise LinkedViewsError("event source view is unknown")
    value=deepcopy(event.get("value"))
    updates=[]
    for link in comp["links"]:
      if not link["enabled"] or link["channel"]!=channel: continue
      targets=[]
      if source==link["sourceViewId"]: targets=link["targetViewIds"]
      elif link["direction"]=="bidirectional" and source in link["targetViewIds"]: targets=[link["sourceViewId"]]+[t for t in link["targetViewIds"] if t!=source]
      for target in targets: updates.append({"viewId":target,"channel":channel,"key":link.get("key"),"value":value,"linkFingerprint":link["fingerprint"]})
    return {"ok":True,"version":VERSION,"sourceViewId":source,"channel":channel,"updates":updates,"propagationCount":len(updates),"eventFingerprint":_hash({"source":source,"channel":channel,"value":value,"updates":updates})}

def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    composition=normalize_composition(payload.get("composition") or payload)
    facet=None
    if payload.get("facet") and payload.get("dataset"): facet=facet_dataset({"facet":payload["facet"],"dataset":payload["dataset"]})
    out={"schema":WORKSPACE_SCHEMA,"version":VERSION,"engineVersion":ENGINE_VERSION,"composition":composition,"facetResult":facet,"controls":{"linkedSelection":True,"linkedFiltering":True,"linkedStateAxis":True,"faceting":True,"mixedRendererComposition":True},"provenance":deepcopy(payload.get("provenance") or {})}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"})
    return {"ok":True,"workspace":out}

def health() -> dict[str, Any]:
    return {"ok":True,"status":"linked-views-faceting-composition-ready","version":VERSION,"engineVersion":ENGINE_VERSION,"linkedViews":True,"linkedSelection":True,"linkedFiltering":True,"linkedStateAxis":True,"faceting":True,"mixedRendererComposition":True,"rendererRegistry":["svg2d","canvas3d","canvas4d"],"v0780TimeParameterCompatibility":True,"v0770SceneCompatibility":True,"v0760AdaptiveCompatibility":True,"v0750DataBindingCompatibility":True,"automaticLinkInference":False,"crossDatasetJoin":False,"statisticalCouplingInference":False,"syntheticPanels":False,"arbitraryCode":False,"limits":{"views":MAX_VIEWS,"facets":MAX_FACETS,"links":MAX_LINKS,"sourceRows":MAX_ROWS}}

def policies() -> dict[str, Any]: return health()
