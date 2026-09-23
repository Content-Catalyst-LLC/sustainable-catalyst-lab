from app.competing_model_hypothesis_analysis_v01350 import *

def test_catalog_and_boundaries():
    c=catalog(); b=interpretation_boundaries_report()
    assert c["comparison_family_count"]>=20 and c["figure_family_count"]>=15
    assert c["automatic_winner_selection"] is False and b["determine_truth"] is False

def test_hypothesis_registry_no_rank():
    r=hypothesis_registry({"hypotheses":[{"hypothesis_ref":"h1","kind":"competing","statement":"x"}]})
    assert r["hypotheses"][0]["automatic_rank"] is None and r["automatic_hypothesis_ranking"] is False

def test_prediction_observation_matrix_preserves_declared_relation():
    r=prediction_observation_matrix({"comparisons":[{"prediction_ref":"p1","observation_ref":"o1","relation":"challenges","hypothesis_refs":["h1"]}]})
    assert r["matrix"][0]["relation"]=="challenges" and r["matrix"][0]["automatic_hypothesis_update"] is False

def test_contradictions_preserved():
    r=contradiction_matrix({"candidates":[{"candidate_ref":"h1","supporting_evidence_refs":["e1"],"challenging_evidence_refs":["e2"]}]})
    assert r["candidates"][0]["mixed_evidence"] is True and r["automatic_resolution"] is False

def test_diagnostic_bridge_does_not_reject():
    r=diagnostic_bridge({"assumption_refs":["a1"],"diagnostic_refs":["d1"]})
    assert r["v01330_reference_first"] is True and r["automatic_model_rejection"] is False

def test_pairwise_has_no_winner():
    r=pairwise_comparison({"candidate_a_ref":"h1","candidate_b_ref":"h2","comparison_dimensions":{"prediction_match":"different"}})
    assert r["automatic_pairwise_winner"] is None and r["researcher_interpretation_required"] is True

def test_comparison_matrix_does_not_score_or_rank():
    r=comparison_matrix({"candidate_refs":["h2","h1"],"dimensions":["evidence","diagnostics"]})
    assert r["row_order"]==["h2","h1"] and r["automatic_scoring"] is False and r["automatic_ranking"] is False

def test_replication_disagreement_preserved():
    r=replication_bridge({"replication_refs":["r1"],"agreement_state":"disagrees"})
    assert r["replication_disagreement_preserved"] is True and r["automatic_replication_certification"] is False

def test_readiness_structural_not_truth():
    checks={k:True for k in ["candidates_registered","predictions_registered","observations_registered","evidence_linked","diagnostics_reviewed","contradictions_reviewed","researcher_adjudication_plan"]}
    r=readiness_report({"checks":checks})
    assert r["structurally_ready"] is True and r["winner_certified"] is False and r["scientific_validity_certified"] is False

def test_snapshot_deterministic():
    a=build_snapshot({"content":{"b":2,"a":1}}); b=build_snapshot({"content":{"a":1,"b":2}})
    assert a["snapshot"]["snapshot_ref"]==b["snapshot"]["snapshot_ref"]

def test_core_plan_reference_first():
    r=core_object_plan({"project_ref":"p1","hypothesis_refs":["h1"],"model_refs":["m1"]})
    assert r["reference_first"] is True and r["core_does_not_select_winner"] is True and r["automatic_core_submission"] is False
