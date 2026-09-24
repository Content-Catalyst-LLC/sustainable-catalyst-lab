from app import graph_studio_canonical_runtime_v013581 as m

def test_health_and_catalog():
    h=m.health(); assert h['ok'] and h['version']=='0.135.8.1' and h['api_route_count']==16
    c=m.catalog(); assert c['view_count']==8 and c['capability_panel_count']==13

def test_single_view_and_adapter_boundaries():
    assert m.verify_runtime({'visible_views':['figure']})['ok'] is True
    assert m.verify_runtime({'visible_views':['figure','analysis']})['ok'] is False
    assert m.isolate_capability({'capability':'webgpu'})['primary_renderer_owner'] is False
    assert m.asset_audit({'primary_renderer_owners':['canonical-runtime']})['ok'] is True
    assert m.boundaries_report()['presentation_state_is_scientific_record'] is False
