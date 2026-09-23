from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from statistics import mean, median
from typing import Any

VERSION = "0.133.0"
ENGINE_VERSION = "14.0.0"
SCHEMA = "sc-lab-statistical-assumption-diagnostic-intelligence/0.133.0"
SNAPSHOT_SCHEMA = "sc-lab-statistical-assumption-diagnostic-intelligence-snapshot/0.133.0"
MAX_ROWS = 20000
MAX_REFS = 50000
MAX_ASSUMPTIONS = 10000
MAX_DIAGNOSTICS = 20000

ASSUMPTION_STATES = {"satisfied", "violated", "uncertain", "untested", "not-applicable"}
ASSUMPTION_FAMILIES = {
    "distributional-shape", "linearity-functional-form", "independence-dependence", "variance-structure",
    "multicollinearity-identifiability", "influence-leverage", "sampling-randomization", "missingness-measurement",
    "bayesian-prior-sampler", "causal-identification-overlap", "parallel-trends-continuity", "time-series-stationarity",
    "time-series-residual-whiteness", "spatial-dependence-weights", "simulation-convergence", "sensitivity-stability",
    "experimental-design-integrity", "model-specification", "validation-generalization", "numerical-stability",
    "reproducibility-provenance", "scope-transportability", "researcher-adjudication",
}
FIGURE_FAMILIES = {
    "assumption-state-matrix", "diagnostic-evidence-map", "violation-map", "uncertainty-map", "untested-assumption-map",
    "residual-diagnostic-panel", "distribution-diagnostic-panel", "dependence-diagnostic-panel", "variance-diagnostic-panel",
    "influence-diagnostic-panel", "convergence-diagnostic-panel", "causal-overlap-panel", "time-series-diagnostic-panel",
    "spatial-diagnostic-panel", "cross-method-diagnostic-map", "remediation-options-map",
}

ASSUMPTION_CATALOG: dict[str, dict[str, Any]] = {
    "residual-centered": {"family":"model-specification","diagnostics":["residuals"],"methods":["linear-regression","generalized-linear-model","time-series-forecasting"]},
    "residual-independence": {"family":"independence-dependence","diagnostics":["residuals","independence","time-series"],"methods":["linear-regression","time-series-forecasting"]},
    "normal-errors-when-required": {"family":"distributional-shape","diagnostics":["distribution","residuals"],"methods":["linear-regression","anova"]},
    "homoskedasticity-when-required": {"family":"variance-structure","diagnostics":["variance","residuals"],"methods":["linear-regression","anova"]},
    "linear-functional-form": {"family":"linearity-functional-form","diagnostics":["residuals"],"methods":["linear-regression"]},
    "no-severe-multicollinearity": {"family":"multicollinearity-identifiability","diagnostics":["multicollinearity"],"methods":["linear-regression","generalized-linear-model"]},
    "no-dominant-influence": {"family":"influence-leverage","diagnostics":["influence"],"methods":["linear-regression","generalized-linear-model"]},
    "independent-observational-units": {"family":"independence-dependence","diagnostics":["independence"],"methods":["linear-regression","experimental-design-power"]},
    "distribution-family-adequate": {"family":"distributional-shape","diagnostics":["distribution","residuals"],"methods":["generalized-linear-model"]},
    "sampler-mixing-adequate": {"family":"bayesian-prior-sampler","diagnostics":["convergence"],"methods":["bayesian-regression","hierarchical-bayesian"]},
    "posterior-effective-sample-adequate": {"family":"bayesian-prior-sampler","diagnostics":["convergence"],"methods":["bayesian-regression","hierarchical-bayesian"]},
    "causal-overlap": {"family":"causal-identification-overlap","diagnostics":["causal-overlap"],"methods":["causal-matching-weighting"]},
    "parallel-trends-plausible": {"family":"parallel-trends-continuity","diagnostics":["causal-design"],"methods":["difference-in-differences"]},
    "rd-continuity-plausible": {"family":"parallel-trends-continuity","diagnostics":["causal-design"],"methods":["regression-discontinuity"]},
    "stationarity-when-required": {"family":"time-series-stationarity","diagnostics":["time-series"],"methods":["time-series-forecasting"]},
    "residual-whiteness": {"family":"time-series-residual-whiteness","diagnostics":["time-series","residuals"],"methods":["time-series-forecasting"]},
    "spatial-weights-declared": {"family":"spatial-dependence-weights","diagnostics":["spatial"],"methods":["spatial-autocorrelation","spatiotemporal-analysis"]},
    "simulation-convergence-checked": {"family":"simulation-convergence","diagnostics":["simulation"],"methods":["monte-carlo-simulation"]},
    "sensitivity-stability-checked": {"family":"sensitivity-stability","diagnostics":["simulation","sensitivity"],"methods":["global-sensitivity"]},
    "randomization-or-allocation-declared": {"family":"experimental-design-integrity","diagnostics":["experimental-design"],"methods":["experimental-design-power"]},
    "missingness-mechanism-considered": {"family":"missingness-measurement","diagnostics":["missingness"],"methods":["any"]},
    "measurement-quality-considered": {"family":"missingness-measurement","diagnostics":["missingness"],"methods":["any"]},
    "validation-strategy-declared": {"family":"validation-generalization","diagnostics":["validation"],"methods":["cross-validation-predictive","time-series-forecasting"]},
    "numerical-stability-checked": {"family":"numerical-stability","diagnostics":["numerical"],"methods":["any"]},
    "provenance-complete": {"family":"reproducibility-provenance","diagnostics":["provenance"],"methods":["any"]},
    "scope-boundaries-declared": {"family":"scope-transportability","diagnostics":["scope"],"methods":["any"]},
}

DIAGNOSTIC_CATALOG = {
    "residuals": {"label":"Residual diagnostics","automatic_assumption_decision":False},
    "distribution": {"label":"Distribution diagnostics","automatic_assumption_decision":False},
    "independence": {"label":"Independence/dependence diagnostics","automatic_assumption_decision":False},
    "variance": {"label":"Variance-structure diagnostics","automatic_assumption_decision":False},
    "multicollinearity": {"label":"Multicollinearity diagnostics","automatic_assumption_decision":False},
    "influence": {"label":"Influence/leverage diagnostics","automatic_assumption_decision":False},
    "convergence": {"label":"Bayesian/sampler convergence diagnostics","automatic_convergence_certification":False},
    "causal-overlap": {"label":"Causal overlap diagnostics","automatic_identification_certification":False},
    "causal-design": {"label":"Causal design diagnostics","automatic_identification_certification":False},
    "time-series": {"label":"Time-series diagnostics","automatic_stationarity_certification":False},
    "spatial": {"label":"Spatial dependence diagnostics","automatic_significance_labels":False},
    "missingness": {"label":"Missingness and measurement diagnostics","automatic_missingness_mechanism_inference":False},
    "simulation": {"label":"Simulation convergence diagnostics","automatic_convergence_certification":False},
    "sensitivity": {"label":"Sensitivity stability diagnostics","automatic_parameter_importance_claims":False},
    "experimental-design": {"label":"Experimental design diagnostics","automatic_design_validity_certification":False},
    "validation": {"label":"Validation/generalization diagnostics","automatic_generalization":False},
    "numerical": {"label":"Numerical stability diagnostics","automatic_numerical_validity_certification":False},
    "provenance": {"label":"Reproducibility/provenance diagnostics","automatic_scientific_validity_certification":False},
    "scope": {"label":"Scope/transportability diagnostics","automatic_generalization":False},
}

class StatisticalAssumptionDiagnosticIntelligenceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str: return sha256(_stable(v).encode("utf-8")).hexdigest()

def _list(v: Any, label: str, maximum: int = MAX_ROWS) -> list[Any]:
    if v is None: return []
    if not isinstance(v,list): raise StatisticalAssumptionDiagnosticIntelligenceError(f"{label} must be an array.")
    if len(v)>maximum: raise StatisticalAssumptionDiagnosticIntelligenceError(f"{label} exceeds configured maximum of {maximum}.")
    return v

def _refs(v: Any, label: str, maximum: int = MAX_REFS) -> list[str]:
    return [str(x)[:300] for x in _list(v,label,maximum)]

def _floats(v: Any, label: str) -> list[float]:
    out=[]
    for x in _list(v,label):
        try: y=float(x)
        except Exception: raise StatisticalAssumptionDiagnosticIntelligenceError(f"{label} must contain numeric values.")
        if not math.isfinite(y): raise StatisticalAssumptionDiagnosticIntelligenceError(f"{label} must contain finite values.")
        out.append(y)
    return out

def _mean(xs:list[float]) -> float|None: return (sum(xs)/len(xs)) if xs else None

def _sd(xs:list[float]) -> float|None:
    if len(xs)<2: return None
    m=_mean(xs); return math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))

def _corr(x:list[float], y:list[float]) -> float|None:
    n=min(len(x),len(y))
    if n<2:return None
    x=x[:n];y=y[:n];mx=_mean(x);my=_mean(y);sx=sum((a-mx)**2 for a in x);sy=sum((b-my)**2 for b in y)
    if sx<=0 or sy<=0:return None
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sx*sy)

def schema_info():
    return {"ok":True,"schema":SCHEMA,"snapshot_schema":SNAPSHOT_SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,
            "states":sorted(ASSUMPTION_STATES),"limits":{"assumptions":MAX_ASSUMPTIONS,"diagnostics":MAX_DIAGNOSTICS,"refs":MAX_REFS}}

def catalog():
    return {"ok":True,"version":VERSION,"assumption_families":sorted(ASSUMPTION_FAMILIES),"figure_families":sorted(FIGURE_FAMILIES),
            "assumption_catalog":copy.deepcopy(ASSUMPTION_CATALOG),"diagnostic_catalog":copy.deepcopy(DIAGNOSTIC_CATALOG),
            "assumption_catalog_count":len(ASSUMPTION_CATALOG),"diagnostic_catalog_count":len(DIAGNOSTIC_CATALOG),
            "automatic_method_invalidation":False,"automatic_assumption_certification":False,"automatic_method_selection":False,
            "researcher_adjudication_required":True,"automatic_core_submission":False,"determine_truth":False}

def manifest():
    return {"ok":True,"status":"statistical-assumption-diagnostic-intelligence-ready","version":VERSION,"engine_version":ENGINE_VERSION,
            "cross_method_assumption_intelligence":True,"diagnostic_evidence_synthesis":True,"uncertainty_and_untested_states_preserved":True,
            "researcher_adjudication_required":True,"automatic_method_invalidation":False,"automatic_assumption_certification":False,
            "automatic_scientific_validity_certification":False,"automatic_core_submission":False,"determine_truth":False}

def health():
    return {**manifest(),"schema":SCHEMA,"assumption_family_count":len(ASSUMPTION_FAMILIES),"figure_family_count":len(FIGURE_FAMILIES),
            "assumption_catalog_count":len(ASSUMPTION_CATALOG),"diagnostic_catalog_count":len(DIAGNOSTIC_CATALOG),"api_route_count":45}

def normalize_context(payload:dict[str,Any]):
    if not isinstance(payload,dict): raise StatisticalAssumptionDiagnosticIntelligenceError("payload must be an object.")
    c={"context_ref":str(payload.get("context_ref") or f"diagnostic-context:{_hash(payload)[:16]}")[:300],
       "project_ref":payload.get("project_ref"),"session_ref":payload.get("session_ref"),"question_refs":_refs(payload.get("question_refs"),"question_refs"),
       "hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs"),"method_refs":_refs(payload.get("method_refs"),"method_refs"),
       "model_refs":_refs(payload.get("model_refs"),"model_refs"),"dataset_refs":_refs(payload.get("dataset_refs"),"dataset_refs"),
       "design_refs":_refs(payload.get("design_refs"),"design_refs"),"diagnostic_refs":_refs(payload.get("diagnostic_refs"),"diagnostic_refs"),
       "scope":copy.deepcopy(payload.get("scope") or {}),"researcher_declared":True,"automatic_context_inference":False}
    c["context_hash"]=_hash(c); return {"ok":True,"version":VERSION,"context":c}

def assumption_registry(payload:dict[str,Any]|None=None):
    payload=payload or {}; refs=_refs(payload.get("assumption_refs"),"assumption_refs",MAX_ASSUMPTIONS) or list(ASSUMPTION_CATALOG)
    rows=[]
    for ref in refs:
        spec=ASSUMPTION_CATALOG.get(ref)
        rows.append({"assumption_ref":ref,**(copy.deepcopy(spec) if spec else {"family":"researcher-declared","diagnostics":[],"methods":[]}),
                     "registered":spec is not None,"default_state":"untested","researcher_adjudication_required":True})
    return {"ok":True,"version":VERSION,"assumptions":rows,"assumption_count":len(rows),"registry_hash":_hash(rows),"automatic_assumption_certification":False}

def diagnostic_registry(payload:dict[str,Any]|None=None):
    payload=payload or {}; refs=_refs(payload.get("diagnostic_refs"),"diagnostic_refs",MAX_DIAGNOSTICS) or list(DIAGNOSTIC_CATALOG)
    rows=[]
    for ref in refs:
        spec=DIAGNOSTIC_CATALOG.get(ref)
        rows.append({"diagnostic_ref":ref,**(copy.deepcopy(spec) if spec else {"label":ref}),"registered":spec is not None,"researcher_interpretation_required":True})
    return {"ok":True,"version":VERSION,"diagnostics":rows,"diagnostic_count":len(rows),"registry_hash":_hash(rows)}

def normalize_diagnostic_observations(payload:dict[str,Any]):
    rows=[]
    for i,row in enumerate(_list(payload.get("observations"),"observations",MAX_DIAGNOSTICS)):
        if not isinstance(row,dict): raise StatisticalAssumptionDiagnosticIntelligenceError("diagnostic observations must be objects.")
        rows.append({"observation_ref":str(row.get("observation_ref") or f"diagnostic-observation:{i+1}"),"diagnostic_ref":row.get("diagnostic_ref"),
                     "assumption_refs":_refs(row.get("assumption_refs"),"assumption_refs"),"value":copy.deepcopy(row.get("value")),"threshold":copy.deepcopy(row.get("threshold")),
                     "declared_interpretation":row.get("declared_interpretation"),"source_refs":_refs(row.get("source_refs"),"source_refs"),
                     "researcher_declared":True,"automatic_assumption_decision":False})
    return {"ok":True,"version":VERSION,"observations":rows,"observation_hash":_hash(rows)}

def evaluate_assumptions(payload:dict[str,Any]):
    rows=[]
    for i,row in enumerate(_list(payload.get("assumptions"),"assumptions",MAX_ASSUMPTIONS)):
        if not isinstance(row,dict): continue
        state=str(row.get("state") or "untested").lower()
        if state not in ASSUMPTION_STATES: raise StatisticalAssumptionDiagnosticIntelligenceError(f"invalid assumption state: {state}")
        rows.append({"assumption_ref":str(row.get("assumption_ref") or f"assumption:{i+1}"),"method_ref":row.get("method_ref"),"state":state,
                     "diagnostic_evidence_refs":_refs(row.get("diagnostic_evidence_refs"),"diagnostic_evidence_refs"),"rationale":row.get("rationale"),
                     "researcher_adjudicated":bool(row.get("researcher_adjudicated",False)),"automatic_assumption_certification":False,
                     "automatic_method_invalidation":False})
    counts={s:sum(1 for r in rows if r["state"]==s) for s in sorted(ASSUMPTION_STATES)}
    return {"ok":True,"version":VERSION,"assumptions":rows,"state_counts":counts,"evaluation_hash":_hash(rows),"researcher_adjudication_required":True}

def assumption_matrix(payload:dict[str,Any]):
    methods=_refs(payload.get("method_refs"),"method_refs") or [None]; assumptions=payload.get("assumptions") or []
    evals=evaluate_assumptions({"assumptions":assumptions})["assumptions"] if assumptions else []
    lookup={(e.get("method_ref"),e["assumption_ref"]):e for e in evals}; refs=_refs(payload.get("assumption_refs"),"assumption_refs") or [e["assumption_ref"] for e in evals]
    rows=[]
    for m in methods:
        for a in refs:
            e=lookup.get((m,a)) or lookup.get((None,a)) or {"state":"untested","diagnostic_evidence_refs":[]}
            rows.append({"method_ref":m,"assumption_ref":a,"state":e["state"],"diagnostic_evidence_refs":copy.deepcopy(e.get("diagnostic_evidence_refs") or []),"automatic_method_invalidation":False})
    return {"ok":True,"version":VERSION,"matrix":rows,"matrix_hash":_hash(rows),"automatic_assumption_certification":False}

def _state_report(payload:dict[str,Any], state:str, key:str):
    rows=[r for r in evaluate_assumptions(payload)["assumptions"] if r["state"]==state]
    return {"ok":True,"version":VERSION,key:rows,"count":len(rows),"automatic_method_invalidation":False,"researcher_review_required":True}

def violation_report(payload): return _state_report(payload,"violated","violations")
def uncertainty_report(payload): return _state_report(payload,"uncertain","uncertain_assumptions")
def untested_report(payload): return _state_report(payload,"untested","untested_assumptions")

def dependency_graph(payload:dict[str,Any]):
    nodes=[]; edges=[]
    for a in _list(payload.get("assumptions"),"assumptions",MAX_ASSUMPTIONS):
        if not isinstance(a,dict): continue
        ref=str(a.get("assumption_ref")); nodes.append({"ref":ref,"kind":"assumption"})
        for dep in _refs(a.get("depends_on"),"depends_on"): edges.append({"from":dep,"to":ref,"relation":"assumption-dependency"})
        for d in _refs(a.get("diagnostic_refs"),"diagnostic_refs"): edges.append({"from":d,"to":ref,"relation":"diagnostic-informs-assumption"})
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"graph_hash":_hash({"nodes":nodes,"edges":edges}),"automatic_causal_interpretation":False}

def method_impact_report(payload:dict[str,Any]):
    rows=[]
    for m in _refs(payload.get("method_refs"),"method_refs"):
        affected=[]
        for a in evaluate_assumptions(payload)["assumptions"]:
            if a.get("method_ref") in (None,m) and a["state"] in {"violated","uncertain","untested"}: affected.append({"assumption_ref":a["assumption_ref"],"state":a["state"]})
        rows.append({"method_ref":m,"affected_assumptions":affected,"automatic_method_rejection":False,"researcher_decision_required":True})
    return {"ok":True,"version":VERSION,"methods":rows,"automatic_method_ranking":False,"automatic_method_selection":False}

def remediation_options(payload:dict[str,Any]):
    rows=[]
    for i,o in enumerate(_list(payload.get("options"),"options")):
        if isinstance(o,dict): rows.append({"option_ref":o.get("option_ref") or f"remediation:{i+1}",**copy.deepcopy(o),"automatic_application":False})
        else: rows.append({"option_ref":f"remediation:{i+1}","description":str(o),"automatic_application":False})
    return {"ok":True,"version":VERSION,"options":rows,"selected_option_ref":None,"automatic_remediation":False,"researcher_selection_required":True}

def residual_diagnostics(payload:dict[str,Any]):
    xs=_floats(payload.get("residuals"),"residuals"); m=_mean(xs); sd=_sd(xs); mae=_mean([abs(x) for x in xs]) if xs else None
    lag1=_corr(xs[:-1],xs[1:]) if len(xs)>=3 else None
    return {"ok":True,"version":VERSION,"n":len(xs),"mean_residual":m,"sd_residual":sd,"mean_absolute_residual":mae,"lag1_correlation":lag1,
            "automatic_model_rejection":False,"automatic_whiteness_certification":False,"researcher_interpretation_required":True}

def distribution_diagnostics(payload:dict[str,Any]):
    xs=_floats(payload.get("values"),"values"); n=len(xs); m=_mean(xs); sd=_sd(xs); skew=None; kurt=None
    if n>=3 and sd and sd>0: skew=sum(((x-m)/sd)**3 for x in xs)/n
    if n>=4 and sd and sd>0: kurt=sum(((x-m)/sd)**4 for x in xs)/n-3
    return {"ok":True,"version":VERSION,"n":n,"mean":m,"sd":sd,"median":median(xs) if xs else None,"skewness":skew,"excess_kurtosis":kurt,
            "automatic_normality_certification":False,"automatic_distribution_selection":False}

def independence_diagnostics(payload:dict[str,Any]):
    xs=_floats(payload.get("values"),"values"); lag1=_corr(xs[:-1],xs[1:]) if len(xs)>=3 else None
    return {"ok":True,"version":VERSION,"n":len(xs),"lag1_correlation":lag1,"cluster_ref":payload.get("cluster_ref"),"repeated_measures":bool(payload.get("repeated_measures",False)),
            "automatic_independence_certification":False,"researcher_interpretation_required":True}

def variance_diagnostics(payload:dict[str,Any]):
    groups=[]
    for i,g in enumerate(_list(payload.get("groups"),"groups")):
        if not isinstance(g,dict): continue
        xs=_floats(g.get("values"),f"groups[{i}].values"); groups.append({"group_ref":g.get("group_ref") or f"group:{i+1}","n":len(xs),"variance":(_sd(xs)**2 if _sd(xs) is not None else None)})
    vals=[g["variance"] for g in groups if g["variance"] is not None and g["variance"]>0]
    ratio=(max(vals)/min(vals)) if len(vals)>=2 else None
    return {"ok":True,"version":VERSION,"groups":groups,"max_min_variance_ratio":ratio,"automatic_homoskedasticity_certification":False}

def multicollinearity_diagnostics(payload:dict[str,Any]):
    rows=[]
    for r in _list(payload.get("vif"),"vif"):
        if isinstance(r,dict): rows.append({"term":r.get("term"),"vif":float(r.get("vif")) if r.get("vif") is not None else None})
    vals=[r["vif"] for r in rows if r["vif"] is not None]
    return {"ok":True,"version":VERSION,"vif":rows,"max_vif":max(vals) if vals else None,"automatic_term_removal":False,"automatic_multicollinearity_certification":False}

def influence_diagnostics(payload:dict[str,Any]):
    rows=[]
    for r in _list(payload.get("observations"),"observations"):
        if isinstance(r,dict): rows.append({"observation_ref":r.get("observation_ref"),"leverage":r.get("leverage"),"cooks_distance":r.get("cooks_distance"),"studentized_residual":r.get("studentized_residual")})
    return {"ok":True,"version":VERSION,"observations":rows,"automatic_observation_deletion":False,"automatic_model_rejection":False}

def convergence_diagnostics(payload:dict[str,Any]):
    return {"ok":True,"version":VERSION,"rhat":copy.deepcopy(payload.get("rhat") or {}),"ess":copy.deepcopy(payload.get("ess") or {}),"mcse":copy.deepcopy(payload.get("mcse") or {}),
            "acceptance_rate":payload.get("acceptance_rate"),"divergences":payload.get("divergences"),"warnings":copy.deepcopy(payload.get("warnings") or []),
            "automatic_convergence_certification":False,"researcher_interpretation_required":True}

def causal_overlap_diagnostics(payload:dict[str,Any]):
    treated=_floats(payload.get("treated_scores"),"treated_scores"); control=_floats(payload.get("control_scores"),"control_scores")
    overlap=None
    if treated and control: overlap=max(0.0,min(max(treated),max(control))-max(min(treated),min(control)))
    return {"ok":True,"version":VERSION,"treated_range":[min(treated),max(treated)] if treated else None,"control_range":[min(control),max(control)] if control else None,
            "range_overlap_width":overlap,"automatic_overlap_certification":False,"automatic_causal_identification_certification":False}

def time_series_diagnostics(payload:dict[str,Any]):
    xs=_floats(payload.get("values"),"values"); lag1=_corr(xs[:-1],xs[1:]) if len(xs)>=3 else None
    return {"ok":True,"version":VERSION,"n":len(xs),"lag1_correlation":lag1,"frequency":payload.get("frequency"),"differencing_order":payload.get("differencing_order"),
            "stationarity_test":copy.deepcopy(payload.get("stationarity_test") or {}),"whiteness_test":copy.deepcopy(payload.get("whiteness_test") or {}),
            "automatic_stationarity_certification":False,"automatic_model_selection":False}

def spatial_diagnostics(payload:dict[str,Any]):
    return {"ok":True,"version":VERSION,"weights_ref":payload.get("weights_ref"),"crs":payload.get("crs"),"global_moran_i":payload.get("global_moran_i"),
            "local_diagnostics_refs":_refs(payload.get("local_diagnostics_refs"),"local_diagnostics_refs"),"automatic_significance_labels":False,
            "automatic_spatial_causality":False,"spatial_association_is_not_causality":True}

def missingness_diagnostics(payload:dict[str,Any]):
    rows=[]
    for r in _list(payload.get("variables"),"variables"):
        if isinstance(r,dict): rows.append({"variable_ref":r.get("variable_ref"),"missing_count":r.get("missing_count"),"row_count":r.get("row_count"),"declared_mechanism":r.get("declared_mechanism")})
    return {"ok":True,"version":VERSION,"variables":rows,"measurement_quality_refs":_refs(payload.get("measurement_quality_refs"),"measurement_quality_refs"),
            "automatic_imputation":False,"automatic_missingness_mechanism_inference":False}

def simulation_diagnostics(payload:dict[str,Any]):
    checkpoints=_list(payload.get("checkpoints"),"checkpoints"); return {"ok":True,"version":VERSION,"checkpoints":copy.deepcopy(checkpoints),"seed_refs":_refs(payload.get("seed_refs"),"seed_refs"),
            "replication_refs":_refs(payload.get("replication_refs"),"replication_refs"),"automatic_convergence_certification":False,"automatic_probability_as_truth":False}

def experimental_design_diagnostics(payload:dict[str,Any]):
    return {"ok":True,"version":VERSION,"randomization_declared":bool(payload.get("randomization_declared",False)),"allocation_declared":bool(payload.get("allocation_declared",False)),
            "blocking_declared":bool(payload.get("blocking_declared",False)),"cluster_structure_declared":bool(payload.get("cluster_structure_declared",False)),
            "attrition_reported":bool(payload.get("attrition_reported",False)),"protocol_deviation_refs":_refs(payload.get("protocol_deviation_refs"),"protocol_deviation_refs"),
            "automatic_design_validity_certification":False}

def robustness_plan(payload:dict[str,Any]):
    rows=copy.deepcopy(_list(payload.get("checks"),"checks")); return {"ok":True,"version":VERSION,"checks":rows,"automatic_robustness_certification":False,"researcher_review_required":True}

def sensitivity_plan(payload:dict[str,Any]):
    rows=copy.deepcopy(_list(payload.get("analyses"),"analyses")); return {"ok":True,"version":VERSION,"analyses":rows,"automatic_sensitivity_interpretation":False,"researcher_review_required":True}

def cross_method_synthesis(payload:dict[str,Any]):
    evals=evaluate_assumptions(payload)["assumptions"]; methods={}
    for e in evals:
        m=e.get("method_ref") or "cross-method"; methods.setdefault(m,{s:0 for s in ASSUMPTION_STATES}); methods[m][e["state"]]+=1
    return {"ok":True,"version":VERSION,"method_state_counts":methods,"diagnostic_refs":_refs(payload.get("diagnostic_refs"),"diagnostic_refs"),
            "automatic_method_ranking":False,"automatic_winner":None,"automatic_scientific_validity_certification":False}

def adjudication_record(payload:dict[str,Any]):
    state=str(payload.get("state") or "uncertain").lower()
    if state not in ASSUMPTION_STATES: raise StatisticalAssumptionDiagnosticIntelligenceError("invalid adjudication state")
    row={"adjudication_ref":str(payload.get("adjudication_ref") or f"adjudication:{_hash(payload)[:16]}"),"assumption_ref":payload.get("assumption_ref"),"method_ref":payload.get("method_ref"),
         "state":state,"rationale":payload.get("rationale"),"diagnostic_evidence_refs":_refs(payload.get("diagnostic_evidence_refs"),"diagnostic_evidence_refs"),
         "researcher_declared":True,"automatic_adjudication":False}
    row["adjudication_hash"]=_hash(row); return {"ok":True,"version":VERSION,"adjudication":row}

def readiness_report(payload:dict[str,Any]):
    checks=copy.deepcopy(payload.get("checks") or {}); required=["method_context","assumptions_registered","diagnostics_declared","untested_reviewed","researcher_adjudication_plan"]
    missing=[k for k in required if checks.get(k) is not True]
    return {"ok":True,"version":VERSION,"structurally_ready":not missing,"missing":missing,"ready_for_scientific_acceptance":False,"scientific_validity_certified":False,"researcher_review_required":True}

def status_report(payload:dict[str,Any]):
    assumptions=evaluate_assumptions(payload)["assumptions"] if payload.get("assumptions") is not None else []
    return {"ok":True,"version":VERSION,"status":"researcher-review-required","assumption_count":len(assumptions),"state_counts":{s:sum(1 for a in assumptions if a["state"]==s) for s in ASSUMPTION_STATES},
            "automatic_pass_fail":False,"automatic_method_invalidation":False}

def visualization_plan(payload:dict[str,Any]):
    figs=_refs(payload.get("figure_families"),"figure_families") or sorted(FIGURE_FAMILIES)
    return {"ok":True,"version":VERSION,"figures":[{"figure_family":f,"semantic_role":"diagnostic-intelligence","evidence_weight":None} for f in figs],
            "automatic_visual_prominence_as_evidence_weight":False}

def provenance_aggregate(payload:dict[str,Any]):
    p={"source_refs":_refs(payload.get("source_refs"),"source_refs"),"dataset_refs":_refs(payload.get("dataset_refs"),"dataset_refs"),"model_refs":_refs(payload.get("model_refs"),"model_refs"),
       "diagnostic_refs":_refs(payload.get("diagnostic_refs"),"diagnostic_refs"),"assumption_refs":_refs(payload.get("assumption_refs"),"assumption_refs"),"execution_refs":_refs(payload.get("execution_refs"),"execution_refs")}
    p["provenance_hash"]=_hash(p); return {"ok":True,"version":VERSION,"provenance":p,"automatic_evidence_promotion":False}

def project_binding(payload): return {"ok":True,"version":VERSION,"project_ref":payload.get("project_ref"),"workspace_ref":payload.get("workspace_ref"),"reference_first":True,"automatic_project_mutation":False}
def session_binding(payload): return {"ok":True,"version":VERSION,"session_ref":payload.get("session_ref"),"context_ref":payload.get("context_ref"),"reference_first":True,"automatic_session_mutation":False}
def handoff_plan(payload): return {"ok":True,"version":VERSION,"source_product":"lab","target_product":payload.get("target_product"),"object_refs":_refs(payload.get("object_refs"),"object_refs"),"reference_first":True,"automatic_execution":False,"automatic_submission":False}

def core_object_plan(payload:dict[str,Any]):
    return {"ok":True,"version":VERSION,"core_minimum_version":"3.0.0","object_type":"statistical-assumption-diagnostic-intelligence",
            "project_ref":payload.get("project_ref"),"method_refs":_refs(payload.get("method_refs"),"method_refs"),"assumption_refs":_refs(payload.get("assumption_refs"),"assumption_refs"),
            "diagnostic_refs":_refs(payload.get("diagnostic_refs"),"diagnostic_refs"),"adjudication_refs":_refs(payload.get("adjudication_refs"),"adjudication_refs"),
            "reference_first":True,"core_does_not_execute_diagnostics":True,"core_does_not_certify_assumptions":True,"automatic_core_submission":False}

def build_snapshot(payload:dict[str,Any]):
    content=copy.deepcopy(payload.get("content") or payload); ref=f"diagnostic-snapshot:{_hash(content)}"
    return {"ok":True,"version":VERSION,"snapshot":{"snapshot_ref":ref,"schema":SNAPSHOT_SCHEMA,"content":content,"content_hash":_hash(content),"immutable":True},"automatic_interpretation":False}

def revision_plan(payload): return {"ok":True,"version":VERSION,"base_snapshot_ref":payload.get("base_snapshot_ref"),"changes":copy.deepcopy(_list(payload.get("changes"),"changes")),"automatic_application":False,"new_snapshot_required":True}
def export_plan(payload): return {"ok":True,"version":VERSION,"format":payload.get("format") or "json","object_refs":_refs(payload.get("object_refs"),"object_refs"),"include_provenance":bool(payload.get("include_provenance",True)),"include_diagnostics":bool(payload.get("include_diagnostics",True)),"automatic_publication":False}

def interpretation_boundaries_report(payload:dict[str,Any]|None=None):
    return {"ok":True,"version":VERSION,"assumption_state_is_not_scientific_truth":True,"diagnostic_threshold_is_not_automatic_invalidity":True,
            "violated_does_not_mean_method_useless":True,"satisfied_does_not_mean_method_valid":True,"untested_is_preserved":True,"uncertainty_is_preserved":True,
            "automatic_method_invalidation":False,"automatic_assumption_certification":False,"automatic_method_selection":False,"automatic_hypothesis_selection":False,
            "automatic_significance_labels":False,"automatic_causal_inference":False,"automatic_generalization":False,"automatic_scientific_validity_certification":False,
            "automatic_core_submission":False,"determine_truth":False,"researcher_adjudication_required":True}
