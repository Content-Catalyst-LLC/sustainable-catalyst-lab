from __future__ import annotations
import copy, json
from hashlib import sha256
from typing import Any

VERSION='0.135.4'; ENGINE_VERSION='16.4.0'
SCHEMA='sc-lab-interactive-scientific-scene-drilldown/0.135.4'
SNAPSHOT_SCHEMA='sc-lab-interactive-scientific-scene-drilldown-snapshot/0.135.4'
MAX_LAYERS=64; MAX_TARGETS=20000; MAX_PATH_DEPTH=64; MAX_MAPPINGS=512; MAX_REFS=10000
LAYER_TYPES={'figure','data','model','uncertainty','diagnostics','evidence','provenance','annotation','spatial','temporal','volume','trajectory'}
DRILL_TARGET_TYPES={'object','row','point','cell','node','edge','layer','frame'}
VIEW_MODES={'inspect','drill','isolate','compare','slice','trace'}
NAVIGATION_MODES={'pan-zoom','orbit','fly','time-scrub','graph-focus'}
LOD_MODES={'full','adaptive','summary','reference'}
LAYER_STATES={'bound','declared','derived','unbound','external'}

class InteractiveScientificSceneDrillDownError(ValueError):
    def __init__(self, detail, status_code=400): super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _list(v,label,limit):
    if v is None: return []
    if not isinstance(v,list): raise InteractiveScientificSceneDrillDownError(f'{label} must be an array.')
    if len(v)>limit: raise InteractiveScientificSceneDrillDownError(f'{label} exceeds configured maximum of {limit}.')
    return v
def _req(v,label):
    s=str(v or '').strip()
    if not s: raise InteractiveScientificSceneDrillDownError(f'{label} is required.')
    return s[:500]
def _refs(v,label,limit=MAX_REFS): return [str(x)[:500] for x in _list(v,label,limit)]

def schema_info():
    return {'ok':True,'schema':SCHEMA,'snapshot_schema':SNAPSHOT_SCHEMA,'version':VERSION,'engine_version':ENGINE_VERSION,'layer_types':sorted(LAYER_TYPES),'drill_target_types':sorted(DRILL_TARGET_TYPES),'view_modes':sorted(VIEW_MODES),'navigation_modes':sorted(NAVIGATION_MODES),'lod_modes':sorted(LOD_MODES),'limits':{'layers':MAX_LAYERS,'targets':MAX_TARGETS,'path_depth':MAX_PATH_DEPTH,'mappings':MAX_MAPPINGS,'refs':MAX_REFS}}
def catalog():
    return {'ok':True,'version':VERSION,'layer_types':sorted(LAYER_TYPES),'layer_type_count':len(LAYER_TYPES),'drill_target_types':sorted(DRILL_TARGET_TYPES),'drill_target_type_count':len(DRILL_TARGET_TYPES),'view_modes':sorted(VIEW_MODES),'view_mode_count':len(VIEW_MODES),'navigation_modes':sorted(NAVIGATION_MODES),'navigation_mode_count':len(NAVIGATION_MODES),'lod_modes':sorted(LOD_MODES),'lod_mode_count':len(LOD_MODES),'drill_hierarchy_must_be_explicit':True,'camera_is_presentation_state':True,'viewport_is_presentation_state':True,'automatic_hierarchy_inference':False,'automatic_join_inference':False,'automatic_scientific_interpretation':False,'automatic_core_submission':False}
def manifest():
    return {'ok':True,'status':'interactive-scientific-scene-drilldown-ready','version':VERSION,'engine_version':ENGINE_VERSION,'interactive_scene':True,'visual_drill_down':True,'explicit_hierarchy_navigation':True,'cross_layer_inspection':True,'lod_planning':True,'spatial_temporal_drill_down':True,'evidence_provenance_trace':True,'v01353_canvas_bridge':True,'v01352_graph_bridge':True,'v01351_visual_experience_bridge':True,'platform_core_reference_bridge':True,'camera_mutates_scientific_record':False,'drill_down_mutates_scientific_record':False,'automatic_hierarchy_inference':False,'automatic_join_inference':False,'automatic_scientific_interpretation':False,'automatic_core_submission':False}
def health():
    return {**manifest(),'schema':SCHEMA,'layer_type_count':12,'drill_target_type_count':8,'view_mode_count':6,'navigation_mode_count':5,'lod_mode_count':4,'api_route_count':45}

def _layer(raw,i):
    if not isinstance(raw,dict): raise InteractiveScientificSceneDrillDownError(f'layers[{i}] must be an object.')
    t=str(raw.get('layer_type') or raw.get('type') or 'figure').lower()
    if t not in LAYER_TYPES: raise InteractiveScientificSceneDrillDownError(f'layers[{i}].layer_type invalid.')
    state=str(raw.get('state') or 'declared').lower()
    if state not in LAYER_STATES: raise InteractiveScientificSceneDrillDownError(f'layers[{i}].state invalid.')
    lid=str(raw.get('layer_id') or f'layer:{i}:{_hash(raw)[:12]}')[:500]
    return {'layer_id':lid,'layer_type':t,'title':str(raw.get('title') or t.replace('-',' ').title())[:500],'state':state,'object_refs':_refs(raw.get('object_refs'),'object_refs'),'parent_layer_ref':raw.get('parent_layer_ref'),'mapping_ref':raw.get('mapping_ref'),'coordinate_space':str(raw.get('coordinate_space') or 'declared')[:100],'visible':bool(raw.get('visible',True)),'opacity':max(0.0,min(1.0,float(raw.get('opacity',1.0)))),'metadata':copy.deepcopy(raw.get('metadata') if isinstance(raw.get('metadata'),dict) else {})}

def _target(raw,i=0):
    if not isinstance(raw,dict): raise InteractiveScientificSceneDrillDownError('target must be an object.')
    t=str(raw.get('target_type') or raw.get('type') or 'object').lower()
    if t not in DRILL_TARGET_TYPES: raise InteractiveScientificSceneDrillDownError('target.target_type invalid.')
    ref=_req(raw.get('ref') or raw.get('object_ref') or raw.get('target_ref'),'target.ref')
    children=_refs(raw.get('child_refs'),'target.child_refs',MAX_TARGETS)
    return {'target_ref':ref,'target_type':t,'layer_ref':raw.get('layer_ref'),'parent_ref':raw.get('parent_ref'),'child_refs':children,'child_count':len(children),'label':str(raw.get('label') or ref)[:500],'state':str(raw.get('state') or 'bound')[:100],'metadata':copy.deepcopy(raw.get('metadata') if isinstance(raw.get('metadata'),dict) else {}),'hierarchy_declared':raw.get('parent_ref') is not None or bool(children)}

def normalize_scene(payload):
    if not isinstance(payload,dict): raise InteractiveScientificSceneDrillDownError('payload must be an object.')
    view=str(payload.get('view_mode') or 'inspect').lower(); nav=str(payload.get('navigation_mode') or 'pan-zoom').lower(); lod=str(payload.get('lod_mode') or 'adaptive').lower()
    if view not in VIEW_MODES: raise InteractiveScientificSceneDrillDownError('view_mode invalid.')
    if nav not in NAVIGATION_MODES: raise InteractiveScientificSceneDrillDownError('navigation_mode invalid.')
    if lod not in LOD_MODES: raise InteractiveScientificSceneDrillDownError('lod_mode invalid.')
    layers=[_layer(x,i) for i,x in enumerate(_list(payload.get('layers'),'layers',MAX_LAYERS))]
    ids=[x['layer_id'] for x in layers]
    if len(ids)!=len(set(ids)): raise InteractiveScientificSceneDrillDownError('layer_id values must be unique.')
    mappings=[]
    for i,m in enumerate(_list(payload.get('mappings'),'mappings',MAX_MAPPINGS)):
        if not isinstance(m,dict): raise InteractiveScientificSceneDrillDownError(f'mappings[{i}] must be an object.')
        mappings.append({'mapping_ref':_req(m.get('mapping_ref'),f'mappings[{i}].mapping_ref'),'source_ref':_req(m.get('source_ref'),f'mappings[{i}].source_ref'),'target_ref':_req(m.get('target_ref'),f'mappings[{i}].target_ref'),'declared':True,'metadata':copy.deepcopy(m.get('metadata') if isinstance(m.get('metadata'),dict) else {})})
    scene={'scene_ref':str(payload.get('scene_ref') or f'interactive-scene:{_hash(payload)[:16]}')[:500],'project_ref':payload.get('project_ref'),'session_ref':payload.get('session_ref'),'canvas_ref':payload.get('canvas_ref'),'view_mode':view,'navigation_mode':nav,'lod_mode':lod,'layers':layers,'mappings':mappings,'layer_count':len(layers),'mapping_count':len(mappings),'camera_state':copy.deepcopy(payload.get('camera_state') if isinstance(payload.get('camera_state'),dict) else {}),'viewport_state':copy.deepcopy(payload.get('viewport_state') if isinstance(payload.get('viewport_state'),dict) else {}),'time_state':copy.deepcopy(payload.get('time_state') if isinstance(payload.get('time_state'),dict) else {}),'camera_is_presentation_state':True,'viewport_is_presentation_state':True,'drill_down_mutates_scientific_record':False,'automatic_hierarchy_inference':False,'automatic_join_inference':False}
    scene['scene_hash']=_hash(scene)
    return {'ok':True,'version':VERSION,'scene':scene}
def _scene(p): return normalize_scene(p)['scene']
def compose_scene(p):
    s=_scene(p); return {'ok':True,'version':VERSION,'scene':s,'visible_layer_refs':[x['layer_id'] for x in s['layers'] if x['visible']],'drill_down_enabled':True,'mapping_count':s['mapping_count'],'scientific_objects_mutated':False,'automatic_hierarchy_inference':False,'automatic_join_inference':False}
def layer_plan(p): return {'ok':True,'version':VERSION,'layer':_layer(p,0),'layer_state_is_reference_first':True,'scientific_values_mutated':False}
def _typed_layer(p,t,extra=None):
    x=_layer({**p,'layer_type':t},0); r={'ok':True,'version':VERSION,'layer':x,'scientific_values_mutated':False}; r.update(extra or {}); return r
def figure_layer_plan(p): return _typed_layer(p,'figure',{'v01353_canvas_bridge':True,'renderer_state_is_presentation':True})
def data_layer_plan(p): return _typed_layer(p,'data',{'row_identity_must_be_explicit':True,'automatic_join_inference':False})
def uncertainty_layer_plan(p): return _typed_layer(p,'uncertainty',{'uncertainty_semantics_must_be_declared':True,'automatic_probability_interpretation':False})
def evidence_layer_plan(p): return _typed_layer(p,'evidence',{'automatic_evidence_weighting':False,'automatic_claim_status_change':False})
def provenance_layer_plan(p): return _typed_layer(p,'provenance',{'v01352_graph_bridge':True,'automatic_provenance_inference':False})
def spatial_layer_plan(p): return _typed_layer(p,'spatial',{'crs_must_be_declared':True,'automatic_reprojection':False})
def temporal_layer_plan(p): return _typed_layer(p,'temporal',{'time_semantics_must_be_declared':True,'automatic_interpolation':False})
def drill_target(p): return {'ok':True,'version':VERSION,'target':_target(p),'automatic_hierarchy_inference':False}
def drill_path(p):
    path=[_target(x,i) for i,x in enumerate(_list(p.get('path'),'path',MAX_PATH_DEPTH))]
    for i in range(1,len(path)):
        if path[i]['parent_ref'] not in (None,path[i-1]['target_ref']): raise InteractiveScientificSceneDrillDownError(f'path[{i}] parent_ref does not match preceding explicit target.')
    return {'ok':True,'version':VERSION,'path':path,'depth':len(path),'path_is_explicit':True,'automatic_hierarchy_inference':False,'scientific_objects_mutated':False}
def drill_children(p):
    parent=_target(p.get('parent') or p,0); children=[_target(x,i) for i,x in enumerate(_list(p.get('children'),'children',MAX_TARGETS))]
    invalid=[x['target_ref'] for x in children if x.get('parent_ref') not in (None,parent['target_ref'])]
    if invalid: raise InteractiveScientificSceneDrillDownError('children contain parent_ref values that do not match the explicit parent.')
    return {'ok':True,'version':VERSION,'parent':parent,'children':children,'child_count':len(children),'automatic_child_discovery':False}
def breadcrumb_plan(p): return {'ok':True,'version':VERSION,'refs':_refs(p.get('refs'),'refs',MAX_PATH_DEPTH),'presentation_only':True,'automatic_hierarchy_inference':False}
def detail_panel_plan(p): return {'ok':True,'version':VERSION,'target':_target(p.get('target') or p),'fields':_refs(p.get('fields'),'fields',512),'show_provenance':bool(p.get('show_provenance',True)),'show_uncertainty':bool(p.get('show_uncertainty',True)),'scientific_values_read_only':True}
def selection_bridge(p): return {'ok':True,'version':VERSION,'selection_refs':_refs(p.get('selection_refs'),'selection_refs'),'target_refs':_refs(p.get('target_refs'),'target_refs'),'mapping_ref':p.get('mapping_ref'),'mapping_required_when_ids_differ':True,'automatic_join_inference':False,'presentation_state_only':True}
def linked_context_plan(p): return {'ok':True,'version':VERSION,'scene_ref':p.get('scene_ref'),'canvas_ref':p.get('canvas_ref'),'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'panel_refs':_refs(p.get('panel_refs'),'panel_refs'),'v01353_canvas_bridge':True,'v01352_graph_bridge':True,'reference_first':True}
def mapping_validation(p):
    mappings=_list(p.get('mappings'),'mappings',MAX_MAPPINGS); missing=[i for i,x in enumerate(mappings) if not isinstance(x,dict) or not x.get('mapping_ref') or not x.get('source_ref') or not x.get('target_ref')]
    return {'ok':True,'version':VERSION,'mapping_count':len(mappings),'valid':not missing,'invalid_indices':missing,'automatic_mapping_generation':False}
def viewport_plan(p): return {'ok':True,'version':VERSION,'viewport':copy.deepcopy(p.get('viewport') or {}),'presentation_only':True,'scientific_objects_mutated':False}
def camera_plan(p): return {'ok':True,'version':VERSION,'camera':copy.deepcopy(p.get('camera') or {}),'navigation_mode':str(p.get('navigation_mode') or 'orbit'),'presentation_only':True,'scientific_objects_mutated':False}
def time_scrub_plan(p): return {'ok':True,'version':VERSION,'time_ref':p.get('time_ref'),'frame_refs':_refs(p.get('frame_refs'),'frame_refs',MAX_TARGETS),'interpolation':str(p.get('interpolation') or 'none'),'automatic_interpolation':False,'presentation_only':True}
def slice_plan(p): return {'ok':True,'version':VERSION,'layer_ref':p.get('layer_ref'),'axis':str(p.get('axis') or 'z')[:20],'position':copy.deepcopy(p.get('position')),'slice_definition_must_be_declared':True,'presentation_only':True}
def isolate_plan(p): return {'ok':True,'version':VERSION,'target_refs':_refs(p.get('target_refs'),'target_refs'),'hidden_layer_refs':_refs(p.get('hidden_layer_refs'),'hidden_layer_refs',MAX_LAYERS),'presentation_only':True,'scientific_objects_mutated':False}
def compare_plan(p): return {'ok':True,'version':VERSION,'left_refs':_refs(p.get('left_refs'),'left_refs'),'right_refs':_refs(p.get('right_refs'),'right_refs'),'mapping_ref':p.get('mapping_ref'),'automatic_alignment':False,'automatic_scientific_interpretation':False}
def trace_plan(p): return {'ok':True,'version':VERSION,'start_ref':p.get('start_ref'),'path_refs':_refs(p.get('path_refs'),'path_refs',MAX_PATH_DEPTH),'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'structural_trace_is_not_causal_effect':True,'automatic_provenance_inference':False}
def lod_plan(p): return {'ok':True,'version':VERSION,'mode':str(p.get('mode') or 'adaptive'),'target_refs':_refs(p.get('target_refs'),'target_refs'),'max_visible_objects':int(p.get('max_visible_objects') or 5000),'lod_is_rendering_policy':True,'scientific_values_mutated':False}
def density_plan(p): return {'ok':True,'version':VERSION,'target_refs':_refs(p.get('target_refs'),'target_refs'),'strategy':str(p.get('strategy') or 'reference'),'aggregation_requires_declared_method':True,'automatic_statistical_aggregation':False}
def evidence_context_plan(p): return {'ok':True,'version':VERSION,'evidence_refs':_refs(p.get('evidence_refs'),'evidence_refs'),'claim_refs':_refs(p.get('claim_refs'),'claim_refs'),'automatic_evidence_weighting':False,'automatic_claim_status_change':False}
def uncertainty_context_plan(p): return {'ok':True,'version':VERSION,'uncertainty_refs':_refs(p.get('uncertainty_refs'),'uncertainty_refs'),'automatic_probability_interpretation':False,'values_must_be_bound_or_declared':True}
def diagnostic_context_plan(p): return {'ok':True,'version':VERSION,'diagnostic_refs':_refs(p.get('diagnostic_refs'),'diagnostic_refs'),'assumption_refs':_refs(p.get('assumption_refs'),'assumption_refs'),'automatic_validity_judgment':False,'automatic_method_rejection':False}
def provenance_context_plan(p): return {'ok':True,'version':VERSION,'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'execution_refs':_refs(p.get('execution_refs'),'execution_refs'),'v01352_graph_bridge':True,'automatic_provenance_inference':False}
def spatial_context_plan(p): return {'ok':True,'version':VERSION,'crs':p.get('crs'),'spatial_refs':_refs(p.get('spatial_refs'),'spatial_refs'),'automatic_reprojection':False,'automatic_spatial_join':False}
def animation_plan(p): return {'ok':True,'version':VERSION,'frame_refs':_refs(p.get('frame_refs'),'frame_refs',MAX_TARGETS),'duration_ms':int(p.get('duration_ms') or 1000),'loop':bool(p.get('loop',False)),'presentation_only':True,'automatic_interpolation':False}
def measurement_plan(p): return {'ok':True,'version':VERSION,'measurement_refs':_refs(p.get('measurement_refs'),'measurement_refs'),'display_units':p.get('display_units'),'measurement_values_must_be_bound_or_declared':True,'automatic_unit_inference':False}
def annotation_focus_plan(p): return {'ok':True,'version':VERSION,'annotation_refs':_refs(p.get('annotation_refs'),'annotation_refs'),'target_refs':_refs(p.get('target_refs'),'target_refs'),'annotations_do_not_change_scientific_values':True,'automatic_scientific_interpretation':False}
def build_snapshot(p):
    s=_scene(p); snap={'schema':SNAPSHOT_SCHEMA,'version':VERSION,'scene_ref':s['scene_ref'],'scene_hash':s['scene_hash'],'view_mode':s['view_mode'],'navigation_mode':s['navigation_mode'],'lod_mode':s['lod_mode'],'camera_state':s['camera_state'],'viewport_state':s['viewport_state'],'time_state':s['time_state'],'visible_layer_refs':[x['layer_id'] for x in s['layers'] if x['visible']],'scientific_object_refs':sorted({r for x in s['layers'] for r in x['object_refs']})}; snap['snapshot_hash']=_hash(snap); return {'ok':True,'version':VERSION,'snapshot':snap,'presentation_state_separated':True}
def revision_plan(p): return {'ok':True,'version':VERSION,'base_snapshot_ref':p.get('base_snapshot_ref'),'operations':copy.deepcopy(_list(p.get('operations'),'operations',1000)),'automatic_scientific_object_mutation':False,'requires_explicit_apply':True}
def export_plan(p): return {'ok':True,'version':VERSION,'formats':[str(x).lower() for x in _list(p.get('formats') or ['json','svg','png'],'formats',20)],'include_scene_spec':True,'include_drill_path':bool(p.get('include_drill_path',True)),'include_object_refs':True,'scientific_values_only_if_bound_or_declared':True}
def handoff_plan(p): return {'ok':True,'version':VERSION,'destination':str(p.get('destination') or 'platform-core')[:100],'scene_refs':_refs(p.get('scene_refs'),'scene_refs'),'scientific_object_refs':_refs(p.get('scientific_object_refs'),'scientific_object_refs'),'reference_first':True,'automatic_submission':False}
def core_object_plan(p): return {'ok':True,'version':VERSION,'object_type':'interactive-scientific-scene','scene_refs':_refs(p.get('scene_refs'),'scene_refs'),'scientific_object_refs':_refs(p.get('scientific_object_refs'),'scientific_object_refs'),'lab_owns_interactive_scene_state':True,'core_owns_canonical_research_objects':True,'automatic_core_submission':False,'reference_first':True}
def readiness_report(p):
    s=_scene(p); warnings=[]
    if not s['layers']: warnings.append('No scene layers are declared.')
    if any(x['state']=='unbound' for x in s['layers']): warnings.append('One or more layers are unbound.')
    return {'ok':True,'version':VERSION,'scene_ref':s['scene_ref'],'ready_for_interactive_inspection':bool(s['layers']),'warning_count':len(warnings),'warnings':warnings,'scientific_validity_certified':False,'automatic_scientific_interpretation':False,'automatic_core_submission':False}
def interpretation_boundaries_report(p=None): return {'ok':True,'version':VERSION,'drill_down_mutates_scientific_record':False,'camera_mutates_scientific_record':False,'viewport_mutates_scientific_record':False,'automatic_hierarchy_inference':False,'automatic_join_inference':False,'automatic_reprojection':False,'automatic_interpolation':False,'automatic_probability_interpretation':False,'automatic_evidence_weighting':False,'automatic_claim_status_change':False,'automatic_validity_judgment':False,'automatic_scientific_interpretation':False,'automatic_core_submission':False,'determine_truth':False}
