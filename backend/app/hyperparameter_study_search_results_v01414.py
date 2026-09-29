from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.141.4"
PREDECESSOR_VERSION="0.141.3"
TELEMETRY_VERSION="0.141.2"
ARCHITECTURE_VERSION="0.141.1"
ML_WORKSPACE_VERSION="0.141.0"
RESEARCH_OS_VERSION="0.140.0"
INTEGRITY_BASELINE="0.140.0.1"
SCHEMA="sc-lab-hyperparameter-study-search-results/0.141.4"
STUDY_SCHEMA="sc-lab-hyperparameter-study/0.141.4"
TRIAL_SCHEMA="sc-lab-hyperparameter-trial-result/0.141.4"
SNAPSHOT_SCHEMA="sc-lab-hyperparameter-study-snapshot/0.141.4"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-hyperparameter-study-execution-handoff/1.0"
CORE_HANDOFF_SCHEMA="sc-core-hyperparameter-study-visual-object-handoff/1.0"

BOUNDARY=(
    "Lab defines and analyzes governed hyperparameter studies but does not execute search/training, silently infer objective direction, "
    "select a winning model, promote a checkpoint, or convert optimization results into scientific evidence. Candidate sets remain descriptive and reviewable."
)
SEARCH_STRATEGIES=("grid","random","bayesian","tpe","successive-halving","hyperband","external")
PARAMETER_TYPES=("float","integer","categorical","boolean")
TRIAL_STATUSES=("pending","running","completed","pruned","failed","cancelled")
RESULT_VIEWS=("search-progress","parameter-value-matrix","objective-result-matrix","parallel-coordinates","parameter-objective-scatter","trial-status","pareto-frontier")


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

def _direction(v):
    x=_txt(v,32).lower()
    return x if x in ("min","max") else ""

def normalize_space(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    params=_list(_get(root,"parameters","searchSpace","space",default=[]))
    out=[]; issues=[]
    for i,p in enumerate(params):
        p=p if isinstance(p,dict) else {"name":str(p)}
        name=_txt(_get(p,"name","parameter","id"),256) or f"parameter-{i+1}"
        typ=_txt(_get(p,"type","parameterType"),32).lower() or "float"
        if typ not in PARAMETER_TYPES: issues.append({"parameter":name,"issue":"unsupported-parameter-type","value":typ})
        typ=typ if typ in PARAMETER_TYPES else "float"
        scale=_txt(p.get("scale"),32).lower() or "linear"
        if scale not in ("linear","log"): scale="linear"
        low=_num(_get(p,"low","min","minimum")); high=_num(_get(p,"high","max","maximum")); choices=_list(_get(p,"choices","values",default=[]))
        if typ in ("float","integer") and (low is None or high is None or low>high): issues.append({"parameter":name,"issue":"invalid-or-missing-bounds"})
        if typ in ("categorical","boolean") and not choices:
            choices=[False,True] if typ=="boolean" else []
            if typ=="categorical": issues.append({"parameter":name,"issue":"missing-choices"})
        out.append({"name":name,"type":typ,"low":low,"high":high,"choices":choices,"scale":scale,
                    "step":_num(p.get("step")),"conditionalOn":_dict(p.get("conditionalOn")),"provenance":_dict(p.get("provenance"))})
    rec={"schema":SCHEMA,"version":VERSION,"recordType":"hyperparameter-search-space","parameters":out,"issues":issues,
         "workspaceExecutionAuthority":True,"labExecutesSearch":False,"boundary":BOUNDARY}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"searchSpace":rec,"valid":not issues,"boundary":BOUNDARY}

def _objectives(root):
    items=_list(_get(root,"objectives","objectiveDefinitions",default=[]))
    if not items and _get(root,"objective","metric") is not None:
        items=[{"name":_get(root,"objective","metric"),"direction":root.get("direction"),"split":root.get("split")}]
    out=[]
    for i,o in enumerate(items):
        o=o if isinstance(o,dict) else {"name":o}
        out.append({"objectiveId":_txt(_get(o,"objectiveId","id"),256) or f"objective-{i+1}",
                    "name":_txt(_get(o,"name","metric"),256) or f"objective-{i+1}",
                    "direction":_direction(o.get("direction")),"split":_txt(o.get("split"),128),
                    "unit":_txt(o.get("unit"),64),"definitionRef":_txt(_get(o,"definitionRef","metricDefinitionRef"),1024)})
    return out

def study_spec(payload:dict):
    root=payload if isinstance(payload,dict) else {}
    space=normalize_space(root).get("searchSpace",{})
    objectives=_objectives(root); missing=[x["name"] for x in objectives if not x["direction"]]
    strategy=_txt(_get(root,"strategy","searchStrategy"),64).lower() or "external"
    if strategy not in SEARCH_STRATEGIES: strategy="external"
    rec={"schema":STUDY_SCHEMA,"version":VERSION,"recordType":"hyperparameter-study",
         "studyId":_txt(_get(root,"studyId","id"),512) or f"study-{_fp(space)[:16]}","title":_txt(root.get("title"),512) or "Hyperparameter study",
         "experimentId":_txt(root.get("experimentId"),512),"datasetRef":_txt(root.get("datasetRef"),1024),"splitRef":_txt(root.get("splitRef"),1024),
         "architectureRef":_txt(root.get("architectureRef"),1024),"baseTrainingConfigurationRef":_txt(_get(root,"baseTrainingConfigurationRef","trainingConfigurationRef"),1024),
         "environmentRef":_txt(root.get("environmentRef"),1024),"searchStrategy":strategy,"searchSpace":space,"objectives":objectives,
         "budget":{"maxTrials":int(_num(_get(root,"maxTrials",default=0)) or 0),"maxWallSeconds":_num(root.get("maxWallSeconds")),"resourceBudget":_dict(root.get("resourceBudget"))},
         "seed":_get(root,"seed"),"objectiveDirectionsComplete":not missing,"missingObjectiveDirections":missing,
         "workspaceExecutionAuthority":True,"labExecutesSearch":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"study":rec,"readyForExecutionHandoff":not missing and not space.get("issues"),"boundary":BOUNDARY}

def workspace_handoff(payload:dict):
    spec=study_spec(payload); study=spec["study"]
    packet={"schema":WORKSPACE_HANDOFF_SCHEMA,"labRelease":VERSION,"study":study,"executionAuthority":"workspace","labExecutesSearch":False,
            "ready":spec["readyForExecutionHandoff"],"automaticWinnerSelection":False,"automaticModelPromotion":False,"boundary":BOUNDARY}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def normalize_trial(item:Any,index:int,objective_defs=None):
    raw=item if isinstance(item,dict) else {"trialId":item}; objective_defs=objective_defs or []
    tid=_txt(_get(raw,"trialId","trial_id","id"),512) or f"trial-{index+1}"
    status=_txt(raw.get("status"),32).lower() or "completed"; status=status if status in TRIAL_STATUSES else "completed"
    params=_dict(_get(raw,"parameters","params","hyperparameters",default={}))
    values={}
    source=_get(raw,"objectives","objectiveValues","metrics",default={})
    if isinstance(source,dict):
        for k,v in source.items(): values[_txt(k,256)]=_num(v)
    elif isinstance(source,list):
        for x in source:
            if isinstance(x,dict): values[_txt(_get(x,"name","metric"),256)]=_num(x.get("value"))
    for o in objective_defs:
        if o["name"] not in values: values[o["name"]]=None
    return {"schema":TRIAL_SCHEMA,"trialId":tid,"number":int(_num(_get(raw,"number","trialNumber",default=index)) or index),"status":status,
            "parameters":params,"objectives":values,"runId":_txt(raw.get("runId"),512),"checkpointRef":_txt(raw.get("checkpointRef"),1024),
            "startedAt":_txt(raw.get("startedAt"),128),"completedAt":_txt(raw.get("completedAt"),128),"durationSeconds":_num(raw.get("durationSeconds")),
            "reason":_txt(_get(raw,"reason","statusReason","failureReason"),2048),"provenanceRef":_txt(raw.get("provenanceRef"),1024),"metadata":_dict(raw.get("metadata"))}

def normalize_trials(payload:dict):
    root=payload if isinstance(payload,dict) else {}; objectives=_objectives(root)
    items=_list(_get(root,"trials","results","searchResults",default=[]))
    trials=[normalize_trial(x,i,objectives) for i,x in enumerate(items)]
    rec={"schema":SCHEMA,"version":VERSION,"recordType":"hyperparameter-study-results","studyId":_txt(root.get("studyId"),512),"objectives":objectives,
         "trials":trials,"workspaceExecutionAuthority":True,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
    rec["fingerprint"]=_fp({k:v for k,v in rec.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"results":rec,"boundary":BOUNDARY}

def trial_registry(payload):
    trials=normalize_trials(payload)["results"]["trials"]
    rows=[{"trialId":t["trialId"],"number":t["number"],"status":t["status"],"runId":t["runId"],"checkpointRef":t["checkpointRef"],"provenanceRef":t["provenanceRef"]} for t in trials]
    return {"ok":True,"version":VERSION,"trials":rows,"count":len(rows),"boundary":BOUNDARY}

def objective_catalog(payload):
    root=payload if isinstance(payload,dict) else {}; defs=_objectives(root); seen={x["name"]:x for x in defs}
    for t in normalize_trials(root)["results"]["trials"]:
        for name in t["objectives"]:
            seen.setdefault(name,{"objectiveId":f"objective-{len(seen)+1}","name":name,"direction":"","split":"","unit":"","definitionRef":""})
    rows=list(seen.values())
    return {"ok":True,"version":VERSION,"objectives":rows,"directionsComplete":all(bool(x["direction"]) for x in rows) if rows else False,"boundary":BOUNDARY}

def trial_status_audit(payload):
    trials=normalize_trials(payload)["results"]["trials"]; counts={s:0 for s in TRIAL_STATUSES}
    for t in trials: counts[t["status"]]=counts.get(t["status"],0)+1
    return {"ok":True,"version":VERSION,"counts":counts,"total":len(trials),"completed":counts.get("completed",0),"failedOrPruned":counts.get("failed",0)+counts.get("pruned",0),"qualityInferred":False,"boundary":BOUNDARY}

def budget_utilization(payload):
    root=payload if isinstance(payload,dict) else {}; trials=normalize_trials(root)["results"]["trials"]
    max_trials=int(_num(_get(root,"maxTrials",default=_get(_dict(root.get("budget")),"maxTrials",default=0))) or 0)
    observed=len(trials); completed=sum(t["status"]=="completed" for t in trials)
    return {"ok":True,"version":VERSION,"configuredMaxTrials":max_trials or None,"observedTrials":observed,"completedTrials":completed,
            "trialBudgetFraction":(observed/max_trials if max_trials>0 else None),"budgetUseIsNotModelQuality":True,"boundary":BOUNDARY}

def search_progress(payload):
    root=payload if isinstance(payload,dict) else {}; trials=normalize_trials(root)["results"]["trials"]; defs=_objectives(root)
    rows=[]
    for t in sorted(trials,key=lambda x:(x["number"],x["trialId"])):
        rows.append({"trialId":t["trialId"],"number":t["number"],"status":t["status"],"objectives":t["objectives"]})
    return {"ok":True,"version":VERSION,"series":rows,"objectives":defs,"automaticTrendJudgment":False,"boundary":BOUNDARY}

def parameter_value_matrix(payload):
    trials=normalize_trials(payload)["results"]["trials"]; names=sorted({k for t in trials for k in t["parameters"]})
    rows=[{"trialId":t["trialId"],"status":t["status"],"values":{k:t["parameters"].get(k) for k in names}} for t in trials]
    return {"ok":True,"version":VERSION,"matrix":{"view":"parameter-value-matrix","columns":names,"rows":rows,"automaticRanking":False},"boundary":BOUNDARY}

def objective_result_matrix(payload):
    trials=normalize_trials(payload)["results"]["trials"]; names=sorted({k for t in trials for k in t["objectives"]})
    rows=[{"trialId":t["trialId"],"status":t["status"],"values":{k:t["objectives"].get(k) for k in names}} for t in trials]
    return {"ok":True,"version":VERSION,"matrix":{"view":"objective-result-matrix","columns":names,"rows":rows,"automaticRanking":False,"automaticWinnerSelection":False},"boundary":BOUNDARY}

def parameter_effect_summary(payload):
    root=payload if isinstance(payload,dict) else {}; objective=_txt(_get(root,"objective","metric"),256); trials=normalize_trials(root)["results"]["trials"]
    rows=[]
    for p in sorted({k for t in trials for k in t["parameters"]}):
        pairs=[(_num(t["parameters"].get(p)),_num(t["objectives"].get(objective))) for t in trials if t["status"]=="completed"]
        pairs=[x for x in pairs if x[0] is not None and x[1] is not None]
        corr=None
        if len(pairs)>=2:
            xs=[x for x,_ in pairs]; ys=[y for _,y in pairs]
            if len(set(xs))>1 and len(set(ys))>1:
                mx,my=statistics.fmean(xs),statistics.fmean(ys); num=sum((x-mx)*(y-my) for x,y in pairs); den=(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))**0.5
                corr=num/den if den else None
        rows.append({"parameter":p,"objective":objective,"n":len(pairs),"pearsonAssociation":corr,"causalEffectInferred":False,"preferenceInferred":False})
    return {"ok":True,"version":VERSION,"rows":rows,"descriptiveAssociationOnly":True,"boundary":BOUNDARY}

def trial_comparability(payload):
    root=payload if isinstance(payload,dict) else {}; trials=normalize_trials(root)["results"]["trials"]
    dataset=_txt(root.get("datasetRef"),1024); split=_txt(root.get("splitRef"),1024); arch=_txt(root.get("architectureRef"),1024); env=_txt(root.get("environmentRef"),1024)
    rows=[]
    for t in trials:
        meta=t["metadata"]; dims={"dataset":{"study":dataset,"trial":_txt(meta.get("datasetRef"),1024) or dataset},"split":{"study":split,"trial":_txt(meta.get("splitRef"),1024) or split},"architecture":{"study":arch,"trial":_txt(meta.get("architectureRef"),1024) or arch},"environment":{"study":env,"trial":_txt(meta.get("environmentRef"),1024) or env}}
        for v in dims.values(): v["same"]=bool(v["study"] and v["trial"] and v["study"]==v["trial"]); v["unknown"]=not bool(v["study"] and v["trial"])
        rows.append({"trialId":t["trialId"],"dimensions":dims,"strictlyComparable":all(x["same"] for x in dims.values()),"automaticEquivalence":False})
    return {"ok":True,"version":VERSION,"trials":rows,"comparabilityExplicit":True,"boundary":BOUNDARY}

def single_objective_candidate_set(payload):
    root=payload if isinstance(payload,dict) else {}; objective=_txt(_get(root,"objective","metric"),256); direction=_direction(root.get("direction"))
    if not objective: return {"ok":False,"version":VERSION,"error":"objective required","boundary":BOUNDARY}
    if not direction: return {"ok":False,"version":VERSION,"error":"explicit objective direction min|max required","boundary":BOUNDARY}
    trials=normalize_trials(root)["results"]["trials"]
    rows=[{"trialId":t["trialId"],"value":_num(t["objectives"].get(objective)),"checkpointRef":t["checkpointRef"]} for t in trials if t["status"]=="completed" and _num(t["objectives"].get(objective)) is not None]
    if not rows: candidates=[]; extreme=None
    else:
        vals=[r["value"] for r in rows]; extreme=min(vals) if direction=="min" else max(vals); candidates=[r for r in rows if r["value"]==extreme]
    return {"ok":True,"version":VERSION,"objective":objective,"direction":direction,"extremeValue":extreme,"candidateSet":candidates,
            "winner":None,"automaticWinnerSelection":False,"automaticModelPromotion":False,"candidateSetRequiresReview":True,"boundary":BOUNDARY}

def _dominates(a,b,defs):
    any_better=False
    for o in defs:
        d=o["direction"]; name=o["name"]
        if not d: return False
        av,bv=_num(a["objectives"].get(name)),_num(b["objectives"].get(name))
        if av is None or bv is None: return False
        if d=="min":
            if av>bv: return False
            if av<bv: any_better=True
        else:
            if av<bv: return False
            if av>bv: any_better=True
    return any_better

def pareto_frontier(payload):
    root=payload if isinstance(payload,dict) else {}; defs=_objectives(root)
    if len(defs)<2: return {"ok":False,"version":VERSION,"error":"at least two objectives required","boundary":BOUNDARY}
    missing=[o["name"] for o in defs if not o["direction"]]
    if missing: return {"ok":False,"version":VERSION,"error":"explicit objective direction min|max required for every objective","missingDirections":missing,"boundary":BOUNDARY}
    trials=[t for t in normalize_trials(root)["results"]["trials"] if t["status"]=="completed" and all(_num(t["objectives"].get(o["name"])) is not None for o in defs)]
    front=[]
    for t in trials:
        if not any(_dominates(other,t,defs) for other in trials if other["trialId"]!=t["trialId"]):
            front.append({"trialId":t["trialId"],"objectives":{o["name"]:t["objectives"].get(o["name"]) for o in defs},"checkpointRef":t["checkpointRef"]})
    return {"ok":True,"version":VERSION,"objectives":defs,"nondominatedCandidateSet":front,"winner":None,"automaticRanking":False,"automaticWinnerSelection":False,"scientificSuperiorityInferred":False,"boundary":BOUNDARY}

def failed_pruned_audit(payload):
    trials=normalize_trials(payload)["results"]["trials"]
    rows=[{"trialId":t["trialId"],"status":t["status"],"reason":t["reason"],"parameters":t["parameters"],"provenanceRef":t["provenanceRef"]} for t in trials if t["status"] in ("failed","pruned","cancelled")]
    return {"ok":True,"version":VERSION,"rows":rows,"count":len(rows),"failureIsNotPerformanceEvidence":True,"boundary":BOUNDARY}

def search_visual_spec(payload):
    root=payload if isinstance(payload,dict) else {}; view=_txt(root.get("view"),64) or "search-progress"
    if view not in RESULT_VIEWS: return {"ok":False,"version":VERSION,"error":"unsupported result view","supportedViews":list(RESULT_VIEWS),"boundary":BOUNDARY}
    content={"studyId":_txt(root.get("studyId"),512),"view":view}
    if view=="search-progress": content["data"]=search_progress(root)["series"]
    elif view=="parameter-value-matrix": content["matrix"]=parameter_value_matrix(root)["matrix"]
    elif view=="objective-result-matrix": content["matrix"]=objective_result_matrix(root)["matrix"]
    elif view=="trial-status": content["audit"]=trial_status_audit(root)
    elif view=="pareto-frontier": content["frontier"]=pareto_frontier(root)
    else: content["trials"]=normalize_trials(root)["results"]["trials"]
    spec={"schema":"sc-lab-hyperparameter-search-visual-spec/0.141.4","version":VERSION,"visualType":view,"content":content,
          "automaticRanking":False,"automaticWinnerSelection":False,"candidateSetIsWinner":False,"boundary":BOUNDARY}
    spec["fingerprint"]=_fp(spec)
    return {"ok":True,"version":VERSION,"visualSpec":spec,"boundary":BOUNDARY}

def core_visual_handoff(payload):
    spec=search_visual_spec(payload)
    if not spec.get("ok"): return spec
    packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"objectType":"HyperparameterStudySearchResults","visualSpec":spec["visualSpec"],
            "canonicalVisualObjectAuthority":"platform-core","automaticWinnerSelection":False,"automaticModelPromotion":False}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}

def export_bundle(payload):
    root=payload if isinstance(payload,dict) else {}
    bundle={"schema":"sc-lab-hyperparameter-study-export/0.141.4","version":VERSION,"study":study_spec(root)["study"],"results":normalize_trials(root)["results"],
            "statusAudit":trial_status_audit(root),"parameterMatrix":parameter_value_matrix(root)["matrix"],"objectiveMatrix":objective_result_matrix(root)["matrix"],
            "automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False}
    bundle["fingerprint"]=_fp(bundle)
    return {"ok":True,"version":VERSION,"bundle":bundle,"boundary":BOUNDARY}

def snapshot(payload):
    root=payload if isinstance(payload,dict) else {}
    content={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"study":study_spec(root)["study"],"results":normalize_trials(root)["results"],
             "statusAudit":trial_status_audit(root),"parameterMatrix":parameter_value_matrix(root)["matrix"],"objectiveMatrix":objective_result_matrix(root)["matrix"]}
    fp=_fp(content)
    return {"ok":True,"version":VERSION,"snapshot":{**content,"snapshotId":f"hps-{fp[:24]}","fingerprint":fp},"generatedAt":_now(),"fingerprintExcludesGeneratedAt":True,"boundary":BOUNDARY}

def compare_snapshots(payload):
    root=payload if isinstance(payload,dict) else {}; left=_dict(root.get("left")); right=_dict(root.get("right"))
    def body(x):
        x=copy.deepcopy(x.get("snapshot") if isinstance(x.get("snapshot"),dict) else x)
        for k in ("snapshotId","fingerprint","generatedAt"): x.pop(k,None)
        return x
    a,b=body(left),body(right); keys=sorted(set(a)|set(b)); changes=[{"field":k,"left":a.get(k),"right":b.get(k)} for k in keys if a.get(k)!=b.get(k)]
    return {"ok":True,"version":VERSION,"equal":not changes,"changes":changes,"winnerInferred":False,"scientificSignificanceInferred":False,"boundary":BOUNDARY}

def reproducibility_packet(payload):
    snap=snapshot(payload)["snapshot"]
    packet={"schema":"sc-lab-hyperparameter-study-reproducibility-package/0.141.4","version":VERSION,"snapshot":snap,
            "requirements":["search-space definition","objective definitions and explicit directions","search strategy and seed","trial parameters and statuses","objective observations","dataset/split lineage","architecture/training configuration lineage","execution environment and provenance"],
            "reproducibilityCertified":False,"automaticWinnerSelection":False}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"package":packet,"reproducibilityCertified":False,"boundary":BOUNDARY}

def interpretation_boundary(_=None):
    return {"ok":True,"version":VERSION,"statements":["objective direction must be declared, not inferred","extreme trial is a review candidate, not a winner","Pareto membership is not scientific superiority","parameter association is descriptive and not causal","failed or pruned trial status is not performance evidence","optimization result is not scientific evidence"],"boundary":BOUNDARY}

def policy():
    return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"labExecutesSearch":False,"objectiveDirectionInferred":False,"automaticRanking":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"studySchema":STUDY_SCHEMA,"trialSchema":TRIAL_SCHEMA,"workspaceHandoffSchema":WORKSPACE_HANDOFF_SCHEMA,"coreHandoffSchema":CORE_HANDOFF_SCHEMA,"searchStrategies":list(SEARCH_STRATEGIES),"parameterTypes":list(PARAMETER_TYPES),"resultViews":list(RESULT_VIEWS),"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":["v0.140.0.1 installed-runtime integrity policy retained","v0.141.0 ML Experiment Workspace retained","v0.141.1 neural architecture/training configuration retained","v0.141.2 telemetry visualization retained","v0.141.3 explicit comparability retained","objective direction declared for candidate derivation"],"automaticGateWaiver":False,"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"hyperparameterStudySearchResults":True,"modelComparisonExperimentMatrixVersion":PREDECESSOR_VERSION,
            "trainingCurvesMetricsCheckpointVisualizationVersion":TELEMETRY_VERSION,"neuralArchitectureTrainingConfigurationVersion":ARCHITECTURE_VERSION,
            "machineLearningExperimentWorkspaceVersion":ML_WORKSPACE_VERSION,"scientificResearchOperatingSystemVersion":RESEARCH_OS_VERSION,
            "manifestIntegrityBaseline":INTEGRITY_BASELINE,"api_route_count":31,"workspaceExecutionAuthority":True,"labExecutesSearch":False,
            "objectiveDirectionInferred":False,"automaticRanking":False,"automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"searchSpaceDefinition":True,"studySpecification":True,"workspaceExecutionHandoff":True,"trialRegistry":True,
            "objectiveCatalog":True,"statusAudit":True,"budgetUtilization":True,"searchProgress":True,"parameterValueMatrix":True,"objectiveResultMatrix":True,
            "descriptiveParameterAssociation":True,"trialComparability":True,"singleObjectiveCandidateSet":True,"paretoCandidateSet":True,"failurePruningAudit":True,
            "visualSpecs":True,"coreVisualHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPacket":True,
            "automaticWinnerSelection":False,"automaticModelPromotion":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
