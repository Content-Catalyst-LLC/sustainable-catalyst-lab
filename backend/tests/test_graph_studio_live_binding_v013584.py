from app import graph_studio_live_binding_v013584 as m


def test_health_and_acceptance():
    h=m.health(); assert h["ok"] is True and h["api_route_count"] == 12
    a=m.acceptance_report(); assert a["renderer_31_hosts"] == 1 and a["primary_viewports"] == 1 and a["legacy_primary_owners"] == 0


def test_binding_does_not_invent_ids():
    p=m.binding_plan({"project_id":"p1","figure_id":"missing","available_figure_ids":["f2","f1"]})
    assert p["resolved_figure_id"] == "f2" and p["invented_figure_id"] is False


def test_restore_is_project_scoped():
    s={"project_id":"p1","figure_id":"f1","renderer_mode":"provenance"}
    assert m.restore_plan({"project_id":"p1","state":s})["restore_figure_id"] == "f1"
    assert m.restore_plan({"project_id":"p2","state":s})["restore_figure_id"] is None


def test_provenance_boundaries():
    p=m.provenance_plan({"selected_node":"figure","mode":"upstream","relation_filter":"supports"})
    assert p["selected_node"] == "figure" and p["mode"] == "upstream" and p["inferred_relationships"] is False and p["causal_interpretation"] is False
    s=m.selection_plan({"node_id":"evidence"}); assert s["selection_changes_evidence_weight"] is False and s["selection_changes_claim_status"] is False
