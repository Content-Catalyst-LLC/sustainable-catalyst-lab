from app.main import app
from app.interactive_scientific_scene_drilldown_v01354 import *

def sample():
    return {'scene_ref':'scene:test','canvas_ref':'canvas:test','view_mode':'drill','navigation_mode':'pan-zoom','lod_mode':'adaptive','layers':[
      {'layer_id':'figure','layer_type':'figure','state':'derived','object_refs':['figure:1']},
      {'layer_id':'data','layer_type':'data','state':'bound','object_refs':['dataset:1']},
      {'layer_id':'prov','layer_type':'provenance','state':'bound','object_refs':['graph:1']},
      {'layer_id':'unc','layer_type':'uncertainty','state':'declared','object_refs':['uncertainty:1']},
    ],'mappings':[{'mapping_ref':'map:figure-row','source_ref':'figure:point:1','target_ref':'row:1'}]}

def test_health_catalog_routes():
    assert health()['version']=='0.135.4' and health()['api_route_count']==45
    assert catalog()['layer_type_count']==12 and catalog()['drill_target_type_count']==8
    assert catalog()['view_mode_count']==6 and catalog()['navigation_mode_count']==5 and catalog()['lod_mode_count']==4
    paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
    assert len({p for p in paths if p.startswith('/v1/interactive-scientific-scene-drilldown')})==45

def test_scene_normalization_and_composition_are_reference_first():
    s=normalize_scene(sample())['scene']; assert s['layer_count']==4 and s['mapping_count']==1
    assert s['camera_is_presentation_state'] and s['drill_down_mutates_scientific_record'] is False
    assert s['automatic_hierarchy_inference'] is False and s['automatic_join_inference'] is False
    c=compose_scene(sample()); assert c['drill_down_enabled'] and c['scientific_objects_mutated'] is False

def test_drill_path_requires_explicit_parent_relationships():
    r=drill_path({'path':[{'ref':'scene','target_type':'object'},{'ref':'layer:1','target_type':'layer','parent_ref':'scene'},{'ref':'row:1','target_type':'row','parent_ref':'layer:1'}]})
    assert r['depth']==3 and r['path_is_explicit'] and r['automatic_hierarchy_inference'] is False

def test_layers_preserve_scientific_boundaries():
    assert data_layer_plan({'object_refs':['d']})['automatic_join_inference'] is False
    assert uncertainty_layer_plan({'object_refs':['u']})['automatic_probability_interpretation'] is False
    assert evidence_layer_plan({'object_refs':['e']})['automatic_evidence_weighting'] is False
    assert provenance_layer_plan({'object_refs':['g']})['automatic_provenance_inference'] is False
    assert spatial_layer_plan({'object_refs':['s']})['automatic_reprojection'] is False
    assert temporal_layer_plan({'object_refs':['t']})['automatic_interpolation'] is False

def test_camera_viewport_lod_and_slicing_are_presentation_state():
    assert camera_plan({'camera':{'x':1}})['presentation_only']
    assert viewport_plan({'viewport':{'zoom':2}})['scientific_objects_mutated'] is False
    assert lod_plan({'target_refs':['x']})['scientific_values_mutated'] is False
    assert slice_plan({'layer_ref':'volume:1','axis':'z','position':0.5})['presentation_only']

def test_mapping_and_context_are_explicit():
    m=mapping_validation({'mappings':[{'mapping_ref':'m','source_ref':'a','target_ref':'b'}]}); assert m['valid'] and m['automatic_mapping_generation'] is False
    assert selection_bridge({'selection_refs':['a'],'target_refs':['b'],'mapping_ref':'m'})['automatic_join_inference'] is False
    assert linked_context_plan({'canvas_ref':'c','graph_refs':['g']})['v01353_canvas_bridge'] and linked_context_plan({'canvas_ref':'c','graph_refs':['g']})['v01352_graph_bridge']

def test_context_plans_do_not_judge_science():
    assert evidence_context_plan({'evidence_refs':['e']})['automatic_claim_status_change'] is False
    assert diagnostic_context_plan({'diagnostic_refs':['d']})['automatic_method_rejection'] is False
    assert uncertainty_context_plan({'uncertainty_refs':['u']})['automatic_probability_interpretation'] is False
    assert provenance_context_plan({'graph_refs':['g']})['automatic_provenance_inference'] is False
    assert spatial_context_plan({'crs':'EPSG:4326'})['automatic_spatial_join'] is False

def test_snapshot_handoff_core_readiness_and_boundaries():
    p=sample(); assert build_snapshot(p)['snapshot']['snapshot_hash']==build_snapshot(p)['snapshot']['snapshot_hash']
    assert revision_plan({'operations':[]})['requires_explicit_apply']
    assert handoff_plan({'scene_refs':['s']})['automatic_submission'] is False
    assert core_object_plan({'scene_refs':['s']})['core_owns_canonical_research_objects'] is True
    assert readiness_report(p)['scientific_validity_certified'] is False
    b=interpretation_boundaries_report(); assert b['determine_truth'] is False and b['automatic_hierarchy_inference'] is False and b['drill_down_mutates_scientific_record'] is False
