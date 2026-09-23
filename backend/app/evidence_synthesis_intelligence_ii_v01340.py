from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

from .systematic_evidence_synthesis_v0640 import _pool as legacy_meta_pool

VERSION = "0.134.0"
ENGINE_VERSION = "15.0.0"
SCHEMA = "sc-lab-evidence-synthesis-intelligence-ii/0.134.0"
SNAPSHOT_SCHEMA = "sc-lab-evidence-synthesis-intelligence-snapshot/0.134.0"
MAX_RECORDS = 20000
MAX_REFS = 50000
MAX_STUDIES = 5000
MAX_CLAIMS = 5000

SYNTHESIS_STATES = {"supports", "challenges", "mixed", "inconclusive", "not-evaluated"}
EVIDENCE_KINDS = {
    "study", "dataset", "model", "simulation", "replication", "finding", "claim-evidence",
    "causal-estimate", "spatial-result", "time-series-result", "experimental-result", "qualitative-result",
}
SYNTHESIS_FAMILIES = {
    "quantitative-meta-analysis", "qualitative-synthesis", "mixed-methods", "replication-synthesis",
    "claim-centered-synthesis", "hypothesis-centered-synthesis", "contradiction-analysis", "heterogeneity-analysis",
    "uncertainty-synthesis", "coverage-gap-analysis", "robustness-synthesis", "sensitivity-synthesis",
    "assumption-aware-synthesis", "diagnostic-aware-synthesis", "provenance-aware-synthesis", "narrative-synthesis",
    "cross-method-synthesis", "cross-study-synthesis", "subgroup-synthesis", "evidence-lineage",
}
FIGURE_FAMILIES = {
    "forest-plot", "evidence-direction-matrix", "claim-evidence-map", "heterogeneity-panel", "replication-map",
    "contradiction-map", "study-characteristics-matrix", "evidence-lineage-graph", "uncertainty-summary",
    "coverage-gap-map", "subgroup-forest", "leave-one-out-panel", "funnel-diagnostic-plan", "synthesis-dashboard",
    "hypothesis-evidence-map", "mixed-methods-convergence-map",
}

class EvidenceSynthesisIntelligenceIIError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail = detail; self.status_code = status_code

def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()

def _list(v: Any, label: str, maximum: int = MAX_RECORDS) -> list[Any]:
    if v is None: return []
    if not isinstance(v, list): raise EvidenceSynthesisIntelligenceIIError(f"{label} must be an array.")
    if len(v) > maximum: raise EvidenceSynthesisIntelligenceIIError(f"{label} exceeds configured maximum of {maximum}.")
    return v

def _refs(v: Any, label: str, maximum: int = MAX_REFS) -> list[str]:
    return [str(x)[:300] for x in _list(v, label, maximum)]

def _finite(v: Any, label: str) -> float:
    try: x = float(v)
    except Exception: raise EvidenceSynthesisIntelligenceIIError(f"{label} must be numeric.")
    if not math.isfinite(x): raise EvidenceSynthesisIntelligenceIIError(f"{label} must be finite.")
    return x

def schema_info():
    return {"ok":True,"schema":SCHEMA,"snapshot_schema":SNAPSHOT_SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,
            "synthesis_states":sorted(SYNTHESIS_STATES),"limits":{"studies":MAX_STUDIES,"claims":MAX_CLAIMS,"refs":MAX_REFS}}

def catalog():
    return {"ok":True,"version":VERSION,"synthesis_families":sorted(SYNTHESIS_FAMILIES),"evidence_kinds":sorted(EVIDENCE_KINDS),
            "figure_families":sorted(FIGURE_FAMILIES),"synthesis_family_count":len(SYNTHESIS_FAMILIES),"evidence_kind_count":len(EVIDENCE_KINDS),
            "figure_family_count":len(FIGURE_FAMILIES),"automatic_consensus_certification":False,"automatic_study_quality_scoring":False,
            "automatic_truth_inference":False,"automatic_core_submission":False}

def manifest():
    return {"ok":True,"status":"evidence-synthesis-intelligence-ii-ready","version":VERSION,"engine_version":ENGINE_VERSION,
            "cross_study_synthesis":True,"quantitative_pooling_bridge_v0640":True,"contradictions_preserved":True,
            "heterogeneity_preserved":True,"replication_disagreement_preserved":True,"researcher_adjudication_required":True,
            "automatic_study_quality_scoring":False,"automatic_consensus_certification":False,"automatic_truth_inference":False,
            "automatic_scientific_validity_certification":False,"automatic_core_submission":False}

def health():
    return {**manifest(),"schema":SCHEMA,"synthesis_family_count":len(SYNTHESIS_FAMILIES),"evidence_kind_count":len(EVIDENCE_KINDS),
            "figure_family_count":len(FIGURE_FAMILIES),"api_route_count":44}

def normalize_context(payload:dict[str,Any]):
    if not isinstance(payload,dict): raise EvidenceSynthesisIntelligenceIIError("payload must be an object.")
    row={"context_ref":str(payload.get("context_ref") or f"synthesis-context:{_hash(payload)[:16]}")[:300],"project_ref":payload.get("project_ref"),
         "session_ref":payload.get("session_ref"),"question_refs":_refs(payload.get("question_refs"),"question_refs"),
         "hypothesis_refs":_refs(payload.get("hypothesis_refs"),"hypothesis_refs"),"claim_refs":_refs(payload.get("claim_refs"),"claim_refs"),
         "study_refs":_refs(payload.get("study_refs"),"study_refs"),"dataset_refs":_refs(payload.get("dataset_refs"),"dataset_refs"),
         "model_refs":_refs(payload.get("model_refs"),"model_refs"),"replication_refs":_refs(payload.get("replication_refs"),"replication_refs"),
         "scope":copy.deepcopy(payload.get("scope") or {}),"researcher_declared":True,"automatic_scope_inference":False}
    row["context_hash"]=_hash(row); return {"ok":True,"version":VERSION,"context":row}

def normalize_protocol(payload:dict[str,Any]):
    metric=str(payload.get("effect_metric") or "generic")[:120]
    model=str(payload.get("model_choice") or "random-effects").lower()
    if model not in {"fixed-effect","random-effects"}: raise EvidenceSynthesisIntelligenceIIError("model_choice must be fixed-effect or random-effects.")
    p={"protocol_ref":str(payload.get("protocol_ref") or f"synthesis-protocol:{_hash(payload)[:16]}"),"question_refs":_refs(payload.get("question_refs"),"question_refs"),
       "claim_refs":_refs(payload.get("claim_refs"),"claim_refs"),"effect_metric":metric,"model_choice":model,
       "inclusion_criteria":copy.deepcopy(_list(payload.get("inclusion_criteria"),"inclusion_criteria")),
       "exclusion_criteria":copy.deepcopy(_list(payload.get("exclusion_criteria"),"exclusion_criteria")),
       "subgroup_fields":_refs(payload.get("subgroup_fields"),"subgroup_fields"),"researcher_declared":True,"automatic_protocol_generation":False}
    p["protocol_hash"]=_hash(p); return {"ok":True,"version":VERSION,"protocol":p}

def normalize_evidence(payload:dict[str,Any]):
    rows=[]
    for i,r in enumerate(_list(payload.get("evidence"),"evidence",MAX_STUDIES)):
        if not isinstance(r,dict): raise EvidenceSynthesisIntelligenceIIError("evidence records must be objects.")
        kind=str(r.get("kind") or "study").lower()
        if kind not in EVIDENCE_KINDS: kind="study"
        state=str(r.get("state") or "not-evaluated").lower()
        if state not in SYNTHESIS_STATES: raise EvidenceSynthesisIntelligenceIIError(f"invalid synthesis state: {state}")
        row={"evidence_ref":str(r.get("evidence_ref") or f"evidence:{i+1}"),"kind":kind,"source_ref":r.get("source_ref"),
             "study_ref":r.get("study_ref"),"claim_refs":_refs(r.get("claim_refs"),"claim_refs"),"finding_refs":_refs(r.get("finding_refs"),"finding_refs"),
             "state":state,"effect_direction":r.get("effect_direction"),"effect":r.get("effect"),"standard_error":r.get("standard_error"),
             "sample_size":r.get("sample_size"),"subgroup":r.get("subgroup"),"replication_of_ref":r.get("replication_of_ref"),
             "assumption_refs":_refs(r.get("assumption_refs"),"assumption_refs"),"diagnostic_refs":_refs(r.get("diagnostic_refs"),"diagnostic_refs"),
             "provenance_refs":_refs(r.get("provenance_refs"),"provenance_refs"),"researcher_declared":True,"automatic_evidence_weight":None}
        row["evidence_hash"]=_hash(row); rows.append(row)
    return {"ok":True,"version":VERSION,"evidence":rows,"evidence_count":len(rows),"evidence_set_hash":_hash(rows),"automatic_quality_scoring":False}

def findings_registry(payload):
    rows=[]
    for i,r in enumerate(_list(payload.get("findings"),"findings")):
        if isinstance(r,dict): rows.append({"finding_ref":str(r.get("finding_ref") or f"finding:{i+1}"),"claim_refs":_refs(r.get("claim_refs"),"claim_refs"),"study_ref":r.get("study_ref"),"summary":r.get("summary"),"state":r.get("state") or "not-evaluated","automatic_claim_promotion":False})
    return {"ok":True,"version":VERSION,"findings":rows,"registry_hash":_hash(rows)}

def claims_registry(payload):
    rows=[]
    for i,r in enumerate(_list(payload.get("claims"),"claims",MAX_CLAIMS)):
        if isinstance(r,dict): rows.append({"claim_ref":str(r.get("claim_ref") or f"claim:{i+1}"),"statement":r.get("statement"),"scope":copy.deepcopy(r.get("scope") or {}),"evidence_refs":_refs(r.get("evidence_refs"),"evidence_refs"),"automatic_truth_status":None})
    return {"ok":True,"version":VERSION,"claims":rows,"registry_hash":_hash(rows),"automatic_truth_inference":False}

def study_characteristics_matrix(payload):
    rows=[]
    for r in _list(payload.get("studies"),"studies",MAX_STUDIES):
        if isinstance(r,dict): rows.append({"study_ref":r.get("study_ref"),"design":r.get("design"),"population":r.get("population"),"context":r.get("context"),"sample_size":r.get("sample_size"),"methods":copy.deepcopy(r.get("methods") or []),"assumption_refs":_refs(r.get("assumption_refs"),"assumption_refs"),"diagnostic_refs":_refs(r.get("diagnostic_refs"),"diagnostic_refs")})
    return {"ok":True,"version":VERSION,"matrix":rows,"matrix_hash":_hash(rows),"automatic_comparability_certification":False}

def evidence_matrix(payload):
    ev=normalize_evidence(payload)["evidence"]; claims=_refs(payload.get("claim_refs"),"claim_refs") or sorted({c for r in ev for c in r["claim_refs"]})
    rows=[]
    for c in claims:
        for r in ev:
            if c in r["claim_refs"]: rows.append({"claim_ref":c,"evidence_ref":r["evidence_ref"],"state":r["state"],"effect_direction":r.get("effect_direction"),"automatic_weight":None})
    return {"ok":True,"version":VERSION,"matrix":rows,"matrix_hash":_hash(rows),"automatic_evidence_weighting":False}

def direction_agreement_report(payload):
    ev=normalize_evidence(payload)["evidence"]; dirs={}
    for r in ev:
        d=str(r.get("effect_direction") or "undeclared"); dirs[d]=dirs.get(d,0)+1
    declared=[d for d in dirs if d!="undeclared"]
    return {"ok":True,"version":VERSION,"direction_counts":dirs,"multiple_declared_directions":len(declared)>1,"automatic_consensus":False,"researcher_interpretation_required":True}

def contradiction_report(payload):
    ev=normalize_evidence(payload)["evidence"]; by_claim={}
    for r in ev:
        for c in r["claim_refs"]: by_claim.setdefault(c,[]).append(r)
    rows=[]
    for c,items in by_claim.items():
        states=sorted({r["state"] for r in items}); dirs=sorted({str(r.get("effect_direction")) for r in items if r.get("effect_direction") is not None})
        rows.append({"claim_ref":c,"evidence_refs":[r["evidence_ref"] for r in items],"states":states,"directions":dirs,"contradiction_present":("supports" in states and "challenges" in states) or len(dirs)>1,"automatic_resolution":False})
    return {"ok":True,"version":VERSION,"contradictions":rows,"contradiction_count":sum(r["contradiction_present"] for r in rows),"automatic_truth_inference":False}

def _effect_rows(payload):
    rows=[]
    for i,r in enumerate(_list(payload.get("effects"),"effects",MAX_STUDIES)):
        if not isinstance(r,dict): continue
        effect=_finite(r.get("effect"),f"effects[{i}].effect")
        se=_finite(r.get("standard_error"),f"effects[{i}].standard_error")
        if se<=0: raise EvidenceSynthesisIntelligenceIIError("standard_error must be > 0.")
        rows.append({"id":str(r.get("effect_ref") or f"effect:{i+1}"),"effect":effect,"standardError":se,"variance":se*se,"study_ref":r.get("study_ref"),"subgroup":r.get("subgroup")})
    return rows

def quantitative_synthesis(payload):
    rows=_effect_rows(payload)
    if len(rows)<2: raise EvidenceSynthesisIntelligenceIIError("quantitative synthesis requires at least two aggregate effect estimates.")
    model=str(payload.get("model_choice") or "random-effects").lower()
    if model not in {"fixed-effect","random-effects"}: raise EvidenceSynthesisIntelligenceIIError("model_choice must be fixed-effect or random-effects.")
    pooled=legacy_meta_pool(rows,model)
    return {"ok":True,"version":VERSION,"model":model,"effect_metric":payload.get("effect_metric") or "generic","meta_analysis":pooled,
            "effect_refs":[r["id"] for r in rows],"automatic_causal_certification":False,"automatic_truth_inference":False,"human_synthesis_review_required":True}

def heterogeneity_report(payload):
    q=quantitative_synthesis(payload); m=q["meta_analysis"]
    return {"ok":True,"version":VERSION,"k":m["k"],"q":m["q"],"q_df":m["qDf"],"i_squared_percent":m["iSquaredPercent"],"tau_squared":m["tauSquared"],
            "automatic_heterogeneity_judgment":False,"automatic_model_switching":False}

def subgroup_synthesis(payload):
    rows=_effect_rows(payload); groups={}
    for r in rows: groups.setdefault(str(r.get("subgroup") or "unclassified"),[]).append(r)
    out=[]; model=str(payload.get("model_choice") or "random-effects")
    for g,items in groups.items(): out.append({"subgroup":g,"k":len(items),"meta_analysis":legacy_meta_pool(items,model) if len(items)>=2 else None,"automatic_subgroup_claim":False})
    return {"ok":True,"version":VERSION,"subgroups":out,"automatic_interaction_claim":False}

def leave_one_out_synthesis(payload):
    rows=_effect_rows(payload); model=str(payload.get("model_choice") or "random-effects"); out=[]
    if len(rows)>=3:
        for i,r in enumerate(rows):
            pooled=legacy_meta_pool(rows[:i]+rows[i+1:],model); out.append({"omitted_effect_ref":r["id"],"pooled_effect":pooled["pooledEffect"],"ci_low":pooled["ciLow"],"ci_high":pooled["ciHigh"],"i_squared_percent":pooled["iSquaredPercent"]})
    return {"ok":True,"version":VERSION,"leave_one_out":out,"automatic_robustness_certification":False}

def replication_synthesis(payload):
    ev=normalize_evidence(payload)["evidence"]; rows=[]
    by={r["evidence_ref"]:r for r in ev}
    for r in ev:
        ref=r.get("replication_of_ref")
        if ref:
            original=by.get(ref); rows.append({"replication_ref":r["evidence_ref"],"original_ref":ref,"original_present":original is not None,
                "state_agreement":(original or {}).get("state")==r.get("state") if original else None,"direction_agreement":(original or {}).get("effect_direction")==r.get("effect_direction") if original else None,
                "automatic_replication_success":False})
    return {"ok":True,"version":VERSION,"replications":rows,"automatic_replication_certification":False,"replication_disagreement_preserved":True}

def qualitative_theme_registry(payload):
    rows=[]
    for i,r in enumerate(_list(payload.get("themes"),"themes")):
        if isinstance(r,dict): rows.append({"theme_ref":str(r.get("theme_ref") or f"theme:{i+1}"),"label":r.get("label"),"evidence_refs":_refs(r.get("evidence_refs"),"evidence_refs"),"researcher_declared":True,"automatic_theme_generation":False})
    return {"ok":True,"version":VERSION,"themes":rows,"theme_hash":_hash(rows),"automatic_qualitative_consensus":False}

def mixed_methods_plan(payload):
    return {"ok":True,"version":VERSION,"quantitative_refs":_refs(payload.get("quantitative_refs"),"quantitative_refs"),"qualitative_refs":_refs(payload.get("qualitative_refs"),"qualitative_refs"),
            "integration_strategy":payload.get("integration_strategy") or "researcher-declared","automatic_convergence_claim":False,"researcher_adjudication_required":True}

def uncertainty_synthesis(payload):
    rows=copy.deepcopy(_list(payload.get("uncertainties"),"uncertainties")); return {"ok":True,"version":VERSION,"uncertainties":rows,"uncertainty_count":len(rows),"uncertainty_preserved":True,"automatic_uncertainty_collapse":False}

def coverage_gap_report(payload):
    claims=_refs(payload.get("claim_refs"),"claim_refs"); matrix=evidence_matrix(payload)["matrix"]; covered={r["claim_ref"] for r in matrix}
    gaps=[c for c in claims if c not in covered]
    return {"ok":True,"version":VERSION,"claim_count":len(claims),"covered_claim_count":len(covered),"gap_claim_refs":gaps,"automatic_research_priority_ranking":False}

def publication_bias_diagnostic_plan(payload):
    return {"ok":True,"version":VERSION,"effect_refs":_refs(payload.get("effect_refs"),"effect_refs"),"requested_diagnostics":copy.deepcopy(payload.get("requested_diagnostics") or ["funnel-plot","small-study-effect-review"]),
            "automatic_publication_bias_correction":False,"automatic_bias_certification":False,"researcher_interpretation_required":True}

def robustness_plan(payload):
    return {"ok":True,"version":VERSION,"checks":copy.deepcopy(_list(payload.get("checks"),"checks")),"automatic_robustness_certification":False,"researcher_review_required":True}

def sensitivity_plan(payload):
    return {"ok":True,"version":VERSION,"analyses":copy.deepcopy(_list(payload.get("analyses"),"analyses")),"automatic_sensitivity_interpretation":False,"researcher_review_required":True}

def assumption_diagnostic_bridge(payload):
    return {"ok":True,"version":VERSION,"assumption_refs":_refs(payload.get("assumption_refs"),"assumption_refs"),"diagnostic_refs":_refs(payload.get("diagnostic_refs"),"diagnostic_refs"),
            "v01330_reference_first":True,"automatic_assumption_adjudication":False,"automatic_study_exclusion":False}

def hypothesis_evidence_map(payload):
    rows=[]
    for h in _refs(payload.get("hypothesis_refs"),"hypothesis_refs"):
        rows.append({"hypothesis_ref":h,"supporting_evidence_refs":_refs((payload.get("supporting") or {}).get(h) if isinstance(payload.get("supporting"),dict) else [],"supporting"),
                     "challenging_evidence_refs":_refs((payload.get("challenging") or {}).get(h) if isinstance(payload.get("challenging"),dict) else [],"challenging"),"automatic_hypothesis_selection":False})
    return {"ok":True,"version":VERSION,"hypotheses":rows,"automatic_hypothesis_ranking":False}

def claim_synthesis(payload):
    ev=normalize_evidence(payload)["evidence"]; rows=[]
    claims=_refs(payload.get("claim_refs"),"claim_refs") or sorted({c for r in ev for c in r["claim_refs"]})
    for c in claims:
        items=[r for r in ev if c in r["claim_refs"]]; counts={s:sum(r["state"]==s for r in items) for s in SYNTHESIS_STATES}
        rows.append({"claim_ref":c,"evidence_count":len(items),"state_counts":counts,"evidence_refs":[r["evidence_ref"] for r in items],"automatic_claim_status":None,"researcher_adjudication_required":True})
    return {"ok":True,"version":VERSION,"claims":rows,"automatic_consensus_certification":False,"automatic_truth_inference":False}

def competing_findings_report(payload):
    rows=copy.deepcopy(_list(payload.get("finding_groups"),"finding_groups")); return {"ok":True,"version":VERSION,"finding_groups":rows,"automatic_resolution":False,"competing_findings_preserved":True}

def narrative_synthesis_plan(payload):
    return {"ok":True,"version":VERSION,"section_refs":_refs(payload.get("section_refs"),"section_refs"),"claim_refs":_refs(payload.get("claim_refs"),"claim_refs"),"evidence_refs":_refs(payload.get("evidence_refs"),"evidence_refs"),
            "include_disagreements":True,"include_heterogeneity":True,"automatic_conclusion_generation":False}

def adjudication_record(payload):
    row={"adjudication_ref":str(payload.get("adjudication_ref") or f"synthesis-adjudication:{_hash(payload)[:16]}"),"claim_ref":payload.get("claim_ref"),"decision":payload.get("decision"),
         "rationale":payload.get("rationale"),"evidence_refs":_refs(payload.get("evidence_refs"),"evidence_refs"),"researcher_declared":True,"automatic_adjudication":False}
    row["adjudication_hash"]=_hash(row); return {"ok":True,"version":VERSION,"adjudication":row}

def status_report(payload):
    return {"ok":True,"version":VERSION,"status":"researcher-review-required","claim_refs":_refs(payload.get("claim_refs"),"claim_refs"),"evidence_refs":_refs(payload.get("evidence_refs"),"evidence_refs"),
            "automatic_pass_fail":False,"automatic_consensus_certification":False}

def readiness_report(payload):
    checks=copy.deepcopy(payload.get("checks") or {}); required=["protocol_declared","evidence_registered","scope_declared","heterogeneity_reviewed","contradictions_reviewed","researcher_adjudication_plan"]
    missing=[k for k in required if checks.get(k) is not True]
    return {"ok":True,"version":VERSION,"structurally_ready":not missing,"missing":missing,"scientific_consensus_certified":False,"scientific_validity_certified":False,"researcher_review_required":True}

def provenance_aggregate(payload):
    p={"source_refs":_refs(payload.get("source_refs"),"source_refs"),"study_refs":_refs(payload.get("study_refs"),"study_refs"),"dataset_refs":_refs(payload.get("dataset_refs"),"dataset_refs"),
       "model_refs":_refs(payload.get("model_refs"),"model_refs"),"execution_refs":_refs(payload.get("execution_refs"),"execution_refs"),"evidence_refs":_refs(payload.get("evidence_refs"),"evidence_refs"),
       "claim_refs":_refs(payload.get("claim_refs"),"claim_refs"),"replication_refs":_refs(payload.get("replication_refs"),"replication_refs")}
    p["provenance_hash"]=_hash(p); return {"ok":True,"version":VERSION,"provenance":p,"automatic_evidence_promotion":False}

def lineage_graph(payload):
    nodes=[]; edges=[]
    for r in _list(payload.get("nodes"),"nodes"):
        if isinstance(r,dict): nodes.append(copy.deepcopy(r))
    for r in _list(payload.get("edges"),"edges"):
        if isinstance(r,dict): edges.append(copy.deepcopy(r))
    return {"ok":True,"version":VERSION,"nodes":nodes,"edges":edges,"graph_hash":_hash({"nodes":nodes,"edges":edges}),"automatic_causal_interpretation":False}

def visualization_plan(payload):
    figs=_refs(payload.get("figure_families"),"figure_families") or sorted(FIGURE_FAMILIES)
    return {"ok":True,"version":VERSION,"figures":[{"figure_family":f,"semantic_role":"evidence-synthesis","evidence_weight":None} for f in figs],"automatic_visual_prominence_as_evidence_weight":False}

def project_binding(payload): return {"ok":True,"version":VERSION,"project_ref":payload.get("project_ref"),"workspace_ref":payload.get("workspace_ref"),"reference_first":True,"automatic_project_mutation":False}
def session_binding(payload): return {"ok":True,"version":VERSION,"session_ref":payload.get("session_ref"),"context_ref":payload.get("context_ref"),"reference_first":True,"automatic_session_mutation":False}
def handoff_plan(payload): return {"ok":True,"version":VERSION,"source_product":"lab","target_product":payload.get("target_product"),"object_refs":_refs(payload.get("object_refs"),"object_refs"),"reference_first":True,"automatic_execution":False,"automatic_submission":False}

def core_object_plan(payload):
    return {"ok":True,"version":VERSION,"core_minimum_version":"3.0.0","object_type":"evidence-synthesis-intelligence","project_ref":payload.get("project_ref"),
            "claim_refs":_refs(payload.get("claim_refs"),"claim_refs"),"evidence_refs":_refs(payload.get("evidence_refs"),"evidence_refs"),"study_refs":_refs(payload.get("study_refs"),"study_refs"),
            "synthesis_refs":_refs(payload.get("synthesis_refs"),"synthesis_refs"),"reference_first":True,"core_owns_canonical_claim_evidence_objects":True,
            "core_does_not_execute_synthesis":True,"core_does_not_certify_consensus":True,"automatic_core_submission":False}

def build_snapshot(payload):
    content=copy.deepcopy(payload.get("content") or payload); ref=f"evidence-synthesis-snapshot:{_hash(content)}"
    return {"ok":True,"version":VERSION,"snapshot":{"snapshot_ref":ref,"schema":SNAPSHOT_SCHEMA,"content":content,"content_hash":_hash(content),"immutable":True},"automatic_interpretation":False}

def revision_plan(payload): return {"ok":True,"version":VERSION,"base_snapshot_ref":payload.get("base_snapshot_ref"),"changes":copy.deepcopy(_list(payload.get("changes"),"changes")),"automatic_application":False,"new_snapshot_required":True}
def export_plan(payload): return {"ok":True,"version":VERSION,"format":payload.get("format") or "json","object_refs":_refs(payload.get("object_refs"),"object_refs"),"include_provenance":bool(payload.get("include_provenance",True)),"include_disagreements":True,"include_heterogeneity":True,"automatic_publication":False}

def interpretation_boundaries_report(payload:dict[str,Any]|None=None):
    return {"ok":True,"version":VERSION,"pooled_effect_is_not_truth":True,"majority_direction_is_not_consensus_certification":True,"replication_match_is_not_claim_proof":True,
            "heterogeneity_is_not_automatically_failure":True,"contradictions_are_preserved":True,"uncertainty_is_preserved":True,"automatic_study_quality_scoring":False,
            "automatic_evidence_weighting":False,"automatic_consensus_certification":False,"automatic_hypothesis_selection":False,"automatic_claim_status_change":False,
            "automatic_causal_inference":False,"automatic_generalization":False,"automatic_scientific_validity_certification":False,"automatic_core_submission":False,
            "determine_truth":False,"researcher_adjudication_required":True}
