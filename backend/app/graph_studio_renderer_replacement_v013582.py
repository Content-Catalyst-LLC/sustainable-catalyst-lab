from __future__ import annotations
from copy import deepcopy

VERSION='0.135.8.2'
ENGINE_VERSION='3.0.0'
SCHEMA='sc-lab-graph-studio-renderer-replacement/0.135.8.2'
WORKSPACE_VIEWS=('figure','analysis','provenance','scene','compare','session','narrative','review')
RENDERER_MODES=('plot','distribution','diagnostics','uncertainty','provenance','scene')
LEGACY_GRAPH_STUDIO=('graph-studio-v0790','graph-studio-v0800','graph-studio-v0810','graph-studio-v0820','graph-studio-v0830','graph-studio-v0840','graph-studio-v0850','graph-studio-v0870','graph-studio-v0880')
ROUTE_COUNT=24

class GraphStudioRendererReplacementError(ValueError):
    def __init__(self,detail:str,status_code:int=400): super().__init__(detail); self.detail=detail; self.status_code=status_code

def _obj(payload):
    if payload is None:return {}
    if not isinstance(payload,dict): raise GraphStudioRendererReplacementError('Payload must be an object.')
    return deepcopy(payload)

def health():
    return {'ok':True,'status':'advanced-visual-analysis-renderer-ready','version':VERSION,'engine_version':ENGINE_VERSION,'schema':SCHEMA,'api_route_count':ROUTE_COUNT,'workspace_view_count':len(WORKSPACE_VIEWS),'renderer_mode_count':len(RENDERER_MODES),'primary_renderer_owner':'graph-studio-renderer-v013582','legacy_graph_studio_execution_allowed':False,'single_primary_viewport':True,'scientific_mutation_from_presentation':False}

def manifest():
    return {'ok':True,'version':VERSION,'engine_version':ENGINE_VERSION,'workspace_views':list(WORKSPACE_VIEWS),'renderer_modes':list(RENDERER_MODES),'legacy_graph_studio_modules_quarantined':list(LEGACY_GRAPH_STUDIO),'retains_visual_research_stack':['0.135.1','0.135.2','0.135.3','0.135.4','0.135.5','0.135.6','0.135.7','0.135.8','0.135.8.1']}

def renderer_registry():
    return {'ok':True,'version':VERSION,'renderers':[
        {'id':'svg2d','role':'primary-2d','owner':'v013582','status':'active'},
        {'id':'canvas2d','role':'high-density-2d','owner':'v013582','status':'ready'},
        {'id':'scene3d','role':'scientific-scene','owner':'v013582','status':'ready'},
        {'id':'webgl2','role':'gpu-adapter','owner':'capability-adapter','status':'available'},
        {'id':'webgpu','role':'gpu-compute-adapter','owner':'capability-adapter','status':'available'},
    ],'legacy_renderer_owner':False}

def view_catalog(): return {'ok':True,'version':VERSION,'views':list(WORKSPACE_VIEWS),'figure_modes':list(RENDERER_MODES),'default_view':'figure','default_mode':'plot'}
def capability_catalog(): return {'ok':True,'capabilities':['2d','distribution','diagnostics','uncertainty','provenance','3d','spatial','temporal','linked-views','compare','session','narrative','review'],'capability_count':13}

def normalize_workspace(payload):
    p=_obj(payload); view=str(p.get('view') or 'figure').strip().lower(); mode=str(p.get('mode') or 'plot').strip().lower()
    if view not in WORKSPACE_VIEWS: raise GraphStudioRendererReplacementError('Unknown workspace view.')
    if mode not in RENDERER_MODES: raise GraphStudioRendererReplacementError('Unknown renderer mode.')
    return {'ok':True,'version':VERSION,'view':view,'mode':mode,'presentation_state_only':True,'mutates_science':False}

def renderer_select(payload):
    p=_obj(payload); requested=str(p.get('requested') or 'auto').lower(); dimensionality=int(p.get('dimensionality') or 2); density=int(p.get('point_count') or 0)
    if requested not in ('auto','svg2d','canvas2d','scene3d','webgl2','webgpu'): raise GraphStudioRendererReplacementError('Unknown renderer.')
    selected=requested
    if requested=='auto': selected='scene3d' if dimensionality>=3 else ('canvas2d' if density>5000 else 'svg2d')
    return {'ok':True,'requested':requested,'selected':selected,'selection_is_presentation_only':True,'values_unchanged':True}

def render_plan(payload):
    p=_obj(payload); rows=p.get('rows') or []
    if not isinstance(rows,list): raise GraphStudioRendererReplacementError('rows must be an array.')
    return {'ok':True,'version':VERSION,'row_count':len(rows),'pipeline':['validate-bound-fields','preserve-units','compute-presentation-extents','render-linked-layers'],'fabricates_values':False,'infers_scientific_model':False}

def analysis_plan(payload):
    p=_obj(payload); return {'ok':True,'views':['plot','distribution','descriptive-delta','missingness'],'source_reference':p.get('source_reference'),'diagnostics_are_descriptive_unless_bound':True}

def provenance_plan(payload):
    p=_obj(payload); nodes=p.get('nodes') or []; edges=p.get('edges') or []
    return {'ok':True,'node_count':len(nodes) if isinstance(nodes,list) else 0,'edge_count':len(edges) if isinstance(edges,list) else 0,'layout':'layered','structural_path_is_causal_path':False,'missing_relationships_inferred':False}

def scene_plan(payload):
    p=_obj(payload); has_z=bool(p.get('z_bound')); return {'ok':True,'mode':'3d' if has_z else '2d-context','z_bound':has_z,'camera_is_presentation_state':True,'reprojection_inferred':False}

def linked_view_plan(payload):
    p=_obj(payload); return {'ok':True,'source_id':p.get('source_id'),'target_ids':p.get('target_ids') or [],'identity_mapping_required':True,'automatic_join_inference':False}

def compare_plan(payload):
    p=_obj(payload); return {'ok':True,'left':p.get('left'),'right':p.get('right'),'modes':['side-by-side','overlay','synchronized'],'equivalence_inferred':False,'causal_effect_inferred':False}

def export_plan(payload):
    p=_obj(payload); fmt=str(p.get('format') or 'svg').lower();
    if fmt not in ('svg','png','csv','json'): raise GraphStudioRendererReplacementError('Unsupported export format.')
    return {'ok':True,'format':fmt,'preserve_provenance':True,'preserve_units':True,'presentation_only':fmt in ('svg','png')}

def lifecycle_plan(payload):
    p=_obj(payload); return {'ok':True,'from_view':p.get('from_view'),'to_view':p.get('to_view'),'actions':['suspend-old-view-listeners','retain-scientific-object-references','activate-one-primary-viewport','restore-linked-presentation-state'],'destroys_scientific_objects':False}

def asset_plan(payload):
    _obj(payload); return {'ok':True,'canonical_assets':['graph-studio-renderer-replacement-v013582.js','sc-lab-graph-studio-renderer-replacement-v013582.css'],'legacy_graph_studio_scripts_execute':False,'legacy_files_retained_for_compatibility':True}

def asset_audit(payload):
    p=_obj(payload); active=p.get('active_graph_studio_modules') or []
    if not isinstance(active,list): raise GraphStudioRendererReplacementError('active_graph_studio_modules must be an array.')
    bad=sorted(set(active).intersection(LEGACY_GRAPH_STUDIO))
    return {'ok':not bad,'legacy_active':bad,'legacy_active_count':len(bad),'canonical_owner_present':'graph-studio-renderer-replacement-v013582' in active or not active}

def dom_audit(payload):
    p=_obj(payload); primary=int(p.get('primary_viewports',1)); legacy=int(p.get('legacy_primary_canvases_visible',0)); stacked=int(p.get('stacked_research_surfaces_visible',0))
    return {'ok':primary==1 and legacy==0 and stacked==0,'primary_viewports':primary,'legacy_primary_canvases_visible':legacy,'stacked_research_surfaces_visible':stacked,'single_primary_viewport':primary==1}

def legacy_audit(payload=None):
    _obj(payload or {}); return {'ok':True,'quarantined':list(LEGACY_GRAPH_STUDIO),'execution_allowed':False,'primary_renderer_owner':False,'compatibility_import_allowed':True}

def session_plan(payload):
    p=_obj(payload); return {'ok':True,'session_reference':p.get('session_reference'),'records_interaction_lineage':True,'interaction_history_is_evidence':False}

def narrative_plan(payload):
    p=_obj(payload); return {'ok':True,'narrative_reference':p.get('narrative_reference'),'figures_are_references':True,'layout_creates_claims':False}

def review_plan(payload):
    p=_obj(payload); return {'ok':True,'review_reference':p.get('review_reference'),'review_comment_is_evidence':False,'review_decision_certifies_validity':False}

def handoff_plan(payload):
    p=_obj(payload); target=str(p.get('target') or 'platform-core')
    return {'ok':True,'target':target,'explicit_confirmation_required':True,'automatic_submission':False,'scientific_objects_by_reference':True}

def identity_report(payload=None):
    _obj(payload or {}); return {'ok':True,'release_version':VERSION,'engine_version':ENGINE_VERSION,'display_identity':f'Lab {VERSION} · Graph Studio Renderer 3.0','public_release_identity_authoritative':True}

def boundaries_report(payload=None):
    _obj(payload or {}); return {'presentation_state_is_scientific_record':False,'renderer_derives_unbound_science':False,'automatic_join_inference':False,'automatic_causal_inference':False,'automatic_evidence_weighting':False,'automatic_claim_status_change':False,'automatic_core_submission':False}
