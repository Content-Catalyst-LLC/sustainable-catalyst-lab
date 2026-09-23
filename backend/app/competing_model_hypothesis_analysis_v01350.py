from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

VERSION = "0.135.0"
ENGINE_VERSION = "16.0.0"
SCHEMA = "sc-lab-competing-model-hypothesis-analysis/0.135.0"
SNAPSHOT_SCHEMA = "sc-lab-competing-model-hypothesis-analysis-snapshot/0.135.0"
MAX_ROWS = 20000
MAX_REFS = 50000
MAX_HYPOTHESES = 5000
MAX_MODELS = 5000

HYPOTHESIS_KINDS = {"primary","null","alternative","competing","mechanistic","descriptive","predictive","other"}
MODEL_KINDS = {"statistical","bayesian","causal","simulation","spatial","time-series","mechanistic","machine-learning","system-dynamics","other"}
RELATION_STATES = {"supports","challenges","consistent","inconsistent","mixed","inconclusive","not-evaluated"}
COMPARISON_FAMILIES = {
    "prediction-observation","evidence-alignment","diagnostic-aware","assumption-aware","synthesis-aware",
    "replication-aware","contradiction-analysis","scope-compatibility","model-fit-evidence","predictive-performance",
    "calibration-evidence","complexity-description","parsimony-planning","discriminating-observation","discriminating-test",
    "pairwise-comparison","cross-candidate-matrix","evidence-exclusion-sensitivity","assumption-state-sensitivity",
    "robustness-planning","counterexample-analysis","unexplained-observation-analysis","researcher-adjudication","revision-planning",
}
FIGURE_FAMILIES = {
    "hypothesis-evidence-matrix","prediction-observation-matrix","model-comparison-grid","contradiction-map",
    "diagnostic-overlay","assumption-overlay","replication-comparison","scope-compatibility-map","pairwise-comparison-card",
    "discriminating-test-map","counterexample-map","unexplained-observation-panel","robustness-dashboard",
    "evidence-exclusion-sensitivity","assumption-sensitivity","lineage-graph","researcher-decision-panel",
}

class CompetingModelHypothesisAnalysisError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code

def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode("utf-8")).hexdigest()

def _list(v: Any, label: str, maximum: int = MAX_ROWS) -> list[Any]:
    if v is None:
        return []
    if not isinstance(v, list):
        raise CompetingModelHypothesisAnalysisError(f"{label} must be an array.")
    if len(v) > maximum:
        raise CompetingModelHypothesisAnalysisError(f"{label} exceeds configured maximum of {maximum}.")
    return v

def _refs(v: Any, label: str, maximum: int = MAX_REFS) -> list[str]:
    return [str(x)[:300] for x in _list(v, label, maximum)]

def schema_info():
    return {
        "ok": True, "schema": SCHEMA, "snapshot_schema": SNAPSHOT_SCHEMA, "version": VERSION,
        "engine_version": ENGINE_VERSION, "relation_states": sorted(RELATION_STATES),
        "limits": {"hypotheses": MAX_HYPOTHESES, "models": MAX_MODELS, "refs": MAX_REFS},
    }

def catalog():
    return {
        "ok": True, "version": VERSION, "comparison_families": sorted(COMPARISON_FAMILIES),
        "hypothesis_kinds": sorted(HYPOTHESIS_KINDS), "model_kinds": sorted(MODEL_KINDS),
        "relation_states": sorted(RELATION_STATES), "figure_families": sorted(FIGURE_FAMILIES),
        "comparison_family_count": len(COMPARISON_FAMILIES), "hypothesis_kind_count": len(HYPOTHESIS_KINDS),
        "model_kind_count": len(MODEL_KINDS), "relation_state_count": len(RELATION_STATES),
        "figure_family_count": len(FIGURE_FAMILIES), "automatic_hypothesis_ranking": False,
        "automatic_model_ranking": False, "automatic_winner_selection": False,
        "automatic_truth_inference": False, "automatic_core_submission": False,
    }

def manifest():
    return {
        "ok": True, "status": "competing-model-hypothesis-analysis-ready", "version": VERSION,
        "engine_version": ENGINE_VERSION, "v01310_hypothesis_reference_bridge": True,
        "v01330_diagnostic_reference_bridge": True, "v01340_evidence_synthesis_reference_bridge": True,
        "contradictions_preserved": True, "replication_disagreement_preserved": True,
        "researcher_adjudication_required": True, "automatic_hypothesis_ranking": False,
        "automatic_model_ranking": False, "automatic_winner_selection": False,
        "automatic_scientific_validity_certification": False, "automatic_truth_inference": False,
        "automatic_core_submission": False,
    }

def health():
    return {
        **manifest(), "schema": SCHEMA, "comparison_family_count": len(COMPARISON_FAMILIES),
        "hypothesis_kind_count": len(HYPOTHESIS_KINDS), "model_kind_count": len(MODEL_KINDS),
        "figure_family_count": len(FIGURE_FAMILIES), "api_route_count": 49,
    }

def normalize_context(payload: dict[str, Any]):
    if not isinstance(payload, dict):
        raise CompetingModelHypothesisAnalysisError("payload must be an object.")
    row = {
        "context_ref": str(payload.get("context_ref") or f"comparison-context:{_hash(payload)[:16]}")[:300],
        "project_ref": payload.get("project_ref"), "session_ref": payload.get("session_ref"),
        "question_refs": _refs(payload.get("question_refs"), "question_refs"),
        "hypothesis_refs": _refs(payload.get("hypothesis_refs"), "hypothesis_refs"),
        "model_refs": _refs(payload.get("model_refs"), "model_refs"),
        "claim_refs": _refs(payload.get("claim_refs"), "claim_refs"),
        "evidence_refs": _refs(payload.get("evidence_refs"), "evidence_refs"),
        "scope": copy.deepcopy(payload.get("scope") or {}), "researcher_declared": True,
        "automatic_scope_inference": False,
    }
    row["context_hash"] = _hash(row)
    return {"ok": True, "version": VERSION, "context": row}

def hypothesis_registry(payload: dict[str, Any]):
    rows = []
    for i, r in enumerate(_list(payload.get("hypotheses"), "hypotheses", MAX_HYPOTHESES)):
        if not isinstance(r, dict):
            raise CompetingModelHypothesisAnalysisError("hypotheses must contain objects.")
        kind = str(r.get("kind") or "competing").lower()
        kind = kind if kind in HYPOTHESIS_KINDS else "other"
        row = {
            "hypothesis_ref": str(r.get("hypothesis_ref") or f"hypothesis:{i+1}"), "kind": kind,
            "statement": r.get("statement"), "prediction_refs": _refs(r.get("prediction_refs"), "prediction_refs"),
            "assumption_refs": _refs(r.get("assumption_refs"), "assumption_refs"),
            "scope": copy.deepcopy(r.get("scope") or {}), "v01310_reference": r.get("v01310_reference"),
            "researcher_declared": True, "automatic_plausibility_score": None, "automatic_rank": None,
        }
        row["hypothesis_hash"] = _hash(row)
        rows.append(row)
    return {"ok": True, "version": VERSION, "hypotheses": rows, "hypothesis_count": len(rows), "automatic_hypothesis_ranking": False}

def model_registry(payload: dict[str, Any]):
    rows = []
    for i, r in enumerate(_list(payload.get("models"), "models", MAX_MODELS)):
        if not isinstance(r, dict):
            raise CompetingModelHypothesisAnalysisError("models must contain objects.")
        kind = str(r.get("kind") or "other").lower()
        kind = kind if kind in MODEL_KINDS else "other"
        row = {
            "model_ref": str(r.get("model_ref") or f"model:{i+1}"), "kind": kind,
            "method_ref": r.get("method_ref"), "hypothesis_refs": _refs(r.get("hypothesis_refs"), "hypothesis_refs"),
            "prediction_refs": _refs(r.get("prediction_refs"), "prediction_refs"),
            "parameter_refs": _refs(r.get("parameter_refs"), "parameter_refs"),
            "assumption_refs": _refs(r.get("assumption_refs"), "assumption_refs"),
            "diagnostic_refs": _refs(r.get("diagnostic_refs"), "diagnostic_refs"),
            "scope": copy.deepcopy(r.get("scope") or {}), "automatic_fit_score": None, "automatic_rank": None,
        }
        row["model_hash"] = _hash(row)
        rows.append(row)
    return {"ok": True, "version": VERSION, "models": rows, "model_count": len(rows), "automatic_model_ranking": False}

def observation_registry(payload):
    rows = []
    for i, r in enumerate(_list(payload.get("observations"), "observations")):
        if isinstance(r, dict):
            row = {
                "observation_ref": str(r.get("observation_ref") or f"observation:{i+1}"),
                "source_ref": r.get("source_ref"), "value": copy.deepcopy(r.get("value")), "units": r.get("units"),
                "scope": copy.deepcopy(r.get("scope") or {}), "evidence_refs": _refs(r.get("evidence_refs"), "evidence_refs"),
                "observed_not_expected": True, "automatic_interpretation": False,
            }
            row["observation_hash"] = _hash(row)
            rows.append(row)
    return {"ok": True, "version": VERSION, "observations": rows, "observation_count": len(rows), "automatic_evidence_promotion": False}

def prediction_registry(payload):
    rows = []
    for i, r in enumerate(_list(payload.get("predictions"), "predictions")):
        if isinstance(r, dict):
            row = {
                "prediction_ref": str(r.get("prediction_ref") or f"prediction:{i+1}"),
                "hypothesis_refs": _refs(r.get("hypothesis_refs"), "hypothesis_refs"),
                "model_refs": _refs(r.get("model_refs"), "model_refs"), "observable_ref": r.get("observable_ref"),
                "expected": copy.deepcopy(r.get("expected")), "scope": copy.deepcopy(r.get("scope") or {}),
                "v01310_reference": r.get("v01310_reference"), "expected_not_observed": True, "automatic_test_result": None,
            }
            row["prediction_hash"] = _hash(row)
            rows.append(row)
    return {"ok": True, "version": VERSION, "predictions": rows, "prediction_count": len(rows), "expected_observations_are_not_evidence": True}

def prediction_observation_matrix(payload):
    rows = []
    for i, r in enumerate(_list(payload.get("comparisons"), "comparisons")):
        if not isinstance(r, dict):
            continue
        relation = str(r.get("relation") or "not-evaluated").lower()
        if relation not in RELATION_STATES:
            raise CompetingModelHypothesisAnalysisError(f"invalid relation: {relation}")
        rows.append({
            "comparison_ref": str(r.get("comparison_ref") or f"prediction-comparison:{i+1}"),
            "prediction_ref": r.get("prediction_ref"), "observation_ref": r.get("observation_ref"),
            "hypothesis_refs": _refs(r.get("hypothesis_refs"), "hypothesis_refs"),
            "model_refs": _refs(r.get("model_refs"), "model_refs"), "relation": relation,
            "rationale": r.get("rationale"), "researcher_declared_or_external_evaluation": True,
            "automatic_hypothesis_update": False,
        })
    return {"ok": True, "version": VERSION, "matrix": rows, "matrix_hash": _hash(rows), "automatic_winner_selection": False}

def evidence_alignment_matrix(payload):
    rows = []
    for i, r in enumerate(_list(payload.get("alignments"), "alignments")):
        if not isinstance(r, dict):
            continue
        state = str(r.get("state") or "not-evaluated").lower()
        if state not in RELATION_STATES:
            raise CompetingModelHypothesisAnalysisError(f"invalid state: {state}")
        rows.append({
            "alignment_ref": str(r.get("alignment_ref") or f"evidence-alignment:{i+1}"),
            "evidence_ref": r.get("evidence_ref"), "hypothesis_ref": r.get("hypothesis_ref"),
            "model_ref": r.get("model_ref"), "state": state, "source_synthesis_ref": r.get("source_synthesis_ref"),
            "weight": None, "automatic_evidence_weighting": False,
        })
    return {"ok": True, "version": VERSION, "alignments": rows, "alignment_hash": _hash(rows), "automatic_evidence_weighting": False}

def diagnostic_bridge(payload):
    return {"ok": True, "version": VERSION, "assumption_refs": _refs(payload.get("assumption_refs"), "assumption_refs"),
            "diagnostic_refs": _refs(payload.get("diagnostic_refs"), "diagnostic_refs"), "v01330_reference_first": True,
            "automatic_model_rejection": False, "automatic_hypothesis_rejection": False}

def synthesis_bridge(payload):
    return {"ok": True, "version": VERSION, "synthesis_refs": _refs(payload.get("synthesis_refs"), "synthesis_refs"),
            "claim_refs": _refs(payload.get("claim_refs"), "claim_refs"), "evidence_refs": _refs(payload.get("evidence_refs"), "evidence_refs"),
            "v01340_reference_first": True, "automatic_consensus_import": False, "automatic_truth_import": False}

def replication_bridge(payload):
    return {"ok": True, "version": VERSION, "replication_refs": _refs(payload.get("replication_refs"), "replication_refs"),
            "reproduction_refs": _refs(payload.get("reproduction_refs"), "reproduction_refs"),
            "agreement_state": payload.get("agreement_state") or "not-evaluated", "replication_disagreement_preserved": True,
            "automatic_replication_certification": False}

def contradiction_matrix(payload):
    rows = []
    for r in _list(payload.get("candidates"), "candidates"):
        if not isinstance(r, dict):
            continue
        supports = _refs(r.get("supporting_evidence_refs"), "supporting_evidence_refs")
        challenges = _refs(r.get("challenging_evidence_refs"), "challenging_evidence_refs")
        rows.append({"candidate_ref": r.get("candidate_ref"), "supporting_evidence_refs": supports,
                     "challenging_evidence_refs": challenges, "mixed_evidence": bool(supports and challenges),
                     "automatic_resolution": False})
    return {"ok": True, "version": VERSION, "candidates": rows, "contradictions_preserved": True, "automatic_resolution": False}

def scope_compatibility_report(payload):
    rows = copy.deepcopy(_list(payload.get("comparisons"), "comparisons"))
    return {"ok": True, "version": VERSION, "comparisons": rows, "researcher_scope_review_required": True,
            "automatic_scope_equivalence": False, "automatic_generalization": False}

def assumption_compatibility_report(payload):
    rows = []
    for r in _list(payload.get("candidates"), "candidates"):
        if isinstance(r, dict):
            rows.append({"candidate_ref": r.get("candidate_ref"),
                         "satisfied_refs": _refs(r.get("satisfied_refs"), "satisfied_refs"),
                         "violated_refs": _refs(r.get("violated_refs"), "violated_refs"),
                         "uncertain_refs": _refs(r.get("uncertain_refs"), "uncertain_refs"),
                         "untested_refs": _refs(r.get("untested_refs"), "untested_refs"), "automatic_rejection": False})
    return {"ok": True, "version": VERSION, "candidates": rows, "automatic_model_rejection": False, "automatic_hypothesis_rejection": False}

def model_fit_evidence_report(payload):
    rows = []
    for r in _list(payload.get("models"), "models", MAX_MODELS):
        if isinstance(r, dict):
            rows.append({"model_ref": r.get("model_ref"), "metrics": copy.deepcopy(r.get("metrics") or {}),
                         "diagnostic_refs": _refs(r.get("diagnostic_refs"), "diagnostic_refs"),
                         "metric_semantics": copy.deepcopy(r.get("metric_semantics") or {}),
                         "automatic_fit_grade": None, "automatic_rank": None})
    return {"ok": True, "version": VERSION, "models": rows, "automatic_model_ranking": False, "fit_is_not_truth": True}

def predictive_performance_report(payload):
    rows = []
    for r in _list(payload.get("models"), "models", MAX_MODELS):
        if isinstance(r, dict):
            rows.append({"model_ref": r.get("model_ref"), "evaluation_refs": _refs(r.get("evaluation_refs"), "evaluation_refs"),
                         "metrics": copy.deepcopy(r.get("metrics") or {}), "evaluation_scope": copy.deepcopy(r.get("evaluation_scope") or {}),
                         "automatic_superiority_claim": False})
    return {"ok": True, "version": VERSION, "models": rows, "prediction_is_not_causation": True, "automatic_winner_selection": False}

def calibration_report(payload):
    return {"ok": True, "version": VERSION, "model_refs": _refs(payload.get("model_refs"), "model_refs"),
            "calibration_refs": _refs(payload.get("calibration_refs"), "calibration_refs"),
            "calibration_metrics": copy.deepcopy(payload.get("calibration_metrics") or {}),
            "automatic_calibration_certification": False, "automatic_rank": None}

def complexity_report(payload):
    rows = []
    for r in _list(payload.get("candidates"), "candidates"):
        if isinstance(r, dict):
            rows.append({"candidate_ref": r.get("candidate_ref"), "parameter_count": r.get("parameter_count"),
                         "structural_notes": r.get("structural_notes"), "computational_notes": r.get("computational_notes"),
                         "researcher_declared": True, "automatic_complexity_penalty": False})
    return {"ok": True, "version": VERSION, "candidates": rows, "automatic_parsimony_judgment": False}

def parsimony_comparison_plan(payload):
    return {"ok": True, "version": VERSION, "candidate_refs": _refs(payload.get("candidate_refs"), "candidate_refs"),
            "criteria": copy.deepcopy(_list(payload.get("criteria"), "criteria")), "researcher_declared_criteria": True,
            "automatic_parsimony_judgment": False, "automatic_winner_selection": False}

def discriminating_observation_plan(payload):
    rows = []
    for r in _list(payload.get("observations"), "observations"):
        if isinstance(r, dict):
            rows.append({"observation_ref": r.get("observation_ref"), "candidate_predictions": copy.deepcopy(r.get("candidate_predictions") or {}),
                         "discriminating_rationale": r.get("discriminating_rationale"), "researcher_declared": True,
                         "automatic_preference": False})
    return {"ok": True, "version": VERSION, "observations": rows, "automatic_hypothesis_selection": False}

def discriminating_test_plan(payload):
    rows = []
    for r in _list(payload.get("tests"), "tests"):
        if isinstance(r, dict):
            rows.append({"test_ref": r.get("test_ref"), "candidate_refs": _refs(r.get("candidate_refs"), "candidate_refs"),
                         "method_ref": r.get("method_ref"), "expected_patterns": copy.deepcopy(r.get("expected_patterns") or {}),
                         "assumption_refs": _refs(r.get("assumption_refs"), "assumption_refs"),
                         "researcher_declared": True, "automatic_test_choice": False})
    return {"ok": True, "version": VERSION, "tests": rows, "automatic_method_selection": False, "automatic_winner_selection": False}

def pairwise_comparison(payload):
    return {"ok": True, "version": VERSION, "candidate_a_ref": payload.get("candidate_a_ref"),
            "candidate_b_ref": payload.get("candidate_b_ref"),
            "comparison_dimensions": copy.deepcopy(payload.get("comparison_dimensions") or {}),
            "supporting_evidence_a": _refs(payload.get("supporting_evidence_a"), "supporting_evidence_a"),
            "supporting_evidence_b": _refs(payload.get("supporting_evidence_b"), "supporting_evidence_b"),
            "challenging_evidence_a": _refs(payload.get("challenging_evidence_a"), "challenging_evidence_a"),
            "challenging_evidence_b": _refs(payload.get("challenging_evidence_b"), "challenging_evidence_b"),
            "automatic_pairwise_winner": None, "researcher_interpretation_required": True}

def comparison_matrix(payload):
    refs = _refs(payload.get("candidate_refs"), "candidate_refs")
    dims = copy.deepcopy(_list(payload.get("dimensions"), "dimensions"))
    return {"ok": True, "version": VERSION, "candidate_refs": refs, "dimensions": dims,
            "cells": copy.deepcopy(_list(payload.get("cells"), "cells")), "row_order": refs,
            "automatic_sorting": False, "automatic_scoring": False, "automatic_ranking": False}

def evidence_exclusion_sensitivity(payload):
    return {"ok": True, "version": VERSION, "candidate_refs": _refs(payload.get("candidate_refs"), "candidate_refs"),
            "excluded_evidence_refs": _refs(payload.get("excluded_evidence_refs"), "excluded_evidence_refs"),
            "comparison_refs": _refs(payload.get("comparison_refs"), "comparison_refs"),
            "researcher_declared_exclusions": True, "automatic_evidence_exclusion": False, "automatic_winner_selection": False}

def assumption_state_sensitivity(payload):
    return {"ok": True, "version": VERSION, "candidate_refs": _refs(payload.get("candidate_refs"), "candidate_refs"),
            "assumption_scenarios": copy.deepcopy(_list(payload.get("assumption_scenarios"), "assumption_scenarios")),
            "v01330_reference_first": True, "automatic_assumption_override": False, "automatic_winner_selection": False}

def robustness_plan(payload):
    return {"ok": True, "version": VERSION, "candidate_refs": _refs(payload.get("candidate_refs"), "candidate_refs"),
            "checks": copy.deepcopy(_list(payload.get("checks"), "checks")), "evidence_exclusion_checks": True,
            "assumption_sensitivity_checks": True, "replication_checks": True, "automatic_robustness_certification": False}

def counterexample_registry(payload):
    rows = []
    for i, r in enumerate(_list(payload.get("counterexamples"), "counterexamples")):
        if isinstance(r, dict):
            rows.append({"counterexample_ref": str(r.get("counterexample_ref") or f"counterexample:{i+1}"),
                         "candidate_refs": _refs(r.get("candidate_refs"), "candidate_refs"),
                         "evidence_refs": _refs(r.get("evidence_refs"), "evidence_refs"),
                         "description": r.get("description"), "researcher_declared": True, "automatic_rejection": False})
    return {"ok": True, "version": VERSION, "counterexamples": rows, "automatic_hypothesis_rejection": False, "automatic_model_rejection": False}

def unexplained_observation_report(payload):
    rows = []
    for r in _list(payload.get("observations"), "observations"):
        if isinstance(r, dict):
            rows.append({"observation_ref": r.get("observation_ref"), "candidate_refs": _refs(r.get("candidate_refs"), "candidate_refs"),
                         "notes": r.get("notes"), "unexplained": bool(r.get("unexplained", True)),
                         "automatic_anomaly_explanation": False})
    return {"ok": True, "version": VERSION, "observations": rows, "candidate_revision_may_be_required": True,
            "automatic_new_hypothesis_generation": False}

def hypothesis_revision_plan(payload):
    return {"ok": True, "version": VERSION, "hypothesis_ref": payload.get("hypothesis_ref"),
            "base_snapshot_ref": payload.get("base_snapshot_ref"), "changes": copy.deepcopy(_list(payload.get("changes"), "changes")),
            "post_hoc_revision_visible": True, "automatic_application": False, "new_snapshot_required": True}

def model_revision_plan(payload):
    return {"ok": True, "version": VERSION, "model_ref": payload.get("model_ref"), "base_model_ref": payload.get("base_model_ref"),
            "changes": copy.deepcopy(_list(payload.get("changes"), "changes")), "reason": payload.get("reason"),
            "automatic_application": False, "new_model_version_required": True}

def researcher_shortlist(payload):
    refs = _refs(payload.get("candidate_refs"), "candidate_refs")
    return {"ok": True, "version": VERSION, "candidate_refs": refs, "rationale": payload.get("rationale"),
            "researcher_declared": True, "automatic_shortlist": False, "order_is_researcher_controlled": True}

def adjudication_record(payload):
    row = {"adjudication_ref": str(payload.get("adjudication_ref") or f"comparison-adjudication:{_hash(payload)[:16]}"),
           "candidate_refs": _refs(payload.get("candidate_refs"), "candidate_refs"), "decision": payload.get("decision"),
           "rationale": payload.get("rationale"), "evidence_refs": _refs(payload.get("evidence_refs"), "evidence_refs"),
           "diagnostic_refs": _refs(payload.get("diagnostic_refs"), "diagnostic_refs"),
           "researcher_declared": True, "automatic_adjudication": False}
    row["adjudication_hash"] = _hash(row)
    return {"ok": True, "version": VERSION, "adjudication": row}

def decision_rule_plan(payload):
    return {"ok": True, "version": VERSION, "candidate_refs": _refs(payload.get("candidate_refs"), "candidate_refs"),
            "rules": copy.deepcopy(_list(payload.get("rules"), "rules")),
            "declared_before_evaluation": bool(payload.get("declared_before_evaluation", False)),
            "researcher_declared": True, "automatic_rule_generation": False, "automatic_rule_execution": False}

def status_report(payload):
    return {"ok": True, "version": VERSION, "status": "researcher-comparison-review-required",
            "candidate_refs": _refs(payload.get("candidate_refs"), "candidate_refs"),
            "unresolved_contradiction_refs": _refs(payload.get("unresolved_contradiction_refs"), "unresolved_contradiction_refs"),
            "automatic_winner_selection": False, "determine_truth": False}

def readiness_report(payload):
    checks = copy.deepcopy(payload.get("checks") or {})
    required = ["candidates_registered", "predictions_registered", "observations_registered", "evidence_linked",
                "diagnostics_reviewed", "contradictions_reviewed", "researcher_adjudication_plan"]
    missing = [k for k in required if checks.get(k) is not True]
    return {"ok": True, "version": VERSION, "structurally_ready": not missing, "missing": missing,
            "scientific_validity_certified": False, "winner_certified": False, "researcher_review_required": True}

def visualization_plan(payload):
    figs = _refs(payload.get("figure_families"), "figure_families") or sorted(FIGURE_FAMILIES)
    return {"ok": True, "version": VERSION,
            "figures": [{"figure_family": f, "semantic_role": "competing-model-hypothesis-analysis", "evidence_weight": None} for f in figs],
            "automatic_visual_prominence_as_evidence_weight": False, "automatic_winner_highlighting": False}

def provenance_aggregate(payload):
    p = {"question_refs": _refs(payload.get("question_refs"), "question_refs"),
         "hypothesis_refs": _refs(payload.get("hypothesis_refs"), "hypothesis_refs"),
         "model_refs": _refs(payload.get("model_refs"), "model_refs"),
         "prediction_refs": _refs(payload.get("prediction_refs"), "prediction_refs"),
         "observation_refs": _refs(payload.get("observation_refs"), "observation_refs"),
         "evidence_refs": _refs(payload.get("evidence_refs"), "evidence_refs"),
         "diagnostic_refs": _refs(payload.get("diagnostic_refs"), "diagnostic_refs"),
         "synthesis_refs": _refs(payload.get("synthesis_refs"), "synthesis_refs"),
         "replication_refs": _refs(payload.get("replication_refs"), "replication_refs")}
    p["provenance_hash"] = _hash(p)
    return {"ok": True, "version": VERSION, "provenance": p, "automatic_evidence_promotion": False}

def lineage_graph(payload):
    nodes = copy.deepcopy(_list(payload.get("nodes"), "nodes"))
    edges = copy.deepcopy(_list(payload.get("edges"), "edges"))
    return {"ok": True, "version": VERSION, "nodes": nodes, "edges": edges,
            "graph_hash": _hash({"nodes": nodes, "edges": edges}), "automatic_causal_interpretation": False,
            "automatic_truth_inference": False}

def project_binding(payload):
    return {"ok": True, "version": VERSION, "project_ref": payload.get("project_ref"), "workspace_ref": payload.get("workspace_ref"),
            "reference_first": True, "automatic_project_mutation": False}

def session_binding(payload):
    return {"ok": True, "version": VERSION, "session_ref": payload.get("session_ref"), "context_ref": payload.get("context_ref"),
            "reference_first": True, "automatic_session_mutation": False}

def handoff_plan(payload):
    return {"ok": True, "version": VERSION, "source_product": "lab", "target_product": payload.get("target_product"),
            "object_refs": _refs(payload.get("object_refs"), "object_refs"), "reference_first": True,
            "automatic_execution": False, "automatic_submission": False}

def core_object_plan(payload):
    return {"ok": True, "version": VERSION, "core_minimum_version": "3.0.0", "object_type": "competing-model-hypothesis-analysis",
            "project_ref": payload.get("project_ref"), "hypothesis_refs": _refs(payload.get("hypothesis_refs"), "hypothesis_refs"),
            "model_refs": _refs(payload.get("model_refs"), "model_refs"), "evidence_refs": _refs(payload.get("evidence_refs"), "evidence_refs"),
            "comparison_refs": _refs(payload.get("comparison_refs"), "comparison_refs"), "reference_first": True,
            "core_owns_canonical_claim_evidence_hypothesis_objects": True, "core_does_not_execute_model_comparison": True,
            "core_does_not_select_winner": True, "automatic_core_submission": False}

def build_snapshot(payload):
    content = copy.deepcopy(payload.get("content") or payload)
    ref = f"competing-model-hypothesis-analysis-snapshot:{_hash(content)}"
    return {"ok": True, "version": VERSION,
            "snapshot": {"snapshot_ref": ref, "schema": SNAPSHOT_SCHEMA, "content": content,
                         "content_hash": _hash(content), "immutable": True},
            "automatic_interpretation": False}

def revision_plan(payload):
    return {"ok": True, "version": VERSION, "base_snapshot_ref": payload.get("base_snapshot_ref"),
            "changes": copy.deepcopy(_list(payload.get("changes"), "changes")), "automatic_application": False,
            "new_snapshot_required": True}

def export_plan(payload):
    return {"ok": True, "version": VERSION, "format": payload.get("format") or "json",
            "object_refs": _refs(payload.get("object_refs"), "object_refs"),
            "include_provenance": bool(payload.get("include_provenance", True)),
            "include_contradictions": True, "include_diagnostics": True, "automatic_publication": False}

def interpretation_boundaries_report(payload: dict[str, Any] | None = None):
    return {"ok": True, "version": VERSION, "prediction_match_is_not_truth": True, "better_fit_is_not_truth": True,
            "predictive_performance_is_not_causal_proof": True, "parsimony_is_not_automatic_superiority": True,
            "replication_agreement_is_not_claim_proof": True, "contradictions_are_preserved": True, "uncertainty_is_preserved": True,
            "automatic_hypothesis_ranking": False, "automatic_model_ranking": False, "automatic_winner_selection": False,
            "automatic_evidence_weighting": False, "automatic_hypothesis_rejection": False, "automatic_model_rejection": False,
            "automatic_causal_inference": False, "automatic_generalization": False,
            "automatic_scientific_validity_certification": False, "automatic_core_submission": False,
            "determine_truth": False, "researcher_adjudication_required": True}
