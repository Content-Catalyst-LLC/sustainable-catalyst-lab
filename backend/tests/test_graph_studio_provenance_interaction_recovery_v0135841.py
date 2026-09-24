from app import graph_studio_provenance_interaction_recovery_v0135841 as m

def test_health_and_acceptance():
    h=m.health(); assert h["ok"] is True and h["api_route_count"] == 8
    assert h["delegated_interaction"] is True and h["programmatic_layout_click"] is False
    a=m.acceptance_report(); assert a["layout_control_count"] == 3 and a["programmatic_layout_clicks"] == 0

def test_layout_and_selection_contracts():
    l=m.layout_contract(); assert l["layouts"] == ["layered","radial","swimlane"] and l["replaces_svg_nodes"] is False
    s=m.selection_contract(); assert s["survives_renderer_node_replacement"] is True and s["changes_claim_status"] is False

def test_interaction_plan_never_requires_synthetic_click():
    p=m.interaction_plan({"layout":"radial","exploration_mode":"upstream","relation_filter":"supports","selected_node":"figure"})
    assert p["layout"] == "radial" and p["exploration_mode"] == "upstream" and p["requires_synthetic_click"] is False
    assert p["scientific_mutation"] is False

def test_invalid_values_fall_back_safely():
    p=m.interaction_plan({"layout":"magic","exploration_mode":"auto","relation_filter":"causes"})
    assert p["layout"] == "layered" and p["exploration_mode"] == "all" and p["relation_filter"] == "all"
