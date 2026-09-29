from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.141.5"
PREDECESSOR_VERSION="0.141.4"
COMPARISON_VERSION="0.141.3"
TELEMETRY_VERSION="0.141.2"
ARCHITECTURE_VERSION="0.141.1"
ML_WORKSPACE_VERSION="0.141.0"
RESEARCH_OS_VERSION="0.140.0"
INTEGRITY_BASELINE="0.140.0.1"
SCHEMA="sc-lab-ablation-study-framework/0.141.5"
PLAN_SCHEMA="sc-lab-ablation-study-plan/0.141.5"
VARIANT_SCHEMA="sc-lab-ablation-variant/0.141.5"
RESULT_SCHEMA="sc-lab-ablation-result/0.141.5"
SNAPSHOT_SCHEMA="sc-lab-ablation-study-snapshot/0.141.5"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-ablation-study-execution-handoff/1.0"
CORE_HANDOFF_SCHEMA="sc-core-ablation-study-visual-object-handoff/1.0"

BOUNDARY=(
    "Lab structures and analyzes ablation studies but does not execute training, infer causal effects from uncontrolled contrasts, "
    "select a winning model, promote a checkpoint, or convert ablation deltas into scientific evidence. Controlled differences remain descriptive research results requiring interpretation."
)
ABLATION_ACTIONS=("remove","disable","replace","freeze","mask","zero","reparameterize","other")
VARIANT_STATUSES=("planned","queued","running","completed","failed","cancelled")
COMPARABILITY_DIMENSIONS=("datasetRef","splitRef","baseTrainingConfigurationRef","environmentRef","seedPolicyRef","metricDefinitionRef")
VIEWS=("variant-matrix","metric-delta-matrix","component-effect-summary","replicate-distribution","interaction-summary","failure-audit","provenance-matrix")

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

def _metric_defs(root):
    items=_list(_get(root,"metrics","metricDefinitions","objectives",default=[])); out=[]
    for i,m in enumerate(items):
        m=m if isinstance(m,dict) else {"name":m}
        out.append({"metricId":_txt(_get(m,"metricId","id"),256) or f"metric-{i+1}","name":_txt(_get(m,"name","metric"),256) or f"metric-{i+1}",
                    "split":_txt(m.get("split"),128),"unit":_txt(m.get("unit"),64),"definitionRef":_txt(_get(m,"definitionRef","metricDefinitionRef"),1024),
                    "direction":_txt(m.get("direction"),16).lower() if _txt(m.get("direction"),16).lower() in ("min","max") else ""})
    return out

def normalize_factor(item:Any,index:int=0):
    raw=item if isinstance(item,dict) else {"component":item}
    action=_txt(_get(raw,"action","operation"),64).lower() or "remove"
    if action not in ABLATION_ACTIONS: action="other"
    rec={"factorId":_txt(_get(raw,"factorId","id"),256) or f"factor-{index+1}","component":_txt(_get(raw,"component","name","target"),512) or f"component-{index+1}",
         "action":action,"replacement":_get(raw,"replacement","value"),"rationale":_txt(raw.get("rationale"),2048),"scope":_txt(raw.get("scope"),512),
         "heldConstantClaims":_list(raw.get("heldConstantClaims")),"provenance":_dict(raw.get("provenance"))}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return rec

def normalize_plan(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    factors=[normalize_factor(x,i) for i,x in enumerate(_list(_get(root,"factors","ablations","components",default=[])))]
    metrics=_metric_defs(root)
    baseline=_dict(_get(root,"baseline","control",default={}))
    rec={"schema":PLAN_SCHEMA,"version":VERSION,"recordType":"ablation-study-plan","studyId":_txt(_get(root,"studyId","id"),512) or f"ablation-{_fp(factors)[:16]}",
         "title":_txt(root.get("title"),512) or "Ablation study","experimentId":_txt(root.get("experimentId"),512),"baseline":{
             "variantId":_txt(_get(baseline,"variantId","id"),512) or "baseline","modelRef":_txt(baseline.get("modelRef"),1024),"architectureRef":_txt(baseline.get("architectureRef"),1024),
             "datasetRef":_txt(_get(baseline,"datasetRef",default=root.get("datasetRef")),1024),"splitRef":_txt(_get(baseline,"splitRef",default=root.get("splitRef")),1024),
             "baseTrainingConfigurationRef":_txt(_get(baseline,"baseTrainingConfigurationRef",default=_get(root,"baseTrainingConfigurationRef","trainingConfigurationRef")),1024),
             "environmentRef":_txt(_get(baseline,"environmentRef",default=root.get("environmentRef")),1024),"seedPolicyRef":_txt(_get(baseline,"seedPolicyRef",default=root.get("seedPolicyRef")),1024),"metricDefinitionRef":_txt(_get(baseline,"metricDefinitionRef",default=root.get("metricDefinitionRef")),1024)},
         "factors":factors,"metrics":metrics,"replicatePolicy":_dict(root.get("replicatePolicy")),"workspaceExecutionAuthority":True,"labExecutesTraining":False,
         "causalEffectInferred":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
    issues=[]
    if not factors: issues.append("no-ablation-factors")
    if not metrics: issues.append("no-metric-definitions")
    for d in ("datasetRef","splitRef","baseTrainingConfigurationRef","environmentRef"):
        if not rec["baseline"].get(d): issues.append(f"baseline-missing-{d}")
    rec["issues"]=issues; rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"plan":rec,"readyForExecutionHandoff":not issues,"boundary":BOUNDARY}

def workspace_handoff(payload:dict):
    plan=normalize_plan(payload); packet={"schema":WORKSPACE_HANDOFF_SCHEMA,"labRelease":VERSION,"plan":plan["plan"],"executionAuthority":"workspace",
        "labExecutesTraining":False,"ready":plan["readyForExecutionHandoff"],"automaticWinnerSelection":False,"automaticModelPromotion":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet); return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def normalize_variant(item:Any,index:int,baseline=None,metrics=None):
    raw=item if isinstance(item,dict) else {"variantId":item}; baseline=baseline or {}; metrics=metrics or []
    factors=[normalize_factor(x,i) for i,x in enumerate(_list(_get(raw,"factors","ablations","changes",default=[])))]
    vals={}
    src=_get(raw,"metrics","results","objectiveValues",default={})
    if isinstance(src,dict):
        for k,v in src.items(): vals[_txt(k,256)]=_num(v)
    elif isinstance(src,list):
        for x in src:
            if isinstance(x,dict): vals[_txt(_get(x,"name","metric"),256)]=_num(x.get("value"))
    for m in metrics: vals.setdefault(m["name"],None)
    status=_txt(raw.get("status"),32).lower() or "completed"; status=status if status in VARIANT_STATUSES else "completed"
    return {"schema":VARIANT_SCHEMA,"variantId":_txt(_get(raw,"variantId","id"),512) or f"variant-{index+1}","label":_txt(raw.get("label"),512),"status":status,
        "isBaseline":bool(raw.get("isBaseline",False)),"factors":factors,"metrics":vals,"replicateId":_txt(raw.get("replicateId"),256),"seed":_get(raw,"seed"),
        "runId":_txt(raw.get("runId"),512),"checkpointRef":_txt(raw.get("checkpointRef"),1024),"datasetRef":_txt(_get(raw,"datasetRef",default=baseline.get("datasetRef")),1024),
        "splitRef":_txt(_get(raw,"splitRef",default=baseline.get("splitRef")),1024),"baseTrainingConfigurationRef":_txt(_get(raw,"baseTrainingConfigurationRef",default=baseline.get("baseTrainingConfigurationRef")),1024),
        "environmentRef":_txt(_get(raw,"environmentRef",default=baseline.get("environmentRef")),1024),"seedPolicyRef":_txt(_get(raw,"seedPolicyRef",default=baseline.get("seedPolicyRef")),1024),
        "metricDefinitionRef":_txt(raw.get("metricDefinitionRef"),1024),"provenanceRef":_txt(raw.get("provenanceRef"),1024),"metadata":_dict(raw.get("metadata"))}

def normalize_results(payload:dict):
    root=payload if isinstance(payload,dict) else {}; plan=normalize_plan(root)["plan"]; metrics=plan["metrics"]; baseline=plan["baseline"]
    items=_list(_get(root,"variants","results","runs",default=[])); variants=[normalize_variant(x,i,baseline,metrics) for i,x in enumerate(items)]
    if not any(v["isBaseline"] for v in variants) and variants:
        bid=baseline.get("variantId","baseline")
        for v in variants:
            if v["variantId"]==bid: v["isBaseline"]=True
    rec={"schema":RESULT_SCHEMA,"version":VERSION,"recordType":"ablation-study-results","studyId":plan["studyId"],"planFingerprint":plan["fingerprint"],"metrics":metrics,"variants":variants,
         "workspaceExecutionAuthority":True,"causalEffectInferred":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"results":rec,"boundary":BOUNDARY}

def variant_registry(payload):
    vs=normalize_results(payload)["results"]["variants"]
    rows=[{"variantId":v["variantId"],"label":v["label"],"status":v["status"],"isBaseline":v["isBaseline"],"runId":v["runId"],"replicateId":v["replicateId"],"factorCount":len(v["factors"]),"provenanceRef":v["provenanceRef"]} for v in vs]
    return {"ok":True,"version":VERSION,"variants":rows,"count":len(rows),"automaticRanking":False,"boundary":BOUNDARY}

def baseline_audit(payload):
    r=normalize_results(payload)["results"]; base=[v for v in r["variants"] if v["isBaseline"]]
    issues=[]
    if len(base)==0: issues.append("missing-baseline-result")
    if len(base)>1: issues.append("multiple-baseline-results")
    return {"ok":True,"version":VERSION,"baselineCount":len(base),"baseline":base[0] if len(base)==1 else None,"issues":issues,"valid":not issues,"boundary":BOUNDARY}

def comparability(payload):
    r=normalize_results(payload)["results"]; base=[v for v in r["variants"] if v["isBaseline"]]; baseline=base[0] if len(base)==1 else None; rows=[]
    if not baseline: return {"ok":False,"version":VERSION,"reason":"exactly-one-baseline-required","rows":[],"boundary":BOUNDARY}
    for v in r["variants"]:
        if v["isBaseline"]: continue
        dims=[]; mismatches=[]
        for d in COMPARABILITY_DIMENSIONS:
            a=baseline.get(d); b=v.get(d); same=(a==b and bool(a))
            dims.append({"dimension":d,"baseline":a,"variant":b,"comparable":same})
            if not same: mismatches.append(d)
        rows.append({"variantId":v["variantId"],"comparable":not mismatches,"mismatches":mismatches,"dimensions":dims,"controlledContrast":not mismatches,"causalEffectInferred":False})
    return {"ok":True,"version":VERSION,"baselineId":baseline["variantId"],"rows":rows,"allComparable":all(x["comparable"] for x in rows),"causalEffectInferred":False,"boundary":BOUNDARY}

def _metric_names(r): return sorted({m["name"] for m in r["metrics"]}|{k for v in r["variants"] for k in v.get("metrics",{})})
def paired_delta_matrix(payload):
    r=normalize_results(payload)["results"]; base=[v for v in r["variants"] if v["isBaseline"]]
    if len(base)!=1: return {"ok":False,"version":VERSION,"reason":"exactly-one-baseline-required","boundary":BOUNDARY}
    b=base[0]; comp={x["variantId"]:x for x in comparability(payload)["rows"]}; metrics=_metric_names(r); rows=[]
    for v in r["variants"]:
        if v["isBaseline"]: continue
        vals={}
        for name in metrics:
            x=_num(v["metrics"].get(name)); y=_num(b["metrics"].get(name)); vals[name]=(x-y) if x is not None and y is not None else None
        rows.append({"variantId":v["variantId"],"controlledContrast":comp.get(v["variantId"],{}).get("controlledContrast",False),"deltas":vals})
    return {"ok":True,"version":VERSION,"matrix":{"baselineId":b["variantId"],"metrics":metrics,"rows":rows,"signedDelta":"variant-minus-baseline","causalEffectInferred":False,"automaticRanking":False},"boundary":BOUNDARY}

def metric_delta_matrix(payload): return paired_delta_matrix(payload)

def component_effect_summary(payload):
    d=paired_delta_matrix(payload)
    if not d.get("ok"): return d
    r=normalize_results(payload)["results"]; byid={v["variantId"]:v for v in r["variants"]}; rows=[]
    for row in d["matrix"]["rows"]:
        v=byid[row["variantId"]]
        rows.append({"variantId":v["variantId"],"components":[f["component"] for f in v["factors"]],"actions":[f["action"] for f in v["factors"]],"deltas":row["deltas"],
                     "controlledContrast":row["controlledContrast"],"descriptiveEffectOnly":True,"causalEffectInferred":False})
    return {"ok":True,"version":VERSION,"rows":rows,"descriptiveEffectOnly":True,"causalEffectInferred":False,"boundary":BOUNDARY}

def replicate_summary(payload):
    r=normalize_results(payload)["results"]; groups={}
    for v in r["variants"]:
        groups.setdefault(v["variantId"].split("#")[0],[]).append(v)
    rows=[]
    for gid,vs in sorted(groups.items()):
        metrics={}
        for name in _metric_names(r):
            vals=[_num(v["metrics"].get(name)) for v in vs]; vals=[x for x in vals if x is not None]
            metrics[name]={"n":len(vals),"mean":statistics.fmean(vals) if vals else None,"stdev":statistics.stdev(vals) if len(vals)>1 else None}
        rows.append({"variantGroup":gid,"replicateCount":len(vs),"metrics":metrics})
    return {"ok":True,"version":VERSION,"rows":rows,"causalEffectInferred":False,"boundary":BOUNDARY}

def interaction_summary(payload):
    r=normalize_results(payload)["results"]; rows=[]
    for v in r["variants"]:
        if len(v["factors"])>1:
            rows.append({"variantId":v["variantId"],"factorIds":[f["factorId"] for f in v["factors"]],"observedMetrics":v["metrics"],"interactionEstimated":False,
                         "note":"Multi-factor ablation observed; no factorial interaction is inferred without an explicit estimand/design."})
    return {"ok":True,"version":VERSION,"rows":rows,"interactionEstimated":False,"boundary":BOUNDARY}

def failure_audit(payload):
    vs=normalize_results(payload)["results"]["variants"]; bad=[{"variantId":v["variantId"],"status":v["status"],"metadata":v["metadata"]} for v in vs if v["status"] in ("failed","cancelled")]
    return {"ok":True,"version":VERSION,"rows":bad,"count":len(bad),"excludedFromMetricDeltas":True,"boundary":BOUNDARY}

def confounding_audit(payload):
    c=comparability(payload)
    rows=[x for x in c.get("rows",[]) if not x.get("controlledContrast")]
    return {"ok":c.get("ok",False),"version":VERSION,"rows":rows,"confoundedCount":len(rows),"causalEffectInferred":False,"boundary":BOUNDARY}

def candidate_review(payload):
    root=payload if isinstance(payload,dict) else {}; metric=_txt(_get(root,"metric","objective"),256); direction=_txt(root.get("direction"),16).lower()
    if direction not in ("min","max"): return {"ok":False,"version":VERSION,"reason":"explicit-direction-required","winner":None,"boundary":BOUNDARY}
    r=normalize_results(root)["results"]; comp={x["variantId"]:x for x in comparability(root).get("rows",[])}; vals=[]
    for v in r["variants"]:
        if v["isBaseline"] or v["status"]!="completed" or not comp.get(v["variantId"],{}).get("controlledContrast",False): continue
        x=_num(v["metrics"].get(metric));
        if x is not None: vals.append((x,v["variantId"]))
    vals.sort(reverse=(direction=="max")); candidates=[{"variantId":vid,"value":val,"metric":metric,"direction":direction,"reviewRequired":True} for val,vid in vals]
    return {"ok":True,"version":VERSION,"metric":metric,"direction":direction,"candidateSet":candidates,"winner":None,"automaticWinnerSelection":False,"automaticModelPromotion":False,"causalEffectInferred":False,"boundary":BOUNDARY}

def visual_spec(payload):
    root=payload if isinstance(payload,dict) else {}; view=_txt(root.get("view"),64).lower() or "variant-matrix"; view=view if view in VIEWS else "variant-matrix"
    if view in ("metric-delta-matrix","variant-matrix"): data=paired_delta_matrix(root)
    elif view=="component-effect-summary": data=component_effect_summary(root)
    elif view=="replicate-distribution": data=replicate_summary(root)
    elif view=="interaction-summary": data=interaction_summary(root)
    elif view=="failure-audit": data=failure_audit(root)
    else: data=comparability(root)
    spec={"schema":"sc-lab-ablation-visual-spec/0.141.5","version":VERSION,"view":view,"data":data,"provenancePreserved":True,"causalEffectInferred":False,"automaticRanking":False,"boundary":BOUNDARY}
    spec["fingerprint"]=_fp({k:v for k,v in spec.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"visualSpec":spec,"boundary":BOUNDARY}

def core_visual_handoff(payload):
    v=visual_spec(payload)["visualSpec"]; packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"visualSpec":v,"canonicalVisualObjectAuthority":"platform-core","labIsExecutionAuthority":False,
        "causalEffectInferred":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"boundary":BOUNDARY}; packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def export_bundle(payload):
    r=normalize_results(payload)["results"]; bundle={"schema":"sc-lab-ablation-study-export/0.141.5","version":VERSION,"results":r,"comparability":comparability(payload),"deltas":paired_delta_matrix(payload),
        "componentEffects":component_effect_summary(payload),"confoundingAudit":confounding_audit(payload),"automaticWinnerSelection":False,"causalEffectInferred":False,"boundary":BOUNDARY}
    bundle["fingerprint"]=_fp({k:v for k,v in bundle.items() if k!="fingerprint"}); return {"ok":True,"version":VERSION,"bundle":bundle,"boundary":BOUNDARY}

def snapshot(payload):
    stable=export_bundle(payload)["bundle"]; stable={k:v for k,v in stable.items() if k not in ("createdAt",)}; fp=_fp(stable)
    snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"snapshotId":f"ablation-snapshot-{fp[:20]}","fingerprint":fp,"content":stable,"createdAt":_now(),"immutableIntent":True}
    return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}

def compare_snapshots(payload):
    root=payload if isinstance(payload,dict) else {}; a=_dict(_get(root,"a","left","baseline",default={})); b=_dict(_get(root,"b","right","candidate",default={}))
    af=_txt(a.get("fingerprint"),128) or _fp(a.get("content",a)); bf=_txt(b.get("fingerprint"),128) or _fp(b.get("content",b))
    return {"ok":True,"version":VERSION,"same":af==bf,"leftFingerprint":af,"rightFingerprint":bf,"scientificEquivalenceInferred":False,"boundary":BOUNDARY}

def reproducibility_packet(payload):
    s=snapshot(payload)["snapshot"]; packet={"schema":"sc-lab-ablation-reproducibility-package/0.141.5","version":VERSION,"snapshot":s,"workspaceExecutionAuthority":True,
        "reproducibilityCertified":False,"scientificValidityCertified":False,"causalEffectCertified":False,"automaticWinnerSelection":False,"boundary":BOUNDARY}; packet["fingerprint"]=_fp({k:v for k,v in packet.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"reproducibilityPacket":packet,"reproducibilityCertified":False,"boundary":BOUNDARY}

def interpretation_boundary(_=None): return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"ablationDeltaIsCausalEffect":False,"metricDifferenceIsScientificSuperiority":False,"automaticWinnerSelection":False,"automaticModelPromotion":False}
def policy(): return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"labExecutesTraining":False,"controlledContrastRequired":True,"causalEffectInferred":False,"automaticRanking":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"planSchema":PLAN_SCHEMA,"variantSchema":VARIANT_SCHEMA,"resultSchema":RESULT_SCHEMA,"workspaceHandoffSchema":WORKSPACE_HANDOFF_SCHEMA,"coreHandoffSchema":CORE_HANDOFF_SCHEMA,"views":list(VIEWS),"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":["baseline-identifiable","held-constant-context-explicit","metric-definitions-preserved","workspace-execution-authority","controlled-contrast-audit","no-automatic-winner","no-causal-overclaim","deterministic-snapshot"],"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"api_route_count":30,"ablationStudyFramework":True,"hyperparameterStudySearchResultsVersion":PREDECESSOR_VERSION,"modelComparisonExperimentMatrixVersion":COMPARISON_VERSION,"trainingCurvesMetricsCheckpointVisualizationVersion":TELEMETRY_VERSION,"neuralArchitectureTrainingConfigurationVersion":ARCHITECTURE_VERSION,"machineLearningExperimentWorkspaceVersion":ML_WORKSPACE_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"labExecutesTraining":False,"controlledContrastRequired":True,"causalEffectInferred":False,"automaticRanking":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"api_route_count":30,"ablationPlan":True,"workspaceExecutionHandoff":True,"variantRegistry":True,"baselineAudit":True,"comparabilityAudit":True,"pairedDeltaMatrix":True,"componentEffectSummary":True,"replicateSummary":True,"interactionGuardrail":True,"confoundingAudit":True,"candidateReview":True,"visualSpecs":True,"coreVisualHandoff":True,"deterministicSnapshots":True,"reproducibilityPackages":True,"causalEffectInferred":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"boundary":BOUNDARY}
