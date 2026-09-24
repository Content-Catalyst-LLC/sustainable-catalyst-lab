from app import graph_studio_bootstrap_finalization_v0135831 as m

def test_health_and_acceptance():
    assert m.health()["ok"] is True
    assert m.health()["api_route_count"] == 8
    a=m.acceptance_report(); assert a["loading_banners"]==0 and a["renderer_31_hosts"]==1 and a["renderer_30_visible_hosts"]==0 and a["primary_viewports"]==1

def test_boundaries():
    assert m.bootstrap_plan()["illustrative_bootstrap_is_scientific_record"] is False
    assert m.hydration_contract()["fabricates_scientific_values"] is False
    assert m.boundaries()["automatic_core_submission"] is False
