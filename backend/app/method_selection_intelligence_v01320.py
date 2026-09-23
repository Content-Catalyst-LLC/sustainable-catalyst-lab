from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

VERSION = "0.132.0"
ENGINE_VERSION = "13.0.0"
SCHEMA = "sc-lab-method-selection-intelligence/0.132.0"
SNAPSHOT_SCHEMA = "sc-lab-method-selection-intelligence-snapshot/0.132.0"
MAX_METHODS = 5000
MAX_REQUIREMENTS = 20000
MAX_ASSUMPTIONS = 20000
MAX_REFS = 50000
MAX_ROWS = 10000

METHOD_FAMILIES = {
    "research-context-normalization", "method-registry", "data-profile", "estimand-profile",
    "study-design-profile", "sample-structure-profile", "temporal-spatial-profile", "uncertainty-profile",
    "candidate-method-generation", "method-eligibility-matrix", "assumption-compatibility-matrix",
    "requirement-gap-analysis", "method-incompatibility-report", "estimand-data-design-alignment",
    "method-comparison", "diagnostic-planning", "sensitivity-planning", "validation-planning",
    "preanalysis-planning", "researcher-shortlist", "method-decision-record", "cross-product-handoff",
}
FIGURE_FAMILIES = {
    "method-landscape", "eligibility-matrix", "assumption-matrix", "requirement-gap-map",
    "estimand-method-map", "design-method-map", "data-method-map", "diagnostic-plan-map",
    "validation-plan-map", "sensitivity-plan-map", "method-comparison-table", "researcher-shortlist-map",
}

METHOD_CATALOG: dict[str, dict[str, Any]] = {
    "descriptive-eda": {"label":"Exploratory Data Analysis", "domains":["descriptive","exploratory"], "outcomes":["any"], "designs":["any"], "requires":[], "forbids":[]},
    "linear-regression": {"label":"Linear Regression", "domains":["association","prediction","explanatory"], "outcomes":["continuous"], "designs":["observational","experimental","any"], "requires":["independent-observations"], "forbids":[]},
    "generalized-linear-model": {"label":"Generalized Linear Model", "domains":["association","prediction","explanatory"], "outcomes":["binary","count","continuous"], "designs":["observational","experimental","any"], "requires":["distribution-family-declared"], "forbids":[]},
    "robust-regression": {"label":"Robust Regression", "domains":["association","prediction"], "outcomes":["continuous"], "designs":["observational","experimental","any"], "requires":[], "forbids":[]},
    "bayesian-regression": {"label":"Bayesian Regression", "domains":["association","prediction","explanatory"], "outcomes":["continuous","binary","count"], "designs":["observational","experimental","any"], "requires":["priors-declared"], "forbids":[]},
    "hierarchical-bayesian": {"label":"Hierarchical Bayesian Modeling", "domains":["association","prediction","partial-pooling"], "outcomes":["continuous","binary","count"], "designs":["multilevel","clustered","any"], "requires":["group-structure-declared","priors-declared"], "forbids":[]},
    "pca-dimensionality-reduction": {"label":"Principal Component Exploration", "domains":["exploratory","dimension-reduction"], "outcomes":["multivariate"], "designs":["any"], "requires":["numeric-feature-matrix"], "forbids":[]},
    "cross-validation-predictive": {"label":"Predictive Modeling with Cross-Validation", "domains":["prediction"], "outcomes":["continuous","binary","count"], "designs":["observational","experimental","any"], "requires":["validation-scheme-declared"], "forbids":[]},
    "monte-carlo-simulation": {"label":"Monte Carlo Simulation", "domains":["simulation","uncertainty","risk"], "outcomes":["modeled"], "designs":["simulation","any"], "requires":["input-distributions-declared","seed-declared"], "forbids":[]},
    "global-sensitivity": {"label":"Global Sensitivity Analysis", "domains":["sensitivity","uncertainty","simulation"], "outcomes":["modeled"], "designs":["simulation","any"], "requires":["parameter-ranges-declared","model-evaluator-available"], "forbids":[]},
    "causal-matching-weighting": {"label":"Causal Matching / Weighting", "domains":["causal","treatment-effect"], "outcomes":["continuous","binary","count"], "designs":["observational"], "requires":["treatment-declared","confounders-declared","overlap-assessable"], "forbids":["post-treatment-adjustment-only"]},
    "difference-in-differences": {"label":"Difference-in-Differences", "domains":["causal","policy-evaluation"], "outcomes":["continuous","binary","count"], "designs":["panel","quasi-experimental"], "requires":["treated-and-control-groups","pre-and-post-periods","parallel-trends-assessable"], "forbids":[]},
    "interrupted-time-series": {"label":"Interrupted Time Series", "domains":["causal","policy-evaluation","time-series"], "outcomes":["continuous","count"], "designs":["time-series","quasi-experimental"], "requires":["intervention-time-declared","ordered-time-index"], "forbids":[]},
    "regression-discontinuity": {"label":"Regression Discontinuity", "domains":["causal","treatment-effect"], "outcomes":["continuous","binary","count"], "designs":["quasi-experimental"], "requires":["running-variable-declared","cutoff-declared","continuity-assessable"], "forbids":[]},
    "spatial-autocorrelation": {"label":"Spatial Autocorrelation Analysis", "domains":["spatial","exploratory"], "outcomes":["continuous","count"], "designs":["spatial","any"], "requires":["coordinates-or-geometry","spatial-weights-declared"], "forbids":[]},
    "spatiotemporal-analysis": {"label":"Spatiotemporal Analysis", "domains":["spatial","time-series","spatiotemporal"], "outcomes":["continuous","count"], "designs":["spatiotemporal","panel"], "requires":["spatial-reference-declared","time-index-declared"], "forbids":[]},
    "time-series-forecasting": {"label":"Scientific Time-Series Forecasting", "domains":["forecasting","time-series","prediction"], "outcomes":["continuous","count"], "designs":["time-series"], "requires":["ordered-time-index","frequency-or-irregularity-declared"], "forbids":[]},
    "experimental-design-power": {"label":"Experimental Design & Power", "domains":["experimental","planning"], "outcomes":["continuous","binary","count"], "designs":["experimental","clustered","factorial","blocked"], "requires":["effect-size-assumption","alpha-declared","power-target-declared"], "forbids":[]},
    "reproduction-replication": {"label":"Research Reproduction / Replication", "domains":["reproducibility","replication"], "outcomes":["any"], "designs":["reproduction","replication","any"], "requires":["source-artifacts-declared"], "forbids":[]},
    "evidence-synthesis": {"label":"Evidence Synthesis", "domains":["synthesis","multi-study"], "outcomes":["any"], "designs":["multi-study"], "requires":["study-level-evidence-declared"], "forbids":[]},
}

class MethodSelectionIntelligenceError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()

def _list(v: Any, label: str, maximum: int = MAX_ROWS) -> list[Any]:
    if v is None: return []
    if not isinstance(v, list): raise MethodSelectionIntelligenceError(f"{label} must be an array.")
    if len(v) > maximum: raise MethodSelectionIntelligenceError(f"{label} exceeds configured maximum of {maximum}.")
    return v

def _refs(v: Any, label: str, maximum: int = MAX_REFS) -> list[str]:
    return [str(x)[:300] for x in _list(v,label,maximum)]

def schema_info() -> dict[str, Any]:
    return {"ok":True,"schema":SCHEMA,"snapshot_schema":SNAPSHOT_SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,
            "limits":{"methods":MAX_METHODS,"requirements":MAX_REQUIREMENTS,"assumptions":MAX_ASSUMPTIONS,"refs":MAX_REFS}}

def catalog() -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"method_families":sorted(METHOD_FAMILIES),"figure_families":sorted(FIGURE_FAMILIES),
            "method_catalog":copy.deepcopy(METHOD_CATALOG),"method_catalog_count":len(METHOD_CATALOG),"researcher_selection_required":True,
            "automatic_method_selection":False,"automatic_method_ranking":False,"automatic_scientific_validity_certification":False,
            "automatic_core_submission":False,"determine_truth":False}

def manifest() -> dict[str, Any]:
    return {"ok":True,"status":"method-selection-intelligence-ready","version":VERSION,"engine_version":ENGINE_VERSION,
            "transparent_eligibility_reasoning":True,"question_hypothesis_alignment":True,"data_design_estimand_alignment":True,
            "assumption_and_requirement_gap_analysis":True,"diagnostic_and_validation_planning":True,"researcher_selection_required":True,
            "automatic_method_selection":False,"automatic_method_ranking":False,"automatic_hypothesis_selection":False,
            "automatic_scientific_validity_certification":False,"automatic_core_submission":False,"determine_truth":False}

def health() -> dict[str, Any]:
    return {**manifest(),"schema":SCHEMA,"method_family_count":len(METHOD_FAMILIES),"figure_family_count":len(FIGURE_FAMILIES),
            "method_catalog_count":len(METHOD_CATALOG),"api_route_count":37}

def normalize_research_context(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise MethodSelectionIntelligenceError("payload must be an object.")
    ctx={
        "context_ref":str(payload.get("context_ref") or f"method-context:{_hash(payload)[:16]}")[:300],
        "question_refs":_refs(payload.get("question_refs"),"question_refs"),"hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs"),
        "question_type":str(payload.get("question_type") or "unspecified")[:100],"research_goal":str(payload.get("research_goal") or payload.get("question_type") or "unspecified")[:100],
        "estimand":copy.deepcopy(payload.get("estimand") or {}),"data":copy.deepcopy(payload.get("data") or {}),"design":copy.deepcopy(payload.get("design") or {}),
        "sample_structure":copy.deepcopy(payload.get("sample_structure") or {}),"temporal":copy.deepcopy(payload.get("temporal") or {}),"spatial":copy.deepcopy(payload.get("spatial") or {}),
        "uncertainty":copy.deepcopy(payload.get("uncertainty") or {}),"constraints":copy.deepcopy(payload.get("constraints") or {}),
        "assumption_refs":_refs(payload.get("assumption_refs"),"assumption_refs"),"source_refs":_refs(payload.get("source_refs"),"source_refs"),
        "researcher_declared":True,"automatic_context_inference":False,
    }
    ctx["context_hash"]=_hash(ctx); return {"ok":True,"version":VERSION,"context":ctx}

def method_registry(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload=payload or {}; requested=_refs(payload.get("method_refs"),"method_refs",MAX_METHODS)
    refs=requested or list(METHOD_CATALOG)
    rows=[]
    for ref in refs:
        base=METHOD_CATALOG.get(ref)
        if base is None:
            rows.append({"method_ref":ref,"label":ref,"registered":False,"requirements":[],"researcher_review_required":True})
        else:
            rows.append({"method_ref":ref,**copy.deepcopy(base),"registered":True,"researcher_review_required":True})
    return {"ok":True,"version":VERSION,"methods":rows,"method_count":len(rows),"registry_hash":_hash(rows),"automatic_method_selection":False}

def data_profile(payload: dict[str, Any]) -> dict[str, Any]:
    p={"outcome_type":str(payload.get("outcome_type") or "unspecified").lower(),"predictor_types":sorted({str(x).lower() for x in _list(payload.get("predictor_types"),"predictor_types")}),
       "row_count":payload.get("row_count"),"feature_count":payload.get("feature_count"),"missingness_declared":bool(payload.get("missingness_declared",False)),
       "repeated_measures":bool(payload.get("repeated_measures",False)),"grouped":bool(payload.get("grouped",False)),"time_index":bool(payload.get("time_index",False)),
       "spatial_reference":bool(payload.get("spatial_reference",False)),"observed_or_modeled":str(payload.get("observed_or_modeled") or "observed")[:100],
       "measurement_scale":payload.get("measurement_scale"),"units":copy.deepcopy(payload.get("units") or {}),"researcher_declared":True}
    p["profile_hash"]=_hash(p); return {"ok":True,"version":VERSION,"data_profile":p,"automatic_data_repair":False,"automatic_imputation":False}

def estimand_profile(payload: dict[str, Any]) -> dict[str, Any]:
    e={"estimand_ref":str(payload.get("estimand_ref") or f"estimand:{_hash(payload)[:16]}")[:300],"target":payload.get("target"),
       "type":str(payload.get("type") or "association")[:100].lower(),"population":payload.get("population"),"unit":payload.get("unit"),
       "contrast":payload.get("contrast"),"horizon":payload.get("horizon"),"treatment_ref":payload.get("treatment_ref"),"outcome_ref":payload.get("outcome_ref"),
       "researcher_declared":True,"automatic_estimand_inference":False}
    e["estimand_hash"]=_hash(e); return {"ok":True,"version":VERSION,"estimand":e}

def design_profile(payload: dict[str, Any]) -> dict[str, Any]:
    d={"design_type":str(payload.get("design_type") or "observational").lower(),"randomized":bool(payload.get("randomized",False)),
       "longitudinal":bool(payload.get("longitudinal",False)),"panel":bool(payload.get("panel",False)),"clustered":bool(payload.get("clustered",False)),
       "blocked":bool(payload.get("blocked",False)),"factorial":bool(payload.get("factorial",False)),"pre_post":bool(payload.get("pre_post",False)),
       "control_group":bool(payload.get("control_group",False)),"intervention_time":payload.get("intervention_time"),"cutoff":payload.get("cutoff"),
       "researcher_declared":True,"automatic_design_classification":False}
    d["design_hash"]=_hash(d); return {"ok":True,"version":VERSION,"design":d}

def sample_structure_profile(payload: dict[str, Any]) -> dict[str, Any]:
    s={"independent_units":bool(payload.get("independent_units",True)),"repeated_measures":bool(payload.get("repeated_measures",False)),
       "groups":payload.get("groups"),"clusters":payload.get("clusters"),"levels":copy.deepcopy(payload.get("levels") or []),
       "weights_available":bool(payload.get("weights_available",False)),"sampling_design":payload.get("sampling_design"),"researcher_declared":True}
    s["structure_hash"]=_hash(s); return {"ok":True,"version":VERSION,"sample_structure":s}

def temporal_spatial_profile(payload: dict[str, Any]) -> dict[str, Any]:
    p={"ordered_time_index":bool(payload.get("ordered_time_index",False)),"frequency":payload.get("frequency"),"irregular_time":bool(payload.get("irregular_time",False)),
       "seasonality_period":payload.get("seasonality_period"),"geometry_available":bool(payload.get("geometry_available",False)),"coordinates_available":bool(payload.get("coordinates_available",False)),
       "crs":payload.get("crs"),"spatial_weights_declared":bool(payload.get("spatial_weights_declared",False)),"spatiotemporal":bool(payload.get("spatiotemporal",False)),
       "researcher_declared":True,"automatic_frequency_inference":False,"automatic_crs_inference":False}
    p["profile_hash"]=_hash(p); return {"ok":True,"version":VERSION,"temporal_spatial_profile":p}

def uncertainty_profile(payload: dict[str, Any]) -> dict[str, Any]:
    p={"requires_interval_estimates":bool(payload.get("requires_interval_estimates",False)),"requires_posterior":bool(payload.get("requires_posterior",False)),
       "requires_simulation":bool(payload.get("requires_simulation",False)),"requires_global_sensitivity":bool(payload.get("requires_global_sensitivity",False)),
       "measurement_uncertainty":bool(payload.get("measurement_uncertainty",False)),"parameter_uncertainty":bool(payload.get("parameter_uncertainty",False)),
       "decision_thresholds":copy.deepcopy(payload.get("decision_thresholds") or []),"researcher_declared":True}
    p["profile_hash"]=_hash(p); return {"ok":True,"version":VERSION,"uncertainty_profile":p}

def _context_tokens(payload: dict[str, Any]) -> set[str]:
    vals=[]
    for key in ("research_goal","question_type","outcome_type","design_type","estimand_type"):
        v=payload.get(key)
        if v is not None: vals.append(str(v).lower())
    vals += [str(x).lower() for x in _list(payload.get("tags"),"tags")]
    if payload.get("time_index") or payload.get("ordered_time_index"): vals += ["time-series","forecasting"]
    if payload.get("spatial_reference") or payload.get("coordinates_available") or payload.get("geometry_available"): vals += ["spatial"]
    if payload.get("spatiotemporal"): vals += ["spatiotemporal","spatial","time-series"]
    if payload.get("causal") or payload.get("treatment_ref"): vals += ["causal","treatment-effect"]
    if payload.get("simulation") or payload.get("modeled"): vals += ["simulation"]
    return set(vals)

def method_candidates(payload: dict[str, Any]) -> dict[str, Any]:
    tokens=_context_tokens(payload); outcome=str(payload.get("outcome_type") or "any").lower(); design=str(payload.get("design_type") or "any").lower()
    refs=_refs(payload.get("method_refs"),"method_refs",MAX_METHODS) or list(METHOD_CATALOG)
    rows=[]
    for ref in refs:
        spec=METHOD_CATALOG.get(ref)
        if not spec:
            rows.append({"method_ref":ref,"status":"needs-information","reasons":["method-not-in-built-in-catalog"],"researcher_review_required":True}); continue
        reasons=[]; status="eligible"
        domains=set(spec["domains"])
        if tokens and not (domains & tokens) and "any" not in domains:
            status="needs-information"; reasons.append("research-goal-or-domain-alignment-not-declared")
        outs=set(spec["outcomes"])
        if outcome != "any" and "any" not in outs and outcome not in outs:
            status="incompatible"; reasons.append(f"outcome-type-{outcome}-not-declared-compatible")
        designs=set(spec["designs"])
        if design != "any" and "any" not in designs and design not in designs:
            if status != "incompatible": status="needs-information"
            reasons.append(f"design-{design}-not-directly-listed")
        if not reasons: reasons=["declared-context-does-not-show-a-known-catalog-incompatibility"]
        rows.append({"method_ref":ref,"label":spec["label"],"status":status,"reasons":reasons,"requirements":copy.deepcopy(spec["requires"]),
                     "forbids":copy.deepcopy(spec["forbids"]),"automatic_score":None,"automatic_rank":None,"researcher_review_required":True})
    return {"ok":True,"version":VERSION,"candidates":rows,"candidate_count":len(rows),"candidate_hash":_hash(rows),
            "automatic_method_selection":False,"automatic_method_ranking":False,"input_order_preserved":True}

def eligibility_matrix(payload: dict[str, Any]) -> dict[str, Any]:
    declared=set(_refs(payload.get("satisfied_requirements"),"satisfied_requirements",MAX_REQUIREMENTS)); rows=[]
    candidates=payload.get("candidates")
    if candidates is None: candidates=method_candidates(payload)["candidates"]
    for row in _list(candidates,"candidates",MAX_METHODS):
        if not isinstance(row,dict): continue
        ref=str(row.get("method_ref")); spec=METHOD_CATALOG.get(ref,{"requires":[]}); req=list(spec.get("requires") or row.get("requirements") or [])
        missing=[r for r in req if r not in declared]
        base_status=str(row.get("status") or "needs-information")
        status="incompatible" if base_status=="incompatible" else ("needs-information" if missing else base_status)
        rows.append({"method_ref":ref,"status":status,"required":req,"satisfied":[r for r in req if r in declared],"missing":missing,"researcher_review_required":True})
    return {"ok":True,"version":VERSION,"eligibility":rows,"eligibility_hash":_hash(rows),"automatic_method_selection":False}

def assumption_matrix(payload: dict[str, Any]) -> dict[str, Any]:
    assumptions=_list(payload.get("assumptions"),"assumptions",MAX_ASSUMPTIONS); methods=_refs(payload.get("method_refs"),"method_refs",MAX_METHODS) or list(METHOD_CATALOG)
    rows=[]
    for ref in methods:
        for i,a in enumerate(assumptions):
            if isinstance(a,dict):
                aref=str(a.get("assumption_ref") or f"assumption:{i+1}"); state=str(a.get("state") or "unknown")
            else: aref=str(a); state="unknown"
            rows.append({"method_ref":ref,"assumption_ref":aref,"state":state,"automatic_assumption_satisfaction":False})
    return {"ok":True,"version":VERSION,"matrix":rows,"row_count":len(rows),"matrix_hash":_hash(rows),"automatic_method_rejection":False}

def requirement_gap_report(payload: dict[str, Any]) -> dict[str, Any]:
    e=eligibility_matrix(payload)["eligibility"]; gaps=[{"method_ref":r["method_ref"],"missing":r["missing"]} for r in e if r["missing"]]
    return {"ok":True,"version":VERSION,"gaps":gaps,"gap_count":sum(len(x["missing"]) for x in gaps),"automatic_remediation":False,"researcher_review_required":True}

def incompatibility_report(payload: dict[str, Any]) -> dict[str, Any]:
    c=method_candidates(payload)["candidates"] if payload.get("candidates") is None else _list(payload.get("candidates"),"candidates",MAX_METHODS)
    rows=[{"method_ref":r.get("method_ref"),"reasons":copy.deepcopy(r.get("reasons") or [])} for r in c if r.get("status")=="incompatible"]
    return {"ok":True,"version":VERSION,"incompatibilities":rows,"count":len(rows),"automatic_method_rejection":False}

def alignment_report(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for r in _list(payload.get("methods") or method_candidates(payload)["candidates"],"methods",MAX_METHODS):
        rows.append({"method_ref":r.get("method_ref"),"estimand_alignment":r.get("estimand_alignment","researcher-review"),
                     "data_alignment":r.get("data_alignment","researcher-review"),"design_alignment":r.get("design_alignment","researcher-review"),
                     "scope_alignment":r.get("scope_alignment","researcher-review"),"automatic_alignment_grade":None})
    return {"ok":True,"version":VERSION,"alignment":rows,"alignment_hash":_hash(rows),"researcher_interpretation_required":True}

def method_comparison(payload: dict[str, Any]) -> dict[str, Any]:
    methods=_list(payload.get("methods"),"methods",MAX_METHODS); rows=[]
    for m in methods:
        if not isinstance(m,dict): continue
        rows.append({"method_ref":m.get("method_ref"),"strengths":copy.deepcopy(m.get("strengths") or []),"limitations":copy.deepcopy(m.get("limitations") or []),
                     "assumptions":copy.deepcopy(m.get("assumptions") or []),"diagnostics":copy.deepcopy(m.get("diagnostics") or []),"estimand":m.get("estimand"),
                     "data_requirements":copy.deepcopy(m.get("data_requirements") or []),"researcher_notes":m.get("researcher_notes")})
    return {"ok":True,"version":VERSION,"comparison":rows,"comparison_hash":_hash(rows),"selected_method_ref":None,"automatic_winner":None,"automatic_ranking":False}

def diagnostic_plan(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,d in enumerate(_list(payload.get("diagnostics"),"diagnostics",MAX_REQUIREMENTS)):
        if isinstance(d,dict): rows.append({"diagnostic_ref":d.get("diagnostic_ref") or f"diagnostic:{i+1}",**copy.deepcopy(d),"interpretation":"researcher-review"})
        else: rows.append({"diagnostic_ref":f"diagnostic:{i+1}","name":str(d),"interpretation":"researcher-review"})
    return {"ok":True,"version":VERSION,"diagnostics":rows,"automatic_assumption_certification":False,"automatic_method_acceptance":False}

def sensitivity_plan(payload: dict[str, Any]) -> dict[str, Any]:
    rows=copy.deepcopy(_list(payload.get("analyses"),"analyses",MAX_REQUIREMENTS))
    return {"ok":True,"version":VERSION,"analyses":rows,"analysis_count":len(rows),"automatic_robustness_certification":False,"automatic_method_selection":False}

def validation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    rows=copy.deepcopy(_list(payload.get("checks"),"checks",MAX_REQUIREMENTS))
    return {"ok":True,"version":VERSION,"checks":rows,"check_count":len(rows),"automatic_validity_certification":False,"researcher_review_required":True}

def preanalysis_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan={"question_refs":_refs(payload.get("question_refs"),"question_refs"),"hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs"),
          "candidate_method_refs":_refs(payload.get("candidate_method_refs"),"candidate_method_refs",MAX_METHODS),"required_diagnostics":copy.deepcopy(payload.get("required_diagnostics") or []),
          "sensitivity_checks":copy.deepcopy(payload.get("sensitivity_checks") or []),"validation_checks":copy.deepcopy(payload.get("validation_checks") or []),
          "decision_rule":payload.get("decision_rule"),"researcher_selection_required":True,"automatic_execution":False}
    plan["plan_hash"]=_hash(plan); return {"ok":True,"version":VERSION,"preanalysis_plan":plan}

def researcher_shortlist(payload: dict[str, Any]) -> dict[str, Any]:
    refs=_refs(payload.get("method_refs"),"method_refs",MAX_METHODS)
    out={"shortlist_ref":str(payload.get("shortlist_ref") or f"method-shortlist:{_hash(refs)[:16]}")[:300],"method_refs":refs,
         "rationale":payload.get("rationale"),"researcher_declared":True,"automatic_shortlisting":False,"automatic_rank":None}
    out["shortlist_hash"]=_hash(out); return {"ok":True,"version":VERSION,"shortlist":out}

def method_decision_record(payload: dict[str, Any]) -> dict[str, Any]:
    selected=payload.get("selected_method_ref")
    out={"decision_ref":str(payload.get("decision_ref") or f"method-decision:{_hash(payload)[:16]}")[:300],"selected_method_ref":selected,
         "alternatives_considered":_refs(payload.get("alternatives_considered"),"alternatives_considered",MAX_METHODS),"rationale":payload.get("rationale"),
         "known_limitations":copy.deepcopy(payload.get("known_limitations") or []),"assumptions_accepted":copy.deepcopy(payload.get("assumptions_accepted") or []),
         "researcher_declared":True,"automatic_decision":False,"system_endorsement":False}
    out["decision_hash"]=_hash(out); return {"ok":True,"version":VERSION,"decision":out}

def handoff_plan(payload: dict[str, Any]) -> dict[str, Any]:
    p={"method_ref":payload.get("method_ref"),"target_product":payload.get("target_product"),"project_ref":payload.get("project_ref"),
       "question_refs":_refs(payload.get("question_refs"),"question_refs"),"hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs"),
       "dataset_refs":_refs(payload.get("dataset_refs"),"dataset_refs"),"parameter_refs":_refs(payload.get("parameter_refs"),"parameter_refs"),
       "assumption_refs":_refs(payload.get("assumption_refs"),"assumption_refs"),"execution_requested":False,"automatic_submission":False}
    p["handoff_hash"]=_hash(p); return {"ok":True,"version":VERSION,"handoff_plan":p}

def visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figs=_refs(payload.get("figure_families"),"figure_families") or sorted(FIGURE_FAMILIES)
    return {"ok":True,"version":VERSION,"figure_families":figs,"method_refs":_refs(payload.get("method_refs"),"method_refs",MAX_METHODS),
            "preserve_input_order":True,"automatic_visual_ranking":False,"visual_prominence_is_not_methodological_preference":True}

def readiness_report(payload: dict[str, Any]) -> dict[str, Any]:
    checks=payload.get("checks") or {}
    if not isinstance(checks,dict): raise MethodSelectionIntelligenceError("checks must be an object.")
    required=["question","estimand","data_profile","design_profile","candidate_methods","assumptions","diagnostics","validation"]
    missing=[x for x in required if not checks.get(x)]
    return {"ok":True,"version":VERSION,"required_checks":required,"missing":missing,"structurally_ready":not missing,
            "ready_for_scientific_acceptance":False,"method_validity_certified":False,"researcher_selection_required":True}

def status_report(payload: dict[str, Any]) -> dict[str, Any]:
    states=copy.deepcopy(payload.get("states") or {})
    return {"ok":True,"version":VERSION,"states":states,"candidate_count":payload.get("candidate_count"),"selected_method_ref":payload.get("selected_method_ref"),
            "selection_authority":"researcher","automatic_method_selection":False,"scientific_validity_certified":False}

def provenance_aggregate(payload: dict[str, Any]) -> dict[str, Any]:
    refs=_refs(payload.get("source_refs"),"source_refs")+_refs(payload.get("artifact_refs"),"artifact_refs")
    out={"source_refs":refs,"question_refs":_refs(payload.get("question_refs"),"question_refs"),"hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs"),
         "method_refs":_refs(payload.get("method_refs"),"method_refs",MAX_METHODS),"decision_refs":_refs(payload.get("decision_refs"),"decision_refs"),"researcher_declared":True}
    out["provenance_hash"]=_hash(out); return {"ok":True,"version":VERSION,"provenance":out}

def project_binding(payload: dict[str, Any]) -> dict[str, Any]:
    p={"project_ref":payload.get("project_ref"),"question_refs":_refs(payload.get("question_refs"),"question_refs"),"method_refs":_refs(payload.get("method_refs"),"method_refs",MAX_METHODS),
       "decision_refs":_refs(payload.get("decision_refs"),"decision_refs"),"reference_first":True,"automatic_project_mutation":False}
    p["binding_hash"]=_hash(p); return {"ok":True,"version":VERSION,"project_binding":p}

def session_binding(payload: dict[str, Any]) -> dict[str, Any]:
    p={"session_ref":payload.get("session_ref"),"project_ref":payload.get("project_ref"),"context_ref":payload.get("context_ref"),"method_refs":_refs(payload.get("method_refs"),"method_refs",MAX_METHODS),
       "reference_first":True,"automatic_session_mutation":False}
    p["binding_hash"]=_hash(p); return {"ok":True,"version":VERSION,"session_binding":p}

def core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    p={"object_type":"method-selection-intelligence","project_ref":payload.get("project_ref"),"session_ref":payload.get("session_ref"),
       "question_refs":_refs(payload.get("question_refs"),"question_refs"),"hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs"),
       "candidate_method_refs":_refs(payload.get("candidate_method_refs"),"candidate_method_refs",MAX_METHODS),"selected_method_ref":payload.get("selected_method_ref"),
       "decision_ref":payload.get("decision_ref"),"source_refs":_refs(payload.get("source_refs"),"source_refs"),"reference_first":True,
       "core_does_not_select_method":True,"core_does_not_execute_method":True,"automatic_core_submission":False}
    p["plan_hash"]=_hash(p); return {"ok":True,"version":VERSION,"core_object_plan":p,"automatic_core_submission":False,"core_does_not_select_method":True}

def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    content=copy.deepcopy(payload.get("content") or {})
    ref=f"method-selection-snapshot:{_hash(content)}"
    return {"ok":True,"version":VERSION,"snapshot":{"schema":SNAPSHOT_SCHEMA,"snapshot_ref":ref,"content":content,"content_hash":_hash(content),"immutable":True}}

def revision_plan(payload: dict[str, Any]) -> dict[str, Any]:
    changes=copy.deepcopy(_list(payload.get("changes"),"changes",MAX_REQUIREMENTS))
    p={"base_snapshot_ref":payload.get("base_snapshot_ref"),"changes":changes,"reason":payload.get("reason"),"automatic_application":False,"researcher_approval_required":True}
    p["revision_hash"]=_hash(p); return {"ok":True,"version":VERSION,"revision_plan":p}

def export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    formats=_refs(payload.get("formats"),"formats") or ["json","csv","html","pdf"]
    p={"formats":formats,"include_provenance":bool(payload.get("include_provenance",True)),"include_assumptions":bool(payload.get("include_assumptions",True)),
       "include_alternatives":bool(payload.get("include_alternatives",True)),"include_decision_record":bool(payload.get("include_decision_record",True)),"automatic_publication":False}
    p["export_hash"]=_hash(p); return {"ok":True,"version":VERSION,"export_plan":p}

def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"researcher_selection_required":True,"automatic_method_selection":False,"automatic_method_ranking":False,
            "automatic_hypothesis_selection":False,"automatic_assumption_satisfaction":False,"automatic_scientific_validity_certification":False,
            "automatic_causal_inference":False,"automatic_generalization":False,"automatic_core_submission":False,"determine_truth":False,
            "eligible_does_not_mean_valid":True,"incompatible_does_not_mean_impossible":True,"method_selection_is_context_dependent":True}
