from __future__ import annotations
import copy, hashlib, json, math, statistics
from datetime import datetime, timezone
from typing import Any

VERSION="0.145.0"
PREDECESSOR_VERSION="0.144.0"
INTEGRITY_BASELINE="0.140.0.1"
RESEARCH_OS_VERSION="0.140.0"
SCHEMA="sc-lab-simulation-computational-experiment-workspace/0.145.0"
EXPERIMENT_SCHEMA="sc-lab-computational-experiment/0.145.0"
MODEL_SCHEMA="sc-lab-simulation-model/0.145.0"
PARAMETER_SCHEMA="sc-lab-simulation-parameter/0.145.0"
SCENARIO_SCHEMA="sc-lab-simulation-scenario/0.145.0"
RUN_SCHEMA="sc-lab-simulation-run-result/0.145.0"
ENSEMBLE_SCHEMA="sc-lab-simulation-ensemble/0.145.0"
SNAPSHOT_SCHEMA="sc-lab-simulation-workspace-snapshot/0.145.0"
WORKSPACE_HANDOFF_SCHEMA="sc-workspace-simulation-compute-request/1.0"
WORKBENCH_HANDOFF_SCHEMA="sc-workbench-computational-prototype-request/1.0"
CORE_HANDOFF_SCHEMA="sc-platform-core-simulation-research-objects/1.0"
RESEARCH_OS_HANDOFF_SCHEMA="sc-lab-research-os-simulation-handoff/1.0"

BOUNDARY=(
    "The Simulation & Computational Experiment Workspace governs simulation questions, models, parameters, scenarios, returned runs, ensembles, diagnostics, verification, validation, uncertainty, sensitivity, visualization, and reproducibility state. "
    "Workspace/Workbench remain execution authorities for numerical simulation and computational prototypes; Platform Core remains canonical governed-object authority. "
    "Simulation output is modeled output rather than observational evidence, verification is not validation, numerical convergence is not scientific validity, calibration is not independent validation, sensitivity is not causality, and a scenario is not a prediction unless an explicit forecasting contract says so."
)

SIMULATION_FAMILIES=("deterministic","stochastic","monte-carlo","agent-based","discrete-event","system-dynamics","ode","pde","difference-equation","state-space","network","spatial","spatiotemporal","cellular-automata","finite-element","finite-volume","molecular","queueing","optimization-coupled","hybrid","surrogate","digital-twin","other")
EXPERIMENT_FAMILIES=("baseline-run","parameter-sweep","scenario-comparison","ensemble","seed-replication","convergence-study","resolution-study","calibration","validation","verification","sensitivity","uncertainty-propagation","stress-test","counterfactual-scenario","reproduction")
NUMERICAL_METHODS=("explicit-euler","implicit-euler","rk2","rk4","rk45","bdf","adams","finite-difference","finite-volume","finite-element","spectral","newton","fixed-point","monte-carlo","latin-hypercube","sobol","discrete-event","agent-step","custom","other")
EXECUTION_MODES=("workspace-python","workspace-r","workspace-julia","workspace-cpp","workspace-fortran","workbench","remote-hpc","remote-gpu","external","other")
SESSION_STATES=("draft","designed","ready-for-execution","executed","analysis","verification","validation","review","reproduction","publication","archived")
OBJECT_KINDS=("model","parameter","state-variable","input","scenario","run","ensemble","event","diagnostic","verification","validation","sensitivity","uncertainty","visualization","review","reproducibility-package","publication","other")
PARAMETER_ROLES=("parameter","initial-condition","boundary-condition","forcing","control","calibration-target","uncertain-input","scenario-input","constant","derived","other")


def _now(): return datetime.now(timezone.utc).isoformat()
def _txt(v,n=16384): return str(v or "").strip()[:n]
def _dict(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v): return copy.deepcopy(v) if isinstance(v,list) else []
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
def _fp(v): return hashlib.sha256(_canon(v).encode("utf-8")).hexdigest()
def _num(v): return float(v) if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v)) else None
def _finite_values(xs): return [float(x) for x in xs if isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(float(x))]
def _summary(xs):
    v=_finite_values(xs)
    if not v: return {"count":0,"mean":None,"min":None,"max":None,"stdDev":None}
    return {"count":len(v),"mean":statistics.fmean(v),"min":min(v),"max":max(v),"stdDev":statistics.stdev(v) if len(v)>1 else 0.0}

def simulation_catalog(): return {"ok":True,"version":VERSION,"simulationFamilies":list(SIMULATION_FAMILIES),"experimentFamilies":list(EXPERIMENT_FAMILIES),"numericalMethods":list(NUMERICAL_METHODS),"executionModes":list(EXECUTION_MODES),"automaticScenarioSelection":False,"boundary":BOUNDARY}

def normalize_parameter(payload:dict,index:int=0):
    p=_dict(payload); role=_txt(p.get("role"),64).lower() or "parameter"; role=role if role in PARAMETER_ROLES else "other"
    rec={"schema":PARAMETER_SCHEMA,"version":VERSION,"parameterId":_txt(p.get("parameterId") or p.get("id"),512) or f"parameter-{index+1}-{_fp(p)[:12]}","name":_txt(p.get("name"),256),"label":_txt(p.get("label"),512),"role":role,"unit":_txt(p.get("unit"),128),"value":p.get("value"),"bounds":_dict(p.get("bounds")),"distribution":_dict(p.get("distribution")),"sourceRef":_txt(p.get("sourceRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata"))}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_model(payload:dict):
    p=_dict(payload); fam=_txt(p.get("simulationFamily"),64).lower() or "other"; fam=fam if fam in SIMULATION_FAMILIES else "other"
    method=_txt(p.get("numericalMethod"),64).lower() or "other"; method=method if method in NUMERICAL_METHODS else "other"
    rec={"schema":MODEL_SCHEMA,"version":VERSION,"modelId":_txt(p.get("modelId") or p.get("id"),512) or f"model-{_fp(p)[:16]}","title":_txt(p.get("title"),1024),"simulationFamily":fam,"equations":_list(p.get("equations")),"components":_list(p.get("components")),"stateVariables":_list(p.get("stateVariables")),"parameters":[normalize_parameter(x,i) for i,x in enumerate(_list(p.get("parameters")))],"numericalMethod":method,"solver":_dict(p.get("solver")),"timeDomain":_dict(p.get("timeDomain")),"spatialDomain":_dict(p.get("spatialDomain")),"initialConditions":_dict(p.get("initialConditions")),"boundaryConditions":_dict(p.get("boundaryConditions")),"assumptions":[_txt(x,2048) for x in _list(p.get("assumptions")) if _txt(x,2048)],"codeRef":_txt(p.get("codeRef"),2048),"environmentRef":_txt(p.get("environmentRef"),2048),"provenanceRef":_txt(p.get("provenanceRef"),2048),"metadata":_dict(p.get("metadata")),"scientificValidityCertified":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_scenario(payload:dict,index:int=0):
    p=_dict(payload)
    rec={"schema":SCENARIO_SCHEMA,"version":VERSION,"scenarioId":_txt(p.get("scenarioId") or p.get("id"),512) or f"scenario-{index+1}-{_fp(p)[:12]}","label":_txt(p.get("label"),1024),"description":_txt(p.get("description"),4096),"modelRef":_txt(p.get("modelRef"),512),"parameterOverrides":_dict(p.get("parameterOverrides")),"inputRefs":[_txt(x,2048) for x in _list(p.get("inputRefs")) if _txt(x,2048)],"seed":p.get("seed") if isinstance(p.get("seed"),int) else None,"conditions":_dict(p.get("conditions")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"scenarioIsPrediction":False,"metadata":_dict(p.get("metadata"))}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_run(payload:dict,index:int=0):
    p=_dict(payload); status=_txt(p.get("status"),64).lower() or "completed"
    rec={"schema":RUN_SCHEMA,"version":VERSION,"runId":_txt(p.get("runId") or p.get("id"),512) or f"run-{index+1}-{_fp(p)[:12]}","experimentRef":_txt(p.get("experimentRef"),512),"modelRef":_txt(p.get("modelRef"),512),"scenarioRef":_txt(p.get("scenarioRef"),512),"status":status,"seed":p.get("seed") if isinstance(p.get("seed"),int) else None,"parameters":_dict(p.get("parameters")),"outputs":_dict(p.get("outputs")),"series":_list(p.get("series")),"events":_list(p.get("events")),"diagnostics":_list(p.get("diagnostics")),"artifacts":_list(p.get("artifacts")),"runtime":_dict(p.get("runtime")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"modeledOutput":True,"observationalEvidence":False,"scientificValidityCertified":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_ensemble(payload:dict):
    p=_dict(payload); runs=[normalize_run(x,i) for i,x in enumerate(_list(p.get("runs")))]
    rec={"schema":ENSEMBLE_SCHEMA,"version":VERSION,"ensembleId":_txt(p.get("ensembleId") or p.get("id"),512) or f"ensemble-{_fp(p)[:16]}","label":_txt(p.get("label"),1024),"experimentRef":_txt(p.get("experimentRef"),512),"runRefs":[r["runId"] for r in runs],"runs":runs,"samplingDesign":_dict(p.get("samplingDesign")),"weights":_dict(p.get("weights")),"provenanceRef":_txt(p.get("provenanceRef"),2048),"automaticScenarioSelection":False,"scientificValidityCertified":False}
    rec["fingerprint"]=_fp(rec); return rec

def normalize_experiment(payload:dict):
    p=_dict(payload); fam=_txt(p.get("experimentFamily"),64).lower() or "baseline-run"; fam=fam if fam in EXPERIMENT_FAMILIES else "baseline-run"; state=_txt(p.get("state"),64).lower() or "draft"; state=state if state in SESSION_STATES else "draft"
    rec={"schema":EXPERIMENT_SCHEMA,"version":VERSION,"experimentId":_txt(p.get("experimentId") or p.get("id"),512) or f"experiment-{_fp(p)[:16]}","projectRef":_txt(p.get("projectRef"),512),"title":_txt(p.get("title"),1024) or "Simulation & computational experiment","question":_txt(p.get("question"),4096),"experimentFamily":fam,"state":state,"model":normalize_model(p.get("model") or {}),"scenarios":[normalize_scenario(x,i) for i,x in enumerate(_list(p.get("scenarios")))],"runs":[normalize_run(x,i) for i,x in enumerate(_list(p.get("runs")))],"ensembles":[normalize_ensemble(x) for x in _list(p.get("ensembles"))],"verification":_dict(p.get("verification")),"validation":_dict(p.get("validation")),"calibration":_dict(p.get("calibration")),"sensitivity":_dict(p.get("sensitivity")),"uncertainty":_dict(p.get("uncertainty")),"limitations":[_txt(x,4096) for x in _list(p.get("limitations")) if _txt(x,4096)],"review":_dict(p.get("review")),"provenance":_dict(p.get("provenance")),"metadata":_dict(p.get("metadata")),"automaticScientificValidity":False}
    rec["fingerprint"]=_fp(rec); return rec

def workspace_state(payload:dict):
    e=normalize_experiment(payload.get("experiment") if isinstance(payload.get("experiment"),dict) else payload)
    return {"ok":True,"version":VERSION,"experiment":e,"summary":{"scenarioCount":len(e["scenarios"]),"runCount":len(e["runs"]),"ensembleCount":len(e["ensembles"]),"modeledOutputIsEvidence":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def design_audit(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); issues=[]
    if not e["question"]: issues.append("research-question-missing")
    if not e["model"]["title"] and not e["model"]["components"] and not e["model"]["equations"]: issues.append("model-definition-sparse")
    if not e["model"]["assumptions"]: issues.append("model-assumptions-not-declared")
    return {"ok":True,"version":VERSION,"issues":issues,"clean":not issues,"scientificValidityCertified":False,"boundary":BOUNDARY}

def parameter_audit(payload:dict):
    params=[normalize_parameter(x,i) for i,x in enumerate(_list(payload.get("parameters")))]; issues=[]
    for p in params:
        if not p["name"]: issues.append({"parameterId":p["parameterId"],"issue":"name-missing"})
        if p["role"]=="uncertain-input" and not p["distribution"] and not p["bounds"]: issues.append({"parameterId":p["parameterId"],"issue":"uncertainty-declaration-missing"})
    return {"ok":True,"version":VERSION,"parameterCount":len(params),"issues":issues,"automaticDistributionInference":False,"boundary":BOUNDARY}

def initial_state_audit(payload:dict): return {"ok":True,"version":VERSION,"declared":bool(_dict(payload.get("initialConditions"))),"initialConditions":_dict(payload.get("initialConditions")),"adequacyCertified":False,"boundary":BOUNDARY}
def stochasticity_audit(payload:dict): return {"ok":True,"version":VERSION,"seedDeclared":isinstance(payload.get("seed"),int),"replicateCount":len(_list(payload.get("replicates"))),"randomnessSource":_txt(payload.get("randomnessSource"),512),"stochasticAdequacyCertified":False,"boundary":BOUNDARY}
def time_grid_audit(payload:dict): return {"ok":True,"version":VERSION,"timeDomain":_dict(payload.get("timeDomain")),"adaptive":bool(payload.get("adaptive",False)),"timeResolutionAdequacyCertified":False,"boundary":BOUNDARY}
def numerical_method_audit(payload:dict):
    m=_txt(payload.get("numericalMethod"),64).lower() or "other"; return {"ok":True,"version":VERSION,"numericalMethod":m if m in NUMERICAL_METHODS else "other","solver":_dict(payload.get("solver")),"methodAppropriatenessCertified":False,"boundary":BOUNDARY}
def solver_stability_audit(payload:dict): return {"ok":True,"version":VERSION,"diagnostics":_list(payload.get("diagnostics")),"solverStableDeclared":payload.get("solverStable") if isinstance(payload.get("solverStable"),bool) else None,"stabilityCertified":False,"boundary":BOUNDARY}
def conservation_audit(payload:dict):
    rows=[]
    for x in _list(payload.get("checks")):
        if isinstance(x,dict): rows.append({"quantity":_txt(x.get("quantity"),256),"initial":_num(x.get("initial")),"final":_num(x.get("final")),"tolerance":_num(x.get("tolerance")),"status":_txt(x.get("status"),64)})
    return {"ok":True,"version":VERSION,"checks":rows,"conservationCertified":False,"boundary":BOUNDARY}
def convergence_audit(payload:dict):
    vals=_finite_values(payload.get("metricValues") or []); return {"ok":True,"version":VERSION,"metricSummary":_summary(vals),"resolutionLevels":_list(payload.get("resolutionLevels")),"convergenceDeclared":payload.get("converged") if isinstance(payload.get("converged"),bool) else None,"convergenceCertified":False,"scientificValidityCertified":False,"boundary":BOUNDARY}
def calibration_audit(payload:dict): return {"ok":True,"version":VERSION,"targets":_list(payload.get("targets")),"method":_txt(payload.get("method"),256),"objective":_dict(payload.get("objective")),"calibrationIsValidation":False,"independentValidationCertified":False,"boundary":BOUNDARY}
def validation_audit(payload:dict): return {"ok":True,"version":VERSION,"validationDataRef":_txt(payload.get("validationDataRef"),2048),"metrics":_dict(payload.get("metrics")),"domain":_txt(payload.get("domain"),2048),"intendedUse":_txt(payload.get("intendedUse"),2048),"validationIsVerification":False,"scientificValidityCertified":False,"boundary":BOUNDARY}
def verification_audit(payload:dict): return {"ok":True,"version":VERSION,"checks":_list(payload.get("checks")),"referenceSolutionRef":_txt(payload.get("referenceSolutionRef"),2048),"implementationVerified":payload.get("implementationVerified") if isinstance(payload.get("implementationVerified"),bool) else None,"verificationIsValidation":False,"scientificValidityCertified":False,"boundary":BOUNDARY}
def sensitivity_audit(payload:dict): return {"ok":True,"version":VERSION,"method":_txt(payload.get("method"),128),"indices":_list(payload.get("indices")),"parameterImportanceIsCausalEffect":False,"automaticRanking":False,"boundary":BOUNDARY}
def uncertainty_audit(payload:dict): return {"ok":True,"version":VERSION,"sources":_list(payload.get("sources")),"distributions":_list(payload.get("distributions")),"propagationMethod":_txt(payload.get("propagationMethod"),128),"uncertaintyResolved":False,"boundary":BOUNDARY}

def run_registry(payload:dict):
    runs=[normalize_run(x,i) for i,x in enumerate(_list(payload.get("runs")))]; return {"ok":True,"version":VERSION,"runs":runs,"count":len(runs),"automaticRunSelection":False,"boundary":BOUNDARY}
def output_series(payload:dict):
    rows=[]
    for x in _list(payload.get("series")):
        if isinstance(x,dict): rows.append({"name":_txt(x.get("name"),256),"unit":_txt(x.get("unit"),128),"time":_list(x.get("time")),"values":_list(x.get("values")),"summary":_summary(x.get("values") or [])})
    return {"ok":True,"version":VERSION,"series":rows,"modeledOutput":True,"observationalEvidence":False,"boundary":BOUNDARY}
def ensemble_summary(payload:dict):
    runs=_list(payload.get("runs")); metrics={}
    for r in runs:
        if not isinstance(r,dict): continue
        for k,v in _dict(r.get("metrics") or r.get("outputs")).items():
            if isinstance(v,(int,float)) and not isinstance(v,bool): metrics.setdefault(k,[]).append(v)
    return {"ok":True,"version":VERSION,"runCount":len(runs),"metricSummaries":{k:_summary(v) for k,v in metrics.items()},"automaticScenarioSelection":False,"boundary":BOUNDARY}
def distribution_summary(payload:dict): return {"ok":True,"version":VERSION,"summary":_summary(payload.get("values") or []),"quantiles":_dict(payload.get("quantiles")),"distributionFitCertified":False,"boundary":BOUNDARY}
def scenario_matrix(payload:dict):
    rows=[]
    for s in _list(payload.get("scenarios")):
        if isinstance(s,dict): rows.append({"scenarioRef":_txt(s.get("scenarioRef") or s.get("scenarioId"),512),"parameters":_dict(s.get("parameters") or s.get("parameterOverrides")),"metrics":_dict(s.get("metrics"))})
    return {"ok":True,"version":VERSION,"rows":rows,"automaticRanking":False,"automaticPreferredScenario":None,"boundary":BOUNDARY}
def parameter_sweep_matrix(payload:dict): return {"ok":True,"version":VERSION,"axes":_list(payload.get("axes")),"rows":_list(payload.get("rows")),"automaticOptimumSelection":False,"boundary":BOUNDARY}
def response_surface(payload:dict): return {"ok":True,"version":VERSION,"inputs":_list(payload.get("inputs")),"output":_txt(payload.get("output"),256),"points":_list(payload.get("points")),"interpolation":_dict(payload.get("interpolation")),"surrogateTruthClaim":False,"boundary":BOUNDARY}
def event_log(payload:dict): return {"ok":True,"version":VERSION,"events":_list(payload.get("events")),"count":len(_list(payload.get("events"))),"boundary":BOUNDARY}
def checkpoint_index(payload:dict): return {"ok":True,"version":VERSION,"checkpoints":_list(payload.get("checkpoints")),"automaticPromotion":False,"boundary":BOUNDARY}
def compute_budget_plan(payload:dict): return {"ok":True,"version":VERSION,"requestedRuns":payload.get("requestedRuns"),"requestedSteps":payload.get("requestedSteps"),"resources":_dict(payload.get("resources")),"executionMode":_txt(payload.get("executionMode"),64) or "workspace-python","automaticExecution":False,"automaticResourceEscalation":False,"boundary":BOUNDARY}

def provenance_graph(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); nodes=[{"id":e["experimentId"],"kind":"experiment"},{"id":e["model"]["modelId"],"kind":"model"}]; edges=[{"source":e["experimentId"],"target":e["model"]["modelId"],"relation":"uses-model"}]
    for s in e["scenarios"]: nodes.append({"id":s["scenarioId"],"kind":"scenario"}); edges.append({"source":e["experimentId"],"target":s["scenarioId"],"relation":"defines-scenario"})
    for r in e["runs"]: nodes.append({"id":r["runId"],"kind":"run"}); edges.append({"source":r["runId"],"target":r.get("scenarioRef") or e["experimentId"],"relation":"executes"})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"scientificValidityCertified":False,"boundary":BOUNDARY}
def visual_specification(payload:dict): return {"ok":True,"version":VERSION,"visual":{"family":_txt(payload.get("family"),128) or "simulation-dashboard","title":_txt(payload.get("title"),1024),"encodings":_dict(payload.get("encodings")),"layers":_list(payload.get("layers")),"dataRefs":_list(payload.get("dataRefs")),"modeledOutputLabelRequired":True,"automaticInterpretation":False},"boundary":BOUNDARY}

def workspace_execution_handoff(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKSPACE_HANDOFF_SCHEMA,"experimentRef":e["experimentId"],"experimentFingerprint":e["fingerprint"],"requestedOperation":_txt(payload.get("requestedOperation"),256) or "run-simulation","executionAuthority":"workspace","automaticExecution":False,"labExecutesSimulation":False,"payload":_dict(payload.get("executionPayload"))},"boundary":BOUNDARY}
def workbench_handoff(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":WORKBENCH_HANDOFF_SCHEMA,"experimentRef":e["experimentId"],"modelRef":e["model"]["modelId"],"requestedPrototype":_txt(payload.get("requestedPrototype"),256),"executionAuthority":"workbench","automaticExecution":False},"boundary":BOUNDARY}
def core_handoff(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":CORE_HANDOFF_SCHEMA,"canonicalObjectAuthority":"platform-core","experimentRef":e["experimentId"],"experimentFingerprint":e["fingerprint"],"objectKinds":list(OBJECT_KINDS),"automaticCanonicalization":False,"scientificValidityCertified":False},"boundary":BOUNDARY}
def research_os_handoff(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); return {"ok":True,"version":VERSION,"handoff":{"schema":RESEARCH_OS_HANDOFF_SCHEMA,"researchOSVersion":RESEARCH_OS_VERSION,"experimentRef":e["experimentId"],"targetPhase":_txt(payload.get("targetPhase"),128) or "compute","automaticPhaseAdvance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def workspace_snapshot(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); stable=copy.deepcopy(e); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"experiment":stable}; snap["snapshotFingerprint"]=_fp(snap); return {"ok":True,"version":VERSION,"snapshot":snap,"boundary":BOUNDARY}
def compare_snapshots(payload:dict):
    a=workspace_snapshot(payload.get("left") or {})["snapshot"]; b=workspace_snapshot(payload.get("right") or {})["snapshot"]; return {"ok":True,"version":VERSION,"sameWorkspaceState":a["snapshotFingerprint"]==b["snapshotFingerprint"],"leftFingerprint":a["snapshotFingerprint"],"rightFingerprint":b["snapshotFingerprint"],"automaticScientificConclusion":False,"boundary":BOUNDARY}
def export_bundle(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); bundle={"schema":f"{SCHEMA}/export-bundle","version":VERSION,"experiment":e,"provenanceGraph":provenance_graph(e),"verification":e["verification"],"validation":e["validation"],"limitations":e["limitations"],"scientificValidityCertified":False}; bundle["fingerprint"]=_fp(bundle); return {"ok":True,"version":VERSION,"bundle":bundle,"scientificValidityCertified":False,"boundary":BOUNDARY}
def reproducibility_package(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); pkg={"schema":f"{SCHEMA}/reproducibility-package","version":VERSION,"experimentRef":e["experimentId"],"model":e["model"],"scenarios":e["scenarios"],"runs":e["runs"],"ensembles":e["ensembles"],"verification":e["verification"],"validation":e["validation"],"calibration":e["calibration"],"sensitivity":e["sensitivity"],"uncertainty":e["uncertainty"],"limitations":e["limitations"],"review":e["review"],"reproductionCertified":False,"replicationCertified":False,"scientificValidityCertified":False}; pkg["fingerprint"]=_fp(pkg); return {"ok":True,"version":VERSION,"package":pkg,"boundary":BOUNDARY}
def publication_handoff(payload:dict):
    e=normalize_experiment(payload.get("experiment") or payload); return {"ok":True,"version":VERSION,"handoff":{"experimentRef":e["experimentId"],"experimentFingerprint":e["fingerprint"],"verification":e["verification"],"validation":e["validation"],"review":e["review"],"limitations":e["limitations"],"publicationAccepted":False,"automaticAcceptance":False,"scientificValidityCertified":False},"boundary":BOUNDARY}

def interpretation_boundary(payload=None): return {"ok":True,"version":VERSION,"boundaries":{"simulationOutputIsObservationalEvidence":False,"verificationIsValidation":False,"numericalConvergenceIsScientificValidity":False,"calibrationIsIndependentValidation":False,"sensitivityIsCausality":False,"scenarioIsPrediction":False,"automaticPreferredScenario":False,"reproducibilityIsScientificValidity":False},"boundary":BOUNDARY}
def policy(): return {"ok":True,"version":VERSION,"policy":{"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesSimulation":False,"explicitModelAssumptions":True,"verificationValidationSeparated":True,"automaticScenarioRanking":False,"automaticScientificValidity":False,"modeledOutputIsEvidence":False},"boundary":BOUNDARY}
def contract(): return {"ok":True,"version":VERSION,"schema":SCHEMA,"predecessorVersion":PREDECESSOR_VERSION,"researchOSVersion":RESEARCH_OS_VERSION,"experimentSchema":EXPERIMENT_SCHEMA,"modelSchema":MODEL_SCHEMA,"parameterSchema":PARAMETER_SCHEMA,"scenarioSchema":SCENARIO_SCHEMA,"runSchema":RUN_SCHEMA,"ensembleSchema":ENSEMBLE_SCHEMA,"simulationFamilies":list(SIMULATION_FAMILIES),"experimentFamilies":list(EXPERIMENT_FAMILIES),"numericalMethods":list(NUMERICAL_METHODS),"executionModes":list(EXECUTION_MODES),"boundary":BOUNDARY}
def release_gates(): return {"ok":True,"version":VERSION,"gates":{"executionAuthoritySeparated":True,"verificationValidationSeparated":True,"modeledOutputSeparatedFromEvidence":True,"automaticScenarioSelectionDisabled":True,"reproducibilitySeparatedFromValidity":True,"predecessorCompatible":True},"boundary":BOUNDARY}
def health(): return {"ok":True,"version":VERSION,"simulationComputationalExperimentWorkspace":True,"api_route_count":56,"predecessorVersion":PREDECESSOR_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"workspaceExecutionAuthority":True,"workbenchPrototypeExecutionAuthority":True,"platformCoreCanonicalAuthority":True,"labExecutesSimulation":False,"verificationValidationSeparated":True,"automaticScenarioRanking":False,"automaticPreferredScenario":False,"automaticScientificValidity":False,"modeledOutputIsEvidence":False,"boundary":BOUNDARY}
def acceptance_report(): return {"ok":True,"version":VERSION,"accepted":{"simulationExperimentObjectModel":True,"modelParameterScenarioObjects":True,"runAndEnsembleObjects":True,"verificationValidationSeparation":True,"solverConvergenceAudits":True,"calibrationValidationAudits":True,"sensitivityUncertaintyAudits":True,"scenarioAndSweepMatrices":True,"workspaceExecutionHandoff":True,"workbenchHandoff":True,"coreHandoff":True,"researchOSHandoff":True,"deterministicSnapshots":True,"exportBundle":True,"reproducibilityPackage":True},"scientificValidityCertified":False,"validationCertified":False,"boundary":BOUNDARY}
