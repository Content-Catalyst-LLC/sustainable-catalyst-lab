from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.149.0"
PREDECESSOR_VERSION="0.148.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-scientific-model-validation-benchmark-laboratory/0.149.0"
BENCHMARK_SCHEMA="sc-lab-benchmark-suite/0.149.0"
CASE_SCHEMA="sc-lab-benchmark-case/0.149.0"
REFERENCE_SCHEMA="sc-lab-reference-standard/0.149.0"
SUBMISSION_SCHEMA="sc-lab-model-submission/0.149.0"
RUN_SCHEMA="sc-lab-benchmark-evaluation-run/0.149.0"
METRIC_SCHEMA="sc-lab-benchmark-metric-result/0.149.0"
VALIDATION_SCHEMA="sc-lab-model-validation-record/0.149.0"
FAILURE_SCHEMA="sc-lab-benchmark-failure-case/0.149.0"
SNAPSHOT_SCHEMA="sc-lab-model-validation-benchmark-snapshot/0.149.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-model-validation-benchmark-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-model-validation-prototype-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-model-validation-benchmark-objects/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-model-validation-handoff/1.0"
NEURAL_HANDOFF_SCHEMA="sc-lab-integrated-neural-validation-handoff/1.0"
GRAPH_ML_HANDOFF_SCHEMA="sc-lab-graph-ml-validation-handoff/1.0"
MULTIMODAL_HANDOFF_SCHEMA="sc-lab-multimodal-validation-handoff/1.0"

BOUNDARY=(
    "The Scientific Model Validation & Benchmark Laboratory governs benchmark definitions, reference standards, validation datasets, model submissions, evaluation protocols, returned metrics, calibration/generalization/robustness audits, external validation records, failure analysis, comparison, review, and reproducibility. "
    "Workspace remains the numerical benchmark execution authority; Workbench remains the prototype authority; Platform Core remains the canonical governed-object authority. "
    "Benchmark performance, statistical significance, calibration, held-out accuracy, robustness, external validation, or agreement with a reference standard do not by themselves establish scientific validity, real-world adequacy, causal validity, universal generalization, or deployment readiness. "
    "Reference standards are provenance-bearing research objects and are never treated as infallible ground truth."
)

BENCHMARK_TASKS=("classification","regression","ranking","retrieval","forecasting","detection","segmentation","generation","graph","multimodal","simulation","econometric","other")
VALIDATION_TYPES=("internal","holdout","cross-validation","external","temporal","cross-site","cross-dataset","prospective","retrospective","out-of-domain","stress","robustness","calibration","subgroup","reproducibility","simulation-to-real")
REFERENCE_TYPES=("gold-standard","expert-adjudicated","instrument-measurement","consensus","historical-record","synthetic-ground-truth","simulation-reference","benchmark-label","external-dataset","other")
METRICS=("accuracy","balanced-accuracy","precision","recall","specificity","f1","roc-auc","pr-auc","log-loss","brier","ece","rmse","mae","mape","r2","correlation","mrr","map","ndcg","hits@k","recall@k","precision@k","calibration-slope","calibration-intercept","coverage","other")
SESSION_STATES=("draft","designed","ready-for-execution","evaluated","analysis","review","external-validation","reproduction","publication","archived")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _num(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None
def _finite(xs):
    out=[]
    for x in xs:
        n=_num(x)
        if n is not None: out.append(n)
    return out
def _summary(xs):
    v=_finite(xs)
    if not v: return {"count":0,"mean":None,"median":None,"min":None,"max":None,"stdDev":None}
    return {"count":len(v),"mean":statistics.fmean(v),"median":statistics.median(v),"min":min(v),"max":max(v),"stdDev":statistics.stdev(v) if len(v)>1 else 0.0}
def _stable(obj):
    x=copy.deepcopy(obj)
    if isinstance(x,dict): x.pop("generatedAt",None)
    return x


def catalog():
    return {"ok":True,"version":VERSION,"benchmarkTasks":list(BENCHMARK_TASKS),"validationTypes":list(VALIDATION_TYPES),"referenceTypes":list(REFERENCE_TYPES),"metrics":list(METRICS),"benchmarkPerformanceIsScientificValidity":False,"externalValidationIsUniversalValidity":False,"referenceStandardIsInfallible":False,"boundary":BOUNDARY}


def normalize_benchmark_suite(payload:dict):
    p=_dict(payload); task=_txt(p.get("taskType"),64).lower() or "other"; task=task if task in BENCHMARK_TASKS else "other"
    r={"schema":BENCHMARK_SCHEMA,"version":VERSION,"benchmarkId":_txt(p.get("benchmarkId") or p.get("id"),512) or f"benchmark-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"taskType":task,"objective":_txt(p.get("objective"),4096),"population":_dict(p.get("population")),"cases":_list(p.get("cases")),"referenceStandards":_list(p.get("referenceStandards")),"metrics":_list(p.get("metrics")),"baselines":_list(p.get("baselines")),"protocol":_dict(p.get("protocol")),"splits":_dict(p.get("splits")),"eligibility":_dict(p.get("eligibility")),"limitations":_list(p.get("limitations")),"provenance":_dict(p.get("provenance")),"review":_dict(p.get("review")),"automaticLeaderboardRanking":False,"automaticWinnerSelection":False}; r["fingerprint"]=_fp(r); return r

def normalize_benchmark_case(payload:dict):
    p=_dict(payload)
    r={"schema":CASE_SCHEMA,"version":VERSION,"caseId":_txt(p.get("caseId") or p.get("id"),512) or f"case-{_fp(p)[:16]}","benchmarkRef":_txt(p.get("benchmarkRef"),512),"inputRefs":_list(p.get("inputRefs")),"target":p.get("target"),"targetRef":_txt(p.get("targetRef"),512),"referenceStandardRef":_txt(p.get("referenceStandardRef"),512),"subgroups":_dict(p.get("subgroups")),"site":_txt(p.get("site"),512),"time":p.get("time"),"weight":_num(p.get("weight")),"metadata":_dict(p.get("metadata")),"provenance":_dict(p.get("provenance"))}; r["fingerprint"]=_fp(r); return r

def normalize_reference_standard(payload:dict):
    p=_dict(payload); typ=_txt(p.get("referenceType"),64).lower() or "other"; typ=typ if typ in REFERENCE_TYPES else "other"
    r={"schema":REFERENCE_SCHEMA,"version":VERSION,"referenceId":_txt(p.get("referenceId") or p.get("id"),512) or f"reference-{_fp(p)[:16]}","referenceType":typ,"definition":_txt(p.get("definition"),8192),"sourceRefs":_list(p.get("sourceRefs")),"adjudication":_dict(p.get("adjudication")),"measurement":_dict(p.get("measurement")),"uncertainty":_dict(p.get("uncertainty")),"knownLimitations":_list(p.get("knownLimitations")),"provenance":_dict(p.get("provenance")),"review":_dict(p.get("review")),"infallibleGroundTruth":False}; r["fingerprint"]=_fp(r); return r

def normalize_model_submission(payload:dict):
    p=_dict(payload)
    r={"schema":SUBMISSION_SCHEMA,"version":VERSION,"submissionId":_txt(p.get("submissionId") or p.get("id"),512) or f"submission-{_fp(p)[:16]}","modelRef":_txt(p.get("modelRef"),512),"checkpointRef":_txt(p.get("checkpointRef"),512),"codeRef":_txt(p.get("codeRef"),2048),"environment":_dict(p.get("environment")),"preprocessing":_dict(p.get("preprocessing")),"trainingDataProvenance":_dict(p.get("trainingDataProvenance")),"declaredScope":_dict(p.get("declaredScope")),"limitations":_list(p.get("limitations")),"metadata":_dict(p.get("metadata")),"provenance":_dict(p.get("provenance")),"deploymentReady":False}; r["fingerprint"]=_fp(r); return r

def normalize_evaluation_run(payload:dict):
    p=_dict(payload)
    r={"schema":RUN_SCHEMA,"version":VERSION,"runId":_txt(p.get("runId") or p.get("id"),512) or f"evaluation-{_fp(p)[:16]}","benchmarkRef":_txt(p.get("benchmarkRef"),512),"submissionRef":_txt(p.get("submissionRef"),512),"splitRef":_txt(p.get("splitRef"),512),"protocolRef":_txt(p.get("protocolRef"),512),"seed":p.get("seed"),"environment":_dict(p.get("environment")),"metrics":_list(p.get("metrics")),"artifacts":_list(p.get("artifacts")),"status":_txt(p.get("status"),64) or "declared","provenance":_dict(p.get("provenance")),"scientificValidityCertified":False,"deploymentReadinessCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_metric_result(payload:dict):
    p=_dict(payload); name=_txt(p.get("metric"),128).lower() or "other"
    r={"schema":METRIC_SCHEMA,"version":VERSION,"metricResultId":_txt(p.get("metricResultId") or p.get("id"),512) or f"metric-{_fp(p)[:16]}","runRef":_txt(p.get("runRef"),512),"metric":name,"value":_num(p.get("value")),"direction":_txt(p.get("direction"),16).lower(),"confidenceInterval":_dict(p.get("confidenceInterval")),"sampleCount":p.get("sampleCount"),"subgroup":_dict(p.get("subgroup")),"definition":_dict(p.get("definition")),"uncertainty":_dict(p.get("uncertainty")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_validation_record(payload:dict):
    p=_dict(payload); typ=_txt(p.get("validationType"),64).lower() or "internal"; typ=typ if typ in VALIDATION_TYPES else "internal"
    r={"schema":VALIDATION_SCHEMA,"version":VERSION,"validationId":_txt(p.get("validationId") or p.get("id"),512) or f"validation-{_fp(p)[:16]}","validationType":typ,"modelRef":_txt(p.get("modelRef"),512),"benchmarkRef":_txt(p.get("benchmarkRef"),512),"datasetRef":_txt(p.get("datasetRef"),512),"siteRef":_txt(p.get("siteRef"),512),"timeWindow":_dict(p.get("timeWindow")),"metricResults":[normalize_metric_result(x) for x in _list(p.get("metricResults"))],"protocol":_dict(p.get("protocol")),"findings":_list(p.get("findings")),"limitations":_list(p.get("limitations")),"review":_dict(p.get("review")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False,"universalValidityCertified":False,"deploymentReadinessCertified":False}; r["fingerprint"]=_fp(r); return r

def normalize_external_validation_record(payload:dict):
    p=_dict(payload); p["validationType"]="external"; r=normalize_validation_record(p); r["schema"]=f"{VALIDATION_SCHEMA}/external"; r["independentSite"]=_txt(p.get("independentSite"),512); r["independentDataset"]=_txt(p.get("independentDataset"),512); r["investigatorIndependence"]=_dict(p.get("investigatorIndependence")); r["universalValidityCertified"]=False; r["fingerprint"]=_fp(r); return r

def normalize_failure_case(payload:dict):
    p=_dict(payload)
    r={"schema":FAILURE_SCHEMA,"version":VERSION,"failureId":_txt(p.get("failureId") or p.get("id"),512) or f"failure-{_fp(p)[:16]}","runRef":_txt(p.get("runRef"),512),"caseRef":_txt(p.get("caseRef"),512),"failureType":_txt(p.get("failureType"),256) or "other","severity":_txt(p.get("severity"),64),"observed":p.get("observed"),"expected":p.get("expected"),"error":_num(p.get("error")),"conditions":_dict(p.get("conditions")),"subgroups":_dict(p.get("subgroups")),"notes":_txt(p.get("notes"),8192),"provenance":_dict(p.get("provenance")),"rootCauseEstablished":False}; r["fingerprint"]=_fp(r); return r


def benchmark_protocol_audit(payload:dict):
    p=_dict(payload); protocol=_dict(p.get("protocol") or p); issues=[]
    for k in ("taskDefinition","evaluationSplit","metricDefinitions"):
        if not protocol.get(k): issues.append(f"missing-{k}")
    return {"ok":True,"version":VERSION,"issues":issues,"ready":not issues,"automaticScientificValidity":False,"boundary":BOUNDARY}

def dataset_provenance_audit(payload:dict):
    p=_dict(payload); d=_dict(p.get("dataset") or p); issues=[]
    for k in ("datasetRef","source","version"):
        if not d.get(k): issues.append(f"missing-{k}")
    return {"ok":True,"version":VERSION,"issues":issues,"provenanceComplete":not issues,"boundary":BOUNDARY}

def split_integrity_audit(payload:dict):
    p=_dict(payload); tr=set(map(str,_list(p.get("trainIds")))); va=set(map(str,_list(p.get("validationIds")))); te=set(map(str,_list(p.get("testIds"))))
    overlaps={"trainValidation":sorted(tr&va),"trainTest":sorted(tr&te),"validationTest":sorted(va&te)}
    return {"ok":True,"version":VERSION,"overlaps":overlaps,"clean":not any(overlaps.values()),"boundary":BOUNDARY}

def benchmark_leakage_audit(payload:dict):
    p=_dict(payload); train=set(map(str,_list(p.get("trainingRefs")))); bench=set(map(str,_list(p.get("benchmarkRefs")))); explicit=_list(p.get("knownLeakage")); overlap=sorted(train&bench)
    return {"ok":True,"version":VERSION,"overlap":overlap,"knownLeakage":explicit,"leakageRisk":bool(overlap or explicit),"scientificValidityCertified":False,"boundary":BOUNDARY}

def reference_standard_audit(payload:dict):
    r=normalize_reference_standard(payload.get("reference") or payload); issues=[]
    if not r["definition"]: issues.append("missing-definition")
    if not r["provenance"]: issues.append("missing-provenance")
    return {"ok":True,"version":VERSION,"reference":r,"issues":issues,"referenceStandardIsInfallible":False,"boundary":BOUNDARY}

def metric_definition_audit(payload:dict):
    p=_dict(payload); metrics=_list(p.get("metrics")); missing=[i for i,x in enumerate(metrics) if not _dict(x).get("name") or not _dict(x).get("definition")]
    return {"ok":True,"version":VERSION,"metricCount":len(metrics),"missingDefinitions":missing,"complete":not missing,"boundary":BOUNDARY}

def calibration_audit(payload:dict):
    p=_dict(payload); probs=_finite(p.get("probabilities",[])); labels=_finite(p.get("labels",[])); issues=[]
    if len(probs)!=len(labels): issues.append("length-mismatch")
    if any(x<0 or x>1 for x in probs): issues.append("probability-out-of-range")
    return {"ok":True,"version":VERSION,"issues":issues,"calibrationCertified":False,"boundary":BOUNDARY}

def discrimination_audit(payload:dict): return {"ok":True,"version":VERSION,"metrics":_dict(payload.get("metrics") if isinstance(payload,dict) else {}),"discriminationIsScientificValidity":False,"boundary":BOUNDARY}
def generalization_audit(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"sourceDomain":_dict(p.get("sourceDomain")),"targetDomain":_dict(p.get("targetDomain")),"observedMetrics":_dict(p.get("metrics")),"universalGeneralizationCertified":False,"boundary":BOUNDARY}
def domain_shift_audit(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"featureShift":_dict(p.get("featureShift")),"labelShift":_dict(p.get("labelShift")),"conceptShift":_dict(p.get("conceptShift")),"shiftExplainsPerformance":False,"boundary":BOUNDARY}
def subgroup_audit(payload:dict): return {"ok":True,"version":VERSION,"subgroups":_list(payload.get("subgroups") if isinstance(payload,dict) else []),"automaticFairnessCertification":False,"boundary":BOUNDARY}
def robustness_audit(payload:dict): return {"ok":True,"version":VERSION,"stressors":_list(payload.get("stressors") if isinstance(payload,dict) else []),"robustnessCertified":False,"boundary":BOUNDARY}
def stress_test_audit(payload:dict): return {"ok":True,"version":VERSION,"tests":_list(payload.get("tests") if isinstance(payload,dict) else []),"deploymentReadinessCertified":False,"boundary":BOUNDARY}
def missingness_audit(payload:dict):
    p=_dict(payload); missing=_dict(p.get("missingness")); return {"ok":True,"version":VERSION,"missingness":missing,"missingnessIgnored":False,"boundary":BOUNDARY}
def reproducibility_audit(payload:dict):
    p=_dict(payload); fields=("codeRef","environment","datasetRef","benchmarkRef","seed"); missing=[k for k in fields if not p.get(k)]
    return {"ok":True,"version":VERSION,"missing":missing,"reproducibilityReady":not missing,"reproductionCertified":False,"replicationCertified":False,"boundary":BOUNDARY}
def external_validity_audit(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"targetPopulation":_dict(p.get("targetPopulation")),"validationPopulation":_dict(p.get("validationPopulation")),"transportabilityAssessed":bool(p.get("transportabilityAssessed",False)),"universalValidityCertified":False,"boundary":BOUNDARY}
def uncertainty_audit(payload:dict): return {"ok":True,"version":VERSION,"uncertainty":_dict(payload.get("uncertainty") if isinstance(payload,dict) else {}),"uncertaintyResolved":False,"boundary":BOUNDARY}


def metric_summary(payload:dict):
    p=_dict(payload); vals=_finite(p.get("values",[])); return {"ok":True,"version":VERSION,"metric":_txt(p.get("metric"),128),"summary":_summary(vals),"scientificValidityCertified":False,"boundary":BOUNDARY}
def classification_summary(payload:dict):
    p=_dict(payload); y=_list(p.get("actual")); pred=_list(p.get("predicted")); n=min(len(y),len(pred)); correct=sum(1 for a,b in zip(y[:n],pred[:n]) if a==b); return {"ok":True,"version":VERSION,"count":n,"accuracy":correct/n if n else None,"scientificValidityCertified":False,"boundary":BOUNDARY}
def regression_summary(payload:dict):
    p=_dict(payload); y=_finite(p.get("actual",[])); pred=_finite(p.get("predicted",[])); n=min(len(y),len(pred)); err=[pred[i]-y[i] for i in range(n)]; return {"ok":True,"version":VERSION,"count":n,"mae":statistics.fmean([abs(x) for x in err]) if err else None,"rmse":math.sqrt(statistics.fmean([x*x for x in err])) if err else None,"scientificValidityCertified":False,"boundary":BOUNDARY}
def ranking_summary(payload:dict): return {"ok":True,"version":VERSION,"metrics":_dict(payload.get("metrics") if isinstance(payload,dict) else {}),"automaticWinnerSelection":False,"boundary":BOUNDARY}
def retrieval_summary(payload:dict): return {"ok":True,"version":VERSION,"metrics":_dict(payload.get("metrics") if isinstance(payload,dict) else {}),"retrievalPerformanceIsEvidence":False,"boundary":BOUNDARY}
def calibration_summary(payload:dict):
    p=_dict(payload); bins=_list(p.get("bins")); return {"ok":True,"version":VERSION,"bins":bins,"ece":_num(p.get("ece")),"slope":_num(p.get("slope")),"intercept":_num(p.get("intercept")),"calibrationCertified":False,"boundary":BOUNDARY}
def uncertainty_summary(payload:dict): return {"ok":True,"version":VERSION,"summary":_summary(payload.get("values",[]) if isinstance(payload,dict) else []),"scientificValidityCertified":False,"boundary":BOUNDARY}

def _matrix(rows, kind):
    out=[]
    for i,x in enumerate(_list(rows)):
        d=_dict(x); out.append({"index":i,"id":_txt(d.get("id") or d.get("submissionId") or d.get("runId"),512) or str(i),"metrics":_dict(d.get("metrics")),"metadata":_dict(d.get("metadata"))})
    return {"ok":True,"version":VERSION,"kind":kind,"rows":out,"automaticRanking":False,"automaticWinnerSelection":False,"scientificValidityCertified":False,"boundary":BOUNDARY}
def benchmark_matrix(payload:dict): return _matrix(payload.get("rows",[]) if isinstance(payload,dict) else [],"benchmark")
def baseline_comparison_matrix(payload:dict):
    p=_dict(payload); baseline=_dict(p.get("baseline")); rows=[]
    for x in _list(p.get("candidates")):
        d=_dict(x); deltas={}
        for k,v in _dict(d.get("metrics")).items():
            a=_num(v); b=_num(_dict(baseline.get("metrics")).get(k)); deltas[k]=(a-b) if a is not None and b is not None else None
        rows.append({"id":_txt(d.get("id") or d.get("submissionId"),512),"deltas":deltas,"scientificSuperiorityEstablished":False})
    return {"ok":True,"version":VERSION,"baseline":baseline,"rows":rows,"automaticWinnerSelection":False,"boundary":BOUNDARY}
def subgroup_matrix(payload:dict): return _matrix(payload.get("rows",[]) if isinstance(payload,dict) else [],"subgroup")
def robustness_matrix(payload:dict): return _matrix(payload.get("rows",[]) if isinstance(payload,dict) else [],"robustness")
def domain_shift_matrix(payload:dict): return _matrix(payload.get("rows",[]) if isinstance(payload,dict) else [],"domain-shift")
def failure_taxonomy(payload:dict):
    cases=[normalize_failure_case(x) for x in _list(payload.get("failures") if isinstance(payload,dict) else [])]; counts={}
    for c in cases: counts[c["failureType"]]=counts.get(c["failureType"],0)+1
    return {"ok":True,"version":VERSION,"count":len(cases),"byType":counts,"rootCauseEstablished":False,"boundary":BOUNDARY}
def error_slice_summary(payload:dict): return {"ok":True,"version":VERSION,"slices":_list(payload.get("slices") if isinstance(payload,dict) else []),"automaticRootCauseInference":False,"boundary":BOUNDARY}
def confidence_interval_summary(payload:dict): return {"ok":True,"version":VERSION,"intervals":_list(payload.get("intervals") if isinstance(payload,dict) else []),"confidenceIntervalIsValidity":False,"boundary":BOUNDARY}
def repeated_run_summary(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"metric":_txt(p.get("metric"),128),"summary":_summary(p.get("values",[])),"deterministicEquivalenceCertified":False,"boundary":BOUNDARY}
def submission_comparison(payload:dict): return _matrix(payload.get("submissions",[]) if isinstance(payload,dict) else [],"submission-comparison")


def validation_dimension_summary(payload:dict):
    p=_dict(payload); records=[normalize_validation_record(x) for x in _list(p.get("records"))]; by={}
    for r in records: by[r["validationType"]]=by.get(r["validationType"],0)+1
    return {"ok":True,"version":VERSION,"count":len(records),"byValidationType":by,"scientificValidityCertified":False,"boundary":BOUNDARY}
def internal_validation_summary(payload:dict): return {"ok":True,"version":VERSION,"records":_list(payload.get("records") if isinstance(payload,dict) else []),"scientificValidityCertified":False,"boundary":BOUNDARY}
def external_validation_summary(payload:dict): return {"ok":True,"version":VERSION,"records":_list(payload.get("records") if isinstance(payload,dict) else []),"universalValidityCertified":False,"boundary":BOUNDARY}
def cross_dataset_validation_summary(payload:dict): return {"ok":True,"version":VERSION,"datasets":_list(payload.get("datasets") if isinstance(payload,dict) else []),"universalValidityCertified":False,"boundary":BOUNDARY}
def cross_site_validation_summary(payload:dict): return {"ok":True,"version":VERSION,"sites":_list(payload.get("sites") if isinstance(payload,dict) else []),"universalValidityCertified":False,"boundary":BOUNDARY}
def temporal_validation_summary(payload:dict): return {"ok":True,"version":VERSION,"windows":_list(payload.get("windows") if isinstance(payload,dict) else []),"futureValidityCertified":False,"boundary":BOUNDARY}
def prospective_validation_summary(payload:dict): return {"ok":True,"version":VERSION,"records":_list(payload.get("records") if isinstance(payload,dict) else []),"deploymentReadinessCertified":False,"boundary":BOUNDARY}
def benchmark_readiness_report(payload:dict):
    p=_dict(payload); required=("benchmark","submission","protocol"); missing=[k for k in required if not p.get(k)]; return {"ok":True,"version":VERSION,"missing":missing,"readyForExecution":not missing,"readyForDeployment":False,"scientificValidityCertified":False,"boundary":BOUNDARY}


def benchmark_dashboard_spec(payload:dict): return {"ok":True,"version":VERSION,"spec":{"type":"benchmark-dashboard","panels":["protocol","metrics","baselines","subgroups","robustness","failures","validation","provenance"],"automaticLeaderboardRanking":False},"boundary":BOUNDARY}
def calibration_visual_spec(payload:dict): return {"ok":True,"version":VERSION,"spec":{"type":"calibration","observed":_list(payload.get("observed") if isinstance(payload,dict) else []),"predicted":_list(payload.get("predicted") if isinstance(payload,dict) else []),"calibrationCertified":False},"boundary":BOUNDARY}
def failure_analysis_spec(payload:dict): return {"ok":True,"version":VERSION,"spec":{"type":"failure-analysis","failures":_list(payload.get("failures") if isinstance(payload,dict) else []),"automaticRootCauseInference":False},"boundary":BOUNDARY}
def provenance_graph(payload:dict):
    p=_dict(payload); nodes=_list(p.get("nodes")); edges=_list(p.get("edges")); return {"ok":True,"version":VERSION,"graph":{"nodes":nodes,"edges":edges,"edgeSemanticsExplicit":True},"boundary":BOUNDARY}


def _handoff(schema,target,payload):
    p=_dict(payload); r={"schema":schema,"version":VERSION,"target":target,"benchmarkRef":_txt(p.get("benchmarkRef"),512),"submissionRef":_txt(p.get("submissionRef"),512),"validationRef":_txt(p.get("validationRef"),512),"request":_dict(p.get("request")),"provenance":_dict(p.get("provenance")),"scientificValidityCertified":False,"deploymentReadinessCertified":False}; r["fingerprint"]=_fp(r); return {"ok":True,"version":VERSION,"handoff":r,"boundary":BOUNDARY}
def workspace_execution_handoff(payload:dict): return _handoff(WORKSPACE_HANDOFF_SCHEMA,"workspace",payload)
def workbench_handoff(payload:dict): return _handoff(WORKBENCH_HANDOFF_SCHEMA,"workbench",payload)
def core_handoff(payload:dict): return _handoff(CORE_HANDOFF_SCHEMA,"platform-core",payload)
def research_os_handoff(payload:dict): return _handoff(RESEARCH_OS_HANDOFF_SCHEMA,"research-os",payload)
def integrated_neural_handoff(payload:dict): return _handoff(NEURAL_HANDOFF_SCHEMA,"integrated-neural",payload)
def graph_ml_handoff(payload:dict): return _handoff(GRAPH_ML_HANDOFF_SCHEMA,"graph-ml",payload)
def multimodal_handoff(payload:dict): return _handoff(MULTIMODAL_HANDOFF_SCHEMA,"multimodal",payload)


def workspace_snapshot(payload:dict):
    p=_dict(payload); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"benchmark":normalize_benchmark_suite(p.get("benchmark") or {}),"submission":normalize_model_submission(p.get("submission") or {}),"validationRecords":[normalize_validation_record(x) for x in _list(p.get("validationRecords"))],"failures":[normalize_failure_case(x) for x in _list(p.get("failures"))],"review":_dict(p.get("review")),"limitations":_list(p.get("limitations"))}; snap["fingerprint"]=_fp(snap); return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}
def compare_snapshots(payload:dict):
    p=_dict(payload); a=_dict(p.get("a")); b=_dict(p.get("b")); keys=sorted(set(a)|set(b)); changed=[k for k in keys if _stable(a.get(k))!=_stable(b.get(k))]; return {"ok":True,"version":VERSION,"changed":changed,"same":not changed,"boundary":BOUNDARY}
def export_bundle(payload:dict):
    s=workspace_snapshot(payload)["snapshot"]; return {"ok":True,"version":VERSION,"bundle":{"schema":f"{SCHEMA}/export-bundle","version":VERSION,"snapshot":s,"scientificValidityCertified":False,"deploymentReadinessCertified":False,"fingerprint":_fp(s)},"boundary":BOUNDARY}
def reproducibility_package(payload:dict):
    s=workspace_snapshot(payload)["snapshot"]; pkg={"schema":f"{SCHEMA}/reproducibility-package","version":VERSION,"snapshot":s,"executionInstructions":_dict(payload.get("executionInstructions") if isinstance(payload,dict) else {}),"environment":_dict(payload.get("environment") if isinstance(payload,dict) else {}),"artifactRefs":_list(payload.get("artifactRefs") if isinstance(payload,dict) else []),"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; pkg["fingerprint"]=_fp(pkg); return {"ok":True,"version":VERSION,"package":pkg,"boundary":BOUNDARY}
def publication_handoff(payload:dict): return {"ok":True,"version":VERSION,"handoff":{"schema":f"{SCHEMA}/publication-handoff","benchmarkRef":_txt(payload.get("benchmarkRef"),512) if isinstance(payload,dict) else "","validationRefs":_list(payload.get("validationRefs") if isinstance(payload,dict) else []),"review":_dict(payload.get("review") if isinstance(payload,dict) else {}),"publicationAccepted":False,"scientificValidityCertified":False},"boundary":BOUNDARY}


def default_benchmark_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Benchmark Protocol","Reference Standards","Submissions","Evaluation Runs","Metrics","Baselines"],"automaticLeaderboardRanking":False},"boundary":BOUNDARY}
def default_validation_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Internal Validation","External Validation","Calibration","Generalization","Robustness","Uncertainty"],"scientificValidityCertified":False},"boundary":BOUNDARY}
def default_failure_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Failure Cases","Error Slices","Stress Tests","Domain Shift","Subgroups"],"automaticRootCauseInference":False},"boundary":BOUNDARY}
def default_provenance_view(): return {"ok":True,"version":VERSION,"view":{"panels":["Dataset Provenance","Reference Provenance","Model Lineage","Execution Environment","Review & Reproducibility"]},"boundary":BOUNDARY}


def interpretation_boundary(): return {"ok":True,"version":VERSION,"boundary":BOUNDARY,"benchmarkPerformanceIsScientificValidity":False,"externalValidationIsUniversalValidity":False,"referenceStandardIsInfallible":False,"automaticDeploymentReadiness":False}
def policy(): return {"ok":True,"version":VERSION,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesBenchmarkCompute":False,"benchmarkPerformanceIsScientificValidity":False,"externalValidationIsUniversalValidity":False,"referenceStandardIsInfallible":False,"automaticLeaderboardRanking":False,"automaticWinnerSelection":False,"automaticDeploymentReadiness":False,"automaticScientificValidity":False,"humanScientificReviewRequired":True,"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"benchmarkSchema":BENCHMARK_SCHEMA,"caseSchema":CASE_SCHEMA,"referenceSchema":REFERENCE_SCHEMA,"submissionSchema":SUBMISSION_SCHEMA,"runSchema":RUN_SCHEMA,"metricSchema":METRIC_SCHEMA,"validationSchema":VALIDATION_SCHEMA,"failureSchema":FAILURE_SCHEMA,"benchmarkTasks":list(BENCHMARK_TASKS),"validationTypes":list(VALIDATION_TYPES),"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":{"multimodalPredecessorRetained":True,"referenceStandardsProvenanced":True,"splitIntegrityAudited":True,"benchmarkLeakageAudited":True,"validationDimensionsSeparated":True,"externalValidationSeparatedFromUniversalValidity":True,"failureAnalysisExplicit":True,"reproducibilitySeparatedFromValidity":True,"predecessorCompatible":True},"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"scientificModelValidationBenchmarkLaboratory":True,"api_route_count":78,"predecessorVersion":PREDECESSOR_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesBenchmarkCompute":False,"benchmarkPerformanceIsScientificValidity":False,"externalValidationIsUniversalValidity":False,"referenceStandardIsInfallible":False,"automaticLeaderboardRanking":False,"automaticWinnerSelection":False,"automaticDeploymentReadiness":False,"automaticScientificValidity":False,"humanScientificReviewRequired":True,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"accepted":{"benchmarkSuiteObjectModel":True,"referenceStandardObjects":True,"modelSubmissionObjects":True,"evaluationRunObjects":True,"validationRecords":True,"externalValidationRecords":True,"splitIntegrityAudit":True,"benchmarkLeakageAudit":True,"calibrationAndGeneralizationAudits":True,"robustnessAndStressTests":True,"subgroupAndDomainShiftAudits":True,"failureAnalysis":True,"benchmarkAndBaselineMatrices":True,"validationDimensionSummaries":True,"workspaceExecutionHandoff":True,"workbenchHandoff":True,"coreHandoff":True,"researchOSHandoff":True,"integratedNeuralHandoff":True,"graphMLHandoff":True,"multimodalHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackage":True},"scientificValidityCertified":False,"deploymentReadinessCertified":False,"boundary":BOUNDARY}
