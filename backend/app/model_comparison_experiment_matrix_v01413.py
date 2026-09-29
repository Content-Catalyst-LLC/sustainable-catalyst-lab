from __future__ import annotations
import copy, hashlib, json, math
from datetime import datetime, timezone
from typing import Any

VERSION="0.141.3"
PREDECESSOR_VERSION="0.141.2"
ARCHITECTURE_VERSION="0.141.1"
ML_WORKSPACE_VERSION="0.141.0"
RESEARCH_OS_VERSION="0.140.0"
INTEGRITY_BASELINE="0.140.0.1"
SCHEMA="sc-lab-model-comparison-experiment-matrix/0.141.3"
MATRIX_SCHEMA="sc-lab-experiment-comparison-matrix/0.141.3"
SNAPSHOT_SCHEMA="sc-lab-model-comparison-snapshot/0.141.3"
CORE_HANDOFF_SCHEMA="sc-core-model-comparison-visual-object-handoff/1.0"

BOUNDARY=(
 "Lab compares governed experiment records and observed metrics without selecting a winner, promoting a model, or converting model performance into evidence. "
 "Comparability is explicit and dimension-specific: dataset/split, metric definition, architecture/training configuration, execution environment, and provenance differences remain visible."
)
COMPARABILITY_DIMENSIONS=("dataset","split","metric-definition","architecture","training-configuration","environment","provenance")
MATRIX_VIEWS=("experiment-matrix","metric-matrix","configuration-matrix","checkpoint-matrix","provenance-matrix","missingness-matrix","delta-matrix")

def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=4096): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _num(v):
    if isinstance(v,bool): return None
    if isinstance(v,(int,float)) and math.isfinite(float(v)): return float(v)
    try:
        x=float(v); return x if math.isfinite(x) else None
    except Exception: return None

def _get(o,*names,default=None):
    if not isinstance(o,dict): return default
    for n in names:
        if n in o and o[n] is not None: return o[n]
    return default

def _metric_key(m):
    return (_txt(_get(m,"name","metric","metricName"),256), _txt(_get(m,"split","partition","datasetSplit"),128) or "unspecified")

def normalize_record(item:Any,index:int):
    raw=item if isinstance(item,dict) else {"experimentId":item}
    exp=_txt(_get(raw,"experimentId","experiment_id","id"),512) or f"experiment-{index+1}"
    run=_dict(_get(raw,"run","workspaceRun","result",default={}))
    rid=_txt(_get(raw,"runId","run_id"),512) or _txt(_get(run,"runId","run_id","id"),512) or f"run-{index+1}"
    metrics=[]
    source_metrics=_list(_get(raw,"metrics",default=[])) or _list(run.get("metrics"))
    for i,m in enumerate(source_metrics):
        m=m if isinstance(m,dict) else {"value":m}
        name,split=_metric_key(m)
        metrics.append({"metricId":_txt(_get(m,"metricId","id"),256) or f"metric-{i+1}","name":name or "metric","split":split,
            "value":_num(m.get("value")),"step":_num(_get(m,"step","epoch","globalStep")),"unit":_txt(m.get("unit"),64),
            "definitionRef":_txt(_get(m,"definitionRef","metricDefinitionRef"),512),"provenance":_dict(m.get("provenance"))})
    checkpoints=_list(_get(raw,"checkpoints",default=[])) or _list(run.get("checkpoints"))
    return {"experimentId":exp,"runId":rid,"label":_txt(raw.get("label"),256) or exp,
        "datasetRef":_txt(_get(raw,"datasetRef","dataset","datasetId"),1024),"splitRef":_txt(_get(raw,"splitRef","dataSplitRef"),1024),
        "architectureRef":_txt(_get(raw,"architectureRef","modelArchitectureRef"),1024),"trainingConfigurationRef":_txt(_get(raw,"trainingConfigurationRef","configurationRef"),1024),
        "environmentRef":_txt(_get(raw,"environmentRef","executionEnvironmentRef"),1024),"provenanceRef":_txt(_get(raw,"provenanceRef","lineageRef"),1024),
        "metrics":metrics,"checkpoints":copy.deepcopy(checkpoints),"metadata":_dict(raw.get("metadata"))}

def normalize(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    items=_list(_get(root,"experiments","records","runs",default=[]))
    if not items and isinstance(root.get("experiment"),dict): items=[root["experiment"]]
    records=[normalize_record(x,i) for i,x in enumerate(items)]
    out={"schema":SCHEMA,"version":VERSION,"recordType":"model-comparison-set","records":records,"automaticWinnerSelection":False,"automaticRanking":False,"modelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
    out["fingerprint"]=_fp({k:v for k,v in out.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"record":out,"boundary":BOUNDARY}

def metric_catalog(payload):
    recs=normalize(payload)["record"]["records"]; seen={}
    for r in recs:
        for m in r["metrics"]:
            k=(m["name"],m["split"],m["unit"],m["definitionRef"])
            row=seen.setdefault(k,{"name":m["name"],"split":m["split"],"unit":m["unit"],"definitionRef":m["definitionRef"],"experimentIds":[]})
            row["experimentIds"].append(r["experimentId"])
    return {"ok":True,"version":VERSION,"metrics":[{**v,"experimentIds":sorted(set(v["experimentIds"]))} for v in seen.values()],"boundary":BOUNDARY}

def _dim_value(r,dim,metric=None):
    if dim=="dataset": return r.get("datasetRef","")
    if dim=="split": return (metric or {}).get("split","") or r.get("splitRef","")
    if dim=="metric-definition": return (metric or {}).get("definitionRef","")
    if dim=="architecture": return r.get("architectureRef","")
    if dim=="training-configuration": return r.get("trainingConfigurationRef","")
    if dim=="environment": return r.get("environmentRef","")
    if dim=="provenance": return r.get("provenanceRef","")
    return ""

def comparability(payload):
    root=payload if isinstance(payload,dict) else {}; recs=normalize(root)["record"]["records"]
    metric_name=_txt(_get(root,"metric","name"),256); split=_txt(root.get("split"),128)
    def pick_metric(r):
        for m in r["metrics"]:
            if (not metric_name or m["name"]==metric_name) and (not split or m["split"]==split): return m
        return None
    rows=[]
    for i,a in enumerate(recs):
        for b in recs[i+1:]:
            ma,mb=pick_metric(a),pick_metric(b); dims={}
            for d in COMPARABILITY_DIMENSIONS:
                av,bv=_dim_value(a,d,ma),_dim_value(b,d,mb)
                dims[d]={"left":av,"right":bv,"same": bool(av and bv and av==bv),"unknown":not bool(av and bv)}
            strict=all(x["same"] for x in dims.values())
            rows.append({"leftExperimentId":a["experimentId"],"rightExperimentId":b["experimentId"],"dimensions":dims,"strictlyComparable":strict,"automaticEquivalence":False})
    return {"ok":True,"version":VERSION,"pairs":rows,"comparabilityIsDimensionSpecific":True,"boundary":BOUNDARY}

def experiment_matrix(payload):
    root=payload if isinstance(payload,dict) else {}; recs=normalize(root)["record"]["records"]
    metric_name=_txt(_get(root,"metric","name"),256); split=_txt(root.get("split"),128)
    cols=["experimentId","runId","datasetRef","splitRef","architectureRef","trainingConfigurationRef","environmentRef","provenanceRef"]
    rows=[]
    for r in recs:
        row={k:r.get(k) for k in cols}
        vals=[]
        for m in r["metrics"]:
            if (not metric_name or m["name"]==metric_name) and (not split or m["split"]==split): vals.append(m)
        if metric_name:
            row["metric"]=metric_name; row["metricSplit"]=split or None; row["metricValue"]=vals[-1]["value"] if vals else None; row["metricDefinitionRef"]=vals[-1]["definitionRef"] if vals else ""
        rows.append(row)
    matrix={"schema":MATRIX_SCHEMA,"view":"experiment-matrix","columns":list(rows[0].keys()) if rows else cols,"rows":rows,"automaticRanking":False,"automaticWinnerSelection":False}
    matrix["fingerprint"]=_fp(matrix)
    return {"ok":True,"version":VERSION,"matrix":matrix,"boundary":BOUNDARY}

def metric_matrix(payload):
    recs=normalize(payload)["record"]["records"]; keys=sorted({(m["name"],m["split"]) for r in recs for m in r["metrics"]})
    columns=[{"metric":n,"split":s,"key":f"{n}::{s}"} for n,s in keys]; rows=[]
    for r in recs:
        row={"experimentId":r["experimentId"],"runId":r["runId"],"values":{}}
        for n,s in keys:
            pts=[m for m in r["metrics"] if m["name"]==n and m["split"]==s and m["value"] is not None]
            row["values"][f"{n}::{s}"]=pts[-1]["value"] if pts else None
        rows.append(row)
    return {"ok":True,"version":VERSION,"matrix":{"schema":MATRIX_SCHEMA,"view":"metric-matrix","columns":columns,"rows":rows,"automaticRanking":False},"boundary":BOUNDARY}

def configuration_matrix(payload):
    recs=normalize(payload)["record"]["records"]; rows=[]
    for r in recs: rows.append({"experimentId":r["experimentId"],"architectureRef":r["architectureRef"],"trainingConfigurationRef":r["trainingConfigurationRef"],"environmentRef":r["environmentRef"]})
    return {"ok":True,"version":VERSION,"matrix":{"schema":MATRIX_SCHEMA,"view":"configuration-matrix","rows":rows,"automaticPreference":False},"boundary":BOUNDARY}

def provenance_matrix(payload):
    recs=normalize(payload)["record"]["records"]; rows=[{"experimentId":r["experimentId"],"datasetRef":r["datasetRef"],"splitRef":r["splitRef"],"provenanceRef":r["provenanceRef"],"environmentRef":r["environmentRef"]} for r in recs]
    return {"ok":True,"version":VERSION,"matrix":{"schema":MATRIX_SCHEMA,"view":"provenance-matrix","rows":rows},"boundary":BOUNDARY}

def missingness_matrix(payload):
    recs=normalize(payload)["record"]["records"]; fields=("datasetRef","splitRef","architectureRef","trainingConfigurationRef","environmentRef","provenanceRef")
    rows=[]
    for r in recs: rows.append({"experimentId":r["experimentId"],"missing":{f:not bool(r.get(f)) for f in fields},"missingMetricDefinitions":sum(1 for m in r["metrics"] if not m.get("definitionRef"))})
    return {"ok":True,"version":VERSION,"matrix":{"schema":MATRIX_SCHEMA,"view":"missingness-matrix","rows":rows},"boundary":BOUNDARY}

def delta_matrix(payload):
    root=payload if isinstance(payload,dict) else {}; name=_txt(_get(root,"metric","name"),256); split=_txt(root.get("split"),128); recs=normalize(root)["record"]["records"]
    values={}
    for r in recs:
        pts=[m for m in r["metrics"] if (not name or m["name"]==name) and (not split or m["split"]==split) and m["value"] is not None]
        values[r["experimentId"]]=pts[-1]["value"] if pts else None
    ids=[r["experimentId"] for r in recs]; rows=[]
    for a in ids:
        row={"experimentId":a,"deltas":{}}
        for b in ids:
            av,bv=values[a],values[b]; row["deltas"][b]=(av-bv) if av is not None and bv is not None else None
        rows.append(row)
    return {"ok":True,"version":VERSION,"metric":name,"split":split,"matrix":{"schema":MATRIX_SCHEMA,"view":"delta-matrix","rows":rows,"signedDifferenceOnly":True,"winnerInferred":False},"boundary":BOUNDARY}

def checkpoint_matrix(payload):
    recs=normalize(payload)["record"]["records"]; rows=[]
    for r in recs:
        rows.append({"experimentId":r["experimentId"],"runId":r["runId"],"checkpointCount":len(r["checkpoints"]),"checkpoints":r["checkpoints"],"automaticPromotion":False})
    return {"ok":True,"version":VERSION,"matrix":{"schema":MATRIX_SCHEMA,"view":"checkpoint-matrix","rows":rows,"automaticPromotion":False},"boundary":BOUNDARY}

def metric_definition_audit(payload):
    recs=normalize(payload)["record"]["records"]; groups={}
    for r in recs:
        for m in r["metrics"]:
            k=(m["name"],m["split"]); groups.setdefault(k,set()).add(m["definitionRef"] or "<undeclared>")
    rows=[{"metric":k[0],"split":k[1],"definitionRefs":sorted(v),"definitionMismatch":len(v)>1} for k,v in groups.items()]
    return {"ok":True,"version":VERSION,"rows":rows,"mismatchIsWarningNotCorrection":True,"boundary":BOUNDARY}

def pairwise_metric_comparison(payload):
    root=payload if isinstance(payload,dict) else {}; name=_txt(_get(root,"metric","name"),256); split=_txt(root.get("split"),128); recs=normalize(root)["record"]["records"]
    vals={}
    for r in recs:
        pts=[m for m in r["metrics"] if (not name or m["name"]==name) and (not split or m["split"]==split) and m["value"] is not None]
        vals[r["experimentId"]]=pts[-1] if pts else None
    rows=[]
    ids=list(vals)
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            av,bv=vals[a],vals[b]; rows.append({"leftExperimentId":a,"rightExperimentId":b,"leftValue":av["value"] if av else None,"rightValue":bv["value"] if bv else None,"difference":(av["value"]-bv["value"]) if av and bv else None,"winner":None,"automaticRanking":False})
    return {"ok":True,"version":VERSION,"metric":name,"split":split,"pairs":rows,"boundary":BOUNDARY}

def matrix_visual_spec(payload):
    root=payload if isinstance(payload,dict) else {}; view=_txt(root.get("view"),64) or "experiment-matrix"
    f={"experiment-matrix":experiment_matrix,"metric-matrix":metric_matrix,"configuration-matrix":configuration_matrix,"checkpoint-matrix":checkpoint_matrix,"provenance-matrix":provenance_matrix,"missingness-matrix":missingness_matrix,"delta-matrix":delta_matrix}.get(view)
    if not f: return {"ok":False,"version":VERSION,"error":"unsupported matrix view","boundary":BOUNDARY}
    matrix=f(root).get("matrix",{})
    spec={"schema":"sc-lab-model-comparison-visual-spec/0.141.3","visualType":view,"matrix":matrix,"automaticRanking":False,"automaticWinnerSelection":False,"comparabilityOverlay":comparability(root)["pairs"]}
    spec["fingerprint"]=_fp(spec)
    return {"ok":True,"version":VERSION,"visualSpec":spec,"boundary":BOUNDARY}

def core_visual_handoff(payload):
    spec=matrix_visual_spec(payload)
    if not spec.get("ok"): return spec
    packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"objectType":"ModelComparisonMatrix","visualSpec":spec["visualSpec"],"canonicalVisualObjectAuthority":"platform-core","automaticWinnerSelection":False}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def export_bundle(payload):
    root=payload if isinstance(payload,dict) else {}; bundle={"schema":"sc-lab-model-comparison-export/0.141.3","version":VERSION,"source":normalize(root)["record"],"comparability":comparability(root)["pairs"],"experimentMatrix":experiment_matrix(root)["matrix"],"metricMatrix":metric_matrix(root)["matrix"],"missingnessMatrix":missingness_matrix(root)["matrix"],"automaticRanking":False}
    bundle["fingerprint"]=_fp(bundle)
    return {"ok":True,"version":VERSION,"bundle":bundle,"boundary":BOUNDARY}

def snapshot(payload):
    root=payload if isinstance(payload,dict) else {}; content={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"normalized":normalize(root)["record"],"comparability":comparability(root)["pairs"],"visual":matrix_visual_spec(root if root.get("view") else {**root,"view":"experiment-matrix"})["visualSpec"]}; fp=_fp(content)
    return {"ok":True,"version":VERSION,"snapshot":{**content,"snapshotId":f"mcem-{fp[:24]}","fingerprint":fp},"generatedAt":_now(),"fingerprintExcludesGeneratedAt":True,"boundary":BOUNDARY}

def compare_snapshots(payload):
    root=payload if isinstance(payload,dict) else {}; l=_dict(root.get("left")); r=_dict(root.get("right"))
    def body(x):
        x=copy.deepcopy(x.get("snapshot") if isinstance(x.get("snapshot"),dict) else x)
        for k in ("snapshotId","fingerprint","generatedAt"): x.pop(k,None)
        return x
    a,b=body(l),body(r); keys=sorted(set(a)|set(b)); changes=[{"field":k,"left":a.get(k),"right":b.get(k)} for k in keys if a.get(k)!=b.get(k)]
    return {"ok":True,"version":VERSION,"equal":not changes,"changes":changes,"scientificSignificanceInferred":False,"winnerInferred":False,"boundary":BOUNDARY}

def reproducibility_packet(payload):
    snap=snapshot(payload)["snapshot"]; packet={"schema":"sc-lab-model-comparison-reproducibility-package/0.141.3","version":VERSION,"snapshot":snap,"requirements":["experiment/run identity","metric definitions","dataset/split lineage","architecture/training configuration refs","execution environment refs","comparison transform parameters"]}; packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"package":packet,"reproducibilityCertified":False,"boundary":BOUNDARY}

def interpretation_boundary(_=None): return {"ok":True,"version":VERSION,"statements":["numeric difference does not establish scientific superiority","incomparable records remain visible rather than normalized into equivalence","matrix order is not ranking","checkpoint count is not model quality","model performance is not evidence"],"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"explicitComparability":True,"automaticRanking":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"matrixSchema":MATRIX_SCHEMA,"coreHandoffSchema":CORE_HANDOFF_SCHEMA,"comparabilityDimensions":list(COMPARABILITY_DIMENSIONS),"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":["v0.140.0.1 installed-runtime integrity policy retained","v0.141.0 ML Experiment Workspace retained","v0.141.1 architecture/training configuration retained","v0.141.2 training telemetry visualization retained","comparability metadata preserved"],"automaticGateWaiver":False,"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"modelComparisonExperimentMatrix":True,"trainingCurvesMetricsCheckpointVisualizationVersion":PREDECESSOR_VERSION,"neuralArchitectureTrainingConfigurationVersion":ARCHITECTURE_VERSION,"machineLearningExperimentWorkspaceVersion":ML_WORKSPACE_VERSION,"scientificResearchOperatingSystemVersion":RESEARCH_OS_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"api_route_count":30,"explicitComparability":True,"automaticRanking":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"normalization":True,"comparabilityMatrix":True,"experimentMatrix":True,"metricMatrix":True,"configurationMatrix":True,"checkpointMatrix":True,"provenanceMatrix":True,"missingnessMatrix":True,"deltaMatrix":True,"metricDefinitionAudit":True,"pairwiseMetricComparison":True,"matrixVisualSpec":True,"coreVisualHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPacket":True,"automaticRanking":False,"automaticWinnerSelection":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
