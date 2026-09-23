from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

VERSION = "0.131.0"
ENGINE_VERSION = "12.0.0"
SCHEMA = "sc-lab-research-question-hypothesis-workspace/0.131.0"
SNAPSHOT_SCHEMA = "sc-lab-research-question-hypothesis-snapshot/0.131.0"
MAX_QUESTIONS = 5000
MAX_HYPOTHESES = 10000
MAX_VARIABLES = 10000
MAX_OBSERVABLES = 20000
MAX_ASSUMPTIONS = 10000
MAX_EXPECTATIONS = 50000
MAX_TESTS = 10000
MAX_DEVIATIONS = 10000

METHOD_FAMILIES = {
    "question-normalization", "question-registry", "hypothesis-registry", "competing-hypothesis-set",
    "variable-operationalization", "observable-registry", "scope-boundary", "assumption-register",
    "expected-observation-matrix", "falsification-criteria", "disconfirmation-criteria",
    "rival-explanation-register", "discriminating-test-planning", "preregistration-lock",
    "preregistration-deviation", "evidence-link-planning", "method-eligibility-planning",
    "decision-boundary-planning", "provenance-aggregation", "project-core-binding",
}
FIGURE_FAMILIES = {
    "question-map", "hypothesis-tree", "competing-hypothesis-matrix", "variable-operationalization-map",
    "observable-map", "assumption-map", "expected-observation-matrix", "falsification-map",
    "rival-explanation-map", "discriminating-test-map", "evidence-hypothesis-map",
    "decision-boundary-map", "preregistration-timeline", "research-readiness-scorecard",
}
HYPOTHESIS_TYPES = {"primary", "null", "alternative", "competing", "mechanistic", "descriptive", "exploratory"}
VARIABLE_ROLES = {"outcome", "exposure", "treatment", "predictor", "covariate", "mediator", "moderator", "confounder", "instrument", "index", "other"}

class ResearchQuestionHypothesisError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()

def _list(v: Any, label: str, maximum: int) -> list[Any]:
    if v is None: return []
    if not isinstance(v, list): raise ResearchQuestionHypothesisError(f"{label} must be an array.")
    if len(v) > maximum: raise ResearchQuestionHypothesisError(f"{label} exceeds configured maximum of {maximum}.")
    return v

def _refs(v: Any, label: str, maximum: int = MAX_HYPOTHESES) -> list[str]:
    return [str(x)[:300] for x in _list(v,label,maximum)]

def schema_info() -> dict[str, Any]:
    return {"ok":True,"schema":SCHEMA,"snapshot_schema":SNAPSHOT_SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,
            "limits":{"questions":MAX_QUESTIONS,"hypotheses":MAX_HYPOTHESES,"variables":MAX_VARIABLES,"observables":MAX_OBSERVABLES,"assumptions":MAX_ASSUMPTIONS,"expectations":MAX_EXPECTATIONS,"tests":MAX_TESTS,"deviations":MAX_DEVIATIONS}}

def catalog() -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"method_families":sorted(METHOD_FAMILIES),"figure_families":sorted(FIGURE_FAMILIES),
            "hypothesis_types":sorted(HYPOTHESIS_TYPES),"variable_roles":sorted(VARIABLE_ROLES),"researcher_selection_required":True,
            "automatic_hypothesis_selection":False,"automatic_truth_determination":False,"automatic_core_submission":False}

def manifest() -> dict[str, Any]:
    return {"ok":True,"status":"research-question-hypothesis-workspace-ready","version":VERSION,"engine_version":ENGINE_VERSION,
            "question_formalization":True,"competing_hypotheses":True,"operationalization":True,"expected_observation_matrix":True,
            "falsification_and_disconfirmation":True,"preregistration_locking":True,"rival_explanations":True,"discriminating_tests":True,
            "researcher_selection_required":True,"automatic_hypothesis_generation":False,"automatic_hypothesis_selection":False,
            "automatic_evidence_weighting":False,"automatic_scientific_validity_certification":False,"automatic_core_submission":False,"determine_truth":False}

def health() -> dict[str, Any]:
    return {**manifest(),"schema":SCHEMA,"method_family_count":len(METHOD_FAMILIES),"figure_family_count":len(FIGURE_FAMILIES),"api_route_count":33}

def normalize_question(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload,dict): raise ResearchQuestionHypothesisError("payload must be an object.")
    text=str(payload.get("question") or payload.get("text") or "").strip()
    if not text: raise ResearchQuestionHypothesisError("question is required.")
    q={"question_ref":str(payload.get("question_ref") or f"question:{_hash(text)[:16]}")[:300],"question":text[:5000],
       "question_type":str(payload.get("question_type") or "explanatory")[:100],"population":payload.get("population"),"phenomenon":payload.get("phenomenon"),
       "context":payload.get("context"),"time_scope":payload.get("time_scope"),"spatial_scope":payload.get("spatial_scope"),
       "unit_of_analysis":payload.get("unit_of_analysis"),"outcome_refs":_refs(payload.get("outcome_refs"),"outcome_refs",MAX_VARIABLES),
       "exposure_refs":_refs(payload.get("exposure_refs"),"exposure_refs",MAX_VARIABLES),"source_refs":_refs(payload.get("source_refs"),"source_refs",MAX_OBSERVABLES),
       "researcher_declared":True,"automatic_rewrite":False}
    q["question_hash"]=_hash(q); return {"ok":True,"version":VERSION,"question":q}

def question_registry(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]; seen=set()
    for i,q in enumerate(_list(payload.get("questions"),"questions",MAX_QUESTIONS)):
        if not isinstance(q,dict): raise ResearchQuestionHypothesisError(f"questions[{i}] must be an object.")
        norm=normalize_question(q)["question"]
        if norm["question_ref"] in seen: raise ResearchQuestionHypothesisError(f"duplicate question_ref: {norm['question_ref']}")
        seen.add(norm["question_ref"]); rows.append(norm)
    return {"ok":True,"version":VERSION,"questions":rows,"question_count":len(rows),"registry_hash":_hash(rows),"automatic_question_priority":False}

def hypothesis_registry(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]; seen=set()
    for i,h in enumerate(_list(payload.get("hypotheses"),"hypotheses",MAX_HYPOTHESES)):
        if not isinstance(h,dict): raise ResearchQuestionHypothesisError(f"hypotheses[{i}] must be an object.")
        text=str(h.get("statement") or h.get("hypothesis") or "").strip()
        if not text: raise ResearchQuestionHypothesisError(f"hypotheses[{i}].statement is required.")
        ref=str(h.get("hypothesis_ref") or f"hypothesis:{_hash(text)[:16]}")[:300]
        if ref in seen: raise ResearchQuestionHypothesisError(f"duplicate hypothesis_ref: {ref}")
        seen.add(ref); typ=str(h.get("type") or "competing").lower(); typ=typ if typ in HYPOTHESIS_TYPES else "competing"
        rows.append({"hypothesis_ref":ref,"statement":text[:5000],"type":typ,"question_refs":_refs(h.get("question_refs"),"question_refs",MAX_QUESTIONS),
                     "mechanism":h.get("mechanism"),"direction":h.get("direction"),"boundary_conditions":copy.deepcopy(h.get("boundary_conditions") or []),
                     "variable_refs":_refs(h.get("variable_refs"),"variable_refs",MAX_VARIABLES),"researcher_declared":True,"status":str(h.get("status") or "proposed")[:100]})
    return {"ok":True,"version":VERSION,"hypotheses":rows,"hypothesis_count":len(rows),"registry_hash":_hash(rows),"automatic_hypothesis_generation":False,"automatic_hypothesis_selection":False}

def competing_hypothesis_set(payload: dict[str, Any]) -> dict[str, Any]:
    refs=_refs(payload.get("hypothesis_refs"),"hypothesis_refs",MAX_HYPOTHESES)
    if len(refs)<2: raise ResearchQuestionHypothesisError("at least two hypothesis_refs are required.")
    out={"set_ref":str(payload.get("set_ref") or f"hypothesis-set:{_hash(refs)[:16]}")[:300],"question_ref":payload.get("question_ref"),"hypothesis_refs":refs,
         "selection_rule":payload.get("selection_rule"),"status":payload.get("status") or "open","researcher_selection_required":True,"automatic_ranking":False,"automatic_winner":None}
    out["set_hash"]=_hash(out); return {"ok":True,"version":VERSION,"competing_set":out}

def operationalize_variables(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,v in enumerate(_list(payload.get("variables"),"variables",MAX_VARIABLES)):
        if not isinstance(v,dict): raise ResearchQuestionHypothesisError(f"variables[{i}] must be an object.")
        ref=str(v.get("variable_ref") or f"variable:{i+1}")[:300]; role=str(v.get("role") or "other").lower(); role=role if role in VARIABLE_ROLES else "other"
        rows.append({"variable_ref":ref,"name":str(v.get("name") or ref)[:300],"role":role,"concept":v.get("concept"),"operational_definition":v.get("operational_definition"),
                     "measurement_scale":v.get("measurement_scale"),"unit":v.get("unit"),"instrument_ref":v.get("instrument_ref"),"coding":copy.deepcopy(v.get("coding") or {}),
                     "missingness_semantics":v.get("missingness_semantics"),"researcher_declared":True})
    return {"ok":True,"version":VERSION,"variables":rows,"variable_count":len(rows),"operationalization_hash":_hash(rows),"automatic_operationalization":False}

def observable_registry(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,o in enumerate(_list(payload.get("observables"),"observables",MAX_OBSERVABLES)):
        if not isinstance(o,dict): raise ResearchQuestionHypothesisError(f"observables[{i}] must be an object.")
        rows.append({"observable_ref":o.get("observable_ref") or f"observable:{i+1}","description":o.get("description"),"variable_ref":o.get("variable_ref"),
                     "dataset_ref":o.get("dataset_ref"),"method_ref":o.get("method_ref"),"time_scope":o.get("time_scope"),"spatial_scope":o.get("spatial_scope"),
                     "observed":bool(o.get("observed",False)),"expected_only":bool(o.get("expected_only",False)),"provenance":copy.deepcopy(o.get("provenance") or {})})
    return {"ok":True,"version":VERSION,"observables":rows,"observable_count":len(rows),"registry_hash":_hash(rows),"expected_observation_equals_evidence":False}

def scope_boundary(payload: dict[str, Any]) -> dict[str, Any]:
    scope={"population":payload.get("population"),"sampling_frame":payload.get("sampling_frame"),"unit_of_analysis":payload.get("unit_of_analysis"),"time_start":payload.get("time_start"),"time_end":payload.get("time_end"),
           "spatial_scope":payload.get("spatial_scope"),"inclusion_criteria":copy.deepcopy(payload.get("inclusion_criteria") or []),"exclusion_criteria":copy.deepcopy(payload.get("exclusion_criteria") or []),
           "domain_boundaries":copy.deepcopy(payload.get("domain_boundaries") or []),"generalization_boundary":payload.get("generalization_boundary"),"researcher_declared":True}
    scope["scope_hash"]=_hash(scope); return {"ok":True,"version":VERSION,"scope":scope,"automatic_generalization":False}

def assumption_register(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,a in enumerate(_list(payload.get("assumptions"),"assumptions",MAX_ASSUMPTIONS)):
        if not isinstance(a,dict): raise ResearchQuestionHypothesisError(f"assumptions[{i}] must be an object.")
        rows.append({"assumption_ref":a.get("assumption_ref") or f"assumption:{i+1}","statement":a.get("statement"),"category":a.get("category") or "scientific",
                     "hypothesis_refs":_refs(a.get("hypothesis_refs"),"hypothesis_refs",MAX_HYPOTHESES),"testable":bool(a.get("testable",False)),"test_ref":a.get("test_ref"),
                     "status":a.get("status") or "declared","support_refs":_refs(a.get("support_refs"),"support_refs",MAX_OBSERVABLES),"challenge_refs":_refs(a.get("challenge_refs"),"challenge_refs",MAX_OBSERVABLES)})
    return {"ok":True,"version":VERSION,"assumptions":rows,"assumption_count":len(rows),"register_hash":_hash(rows),"automatic_assumption_satisfaction":False}

def expected_observation_matrix(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,e in enumerate(_list(payload.get("expectations"),"expectations",MAX_EXPECTATIONS)):
        if not isinstance(e,dict): raise ResearchQuestionHypothesisError(f"expectations[{i}] must be an object.")
        href=str(e.get("hypothesis_ref") or ""); oref=str(e.get("observable_ref") or "")
        if not href or not oref: raise ResearchQuestionHypothesisError("each expectation requires hypothesis_ref and observable_ref.")
        rows.append({"hypothesis_ref":href[:300],"observable_ref":oref[:300],"expected_pattern":e.get("expected_pattern"),"direction":e.get("direction"),"range":copy.deepcopy(e.get("range")),
                     "if_not_observed":e.get("if_not_observed") or "challenge-not-automatic-rejection","diagnosticity":e.get("diagnosticity"),"researcher_declared":True})
    return {"ok":True,"version":VERSION,"expectations":rows,"expectation_count":len(rows),"matrix_hash":_hash(rows),"automatic_hypothesis_scoring":False}

def _criteria(payload: dict[str, Any], key: str, kind: str) -> dict[str, Any]:
    rows=[]
    for i,c in enumerate(_list(payload.get(key),key,MAX_TESTS)):
        if not isinstance(c,dict): raise ResearchQuestionHypothesisError(f"{key}[{i}] must be an object.")
        rows.append({"criterion_ref":c.get("criterion_ref") or f"{kind}:{i+1}","hypothesis_ref":c.get("hypothesis_ref"),"criterion":c.get("criterion"),"observable_refs":_refs(c.get("observable_refs"),"observable_refs",MAX_OBSERVABLES),
                     "threshold":copy.deepcopy(c.get("threshold")),"scope":copy.deepcopy(c.get("scope")),"consequence":c.get("consequence") or "researcher-review","automatic_rejection":False})
    return {"ok":True,"version":VERSION,"criterion_type":kind,"criteria":rows,"criterion_count":len(rows),"criteria_hash":_hash(rows),"automatic_hypothesis_rejection":False}

def falsification_criteria(payload: dict[str, Any]) -> dict[str, Any]: return _criteria(payload,"criteria","falsification")
def disconfirmation_criteria(payload: dict[str, Any]) -> dict[str, Any]: return _criteria(payload,"criteria","disconfirmation")

def rival_explanations(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,r in enumerate(_list(payload.get("rivals"),"rivals",MAX_HYPOTHESES)):
        if not isinstance(r,dict): raise ResearchQuestionHypothesisError(f"rivals[{i}] must be an object.")
        rows.append({"rival_ref":r.get("rival_ref") or f"rival:{i+1}","statement":r.get("statement"),"target_hypothesis_refs":_refs(r.get("target_hypothesis_refs"),"target_hypothesis_refs",MAX_HYPOTHESES),
                     "mechanism":r.get("mechanism"),"predicted_observation_refs":_refs(r.get("predicted_observation_refs"),"predicted_observation_refs",MAX_OBSERVABLES),"status":r.get("status") or "open"})
    return {"ok":True,"version":VERSION,"rivals":rows,"rival_count":len(rows),"register_hash":_hash(rows),"automatic_dismissal":False}

def discriminating_test_plan(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,t in enumerate(_list(payload.get("tests"),"tests",MAX_TESTS)):
        if not isinstance(t,dict): raise ResearchQuestionHypothesisError(f"tests[{i}] must be an object.")
        rows.append({"test_ref":t.get("test_ref") or f"test:{i+1}","hypothesis_refs":_refs(t.get("hypothesis_refs"),"hypothesis_refs",MAX_HYPOTHESES),"method_ref":t.get("method_ref"),"dataset_ref":t.get("dataset_ref"),
                     "observable_refs":_refs(t.get("observable_refs"),"observable_refs",MAX_OBSERVABLES),"discriminating_pattern":copy.deepcopy(t.get("discriminating_pattern")),"assumption_refs":_refs(t.get("assumption_refs"),"assumption_refs",MAX_ASSUMPTIONS),
                     "planned":True,"automatic_result_interpretation":False})
    return {"ok":True,"version":VERSION,"tests":rows,"test_count":len(rows),"plan_hash":_hash(rows),"automatic_test_selection":False}

def preregistration_lock(payload: dict[str, Any]) -> dict[str, Any]:
    content=copy.deepcopy(payload.get("content") or payload)
    lock={"lock_ref":str(payload.get("lock_ref") or f"prereg:{_hash(content)[:20]}")[:300],"content_hash":_hash(content),"locked_content":content,"locked":True,
          "amendments_require_deviation_record":True,"automatic_mutation":False}
    return {"ok":True,"version":VERSION,"preregistration":lock}

def preregistration_deviation(payload: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,d in enumerate(_list(payload.get("deviations"),"deviations",MAX_DEVIATIONS)):
        if not isinstance(d,dict): raise ResearchQuestionHypothesisError(f"deviations[{i}] must be an object.")
        rows.append({"deviation_ref":d.get("deviation_ref") or f"deviation:{i+1}","lock_ref":d.get("lock_ref"),"field":d.get("field"),"before":copy.deepcopy(d.get("before")),"after":copy.deepcopy(d.get("after")),
                     "reason":d.get("reason"),"declared_by":d.get("declared_by"),"declared_at":d.get("declared_at"),"post_hoc":bool(d.get("post_hoc",True))})
    return {"ok":True,"version":VERSION,"deviations":rows,"deviation_count":len(rows),"register_hash":_hash(rows),"deviations_hidden":False}

def evidence_link_plan(payload: dict[str, Any]) -> dict[str, Any]:
    links=[]
    for i,l in enumerate(_list(payload.get("links"),"links",MAX_EXPECTATIONS)):
        if not isinstance(l,dict): raise ResearchQuestionHypothesisError(f"links[{i}] must be an object.")
        links.append({"link_ref":l.get("link_ref") or f"evidence-link:{i+1}","hypothesis_ref":l.get("hypothesis_ref"),"evidence_ref":l.get("evidence_ref"),"relation":l.get("relation") or "relevant-to",
                      "declared_weight":l.get("declared_weight"),"rationale":l.get("rationale"),"automatic_weighting":False})
    return {"ok":True,"version":VERSION,"links":links,"link_count":len(links),"plan_hash":_hash(links),"automatic_evidence_weighting":False,"automatic_claim_status_change":False}

def method_eligibility_plan(payload: dict[str, Any]) -> dict[str, Any]:
    methods=[]
    for i,m in enumerate(_list(payload.get("methods"),"methods",MAX_TESTS)):
        if not isinstance(m,dict): raise ResearchQuestionHypothesisError(f"methods[{i}] must be an object.")
        methods.append({"method_ref":m.get("method_ref") or f"method:{i+1}","question_refs":_refs(m.get("question_refs"),"question_refs",MAX_QUESTIONS),"hypothesis_refs":_refs(m.get("hypothesis_refs"),"hypothesis_refs",MAX_HYPOTHESES),
                        "required_assumptions":_refs(m.get("required_assumptions"),"required_assumptions",MAX_ASSUMPTIONS),"declared_eligible":m.get("declared_eligible"),"rationale":m.get("rationale")})
    return {"ok":True,"version":VERSION,"methods":methods,"method_count":len(methods),"plan_hash":_hash(methods),"automatic_method_selection":False,"eligibility_equals_validity":False}

def decision_boundary_plan(payload: dict[str, Any]) -> dict[str, Any]:
    boundaries=copy.deepcopy(payload.get("boundaries") or [])
    return {"ok":True,"version":VERSION,"boundaries":boundaries,"boundary_hash":_hash(boundaries),"researcher_declared":True,"automatic_decision":False,"threshold_equals_truth":False}

def status_report(payload: dict[str, Any]) -> dict[str, Any]:
    states=copy.deepcopy(payload.get("states") or {})
    return {"ok":True,"version":VERSION,"states":states,"status_hash":_hash(states),"automatic_overall_grade":False,"status_equals_scientific_validity":False}

def readiness_report(payload: dict[str, Any]) -> dict[str, Any]:
    checks=copy.deepcopy(payload.get("checks") or {})
    required=("question","hypotheses","variables","observables","assumptions","expected_observations","falsification","scope")
    missing=[k for k in required if not checks.get(k)]
    return {"ok":True,"version":VERSION,"checks":checks,"missing":missing,"structurally_ready":not missing,"ready_for_scientific_acceptance":False,"scientific_validity_certified":False}

def provenance_aggregate(payload: dict[str, Any]) -> dict[str, Any]:
    refs=_refs(payload.get("provenance_refs"),"provenance_refs",MAX_EXPECTATIONS)
    lineage=copy.deepcopy(payload.get("lineage") or [])
    return {"ok":True,"version":VERSION,"provenance_refs":refs,"lineage":lineage,"provenance_hash":_hash({"refs":refs,"lineage":lineage}),"provenance_equals_validity":False}

def project_binding(payload: dict[str, Any]) -> dict[str, Any]:
    out={"project_ref":payload.get("project_ref"),"question_refs":_refs(payload.get("question_refs"),"question_refs",MAX_QUESTIONS),"hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs",MAX_HYPOTHESES),"binding_mode":"reference-first","automatic_project_mutation":False}
    out["binding_hash"]=_hash(out); return {"ok":True,"version":VERSION,"binding":out}

def session_binding(payload: dict[str, Any]) -> dict[str, Any]:
    out={"session_ref":payload.get("session_ref"),"project_ref":payload.get("project_ref"),"question_refs":_refs(payload.get("question_refs"),"question_refs",MAX_QUESTIONS),"hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs",MAX_HYPOTHESES),"automatic_session_execution":False}
    out["binding_hash"]=_hash(out); return {"ok":True,"version":VERSION,"binding":out}

def core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    objects=[]
    for ref in _refs(payload.get("question_refs"),"question_refs",MAX_QUESTIONS): objects.append({"object_type":"research-question","source_ref":ref,"action":"reference"})
    for ref in _refs(payload.get("hypothesis_refs"),"hypothesis_refs",MAX_HYPOTHESES): objects.append({"object_type":"hypothesis","source_ref":ref,"action":"reference"})
    plan={"project_ref":payload.get("project_ref"),"session_ref":payload.get("session_ref"),"objects":objects,"minimum_core_version":"3.0.0","reference_first":True}
    return {"ok":True,"version":VERSION,"plan":plan,"plan_hash":_hash(plan),"automatic_core_submission":False,"core_does_not_select_hypotheses":True}

def visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figs=[{"figure_family":x,"enabled":x in set(payload.get("figure_families") or [])} for x in sorted(FIGURE_FAMILIES)]
    return {"ok":True,"version":VERSION,"figures":figs,"publication_profile":payload.get("publication_profile") or "research-workspace","visual_prominence_equals_evidence_weight":False,"automatic_scientific_encoding":False}

def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    content=copy.deepcopy(payload.get("content") or payload); snap={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"content":content,"content_hash":_hash(content),"immutable_snapshot":True}
    snap["snapshot_ref"]="rqhw:"+_hash(snap)[:24]; return {"ok":True,"version":VERSION,"snapshot":snap}

def revision_plan(payload: dict[str, Any]) -> dict[str, Any]:
    changes=copy.deepcopy(payload.get("changes") or [])
    return {"ok":True,"version":VERSION,"base_snapshot_ref":payload.get("base_snapshot_ref"),"changes":changes,"revision_hash":_hash(changes),"requires_new_snapshot":True,"silent_mutation":False}

def export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    formats=[str(x) for x in _list(payload.get("formats") or ["json","csv","markdown","pdf"],"formats",50)]
    return {"ok":True,"version":VERSION,"formats":formats,"include_provenance":bool(payload.get("include_provenance",True)),"include_preregistration":bool(payload.get("include_preregistration",True)),"include_deviations":bool(payload.get("include_deviations",True)),"export_hash":_hash(formats)}

def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"automatic_hypothesis_generation":False,"automatic_hypothesis_selection":False,"automatic_hypothesis_rejection":False,"automatic_method_selection":False,
            "automatic_evidence_weighting":False,"automatic_causal_inference":False,"automatic_generalization":False,"automatic_scientific_validity_certification":False,"automatic_core_submission":False,
            "researcher_selection_required":True,"expected_observation_equals_evidence":False,"falsification_criterion_equals_proof":False,"scientific_validity_certified":False,"determine_truth":False}
