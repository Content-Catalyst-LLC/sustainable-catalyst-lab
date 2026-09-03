from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any

VERSION = "0.82.0"
ENGINE_VERSION = "2.9.0"
RENDERER_OVERLAY = "uncertainty-distribution"
UNCERTAINTY_SCHEMA = "sc-lab-uncertainty-series/0.82.0"
DISTRIBUTION_SCHEMA = "sc-lab-empirical-distribution/0.82.0"
ENSEMBLE_SCHEMA = "sc-lab-ensemble-visualization/0.82.0"
LAYER_SCHEMA = "sc-lab-uncertainty-layer/0.82.0"
FIGURE_SCHEMA = "sc-lab-uncertainty-figure/0.82.0"
WORKSPACE_SCHEMA = "sc-lab-figure-workspace/0.82.0"
MAX_RECORDS = 100_000
MAX_SAMPLES = 250_000
MAX_ENSEMBLE_MEMBERS = 2_000
MAX_STATES_PER_MEMBER = 20_000
MAX_LAYERS = 64
MAX_HISTOGRAM_BINS = 512

class UncertaintyVisualizationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _hash(value: Any) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
    return sha256(payload.encode("utf-8")).hexdigest()

def _finite(value: Any, label: str) -> float:
    try: out=float(value)
    except (TypeError,ValueError): raise UncertaintyVisualizationError(f"{label} must be numeric")
    if not math.isfinite(out): raise UncertaintyVisualizationError(f"{label} must be finite")
    return out

def _identifier(value: Any, fallback: str) -> str:
    text=str(value or fallback).strip()
    if not text: raise UncertaintyVisualizationError("identifier must not be empty")
    return text[:160]

def _level(value: Any, label: str="level") -> float:
    out=_finite(value,label)
    if not 0 < out < 1: raise UncertaintyVisualizationError(f"{label} must be between 0 and 1")
    return out

def _quantile(sorted_samples:list[float], q:float)->float:
    if not sorted_samples: raise UncertaintyVisualizationError("samples must not be empty")
    if len(sorted_samples)==1: return sorted_samples[0]
    pos=(len(sorted_samples)-1)*q; lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi:return sorted_samples[lo]
    f=pos-lo; return sorted_samples[lo]*(1-f)+sorted_samples[hi]*f

def normalize_uncertainty(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise UncertaintyVisualizationError("uncertainty series must be an object")
    kind=str(payload.get("type") or "interval").strip().lower()
    if kind not in {"interval","quantile-ribbon"}: raise UncertaintyVisualizationError("unsupported uncertainty series type")
    semantics=str(payload.get("semantics") or "custom").strip().lower()
    if semantics not in {"confidence","credible","prediction","bootstrap","custom"}: raise UncertaintyVisualizationError("unsupported uncertainty semantics")
    level=payload.get("level")
    if semantics in {"confidence","credible","prediction"} and level is None:
        raise UncertaintyVisualizationError(f"{semantics} interval requires an explicit level")
    level=_level(level) if level is not None else None
    records=payload.get("records") or []
    if not isinstance(records,list) or not records: raise UncertaintyVisualizationError("records must be a non-empty array")
    if len(records)>MAX_RECORDS: raise UncertaintyVisualizationError(f"records exceed {MAX_RECORDS}",413)
    out_records=[]
    quantile_levels=[]
    if kind=="interval":
        for i,r in enumerate(records):
            if not isinstance(r,dict): raise UncertaintyVisualizationError(f"records[{i}] must be an object")
            x=deepcopy(r.get("x",i)); lower=_finite(r.get("lower"),f"records[{i}].lower"); upper=_finite(r.get("upper"),f"records[{i}].upper")
            if lower>upper: raise UncertaintyVisualizationError(f"records[{i}] lower exceeds upper")
            center=r.get("center"); center=_finite(center,f"records[{i}].center") if center is not None else None
            if center is not None and not lower<=center<=upper: raise UncertaintyVisualizationError(f"records[{i}] center must lie within interval")
            out_records.append({"x":x,"center":center,"lower":lower,"upper":upper,"sourceIndex":i})
    else:
        raw_levels=payload.get("quantileLevels") or []
        if not isinstance(raw_levels,list) or len(raw_levels)<2: raise UncertaintyVisualizationError("quantile-ribbon requires at least two quantileLevels")
        quantile_levels=[_level(q,f"quantileLevels[{i}]") for i,q in enumerate(raw_levels)]
        if quantile_levels!=sorted(set(quantile_levels)): raise UncertaintyVisualizationError("quantileLevels must be unique and strictly ascending")
        for i,r in enumerate(records):
            if not isinstance(r,dict): raise UncertaintyVisualizationError(f"records[{i}] must be an object")
            vals=r.get("values")
            if not isinstance(vals,list) or len(vals)!=len(quantile_levels): raise UncertaintyVisualizationError(f"records[{i}].values must match quantileLevels")
            vals=[_finite(v,f"records[{i}].values[{j}]") for j,v in enumerate(vals)]
            if vals!=sorted(vals): raise UncertaintyVisualizationError(f"records[{i}] quantile values must be non-decreasing")
            out_records.append({"x":deepcopy(r.get("x",i)),"values":vals,"sourceIndex":i})
    out={"schema":UNCERTAINTY_SCHEMA,"version":VERSION,"id":_identifier(payload.get("id"),"uncertainty-series"),"type":kind,"semantics":semantics,"level":level,"quantileLevels":quantile_levels,"records":out_records,"recordCount":len(out_records),"units":str(payload.get("units") or "unitless")[:80],"provenance":deepcopy(payload.get("provenance") or {}),"scientificRole":"uncertainty-visualization","isObservation":False,"boundaries":{"automaticUncertaintyInference":False,"automaticIntervalConversion":False,"automaticDistributionAssumption":False,"syntheticSamples":False}}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"}); return out

def normalize_distribution(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise UncertaintyVisualizationError("distribution must be an object")
    samples=payload.get("samples") or []
    if not isinstance(samples,list) or not samples: raise UncertaintyVisualizationError("samples must be a non-empty array")
    if len(samples)>MAX_SAMPLES: raise UncertaintyVisualizationError(f"samples exceed {MAX_SAMPLES}",413)
    samples=[_finite(v,f"samples[{i}]") for i,v in enumerate(samples)]
    semantics=str(payload.get("semantics") or "custom").strip().lower()
    if semantics not in {"observed","bootstrap","posterior","ensemble","residual","custom"}: raise UncertaintyVisualizationError("unsupported distribution semantics")
    bins=int(payload.get("bins",20))
    if not 2<=bins<=MAX_HISTOGRAM_BINS: raise UncertaintyVisualizationError(f"bins must be between 2 and {MAX_HISTOGRAM_BINS}")
    ordered=sorted(samples); lo=ordered[0]; hi=ordered[-1]
    if lo==hi:
        edges=[lo-0.5+(i/bins) for i in range(bins+1)]
    else:
        width=(hi-lo)/bins; edges=[lo+i*width for i in range(bins+1)]
    counts=[0]*bins
    for v in samples:
        idx=bins-1 if v==edges[-1] else int((v-edges[0])/(edges[-1]-edges[0])*bins)
        idx=max(0,min(bins-1,idx)); counts[idx]+=1
    histogram=[{"lower":edges[i],"upper":edges[i+1],"count":counts[i]} for i in range(bins)]
    ecdf=[{"value":v,"p":(i+1)/len(ordered)} for i,v in enumerate(ordered)]
    qs=[0.05,0.25,0.5,0.75,0.95]; qvals={f"{q:.2f}":_quantile(ordered,q) for q in qs}
    out={"schema":DISTRIBUTION_SCHEMA,"version":VERSION,"id":_identifier(payload.get("id"),"empirical-distribution"),"semantics":semantics,"sampleCount":len(samples),"samples":samples,"histogram":{"method":"explicit-fixed-bin-count","bins":bins,"cells":histogram},"ecdf":{"method":"empirical-cdf","points":ecdf},"quantiles":{"method":"linear-order-statistic-interpolation","values":qvals},"boxSummary":{"min":ordered[0],"q1":qvals['0.25'],"median":qvals['0.50'],"q3":qvals['0.75'],"max":ordered[-1]},"units":str(payload.get("units") or "unitless")[:80],"provenance":deepcopy(payload.get("provenance") or {}),"scientificRole":"empirical-distribution-visualization","isObservation":False,"boundaries":{"automaticDistributionAssumption":False,"automaticParametricFit":False,"automaticKDE":False,"syntheticSamples":False,"automaticUncertaintyInference":False}}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"}); return out

def normalize_ensemble(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise UncertaintyVisualizationError("ensemble must be an object")
    members=payload.get("members") or []
    if not isinstance(members,list) or not members: raise UncertaintyVisualizationError("members must be a non-empty array")
    if len(members)>MAX_ENSEMBLE_MEMBERS: raise UncertaintyVisualizationError(f"members exceed {MAX_ENSEMBLE_MEMBERS}",413)
    out_members=[]; reference_x=None
    for mi,m in enumerate(members):
        if not isinstance(m,dict): raise UncertaintyVisualizationError(f"members[{mi}] must be an object")
        states=m.get("states") or []
        if not isinstance(states,list) or not states: raise UncertaintyVisualizationError(f"members[{mi}].states must be non-empty")
        if len(states)>MAX_STATES_PER_MEMBER: raise UncertaintyVisualizationError(f"members[{mi}] states exceed {MAX_STATES_PER_MEMBER}",413)
        norm=[]
        for si,s in enumerate(states):
            if not isinstance(s,dict): raise UncertaintyVisualizationError(f"members[{mi}].states[{si}] must be an object")
            norm.append({"x":deepcopy(s.get("x",si)),"y":_finite(s.get("y"),f"members[{mi}].states[{si}].y"),"sourceIndex":si})
        out_members.append({"id":_identifier(m.get("id"),f"member-{mi+1}"),"states":norm,"stateCount":len(norm),"provenance":deepcopy(m.get("provenance") or {})})
    envelope=None
    if payload.get("deriveEnvelope") is True:
        raw_q=payload.get("quantiles")
        if not isinstance(raw_q,list) or len(raw_q)<2: raise UncertaintyVisualizationError("deriveEnvelope requires explicit quantiles")
        qs=[_level(q,f"quantiles[{i}]") for i,q in enumerate(raw_q)]
        if qs!=sorted(set(qs)): raise UncertaintyVisualizationError("ensemble quantiles must be unique and ascending")
        reference_x=[s["x"] for s in out_members[0]["states"]]
        for i,m in enumerate(out_members[1:],1):
            if [s["x"] for s in m["states"]] != reference_x:
                raise UncertaintyVisualizationError("ensemble envelope requires exact shared state coordinates; v0.82 does not interpolate member states")
        records=[]
        for idx,x in enumerate(reference_x):
            vals=sorted(m["states"][idx]["y"] for m in out_members)
            records.append({"x":deepcopy(x),"values":[_quantile(vals,q) for q in qs]})
        envelope={"quantileLevels":qs,"records":records,"method":"empirical-across-exactly-aligned-members"}
    out={"schema":ENSEMBLE_SCHEMA,"version":VERSION,"id":_identifier(payload.get("id"),"ensemble-visualization"),"members":out_members,"memberCount":len(out_members),"envelope":envelope,"units":str(payload.get("units") or "unitless")[:80],"provenance":deepcopy(payload.get("provenance") or {}),"scientificRole":"ensemble-visualization","isObservation":False,"boundaries":{"automaticEnsembleAlignment":False,"temporalInterpolation":False,"spatialInterpolation":False,"syntheticMembers":False,"forecasting":False,"automaticUncertaintyInference":False}}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"}); return out

def normalize_layer(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict): raise UncertaintyVisualizationError("uncertainty layer must be an object")
    us=[normalize_uncertainty(v) for v in (payload.get("uncertaintySeries") or [])]
    ds=[normalize_distribution(v) for v in (payload.get("distributions") or [])]
    es=[normalize_ensemble(v) for v in (payload.get("ensembles") or [])]
    if not (us or ds or es): raise UncertaintyVisualizationError("layer requires uncertaintySeries, distributions, or ensembles")
    if len(us)+len(ds)+len(es)>MAX_LAYERS: raise UncertaintyVisualizationError(f"layer content exceeds {MAX_LAYERS}",413)
    out={"schema":LAYER_SCHEMA,"version":VERSION,"id":_identifier(payload.get("id"),"uncertainty-layer"),"title":str(payload.get("title") or "Uncertainty / ensemble / distribution")[:240],"visible":payload.get("visible") is not False,"uncertaintySeries":us,"distributions":ds,"ensembles":es,"provenance":deepcopy(payload.get("provenance") or {}),"scientificRole":"uncertainty-visualization-layer","isObservation":False,"boundaries":{"automaticUncertaintyInference":False,"automaticDistributionAssumption":False,"automaticEnsembleAlignment":False}}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"}); return out

def attach_uncertainty(payload:dict[str,Any])->dict[str,Any]:
    if not isinstance(payload,dict) or not isinstance(payload.get("baseFigure"),dict): raise UncertaintyVisualizationError("baseFigure is required")
    raw=payload.get("uncertaintyLayers") or payload.get("layers") or []
    if not isinstance(raw,list) or not raw: raise UncertaintyVisualizationError("at least one uncertainty layer is required")
    layers=[normalize_layer(v) for v in raw]
    base=deepcopy(payload["baseFigure"])
    out={"schema":FIGURE_SCHEMA,"version":VERSION,"engineVersion":ENGINE_VERSION,"rendererOverlay":RENDERER_OVERLAY,"id":_identifier(payload.get("id"),"uncertainty-figure"),"title":str(payload.get("title") or base.get("title") or "Scientific uncertainty figure")[:240],"baseFigure":base,"baseFigureFingerprint":str(base.get("fingerprint") or _hash(base)),"baseRenderer":base.get("renderer"),"uncertaintyLayers":layers,"uncertaintyLayerCount":len(layers),"provenance":deepcopy(payload.get("provenance") or {}),"boundaries":{"baseFigureMutation":False,"automaticUncertaintyInference":False,"automaticDistributionAssumption":False,"automaticIntervalConversion":False,"automaticEnsembleAlignment":False,"syntheticSamples":False,"forecasting":False}}
    out["fingerprint"]=_hash({k:v for k,v in out.items() if k!="fingerprint"}); return out

def build_workspace(payload:dict[str,Any])->dict[str,Any]:
    figures=[]
    for i,item in enumerate(payload.get("figures") or []):
        if isinstance(item,dict) and item.get("uncertaintyLayers"): figures.append(attach_uncertainty(item))
        elif isinstance(item,dict): figures.append(deepcopy(item))
        else: raise UncertaintyVisualizationError(f"figures[{i}] must be an object")
    workspace={"schema":WORKSPACE_SCHEMA,"version":VERSION,"engineVersion":ENGINE_VERSION,"id":_identifier(payload.get("id"),"figure-workspace"),"title":str(payload.get("title") or "Uncertainty visualization workspace")[:240],"figures":figures,"figureCount":len(figures),"provenance":deepcopy(payload.get("provenance") or {}),"compatibility":{"v0810Markup":True,"v0800Spatial":True,"v0790LinkedViews":True,"v0780TimeParameter":True,"v0770Scene":True,"v0760Adaptive":True,"v0750DataBinding":True}}
    workspace["fingerprint"]=_hash({k:v for k,v in workspace.items() if k!="fingerprint"}); return {"ok":True,"workspace":workspace}

def health()->dict[str,Any]:
    return {"ok":True,"status":"uncertainty-ensemble-distribution-ready","version":VERSION,"engineVersion":ENGINE_VERSION,"rendererOverlay":RENDERER_OVERLAY,"intervalBands":True,"confidenceIntervals":True,"credibleIntervals":True,"predictionIntervals":True,"quantileRibbons":True,"empiricalHistogram":True,"ecdf":True,"boxSummary":True,"posteriorSamples":True,"ensembleTrajectories":True,"ensembleEnvelopes":True,"uncertaintyProvenance":True,"baseFigurePreservation":True,"v0810MarkupCompatibility":True,"v0800SpatialCompatibility":True,"v0790LinkedViewsCompatibility":True,"v0780TimeParameterCompatibility":True,"v0770SceneCompatibility":True,"v0760AdaptiveCompatibility":True,"v0750DataBindingCompatibility":True,"automaticUncertaintyInference":False,"automaticDistributionAssumption":False,"automaticParametricFit":False,"automaticKDE":False,"automaticIntervalConversion":False,"automaticEnsembleAlignment":False,"temporalInterpolation":False,"spatialInterpolation":False,"syntheticSamples":False,"forecasting":False,"arbitraryCode":False,"limits":{"records":MAX_RECORDS,"samples":MAX_SAMPLES,"ensembleMembers":MAX_ENSEMBLE_MEMBERS,"statesPerMember":MAX_STATES_PER_MEMBER,"layers":MAX_LAYERS,"histogramBins":MAX_HISTOGRAM_BINS}}

def policies()->dict[str,Any]: return health()
