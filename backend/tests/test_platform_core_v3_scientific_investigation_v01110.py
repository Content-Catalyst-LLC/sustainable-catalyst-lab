from app.platform_core_v3_scientific_investigation_v01110 import (
    bridge_evidence_context, bridge_reasoning_context, bridge_scientific_assets,
    build_core_investigation_binding, build_runtime_integration_plan,
    check_investigation_continuity, health, manifest, map_legacy_argumentation_case,
    map_legacy_scientific_study, normalize_investigation,
)

CTX={"project_ref":"project:p1","session_id":"9","session_key":"s1","title":"Study","workflow_ref":"lab:workflow:w1","project_state_ref":"core:state:1","researcher_ref":"researcher:r1"}

def investigation():
    return {
        "id":"inv1","investigation_type":"computational","title":"Model investigation","status":"active",
        "research_questions":["How does the model behave under the declared assumptions?"],
        "dataset_refs":["lab:dataset:d1"],"model_refs":["lab:model:m1"],"experiment_refs":["lab:experiment:e1"],
        "analysis_refs":["lab:analysis:a1"],"execution_refs":["lab:execution:r1"],"evidence_refs":["lab:evidence:ev1"],
        "claim_refs":["lab:claim:c1"],"hypothesis_refs":["lab:hypothesis:h1"],"visual_refs":["lab:visual:v1"],
        "validation_refs":["lab:validation:x1"],"package_refs":["lab:research-package:p1"],"protocol_refs":["lab:protocol:pr1"],
        "method_refs":["lab:method:mm1"],"source_refs":["library:source:s1"],
    }

def test_normalize_and_core_binding():
    n=normalize_investigation({"context":CTX,"investigation":investigation()}); inv=n["investigation"]
    assert inv["investigation_ref"]=="lab:scientific-investigation:inv1" and inv["investigation_type"]=="computational"
    assert inv["core_selects_hypotheses"] is False and len(inv["investigation_hash"])==64
    b=build_core_investigation_binding({"context":CTX,"investigation":investigation()})
    assert b["automatic_submission"] is False and b["automatic_execution"] is False
    assert b["data"]["session_id"]=="9" and b["data"]["evidence_refs"]==["lab:evidence:ev1"]
    assert b["data"]["metadata"]["execution_refs"]==["lab:execution:r1"]

def test_context_bridges_and_plan():
    payload={"context":CTX,"investigation":investigation()}
    e=bridge_evidence_context(payload); r=bridge_reasoning_context(payload); a=bridge_scientific_assets(payload); p=build_runtime_integration_plan(payload)
    assert e["automatic_evidence_ranking"] is False and r["automatic_hypothesis_ranking"] is False
    assert a["asset_counts"]["execution_refs"]==1 and a["automatic_binding_submission"] is False
    assert p["plan"]["primary_operation"]["endpoint"].endswith("/investigation-bindings")
    assert p["plan"]["automatic_investigation_run"] is False and len(p["plan"]["related_binding_requirements"])>=8

def test_continuity_is_reference_continuity_only():
    c=check_investigation_continuity({"context":CTX,"investigation":investigation(),"expected_context":{"project_ref":"project:p1","session_id":"9"}})
    assert c["ok"] is True and c["reference_continuity_valid"] is True
    assert c["scientific_validity_assessed"] is False and c["evidence_quality_ranked"] is False

def test_legacy_study_mapping_does_not_promote_hypotheses_to_truth():
    study={"schema":"sc-lab-scientific-study/0.61.0","id":"s1","title":"Study","studyType":"experimental","status":"active","researchQuestion":"RQ","hypotheses":["H1"],"evidenceRefs":["lab:evidence:e1"]}
    m=map_legacy_scientific_study({"context":CTX,"study":study})
    assert m["investigation"]["investigation_type"]=="experimental" and m["legacy_hypothesis_text_promoted_to_truth"] is False
    assert len(m["investigation"]["hypothesis_refs"])==1 and m["core_binding"]["automatic_submission"] is False

def test_legacy_argumentation_mapping_keeps_hypotheses_unranked():
    case={"id":"case1","title":"Alternatives","hypotheses":[{"id":"h1"},{"id":"h2"}],"evidenceRefs":["lab:evidence:e1"]}
    m=map_legacy_argumentation_case({"context":CTX,"case":case})
    assert len(m["investigation"]["hypothesis_refs"])==2 and m["automatic_hypothesis_ranking"] is False

def test_manifest_boundaries():
    h=health(); m=manifest()
    assert h["lab_release_version"]=="0.111.0" and h["minimum_core_release"]=="3.0.0"
    assert m["boundaries"]["core_runs_scientific_investigation"] is False
    assert m["boundaries"]["core_determines_truth"] is False
