from __future__ import annotations
import copy, hashlib, json, math
from datetime import datetime, timezone
from typing import Any

VERSION="0.141.2"
PREDECESSOR_VERSION="0.141.1"
ML_WORKSPACE_VERSION="0.141.0"
RESEARCH_OS_VERSION="0.140.0"
INTEGRITY_BASELINE="0.140.0.1"
SCHEMA="sc-lab-training-curves-metrics-checkpoint-visualization/0.141.2"
VISUAL_SPEC_SCHEMA="sc-lab-neural-training-visual-spec/0.141.2"
SNAPSHOT_SCHEMA="sc-lab-training-visualization-snapshot/0.141.2"
CORE_HANDOFF_SCHEMA="sc-core-visual-research-object-handoff/1.0"

BOUNDARY=(
    "Workspace is the execution authority and source of observed training telemetry. Lab normalizes, visualizes, compares, "
    "and annotates that telemetry without changing it. Smoothing is a derived visual transform, convergence diagnostics are "
    "descriptive heuristics, checkpoint extrema are candidates rather than endorsed models, and model metrics are not evidence."
)

DISPLAY_TYPES=("line","multi-line","small-multiples","checkpoint-timeline","metric-table","run-overlay")
SMOOTHING_METHODS=("none","moving-average","ema")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=4096): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _get(o,*names,default=None):
    if not isinstance(o,dict): return default
    for n in names:
        if n in o and o[n] is not None: return o[n]
    return default

def _num(v):
    if isinstance(v,bool): return None
    if isinstance(v,(int,float)) and math.isfinite(float(v)): return float(v)
    try:
        x=float(v); return x if math.isfinite(x) else None
    except Exception: return None

def _step(v, fallback):
    x=_num(v)
    return x if x is not None else float(fallback)

def normalize_metric(item:Any,index:int,run_id=""):
    raw=item if isinstance(item,dict) else {"value":item}
    name=_txt(_get(raw,"name","metric","metricName"),256) or "metric"
    split=_txt(_get(raw,"split","partition","datasetSplit"),128) or "unspecified"
    step=_step(_get(raw,"step","epoch","globalStep","global_step"),index)
    value=_num(raw.get("value"))
    return {
        "metricId":_txt(_get(raw,"metricId","metric_id","id"),256) or f"metric-{index+1}",
        "runId":_txt(_get(raw,"runId","run_id"),512) or run_id,
        "name":name,"split":split,"step":step,"value":value,
        "unit":_txt(raw.get("unit"),64),
        "higherIsBetterDeclared":_get(raw,"higherIsBetter","higher_is_better"),
        "wallTimeSeconds":_num(_get(raw,"wallTimeSeconds","wall_time_seconds","elapsedSeconds")),
        "source":_dict(raw.get("source")),"provenance":_dict(raw.get("provenance")),
    }

def normalize_checkpoint(item:Any,index:int,run_id=""):
    raw=item if isinstance(item,dict) else {"checkpointRef":item}
    return {
        "checkpointId":_txt(_get(raw,"checkpointId","checkpoint_id","id"),512) or f"checkpoint-{index+1}",
        "checkpointRef":_txt(_get(raw,"checkpointRef","ref","artifactRef"),1024),
        "runId":_txt(_get(raw,"runId","run_id"),512) or run_id,
        "step":_step(_get(raw,"step","epoch","globalStep","global_step"),index),
        "artifactHash":_txt(_get(raw,"artifactHash","sha256","hash"),256),
        "metrics":_dict(raw.get("metrics")),"metadata":_dict(raw.get("metadata")),
        "promotedToEvidence":False,"endorsedModel":False,
    }

def normalize_run(item:Any,index:int):
    raw=item if isinstance(item,dict) else {"runId":item}
    rid=_txt(_get(raw,"runId","run_id","id"),512) or f"run-{index+1}"
    metrics=[normalize_metric(x,i,rid) for i,x in enumerate(_list(raw.get("metrics")))]
    cps=[normalize_checkpoint(x,i,rid) for i,x in enumerate(_list(raw.get("checkpoints")))]
    return {"runId":rid,"state":_txt(_get(raw,"state","status"),128) or "unknown","metrics":metrics,"checkpoints":cps,
            "environment":_dict(raw.get("environment")),"provenance":_dict(raw.get("provenance"))}

def normalize(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    exp_id=_txt(_get(root,"experimentId","experiment_id"),512)
    source=_dict(_get(root,"workspaceResult","workspace_result","result",default=root))
    runs=[normalize_run(x,i) for i,x in enumerate(_list(source.get("runs")))]
    if not runs:
        rid=_txt(_get(source,"runId","run_id","id"),512) or _txt(_get(root,"runId","run_id"),512) or "run-1"
        runs=[{"runId":rid,"state":_txt(_get(source,"state","status"),128) or "unknown",
               "metrics":[normalize_metric(x,i,rid) for i,x in enumerate(_list(source.get("metrics")))],
               "checkpoints":[normalize_checkpoint(x,i,rid) for i,x in enumerate(_list(source.get("checkpoints")))],
               "environment":_dict(source.get("environment")),"provenance":_dict(source.get("provenance"))}]
    record={"schema":SCHEMA,"version":VERSION,"recordType":"training-telemetry-visualization-source","experimentId":exp_id,
            "runs":runs,"workspaceExecutionAuthority":True,"labMutatesTelemetry":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
    record["fingerprint"]=_fp({k:v for k,v in record.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"record":record,"boundary":BOUNDARY}

def metric_catalog(payload):
    rec=normalize(payload)["record"]; seen={}
    for run in rec["runs"]:
        for m in run["metrics"]:
            k=(m["name"],m["split"],m["unit"])
            seen.setdefault(k,{"name":m["name"],"split":m["split"],"unit":m["unit"],"pointCount":0,"runIds":set()})
            seen[k]["pointCount"]+=1; seen[k]["runIds"].add(run["runId"])
    rows=[]
    for v in seen.values(): v["runIds"]=sorted(v["runIds"]); rows.append(v)
    return {"ok":True,"version":VERSION,"metrics":sorted(rows,key=lambda x:(x["name"],x["split"])),"boundary":BOUNDARY}

def metric_series(payload):
    root=payload if isinstance(payload,dict) else {}; rec=normalize(root)["record"]
    want_name=_txt(_get(root,"name","metric","metricName"),256); want_split=_txt(root.get("split"),128); want_run=_txt(_get(root,"runId","run_id"),512)
    rows=[]
    for run in rec["runs"]:
        if want_run and run["runId"]!=want_run: continue
        for m in run["metrics"]:
            if want_name and m["name"]!=want_name: continue
            if want_split and m["split"]!=want_split: continue
            rows.append(m)
    rows.sort(key=lambda x:(x["runId"],x["step"],x["name"],x["split"]))
    return {"ok":True,"version":VERSION,"points":rows,"count":len(rows),"telemetryMutated":False,"boundary":BOUNDARY}

def smooth_series(payload):
    root=payload if isinstance(payload,dict) else {}; base=metric_series(root); pts=base["points"]
    method=_txt(root.get("method"),64) or "none"; window=int(_get(root,"window",default=5) or 5); alpha=float(_get(root,"alpha",default=0.2) or 0.2)
    if method not in SMOOTHING_METHODS: return {"ok":False,"version":VERSION,"error":"unsupported smoothing method","boundary":BOUNDARY}
    groups={}
    for p in pts: groups.setdefault((p["runId"],p["name"],p["split"]),[]).append(p)
    out=[]
    for key,arr in groups.items():
        vals=[]; ema=None
        for p in arr:
            val=p["value"]
            if val is None: derived=None
            elif method=="none": derived=val
            elif method=="moving-average":
                vals.append(val); derived=sum(vals[-max(1,window):])/len(vals[-max(1,window):])
            else:
                ema=val if ema is None else alpha*val+(1-alpha)*ema; derived=ema
            out.append({**p,"displayValue":derived,"rawValue":val,"derivedVisualization":method!="none","transform":{"method":method,"window":window if method=="moving-average" else None,"alpha":alpha if method=="ema" else None}})
    return {"ok":True,"version":VERSION,"points":out,"method":method,"rawTelemetryPreserved":True,"derivedVisualization":method!="none","boundary":BOUNDARY}

def training_curve_spec(payload):
    root=payload if isinstance(payload,dict) else {}; data=smooth_series(root)
    if not data.get("ok"): return data
    groups={}
    for p in data["points"]:
        key=(p["runId"],p["name"],p["split"]); groups.setdefault(key,[]).append({"step":p["step"],"value":p["displayValue"],"rawValue":p["rawValue"]})
    series=[{"seriesId":f"{r}:{n}:{s}","runId":r,"metric":n,"split":s,"points":pts} for (r,n,s),pts in sorted(groups.items())]
    spec={"schema":VISUAL_SPEC_SCHEMA,"visualType":"training-curves","x":"step","series":series,"smoothing":data["method"],"sourceFingerprint":normalize(root)["record"]["fingerprint"],"automaticInterpretation":False}
    spec["fingerprint"]=_fp(spec)
    return {"ok":True,"version":VERSION,"visualSpec":spec,"boundary":BOUNDARY}

def metric_summary(payload):
    pts=metric_series(payload)["points"]; vals=[p["value"] for p in pts if p["value"] is not None]
    return {"ok":True,"version":VERSION,"count":len(pts),"numericCount":len(vals),"first":vals[0] if vals else None,"last":vals[-1] if vals else None,
            "min":min(vals) if vals else None,"max":max(vals) if vals else None,"range":(max(vals)-min(vals)) if vals else None,"automaticQualityVerdict":False,"boundary":BOUNDARY}

def train_validation_gap(payload):
    root=payload if isinstance(payload,dict) else {}; metric=_txt(_get(root,"name","metric"),256); run=_txt(_get(root,"runId","run_id"),512)
    rec=normalize(root)["record"]; g={}
    for r in rec["runs"]:
        if run and r["runId"]!=run: continue
        for m in r["metrics"]:
            if metric and m["name"]!=metric: continue
            if m["split"] in ("train","training","val","validation") and m["value"] is not None:
                g.setdefault((r["runId"],m["step"]),{})["train" if m["split"] in ("train","training") else "validation"]=m["value"]
    rows=[]
    for (rid,step),d in sorted(g.items()):
        rows.append({"runId":rid,"step":step,"train":d.get("train"),"validation":d.get("validation"),"gap":(d["validation"]-d["train"]) if "train" in d and "validation" in d else None})
    return {"ok":True,"version":VERSION,"metric":metric,"points":rows,"overfittingInferred":False,"boundary":BOUNDARY}

def checkpoint_timeline(payload):
    rec=normalize(payload)["record"]; rows=[]
    for run in rec["runs"]:
        for c in run["checkpoints"]: rows.append(c)
    rows.sort(key=lambda x:(x["runId"],x["step"],x["checkpointId"]))
    return {"ok":True,"version":VERSION,"checkpoints":rows,"count":len(rows),"automaticPromotion":False,"boundary":BOUNDARY}

def link_checkpoints_to_metric(payload):
    root=payload if isinstance(payload,dict) else {}; name=_txt(_get(root,"name","metric"),256); split=_txt(root.get("split"),128)
    rec=normalize(root)["record"]; rows=[]
    for run in rec["runs"]:
        metrics=[m for m in run["metrics"] if (not name or m["name"]==name) and (not split or m["split"]==split) and m["value"] is not None]
        by_step={m["step"]:m for m in metrics}
        for c in run["checkpoints"]:
            exact=by_step.get(c["step"])
            rows.append({"runId":run["runId"],"checkpointId":c["checkpointId"],"step":c["step"],"metric":exact,"exactStepMatch":exact is not None})
    return {"ok":True,"version":VERSION,"rows":rows,"automaticPromotion":False,"boundary":BOUNDARY}

def checkpoint_candidate(payload):
    root=payload if isinstance(payload,dict) else {}; name=_txt(_get(root,"name","metric"),256); split=_txt(root.get("split"),128); direction=_txt(root.get("direction"),32)
    series=metric_series({**root,"name":name,"split":split})["points"]; usable=[p for p in series if p["value"] is not None]
    if direction not in ("min","max"): return {"ok":False,"version":VERSION,"error":"direction must be explicitly declared as min or max","boundary":BOUNDARY}
    if not usable: return {"ok":True,"version":VERSION,"candidate":None,"automaticPromotion":False,"boundary":BOUNDARY}
    p=(min if direction=="min" else max)(usable,key=lambda x:x["value"])
    cps=checkpoint_timeline(root)["checkpoints"]; same=[c for c in cps if c["runId"]==p["runId"]]
    nearest=min(same,key=lambda c:abs(c["step"]-p["step"])) if same else None
    return {"ok":True,"version":VERSION,"objective":{"metric":name,"split":split,"direction":direction},"extremum":p,"candidateCheckpoint":nearest,
            "candidateOnly":True,"automaticPromotion":False,"scientificValidityCertified":False,"boundary":BOUNDARY}

def run_overlay(payload):
    spec=training_curve_spec(payload)
    if not spec.get("ok"): return spec
    spec["visualSpec"]["visualType"]="run-overlay"; spec["visualSpec"]["automaticWinnerSelection"]=False
    spec["visualSpec"]["fingerprint"]=_fp({k:v for k,v in spec["visualSpec"].items() if k!="fingerprint"})
    return spec

def small_multiples(payload):
    cat=metric_catalog(payload)["metrics"]; panels=[]
    for m in cat:
        panel=training_curve_spec({**(payload if isinstance(payload,dict) else {}),"name":m["name"],"split":m["split"]})["visualSpec"]
        panels.append({"metric":m["name"],"split":m["split"],"visualSpec":panel})
    return {"ok":True,"version":VERSION,"visualType":"small-multiples","panels":panels,"automaticRanking":False,"boundary":BOUNDARY}

def convergence_diagnostics(payload):
    root=payload if isinstance(payload,dict) else {}; pts=[p for p in metric_series(root)["points"] if p["value"] is not None]
    window=max(2,int(_get(root,"window",default=5) or 5)); threshold=float(_get(root,"threshold",default=1e-4) or 1e-4)
    groups={}
    for p in pts: groups.setdefault((p["runId"],p["name"],p["split"]),[]).append(p)
    rows=[]
    for (rid,name,split),arr in groups.items():
        tail=arr[-window:]; slope=None
        if len(tail)>=2:
            dx=tail[-1]["step"]-tail[0]["step"]; slope=(tail[-1]["value"]-tail[0]["value"])/dx if dx else 0.0
        rows.append({"runId":rid,"metric":name,"split":split,"window":len(tail),"tailSlope":slope,"plateauHeuristic":bool(slope is not None and abs(slope)<=threshold),"threshold":threshold})
    return {"ok":True,"version":VERSION,"diagnostics":rows,"descriptiveHeuristicOnly":True,"automaticEarlyStop":False,"convergenceCertified":False,"boundary":BOUNDARY}

def checkpoint_visual_spec(payload):
    rows=checkpoint_timeline(payload)["checkpoints"]
    spec={"schema":VISUAL_SPEC_SCHEMA,"visualType":"checkpoint-timeline","x":"step","checkpoints":rows,"automaticPromotion":False,"sourceFingerprint":normalize(payload)["record"]["fingerprint"]}
    spec["fingerprint"]=_fp(spec)
    return {"ok":True,"version":VERSION,"visualSpec":spec,"boundary":BOUNDARY}

def dashboard_spec(payload):
    spec={"schema":VISUAL_SPEC_SCHEMA,"visualType":"training-dashboard","curves":training_curve_spec(payload)["visualSpec"],"checkpoints":checkpoint_visual_spec(payload)["visualSpec"],
          "metricCatalog":metric_catalog(payload)["metrics"],"convergenceDiagnostics":convergence_diagnostics(payload)["diagnostics"],"automaticModelRanking":False,"automaticCheckpointPromotion":False}
    spec["fingerprint"]=_fp(spec)
    return {"ok":True,"version":VERSION,"dashboard":spec,"boundary":BOUNDARY}

def core_visual_handoff(payload):
    dash=dashboard_spec(payload)["dashboard"]
    packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"objectType":"NeuralTrainingVisualization","visualSpec":dash,"canonicalVisualObjectAuthority":"platform-core","labMayOverrideCoreSemantics":False}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def snapshot(payload):
    rec=normalize(payload)["record"]; content={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"source":rec,"dashboard":dashboard_spec(payload)["dashboard"]}; fp=_fp(content)
    return {"ok":True,"version":VERSION,"snapshot":{**content,"snapshotId":f"tcv-{fp[:24]}","fingerprint":fp},"generatedAt":_now(),"fingerprintExcludesGeneratedAt":True,"boundary":BOUNDARY}

def compare_snapshots(payload):
    root=payload if isinstance(payload,dict) else {}; l=_dict(root.get("left")); r=_dict(root.get("right"))
    def body(x):
        x=copy.deepcopy(x.get("snapshot") if isinstance(x.get("snapshot"),dict) else x)
        for k in ("snapshotId","fingerprint","generatedAt"): x.pop(k,None)
        return x
    a,b=body(l),body(r); keys=sorted(set(a)|set(b)); changes=[{"field":k,"left":a.get(k),"right":b.get(k)} for k in keys if a.get(k)!=b.get(k)]
    return {"ok":True,"version":VERSION,"equal":not changes,"changes":changes,"scientificSignificanceInferred":False,"boundary":BOUNDARY}

def reproducibility_packet(payload):
    snap=snapshot(payload)["snapshot"]; packet={"schema":"sc-lab-training-visualization-reproducibility-package/0.141.2","version":VERSION,"snapshot":snap,
        "requirements":["Workspace run identity","raw metric telemetry","checkpoint artifact lineage","architecture/training configuration fingerprints","visual transform parameters"]}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"package":packet,"reproducibilityCertified":False,"boundary":BOUNDARY}

def health(): return {"ok":True,"version":VERSION,"trainingCurvesMetricsCheckpointVisualization":True,"neuralArchitectureTrainingConfigurationVersion":PREDECESSOR_VERSION,"machineLearningExperimentWorkspaceVersion":ML_WORKSPACE_VERSION,"scientificResearchOperatingSystemVersion":RESEARCH_OS_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"api_route_count":29,"workspaceExecutionAuthority":True,"labMutatesTelemetry":False,"automaticModelRanking":False,"automaticCheckpointPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"visualSpecSchema":VISUAL_SPEC_SCHEMA,"coreHandoffSchema":CORE_HANDOFF_SCHEMA,"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"rawTelemetryImmutable":True,"smoothingDerivedAndDeclared":True,"automaticModelRanking":False,"automaticCheckpointPromotion":False,"convergenceCertified":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":["v0.140.0.1 installed-runtime integrity policy retained","v0.141.0 ML Experiment Workspace retained","v0.141.1 Neural Architecture & Training Configuration retained","Workspace training telemetry required for observed curves","checkpoint provenance preserved"],"automaticGateWaiver":False,"boundary":BOUNDARY}
def interpretation_boundary(_=None): return {"ok":True,"version":VERSION,"statements":["smoothed curve is a derived visualization","metric extremum is not scientific validity","checkpoint candidate is not an endorsed model","plateau heuristic does not certify convergence","training metric is not evidence"],"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"rawMetricNormalization":True,"trainingCurveSpecs":True,"smoothingProvenance":True,"runOverlays":True,"smallMultiples":True,"checkpointTimeline":True,"checkpointMetricLinkage":True,"objectiveCandidateMarkers":True,"trainValidationGap":True,"descriptiveConvergenceDiagnostics":True,"dashboardSpec":True,"coreVisualHandoff":True,"deterministicSnapshots":True,"reproducibilityPacket":True,"manifestIntegrityBaselineV014001":True,"automaticModelRanking":False,"automaticCheckpointPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
