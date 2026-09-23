from app.scientific_visualization_experience_v01351 import *


def test_health_catalog_and_schema():
    assert health()["version"] == "0.135.1"
    assert health()["api_route_count"] == 32
    assert catalog()["panel_family_count"] == 12
    assert catalog()["capability_family_count"] == 12
    assert schema_info()["schema"].endswith("/0.135.1")


def test_workspace_composition_is_multi_panel_and_non_fabricating():
    out = compose_workspace({})["workspace"]
    assert out["panel_count"] == 12
    assert out["linked_selection"] is True
    assert out["fabricate_missing_scientific_values"] is False


def test_model_architecture_is_declarative():
    graph = model_architecture_graph({})["graph"]
    assert len(graph["nodes"]) >= 6
    assert graph["declarative_not_executed"] is True
    assert graph["automatic_model_inference"] is False


def test_analytical_panels_preserve_missing_state():
    panels = analytical_panels_plan({"bindings": {}})["panels"]
    assert panels["sensitivity_influence"]["state"] == "not-linked"
    assert panels["residual_diagnostics"]["state"] == "not-linked"


def test_evidence_and_assumptions_are_reference_first():
    panel = evidence_assumption_panel({"assumption_refs": ["a1"], "evidence_refs": ["e1"]})["panel"]
    assert panel["assumption_refs"] == ["a1"]
    assert panel["evidence_weight_not_inferred"] is True


def test_linked_views_do_not_infer_joins():
    out = linked_view_plan({})
    assert "selection" in out["channels"]
    assert out["automatic_join_inference"] is False


def test_accessibility_audit_is_not_certification():
    out = accessibility_audit({"color_only_encoding": True})
    assert "color-only-encoding" in out["issues"]
    assert out["audit_is_not_certification"] is True


def test_snapshot_determinism():
    payload = {"figure_ref": "f1", "view_mode": "analysis"}
    assert build_snapshot(payload)["snapshot"]["snapshot_hash"] == build_snapshot(payload)["snapshot"]["snapshot_hash"]


def test_core_plan_preserves_lab_core_boundary():
    out = core_visual_object_plan({"figure_refs": ["f1"]})
    assert out["core_owns_semantic_visual_object"] is True
    assert out["lab_owns_scientific_rendering"] is True
    assert out["automatic_core_submission"] is False


def test_interpretation_boundaries():
    out = interpretation_boundaries_report()
    assert out["fabricate_missing_scientific_values"] is False
    assert out["determine_truth"] is False
