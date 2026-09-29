from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.144.0"
PREDECESSOR_VERSION="0.143.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-statistical-econometric-research-workspace/0.144.0"
SESSION_SCHEMA="sc-lab-statistical-econometric-research-session/0.144.0"
DATASET_SCHEMA="sc-lab-statistical-dataset/0.144.0"
ESTIMAND_SCHEMA="sc-lab-econometric-estimand/0.144.0"
SPECIFICATION_SCHEMA="sc-lab-statistical-model-specification/0.144.0"
ESTIMATE_SCHEMA="sc-lab-statistical-estimate-result/0.144.0"
DIAGNOSTIC_SCHEMA="sc-lab-statistical-diagnostic-result/0.144.0"
SNAPSHOT_SCHEMA="sc-lab-statistical-econometric-workspace-snapshot/0.144.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-statistical-econometric-execution-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-statistical-research-objects/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-statistical-econometric-handoff/1.0"

BOUNDARY=(
    "The Statistical & Econometric Research Workspace governs research questions, estimands, model specifications, returned estimates, diagnostics, robustness checks, visualizations, and reproducibility state. "
    "Workspace remains execution authority for statistical/econometric runtimes and numerical estimation; Platform Core remains canonical governed-object authority. "
    "A coefficient is not the estimand itself, statistical significance is not substantive importance, association is not causation, a fitted model is not scientific validity, diagnostic passage is not proof that assumptions hold, and model-selection output is not an automatic scientific winner."
)

MODEL_FAMILIES=(
    "descriptive","ols","wls","gls","logit","probit","poisson","negative-binomial","quantile-regression",
    "fixed-effects","random-effects","first-difference","between-effects","iv-2sls","liml","gmm","difference-in-differences",
    "event-study","regression-discontinuity","synthetic-control","arima","sarima","var","vecm","cointegration","state-space",
    "survival","duration","hazard","bayesian-regression","hierarchical","other"
)
ANALYSIS_FAMILIES=(
    "descriptive-statistics","regression","generalized-linear-model","panel-data","instrumental-variables","gmm",
    "difference-in-differences","event-study","regression-discontinuity","time-series","forecasting","cointegration",
    "robustness","sensitivity","diagnostics","model-comparison","estimand-comparison","uncertainty","reproducibility"
)
ESTIMATORS=("ols","ml","quasi-ml","2sls","liml","gmm","within","between","first-difference","bayesian","m-estimator","quantile","other")
COVARIANCE_ESTIMATORS=("classical","hc0","hc1","hc2","hc3","cluster","two-way-cluster","hac-newey-west","driscoll-kraay","bootstrap","jackknife","posterior","other")
SESSION_STATES=("draft","designed","ready-for-execution","executed","analysis","review","reproduction","publication","archived")
OBJECT_KINDS=("dataset","variable","estimand","specification","estimate","diagnostic","robustness-check","sensitivity-analysis","visualization","review","reproducibility-package","publication","other")
VARIABLE_ROLES=("outcome","treatment","exposure","predictor","control","instrument","fixed-effect","cluster","weight","time","entity","offset","stratum","other")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _num(v): return float(v) if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v)) else None
def _uniq(xs):
    out=[]; seen=set()
    for x in xs:
        k=_canon(x)
        if k not in seen: seen.add(k); out.append(x)
    return out

def _norm_name(v): return _txt(v,256)

def model_catalog():
    return {"ok":True,"version":VERSION,"modelFamilies":list(MODEL_FAMILIES),"estimators":list(ESTIMATORS),"covarianceEstimators":list(COVARIANCE_ESTIMATORS),"automaticWinnerSelection":False,"boundary":BOUNDARY}

def normalize_variable(payload:dict,index:int=0):
    p=_dict(payload); role=_txt(p.get("role"),64).lower() or "other"
    if role not in VARIABLE_ROLES: role="other"
    rec={"variableId":_txt(p.get("variableId") or p.get("id"),512) or f"variable-{index+1}-{_fp(p)[:12]}","name":_norm_name(p.get("name")),"label":_txt(p.get("label"),512),"role":role,"dataType":_txt(p.get("dataType") or p.get("type"),64),"unit":_txt(p.get("unit"),128),"measurementLevel":_txt(p.get("measurementLevel"),64),"transformation":_dict(p.get("transformation")),"missingValuePolicy":_dict(p.get("missingValuePolicy")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata"))}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_dataset(payload:dict):
    p=_dict(payload); vars=[normalize_variable(x,i) for i,x in enumerate(_list(p.get("variables")))]
    rec={"schema":DATASET_SCHEMA,"version":VERSION,"datasetId":_txt(p.get("datasetId") or p.get("id"),512) or f"dataset-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"sourceRefs":[_txt(x,2048) for x in _list(p.get("sourceRefs")) if _txt(x,2048)],"variables":vars,"rowCount":p.get("rowCount") if isinstance(p.get("rowCount"),int) and p.get("rowCount")>=0 else None,"entityIdVariable":_txt(p.get("entityIdVariable"),256),"timeVariable":_txt(p.get("timeVariable"),256),"weightVariable":_txt(p.get("weightVariable"),256),"samplingDesign":_dict(p.get("samplingDesign")),"missingness":_dict(p.get("missingness")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata"))}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_estimand(payload:dict):
    p=_dict(payload)
    rec={"schema":ESTIMAND_SCHEMA,"version":VERSION,"estimandId":_txt(p.get("estimandId") or p.get("id"),512) or f"estimand-{_fp(p)[:16]}","label":_txt(p.get("label"),1024),"population":_txt(p.get("population"),2048),"outcome":_txt(p.get("outcome"),512),"treatmentOrExposure":_txt(p.get("treatmentOrExposure"),512),"contrast":_txt(p.get("contrast"),2048),"timeHorizon":_txt(p.get("timeHorizon"),512),"identificationStrategy":_txt(p.get("identificationStrategy"),2048),"assumptions":[_txt(x,2048) for x in _list(p.get("assumptions")) if _txt(x,2048)],"causal":bool(p.get("causal",False)),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata")),"estimateIsEstimand":False,"identifiedByModelFitAlone":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_specification(payload:dict):
    p=_dict(payload); fam=_txt(p.get("modelFamily"),64).lower() or "other"; est=_txt(p.get("estimator"),64).lower() or "other"; cov=_txt(p.get("covarianceEstimator"),64).lower() or "classical"
    if fam not in MODEL_FAMILIES: fam="other"
    if est not in ESTIMATORS: est="other"
    if cov not in COVARIANCE_ESTIMATORS: cov="other"
    rec={"schema":SPECIFICATION_SCHEMA,"version":VERSION,"specificationId":_txt(p.get("specificationId") or p.get("id"),512) or f"spec-{_fp(p)[:16]}","estimandRef":_txt(p.get("estimandRef"),512),"datasetRef":_txt(p.get("datasetRef"),512),"modelFamily":fam,"estimator":est,"formula":_txt(p.get("formula"),4096),"outcome":_txt(p.get("outcome"),512),"predictors":[_txt(x,512) for x in _list(p.get("predictors")) if _txt(x,512)],"controls":[_txt(x,512) for x in _list(p.get("controls")) if _txt(x,512)],"fixedEffects":[_txt(x,512) for x in _list(p.get("fixedEffects")) if _txt(x,512)],"instruments":[_txt(x,512) for x in _list(p.get("instruments")) if _txt(x,512)],"weights":_txt(p.get("weights"),512),"clusterVariables":[_txt(x,512) for x in _list(p.get("clusterVariables")) if _txt(x,512)],"covarianceEstimator":cov,"lagStructure":_dict(p.get("lagStructure")),"transformations":_list(p.get("transformations")),"sampleRestriction":_dict(p.get("sampleRestriction")),"assumptions":[_txt(x,2048) for x in _list(p.get("assumptions")) if _txt(x,2048)],"software":_dict(p.get("software")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata")),"automaticCausalIdentification":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_estimate(payload:dict,index:int=0):
    p=_dict(payload); coef=[]
    for i,x in enumerate(_list(p.get("coefficients"))):
        if not isinstance(x,dict): continue
        coef.append({"term":_txt(x.get("term") or x.get("name"),512) or f"term-{i+1}","estimate":_num(x.get("estimate")),"stdError":_num(x.get("stdError")),"statistic":_num(x.get("statistic")),"pValue":_num(x.get("pValue")),"confLow":_num(x.get("confLow")),"confHigh":_num(x.get("confHigh")),"df":_num(x.get("df")),"unit":_txt(x.get("unit"),128)})
    rec={"schema":ESTIMATE_SCHEMA,"version":VERSION,"estimateId":_txt(p.get("estimateId") or p.get("id"),512) or f"estimate-{index+1}-{_fp(p)[:12]}","specificationRef":_txt(p.get("specificationRef"),512),"estimandRef":_txt(p.get("estimandRef"),512),"runRef":_txt(p.get("runRef"),512),"coefficients":coef,"fit":_dict(p.get("fit")),"sample":_dict(p.get("sample")),"covariance":_dict(p.get("covariance")),"marginalEffects":_list(p.get("marginalEffects")),"predictionsRef":_txt(p.get("predictionsRef"),2048),"residualsRef":_txt(p.get("residualsRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata")),"scientificValidityCertified":False,"causalEffectCertified":False,"significanceIsSubstantiveImportance":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_diagnostics(payload:dict,index:int=0):
    p=_dict(payload)
    rec={"schema":DIAGNOSTIC_SCHEMA,"version":VERSION,"diagnosticId":_txt(p.get("diagnosticId") or p.get("id"),512) or f"diagnostic-{index+1}-{_fp(p)[:12]}","specificationRef":_txt(p.get("specificationRef"),512),"estimateRef":_txt(p.get("estimateRef"),512),"kind":_txt(p.get("kind"),128),"statistic":_num(p.get("statistic")),"pValue":_num(p.get("pValue")),"threshold":_num(p.get("threshold")),"status":_txt(p.get("status"),64),"details":_dict(p.get("details")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"assumptionProven":False,"diagnosticPassIsProof":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_session(payload:dict):
    p=_dict(payload); state=_txt(p.get("state"),64).lower() or "draft"
    if state not in SESSION_STATES: state="draft"
    rec={"schema":SESSION_SCHEMA,"version":VERSION,"sessionId":_txt(p.get("sessionId") or p.get("id"),512) or f"stats-session-{_fp(p)[:16]}","projectRef":_txt(p.get("projectRef"),512),"title":_txt(p.get("title"),1024) or "Statistical & econometric research session","state":state,"datasets":[normalize_dataset(x) for x in _list(p.get("datasets"))],"estimands":[normalize_estimand(x) for x in _list(p.get("estimands"))],"specifications":[normalize_specification(x) for x in _list(p.get("specifications"))],"estimates":[normalize_estimate(x,i) for i,x in enumerate(_list(p.get("estimates")))],"diagnostics":[normalize_diagnostics(x,i) for i,x in enumerate(_list(p.get("diagnostics")))],"robustnessChecks":_list(p.get("robustnessChecks")),"sensitivityAnalyses":_list(p.get("sensitivityAnalyses")),"limitations":[_txt(x,4096) for x in _list(p.get("limitations")) if _txt(x,4096)],"review":_dict(p.get("review")),"metadata":_dict(p.get("metadata"))}
    stable=copy.deepcopy(rec); rec["fingerprint"]=_fp(stable); return rec

def workspace_state(payload:dict):
    s=normalize_session(payload)
    return {"ok":True,"version":VERSION,"workspace":s,"counts":{"datasets":len(s["datasets"]),"estimands":len(s["estimands"]),"specifications":len(s["specifications"]),"estimates":len(s["estimates"]),"diagnostics":len(s["diagnostics"])},"scientificValidityCertified":False,"boundary":BOUNDARY}

def specification_audit(payload:dict):
    spec=normalize_specification(_dict(payload).get("specification",payload)); issues=[]
    if not spec["datasetRef"]: issues.append("datasetRef-missing")
    if not spec["outcome"]: issues.append("outcome-missing")
    if not spec["formula"] and not spec["predictors"]: issues.append("formula-or-predictors-missing")
    if spec["modelFamily"]=="iv-2sls" and not spec["instruments"]: issues.append("iv-instruments-missing")
    return {"ok":True,"version":VERSION,"specification":spec,"issues":issues,"clean":not issues,"cleanDoesNotCertifyCorrectSpecification":True,"boundary":BOUNDARY}

def identification_audit(payload:dict):
    p=_dict(payload); e=normalize_estimand(_dict(p.get("estimand"))); s=normalize_specification(_dict(p.get("specification"))); issues=[]
    if e["causal"] and not e["identificationStrategy"]: issues.append("causal-estimand-without-identification-strategy")
    if e["causal"] and not e["assumptions"] and not s["assumptions"]: issues.append("causal-identification-assumptions-not-declared")
    if s["modelFamily"] in ("iv-2sls","liml") and not s["instruments"]: issues.append("instrument-set-missing")
    return {"ok":True,"version":VERSION,"issues":issues,"identifiedByAudit":False,"causalIdentificationCertified":False,"boundary":BOUNDARY}

def assumption_audit(payload:dict):
    p=_dict(payload); declared=[_txt(x,2048) for x in _list(p.get("declared")) if _txt(x,2048)]; diagnostics=[normalize_diagnostics(x,i) for i,x in enumerate(_list(p.get("diagnostics")))]
    return {"ok":True,"version":VERSION,"declaredAssumptions":declared,"diagnostics":diagnostics,"diagnosticCount":len(diagnostics),"assumptionsProven":False,"diagnosticPassIsProof":False,"boundary":BOUNDARY}

def missingness_audit(payload:dict):
    p=_dict(payload); rows=[]
    for x in _list(p.get("variables")):
        if not isinstance(x,dict): continue
        n=x.get("n") if isinstance(x.get("n"),int) and x.get("n")>=0 else None; miss=x.get("missing") if isinstance(x.get("missing"),int) and x.get("missing")>=0 else None
        rate=(miss/n) if n and miss is not None else None
        rows.append({"variable":_norm_name(x.get("variable") or x.get("name")),"n":n,"missing":miss,"missingRate":rate})
    return {"ok":True,"version":VERSION,"rows":rows,"missingnessMechanismInferred":False,"automaticImputation":False,"boundary":BOUNDARY}

def _supplied_diag(payload,kind):
    p=_dict(payload); vals=_dict(p.get("diagnostic")); return {"ok":True,"version":VERSION,"kind":kind,"diagnostic":normalize_diagnostics({**vals,"kind":kind}),"computedByLab":False,"assumptionProven":False,"boundary":BOUNDARY}

def multicollinearity_audit(payload:dict): return _supplied_diag(payload,"multicollinearity")
def heteroskedasticity_audit(payload:dict): return _supplied_diag(payload,"heteroskedasticity")
def autocorrelation_audit(payload:dict): return _supplied_diag(payload,"autocorrelation")
def stationarity_audit(payload:dict): return _supplied_diag(payload,"stationarity")
def endogeneity_audit(payload:dict): return _supplied_diag(payload,"endogeneity")

def instrument_audit(payload:dict):
    p=_dict(payload); instruments=[_txt(x,512) for x in _list(p.get("instruments")) if _txt(x,512)]; stats=_dict(p.get("statistics"))
    return {"ok":True,"version":VERSION,"instruments":instruments,"statistics":stats,"relevanceCertified":False,"exogeneityCertified":False,"exclusionRestrictionCertified":False,"boundary":BOUNDARY}

def panel_structure_audit(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"entityVariable":_txt(p.get("entityVariable"),512),"timeVariable":_txt(p.get("timeVariable"),512),"entityCount":p.get("entityCount") if isinstance(p.get("entityCount"),int) else None,"timeCount":p.get("timeCount") if isinstance(p.get("timeCount"),int) else None,"balanced":p.get("balanced") if isinstance(p.get("balanced"),bool) else None,"panelStructureDeclared":bool(_txt(p.get("entityVariable"),512) and _txt(p.get("timeVariable"),512)),"panelAssumptionsCertified":False,"boundary":BOUNDARY}

def time_series_structure_audit(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"timeVariable":_txt(p.get("timeVariable"),512),"frequency":_txt(p.get("frequency"),128),"start":_txt(p.get("start"),128),"end":_txt(p.get("end"),128),"seasonality":_dict(p.get("seasonality")),"stationarityCertified":False,"cointegrationCertified":False,"boundary":BOUNDARY}

def coefficient_table(payload:dict):
    p=_dict(payload); estimates=[normalize_estimate(x,i) for i,x in enumerate(_list(p.get("estimates")))]; rows=[]
    for e in estimates:
        for c in e["coefficients"]: rows.append({"estimateId":e["estimateId"],"specificationRef":e["specificationRef"],**c})
    return {"ok":True,"version":VERSION,"rows":rows,"rowCount":len(rows),"statisticalSignificanceIsSubstantiveImportance":False,"boundary":BOUNDARY}

def fit_summary(payload:dict):
    estimates=[normalize_estimate(x,i) for i,x in enumerate(_list(_dict(payload).get("estimates")))]; rows=[{"estimateId":e["estimateId"],"specificationRef":e["specificationRef"],"fit":e["fit"],"sample":e["sample"]} for e in estimates]
    return {"ok":True,"version":VERSION,"rows":rows,"bestFitModel":None,"automaticRanking":False,"boundary":BOUNDARY}

def marginal_effects_summary(payload:dict):
    estimates=[normalize_estimate(x,i) for i,x in enumerate(_list(_dict(payload).get("estimates")))]; rows=[]
    for e in estimates:
        for x in e["marginalEffects"]:
            if isinstance(x,dict): rows.append({"estimateId":e["estimateId"],**copy.deepcopy(x)})
    return {"ok":True,"version":VERSION,"rows":rows,"marginalEffectIsCausalEffect":False,"boundary":BOUNDARY}

def residual_diagnostics(payload:dict):
    p=_dict(payload); supplied=_list(p.get("diagnostics")); return {"ok":True,"version":VERSION,"diagnostics":[normalize_diagnostics(x,i) for i,x in enumerate(supplied)],"residualDiagnosticsComputedByLab":False,"assumptionsProven":False,"boundary":BOUNDARY}

def robust_inference_summary(payload:dict):
    p=_dict(payload); rows=[]
    for x in _list(p.get("estimates")):
        if not isinstance(x,dict): continue
        rows.append({"label":_txt(x.get("label"),512),"covarianceEstimator":_txt(x.get("covarianceEstimator"),128),"estimate":_num(x.get("estimate")),"stdError":_num(x.get("stdError")),"confLow":_num(x.get("confLow")),"confHigh":_num(x.get("confHigh")),"pValue":_num(x.get("pValue"))})
    return {"ok":True,"version":VERSION,"rows":rows,"robustStandardErrorsDoNotFixIdentification":True,"boundary":BOUNDARY}

def specification_matrix(payload:dict):
    specs=[normalize_specification(x) for x in _list(_dict(payload).get("specifications"))]; fields=("modelFamily","estimator","formula","outcome","predictors","controls","fixedEffects","instruments","weights","clusterVariables","covarianceEstimator","lagStructure","sampleRestriction")
    return {"ok":True,"version":VERSION,"columns":[s["specificationId"] for s in specs],"rows":[{"field":f,"values":[copy.deepcopy(s.get(f)) for s in specs]} for f in fields],"automaticPreferredSpecification":None,"boundary":BOUNDARY}

def robustness_matrix(payload:dict):
    p=_dict(payload); checks=[x for x in _list(p.get("checks")) if isinstance(x,dict)]; metrics=sorted({str(k) for x in checks for k in _dict(x.get("metrics")).keys()})
    return {"ok":True,"version":VERSION,"columns":[_txt(x.get("label") or x.get("id"),512) for x in checks],"rows":[{"metric":m,"values":[_dict(x.get("metrics")).get(m) for x in checks]} for m in metrics],"robustnessIsValidityProof":False,"automaticWinnerSelection":False,"boundary":BOUNDARY}

def model_comparison(payload:dict):
    p=_dict(payload); rows=[]
    for x in _list(p.get("models")):
        if not isinstance(x,dict): continue
        rows.append({"modelRef":_txt(x.get("modelRef") or x.get("specificationRef"),512),"metrics":_dict(x.get("metrics")),"comparability":_dict(x.get("comparability"))})
    return {"ok":True,"version":VERSION,"rows":rows,"automaticRanking":False,"automaticWinnerSelection":False,"metricPerformanceIsScientificValidity":False,"boundary":BOUNDARY}

def estimand_comparison(payload:dict):
    p=_dict(payload); rows=[]
    for x in _list(p.get("estimates")):
        if isinstance(x,dict): rows.append({"estimandRef":_txt(x.get("estimandRef"),512),"estimateRef":_txt(x.get("estimateRef"),512),"value":_num(x.get("value")),"unit":_txt(x.get("unit"),128),"population":_txt(x.get("population"),1024),"timeHorizon":_txt(x.get("timeHorizon"),512)})
    comparable=len({(r["unit"],r["population"],r["timeHorizon"]) for r in rows})<=1 if rows else True
    return {"ok":True,"version":VERSION,"rows":rows,"directlyComparable":comparable,"automaticEquivalence":False,"boundary":BOUNDARY}

def sensitivity_summary(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"analyses":_list(p.get("analyses")),"assumptionsVaried":_list(p.get("assumptionsVaried")),"conclusionStability":_dict(p.get("conclusionStability")),"sensitivityEliminatesUncertainty":False,"automaticValidityConclusion":False,"boundary":BOUNDARY}

def uncertainty_limitations(payload:dict):
    p=_dict(payload); return {"ok":True,"version":VERSION,"samplingUncertainty":_dict(p.get("samplingUncertainty")),"modelUncertainty":_dict(p.get("modelUncertainty")),"measurementUncertainty":_dict(p.get("measurementUncertainty")),"identificationUncertainty":_dict(p.get("identificationUncertainty")),"limitations":[_txt(x,4096) for x in _list(p.get("limitations")) if _txt(x,4096)],"uncertaintyFullyResolved":False,"boundary":BOUNDARY}

def workspace_execution_handoff(payload:dict):
    p=_dict(payload); handoff={"schema":WORKSPACE_HANDOFF_SCHEMA,"version":VERSION,"executionAuthority":"workspace","operation":_txt(p.get("requestedOperation"),256) or "estimate-model","sessionRef":_txt(p.get("sessionId") or p.get("sessionRef"),512),"datasetRefs":[_txt(x,512) for x in _list(p.get("datasetRefs")) if _txt(x,512)],"specification":normalize_specification(_dict(p.get("specification"))),"requestedDiagnostics":_list(p.get("requestedDiagnostics")),"requestedRobustness":_list(p.get("requestedRobustness")),"automaticExecution":False,"labExecutesEstimation":False}
    handoff["fingerprint"]=_fp(handoff); return {"ok":True,"version":VERSION,"handoff":handoff,"boundary":BOUNDARY}

def core_handoff(payload:dict):
    s=normalize_session(payload); h={"schema":CORE_HANDOFF_SCHEMA,"version":VERSION,"canonicalObjectAuthority":"platform-core","sessionFingerprint":s["fingerprint"],"objectCounts":{"datasets":len(s["datasets"]),"estimands":len(s["estimands"]),"specifications":len(s["specifications"]),"estimates":len(s["estimates"])},"automaticCanonicalization":False,"automaticScientificValidity":False}; h["fingerprint"]=_fp(h); return {"ok":True,"version":VERSION,"handoff":h,"boundary":BOUNDARY}

def research_os_handoff(payload:dict):
    s=normalize_session(payload); h={"schema":RESEARCH_OS_HANDOFF_SCHEMA,"version":VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"sessionRef":s["sessionId"],"sessionFingerprint":s["fingerprint"],"recommendedPhase":"analysis","automaticPhaseAdvance":False,"scientificValidityCertified":False}; h["fingerprint"]=_fp(h); return {"ok":True,"version":VERSION,"handoff":h,"boundary":BOUNDARY}

def visual_workspace_spec(payload:dict):
    s=normalize_session(payload); return {"ok":True,"version":VERSION,"visual":{"panels":["estimand","specification","coefficient-table","fit-diagnostics","residuals","robustness","panel-time-series","uncertainty","provenance"],"linkedSelection":True,"sessionRef":s["sessionId"],"provenanceVisible":True,"automaticWinnerHighlight":False},"boundary":BOUNDARY}

def workspace_snapshot(payload:dict):
    s=normalize_session(payload); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"session":s}; stable=copy.deepcopy(snap); snap["snapshotFingerprint"]=_fp(stable); snap["createdAt"]=_now(); return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}

def compare_snapshots(payload:dict):
    p=_dict(payload); a=workspace_snapshot(_dict(p.get("left")))["snapshot"]; b=workspace_snapshot(_dict(p.get("right")))["snapshot"]
    return {"ok":True,"version":VERSION,"leftFingerprint":a["snapshotFingerprint"],"rightFingerprint":b["snapshotFingerprint"],"sameWorkspaceState":a["snapshotFingerprint"]==b["snapshotFingerprint"],"boundary":BOUNDARY}

def export_bundle(payload:dict):
    s=normalize_session(payload); bundle={"schema":"sc-lab-statistical-econometric-export-bundle/0.144.0","version":VERSION,"session":s,"interpretationBoundary":interpretation_boundary()["boundaries"],"scientificValidityCertified":False,"causalIdentificationCertified":False}; bundle["fingerprint"]=_fp(bundle); return {"ok":True,"version":VERSION,"bundle":bundle,"scientificValidityCertified":False,"boundary":BOUNDARY}

def reproducibility_package(payload:dict):
    s=normalize_session(payload); pkg={"schema":"sc-lab-statistical-econometric-reproducibility-package/0.144.0","version":VERSION,"sessionRef":s["sessionId"],"sessionFingerprint":s["fingerprint"],"datasetFingerprints":[x["fingerprint"] for x in s["datasets"]],"specificationFingerprints":[x["fingerprint"] for x in s["specifications"]],"estimateFingerprints":[x["fingerprint"] for x in s["estimates"]],"environmentRefs":[_txt(x.get("software"),2048) if isinstance(x.get("software"),str) else _canon(x.get("software",{})) for x in s["specifications"]],"reproductionInstructions":_dict(_dict(payload).get("reproductionInstructions")),"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; pkg["fingerprint"]=_fp(pkg); return {"ok":True,"version":VERSION,"package":pkg,"boundary":BOUNDARY}

def publication_handoff(payload:dict):
    s=normalize_session(payload); return {"ok":True,"version":VERSION,"handoff":{"sessionRef":s["sessionId"],"sessionFingerprint":s["fingerprint"],"review":s["review"],"limitations":s["limitations"],"publicationAccepted":False,"automaticAcceptance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def interpretation_boundary(payload=None):
    return {"ok":True,"version":VERSION,"boundaries":{"coefficientIsEstimand":False,"statisticalSignificanceIsSubstantiveImportance":False,"associationIsCausation":False,"modelFitIsScientificValidity":False,"diagnosticPassProvesAssumptions":False,"robustStandardErrorsFixIdentification":False,"forecastIsEvidence":False,"automaticModelWinner":False,"reproducibilityIsScientificValidity":False},"boundary":BOUNDARY}

def policy():
    return {"ok":True,"version":VERSION,"policy":{"workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesStatisticalEstimation":False,"explicitEstimandRequired":True,"explicitIdentificationAssumptions":True,"automaticCausalInference":False,"automaticModelRanking":False,"automaticScientificValidity":False},"boundary":BOUNDARY}

def contract():
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"datasetSchema":DATASET_SCHEMA,"estimandSchema":ESTIMAND_SCHEMA,"specificationSchema":SPECIFICATION_SCHEMA,"estimateSchema":ESTIMATE_SCHEMA,"diagnosticSchema":DIAGNOSTIC_SCHEMA,"modelFamilies":list(MODEL_FAMILIES),"analysisFamilies":list(ANALYSIS_FAMILIES),"estimators":list(ESTIMATORS),"covarianceEstimators":list(COVARIANCE_ESTIMATORS),"boundary":BOUNDARY}

def release_gates():
    return {"ok":True,"version":VERSION,"gates":{"estimandSpecificationSeparated":True,"executionAuthoritySeparated":True,"diagnosticsDoNotCertifyAssumptions":True,"associationDoesNotImplyCausation":True,"automaticWinnerSelectionDisabled":True,"reproducibilitySeparatedFromValidity":True,"predecessorCompatible":True},"boundary":BOUNDARY}

def health():
    return {"ok":True,"version":VERSION,"statisticalEconometricResearchWorkspace":True,"api_route_count":52,"predecessorVersion":PREDECESSOR_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesStatisticalEstimation":False,"explicitEstimandModelSeparation":True,"automaticCausalInference":False,"automaticModelRanking":False,"automaticWinnerSelection":False,"automaticScientificValidity":False,"statisticalSignificanceIsSubstantiveImportance":False,"associationIsCausation":False,"boundary":BOUNDARY}

def acceptance_report():
    return {"ok":True,"version":VERSION,"accepted":{"estimandObjectModel":True,"specificationObjectModel":True,"estimateResultObjectModel":True,"diagnosticObjectModel":True,"panelAndTimeSeriesAudit":True,"ivIdentificationAudit":True,"robustnessMatrix":True,"specificationMatrix":True,"workspaceExecutionHandoff":True,"coreHandoff":True,"researchOSHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackage":True},"scientificValidityCertified":False,"causalIdentificationCertified":False,"boundary":BOUNDARY}
