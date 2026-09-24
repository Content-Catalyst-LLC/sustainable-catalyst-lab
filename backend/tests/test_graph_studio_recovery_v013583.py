from app import graph_studio_recovery_v013583 as m
def test_health_and_acceptance():
    h=m.health(); assert h['version']=='0.135.8.3' and h['api_route_count']==16 and h['single_renderer_root'] and h['scientific_state_hydration']
    a=m.acceptance_report(); assert a['renderer_roots']==1 and a['visible_primary_viewports']==1 and a['duplicate_renderer_headers']==0
def test_hydration_and_boundaries():
    p=m.hydration_plan({'reference':'figure:1'}); assert p['priority'][0]=='active-graph' and not p['fabricates_scientific_values']
    b=m.boundaries_report(); assert not b['automatic_causal_inference'] and not b['automatic_core_submission']
def test_provenance():
    p=m.provenance_plan(); assert p['interactive_node_inspection'] and 'radial' in p['layouts'] and not p['structural_paths_are_causal']
