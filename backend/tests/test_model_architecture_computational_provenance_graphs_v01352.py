from app.main import app
from app.model_architecture_computational_provenance_graphs_v01352 import *

def sample():
    return {'graph_ref':'g:test','nodes':[{'node_id':'source:1','node_type':'source','state':'external'},{'node_id':'dataset:1','node_type':'dataset','state':'bound','object_ref':'dataset:v75'},{'node_id':'transform:1','node_type':'transform'},{'node_id':'model:1','node_type':'model','state':'bound'},{'node_id':'execution:1','node_type':'execution','state':'derived'},{'node_id':'uncertainty:1','node_type':'uncertainty','state':'derived'},{'node_id':'figure:1','node_type':'figure','state':'derived'},{'node_id':'evidence:1','node_type':'evidence'},{'node_id':'core:1','node_type':'core-object','state':'external'}],'edges':[{'source':'source:1','target':'dataset:1','edge_type':'sourced-from'},{'source':'dataset:1','target':'transform:1','edge_type':'transformed-by'},{'source':'transform:1','target':'model:1','edge_type':'binds'},{'source':'model:1','target':'execution:1','edge_type':'executes'},{'source':'execution:1','target':'uncertainty:1','edge_type':'quantifies'},{'source':'uncertainty:1','target':'figure:1','edge_type':'visualizes'},{'source':'figure:1','target':'evidence:1','edge_type':'supports'},{'source':'evidence:1','target':'core:1','edge_type':'registered-as'}]}

def test_health_catalog_and_routes():
    assert health()['version']=='0.135.2' and health()['api_route_count']==40
    assert catalog()['node_type_count']==20 and catalog()['edge_type_count']==18
    paths={r.path for r in app.routes if isinstance(getattr(r,'path',None),str)}
    assert len({p for p in paths if p.startswith('/v1/model-architecture-provenance-graphs')})==40

def test_normalization_and_no_fabrication():
    p=sample(); p['nodes'][1]['scientific_value']={'rows':42}; g=normalize_graph(p)['graph']; n={x['node_id']:x for x in g['nodes']}['dataset:1']
    assert n['scientific_value_declared'] and n['scientific_value']=={'rows':42} and g['fabricated_scientific_values'] is False

def test_architecture_and_provenance_are_declared():
    assert build_model_architecture(sample())['automatic_model_inference'] is False
    assert build_provenance_graph(sample())['provenance_is_declared_not_inferred'] is True

def test_paths_and_structural_impact():
    p=sample(); x=path_trace({**p,'source':'dataset:1','target':'figure:1'}); assert x['found'] and x['path'][0]=='dataset:1' and x['path'][-1]=='figure:1'
    assert 'source:1' in upstream_trace({**p,'node_id':'dataset:1'})['reachable_node_ids']
    assert 'core:1' in downstream_trace({**p,'node_id':'dataset:1'})['reachable_node_ids']
    assert impact_path({**p,'node_id':'dataset:1'})['impact_is_structural_not_causal'] is True

def test_audits_do_not_delete_or_invalidate():
    p=sample(); p['nodes'].append({'node_id':'orphan:1','node_type':'diagnostic','state':'unbound'}); assert orphan_report(p)['orphan_count']==1 and orphan_report(p)['automatic_deletion'] is False
    p['edges'].append({'source':'core:1','target':'dataset:1','edge_type':'references'}); assert cycle_audit(p)['cycle_count']>=1 and cycle_audit(p)['cycle_means_error'] is False

def test_layouts_are_deterministic_presentation_state():
    p=sample(); assert layered_layout(p)['positions']==layered_layout(p)['positions']; assert layered_layout(p)['presentation_only'] and swimlane_layout(p)['presentation_only'] and radial_layout(p)['presentation_only']
    assert visual_encoding_plan({})['fabricated_scientific_values'] is False

def test_specialized_views_preserve_boundaries():
    p=sample(); assert build_execution_trace(p)['execution_status_inferred'] is False; assert build_uncertainty_graph(p)['uncertainty_semantics_preserved'] is True; assert build_evidence_lineage(p)['automatic_evidence_weighting'] is False; assert build_core_lineage(p)['lab_mutates_core'] is False

def test_overlays_reference_existing_objects():
    assert assumption_overlay_plan({'assumption_refs':['a1']})['automatic_method_rejection'] is False
    assert diagnostic_overlay_plan({'diagnostic_refs':['d1']})['automatic_validity_judgment'] is False
    assert evidence_overlay_plan({'evidence_refs':['e1']})['automatic_claim_status_change'] is False
    assert linked_selection_plan({'linked_view_refs':['v1']})['automatic_join_inference'] is False

def test_snapshot_revision_core_and_readiness():
    p=sample(); assert build_snapshot(p)['snapshot']['snapshot_hash']==build_snapshot(p)['snapshot']['snapshot_hash']
    assert revision_plan({'operations':[]})['requires_explicit_apply'] is True
    assert core_object_plan({'graph_refs':['g1']})['core_owns_canonical_research_objects'] is True
    assert readiness_report(p)['scientific_validity_certified'] is False

def test_interpretation_boundaries():
    b=interpretation_boundaries_report(); assert b['determine_truth'] is False and b['infer_undeclared_model_structure'] is False and b['automatic_causal_inference'] is False
