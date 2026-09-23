from app.main import app
from app.multi_view_scientific_analysis_canvas_v01353 import *

def sample():
    return {'canvas_ref':'canvas:test','layout_mode':'analysis','panels':[
      {'panel_id':'figure','panel_type':'primary-figure','state':'derived','figure_ref':'figure:1','object_refs':['figure:1']},
      {'panel_id':'diag','panel_type':'diagnostics','state':'bound','object_refs':['diagnostic:1']},
      {'panel_id':'unc','panel_type':'uncertainty','state':'bound','object_refs':['uncertainty:1']},
      {'panel_id':'evidence','panel_type':'evidence','state':'declared','object_refs':['evidence:1']},
      {'panel_id':'prov','panel_type':'provenance','state':'bound','graph_ref':'graph:1','object_refs':['graph:1']},
    ],'links':[
      {'source_panel':'figure','target_panel':'diag','channel':'select','mapping_ref':'map:figure-point-to-row'},
      {'source_panel':'figure','target_panel':'unc','channel':'brush','mapping_ref':'map:figure-point-to-row'},
      {'source_panel':'figure','target_panel':'evidence','channel':'focus','mapping_ref':'map:figure-to-evidence'},
    ]}

def test_health_catalog_routes():
    assert health()['version']=='0.135.3' and health()['api_route_count']==41
    assert catalog()['panel_type_count']==10 and catalog()['layout_mode_count']==5 and catalog()['interaction_channel_count']==8
    paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
    assert len({p for p in paths if p.startswith('/v1/multi-view-scientific-analysis-canvas')})==41

def test_canvas_normalization_and_composition_are_reference_first():
    c=normalize_canvas(sample())['canvas']; assert c['panel_count']==5 and c['link_count']==3
    assert c['selection_is_presentation_state'] and c['filters_mutate_source_data'] is False and c['automatic_join_inference'] is False
    x=compose_canvas(sample()); assert x['linked_selection_enabled'] is True and x['automatic_join_inference'] is False

def test_layouts_are_deterministic_presentation_state():
    p=sample(); assert analysis_layout(p)['positions']==analysis_layout(p)['positions']
    for fn in (analysis_layout,comparison_layout,diagnostics_layout,evidence_layout,presentation_layout):
        r=fn(p); assert r['presentation_only'] and r['scientific_objects_mutated'] is False

def test_panels_preserve_scientific_boundaries():
    assert diagnostics_panel_plan({'diagnostic_refs':['d']})['automatic_validity_judgment'] is False
    assert uncertainty_panel_plan({'uncertainty_refs':['u']})['automatic_probability_interpretation'] is False
    assert evidence_panel_plan({'evidence_refs':['e']})['automatic_evidence_weighting'] is False
    assert provenance_panel_plan({'graph_refs':['g']})['automatic_provenance_inference'] is False
    assert model_graph_panel_plan({'graph_refs':['g']})['automatic_model_inference'] is False

def test_selection_and_filter_are_view_state_only():
    s=selection_normalize({'items':[{'row_ref':'row:1'}]})['selection']; assert s['presentation_state_only'] and s['item_count']==1
    l=selection_link({'selection':{'items':[{'row_ref':'row:1'}]},'target_panel_ids':['diag']}); assert l['automatic_join_inference'] is False
    f=filter_apply({'filter':{'field':'x','operator':'gte','value':2},'rows':[{'x':1},{'x':2},{'x':3}]}); assert f['matched_row_indices']==[1,2] and f['rows_mutated'] is False

def test_context_plans_do_not_judge_science():
    assert evidence_context_plan({'evidence_refs':['e']})['automatic_claim_status_change'] is False
    assert diagnostic_context_plan({'diagnostic_refs':['d']})['automatic_method_rejection'] is False
    assert uncertainty_context_plan({'uncertainty_refs':['u']})['automatic_probability_interpretation'] is False
    assert provenance_context_plan({'graph_refs':['g']})['v01352_graph_bridge'] is True

def test_snapshot_revision_handoff_core_and_readiness():
    p=sample(); assert build_snapshot(p)['snapshot']['snapshot_hash']==build_snapshot(p)['snapshot']['snapshot_hash']
    assert revision_plan({'operations':[]})['requires_explicit_apply'] is True
    assert handoff_plan({'canvas_refs':['c']})['automatic_submission'] is False
    assert core_object_plan({'canvas_refs':['c']})['core_owns_canonical_research_objects'] is True
    assert readiness_report(p)['scientific_validity_certified'] is False

def test_interpretation_boundaries():
    b=interpretation_boundaries_report(); assert b['determine_truth'] is False and b['automatic_join_inference'] is False and b['filters_mutate_source_data'] is False
