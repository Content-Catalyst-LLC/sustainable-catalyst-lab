from __future__ import annotations
import copy, json
from hashlib import sha256
from typing import Any

VERSION='0.135.3'; ENGINE_VERSION='16.3.0'
SCHEMA='sc-lab-multi-view-scientific-analysis-canvas/0.135.3'
SNAPSHOT_SCHEMA='sc-lab-multi-view-scientific-analysis-canvas-snapshot/0.135.3'
MAX_PANELS=24; MAX_LINKS=256; MAX_SELECTION_ITEMS=10000; MAX_FILTERS=128; MAX_OBJECT_REFS=5000
PANEL_TYPES={'primary-figure','secondary-figure','diagnostics','uncertainty','evidence','provenance','model-graph','data-table','annotations','narrative'}
LAYOUT_MODES={'analysis','comparison','diagnostics','evidence','presentation'}
INTERACTION_CHANNELS={'select','brush','hover','cursor','filter','zoom','pan','focus'}
SELECTION_MODES={'replace','add','toggle','range'}
FILTER_OPERATORS={'eq','neq','lt','lte','gt','gte','in','contains'}
PANEL_STATES={'bound','declared','derived','unbound','external'}

class MultiViewScientificAnalysisCanvasError(ValueError):
    def __init__(self, detail, status_code=400): super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _list(v,label,limit):
    if v is None:return []
    if not isinstance(v,list): raise MultiViewScientificAnalysisCanvasError(f'{label} must be an array.')
    if len(v)>limit: raise MultiViewScientificAnalysisCanvasError(f'{label} exceeds configured maximum of {limit}.')
    return v
def _req(v,label):
    s=str(v or '').strip()
    if not s: raise MultiViewScientificAnalysisCanvasError(f'{label} is required.')
    return s[:500]
def _refs(v,label,limit=MAX_OBJECT_REFS): return [str(x)[:500] for x in _list(v,label,limit)]

def schema_info(): return {'ok':True,'schema':SCHEMA,'snapshot_schema':SNAPSHOT_SCHEMA,'version':VERSION,'engine_version':ENGINE_VERSION,'panel_types':sorted(PANEL_TYPES),'layout_modes':sorted(LAYOUT_MODES),'interaction_channels':sorted(INTERACTION_CHANNELS),'selection_modes':sorted(SELECTION_MODES),'filter_operators':sorted(FILTER_OPERATORS),'limits':{'panels':MAX_PANELS,'links':MAX_LINKS,'selection_items':MAX_SELECTION_ITEMS,'filters':MAX_FILTERS,'object_refs':MAX_OBJECT_REFS}}
def catalog(): return {'ok':True,'version':VERSION,'panel_types':sorted(PANEL_TYPES),'panel_type_count':len(PANEL_TYPES),'layout_modes':sorted(LAYOUT_MODES),'layout_mode_count':len(LAYOUT_MODES),'interaction_channels':sorted(INTERACTION_CHANNELS),'interaction_channel_count':len(INTERACTION_CHANNELS),'selection_modes':sorted(SELECTION_MODES),'filter_operators':sorted(FILTER_OPERATORS),'selection_is_presentation_state':True,'filters_mutate_source_data':False,'automatic_join_inference':False,'automatic_scientific_interpretation':False,'automatic_evidence_weighting':False,'automatic_core_submission':False}
def manifest(): return {'ok':True,'status':'multi-view-scientific-analysis-canvas-ready','version':VERSION,'engine_version':ENGINE_VERSION,'coordinated_multi_view_canvas':True,'linked_selections':True,'shared_filters':True,'synchronized_domains':True,'diagnostic_context':True,'uncertainty_context':True,'evidence_context':True,'provenance_context':True,'model_graph_context':True,'v01352_graph_bridge':True,'v01351_visual_experience_bridge':True,'platform_core_reference_bridge':True,'selection_mutates_scientific_record':False,'automatic_join_inference':False,'automatic_scientific_interpretation':False,'automatic_core_submission':False}
def health(): return {**manifest(),'schema':SCHEMA,'panel_type_count':10,'layout_mode_count':5,'interaction_channel_count':8,'api_route_count':41}

def _panel(raw,i):
    if not isinstance(raw,dict): raise MultiViewScientificAnalysisCanvasError(f'panels[{i}] must be an object.')
    t=str(raw.get('panel_type') or raw.get('type') or 'secondary-figure').lower()
    if t not in PANEL_TYPES: raise MultiViewScientificAnalysisCanvasError(f'panels[{i}].panel_type invalid.')
    state=str(raw.get('state') or 'declared').lower()
    if state not in PANEL_STATES: raise MultiViewScientificAnalysisCanvasError(f'panels[{i}].state invalid.')
    pid=str(raw.get('panel_id') or f'panel:{i}:{_hash(raw)[:12]}')[:500]
    return {'panel_id':pid,'panel_type':t,'title':str(raw.get('title') or t.replace('-',' ').title())[:500],'state':state,'object_refs':_refs(raw.get('object_refs'),'object_refs'),'data_ref':raw.get('data_ref'),'figure_ref':raw.get('figure_ref'),'diagnostic_refs':_refs(raw.get('diagnostic_refs'),'diagnostic_refs'),'evidence_refs':_refs(raw.get('evidence_refs'),'evidence_refs'),'graph_ref':raw.get('graph_ref'),'visible':bool(raw.get('visible',True)),'metadata':copy.deepcopy(raw.get('metadata') if isinstance(raw.get('metadata'),dict) else {})}
def _link(raw,i,panel_ids):
    if not isinstance(raw,dict): raise MultiViewScientificAnalysisCanvasError(f'links[{i}] must be an object.')
    a=_req(raw.get('source_panel'),f'links[{i}].source_panel'); b=_req(raw.get('target_panel'),f'links[{i}].target_panel'); c=str(raw.get('channel') or 'select').lower()
    if a not in panel_ids or b not in panel_ids: raise MultiViewScientificAnalysisCanvasError(f'links[{i}] references unknown panel(s).')
    if c not in INTERACTION_CHANNELS: raise MultiViewScientificAnalysisCanvasError(f'links[{i}].channel invalid.')
    return {'link_id':str(raw.get('link_id') or f'link:{_hash([a,b,c,i])[:16]}')[:500],'source_panel':a,'target_panel':b,'channel':c,'mapping_ref':raw.get('mapping_ref'),'explicit_mapping':bool(raw.get('mapping_ref')),'metadata':copy.deepcopy(raw.get('metadata') if isinstance(raw.get('metadata'),dict) else {})}
def _selection(raw,i=0):
    if not isinstance(raw,dict): raise MultiViewScientificAnalysisCanvasError('selection must be an object.')
    mode=str(raw.get('mode') or 'replace').lower()
    if mode not in SELECTION_MODES: raise MultiViewScientificAnalysisCanvasError('selection.mode invalid.')
    items=_list(raw.get('items'),'selection.items',MAX_SELECTION_ITEMS)
    norm=[]
    for j,x in enumerate(items):
        if isinstance(x,dict):
            ref=x.get('object_ref') or x.get('row_ref') or x.get('point_ref') or x.get('id')
            if ref is None: raise MultiViewScientificAnalysisCanvasError(f'selection.items[{j}] requires an explicit reference.')
            norm.append({'ref':str(ref)[:500],'kind':str(x.get('kind') or 'object')[:100],'panel_id':x.get('panel_id')})
        else: norm.append({'ref':str(x)[:500],'kind':'object','panel_id':None})
    return {'selection_ref':str(raw.get('selection_ref') or f'selection:{_hash(norm)[:16]}')[:500],'mode':mode,'items':norm,'item_count':len(norm),'source_panel':raw.get('source_panel'),'presentation_state_only':True}
def _filter(raw,i=0):
    if not isinstance(raw,dict): raise MultiViewScientificAnalysisCanvasError('filter must be an object.')
    field=_req(raw.get('field'),'filter.field'); op=str(raw.get('operator') or 'eq').lower()
    if op not in FILTER_OPERATORS: raise MultiViewScientificAnalysisCanvasError('filter.operator invalid.')
    return {'filter_ref':str(raw.get('filter_ref') or f'filter:{_hash(raw)[:16]}')[:500],'field':field,'operator':op,'value':copy.deepcopy(raw.get('value')),'source_panel':raw.get('source_panel'),'presentation_state_only':True}

def normalize_canvas(payload):
    if not isinstance(payload,dict): raise MultiViewScientificAnalysisCanvasError('payload must be an object.')
    layout=str(payload.get('layout_mode') or 'analysis').lower()
    if layout not in LAYOUT_MODES: raise MultiViewScientificAnalysisCanvasError('layout_mode invalid.')
    panels=[_panel(x,i) for i,x in enumerate(_list(payload.get('panels'),'panels',MAX_PANELS))]; ids=[p['panel_id'] for p in panels]
    if len(ids)!=len(set(ids)): raise MultiViewScientificAnalysisCanvasError('panel_id values must be unique.')
    links=[_link(x,i,set(ids)) for i,x in enumerate(_list(payload.get('links'),'links',MAX_LINKS))]
    selections=[_selection(x,i) for i,x in enumerate(_list(payload.get('selections'),'selections',MAX_FILTERS))]
    filters=[_filter(x,i) for i,x in enumerate(_list(payload.get('filters'),'filters',MAX_FILTERS))]
    canvas={'canvas_ref':str(payload.get('canvas_ref') or f'analysis-canvas:{_hash(payload)[:16]}')[:500],'project_ref':payload.get('project_ref'),'session_ref':payload.get('session_ref'),'layout_mode':layout,'panels':panels,'links':links,'selections':selections,'filters':filters,'panel_count':len(panels),'link_count':len(links),'selection_count':len(selections),'filter_count':len(filters),'selection_is_presentation_state':True,'filters_mutate_source_data':False,'automatic_join_inference':False,'scientific_objects_mutated':False}
    canvas['canvas_hash']=_hash(canvas)
    return {'ok':True,'version':VERSION,'canvas':canvas}
def _canvas(p): return normalize_canvas(p)['canvas']

def _positions(canvas,mode):
    ids=[p['panel_id'] for p in canvas['panels'] if p['visible']]; n=max(1,len(ids)); out={}
    for i,pid in enumerate(ids):
        if mode=='comparison': row=i//2; col=i%2; cols=2
        elif mode=='diagnostics': row=0 if i==0 else 1+(i-1)//3; col=0 if i==0 else (i-1)%3; cols=3
        elif mode=='evidence': row=i//3; col=i%3; cols=3
        elif mode=='presentation': row=i; col=0; cols=1
        else: row=0 if i==0 else 1+(i-1)//2; col=0 if i==0 else (i-1)%2; cols=2
        out[pid]={'row':row,'column':col,'column_span':cols if i==0 and mode in {'analysis','diagnostics'} else 1,'row_span':1}
    return out
def _layout(p,mode):
    c=_canvas({**p,'layout_mode':mode}); return {'ok':True,'version':VERSION,'layout_mode':mode,'positions':_positions(c,mode),'presentation_only':True,'scientific_objects_mutated':False}
def compose_canvas(p):
    c=_canvas(p); return {'ok':True,'version':VERSION,'canvas':c,'positions':_positions(c,c['layout_mode']),'linked_selection_enabled':bool(c['links']),'shared_filters_enabled':bool(c['filters']),'automatic_join_inference':False}
def analysis_layout(p): return _layout(p,'analysis')
def comparison_layout(p): return _layout(p,'comparison')
def diagnostics_layout(p): return _layout(p,'diagnostics')
def evidence_layout(p): return _layout(p,'evidence')
def presentation_layout(p): return _layout(p,'presentation')

def panel_plan(p):
    t=str(p.get('panel_type') or 'secondary-figure').lower()
    if t not in PANEL_TYPES: raise MultiViewScientificAnalysisCanvasError('panel_type invalid.')
    return {'ok':True,'version':VERSION,'panel_type':t,'object_refs':_refs(p.get('object_refs'),'object_refs'),'renderer_ref':p.get('renderer_ref'),'source_panel_ref':p.get('source_panel_ref'),'presentation_only':True,'automatic_scientific_interpretation':False}
def _typed_panel(p,t,extra=None):
    q={**p,'panel_type':t}; r=panel_plan(q); r.update(extra or {}); return r
def primary_figure_plan(p): return _typed_panel(p,'primary-figure',{'figure_ref':p.get('figure_ref'),'renderer_state_is_presentation':True})
def diagnostics_panel_plan(p): return _typed_panel(p,'diagnostics',{'diagnostic_refs':_refs(p.get('diagnostic_refs'),'diagnostic_refs'),'automatic_validity_judgment':False})
def uncertainty_panel_plan(p): return _typed_panel(p,'uncertainty',{'uncertainty_refs':_refs(p.get('uncertainty_refs'),'uncertainty_refs'),'automatic_probability_interpretation':False})
def evidence_panel_plan(p): return _typed_panel(p,'evidence',{'evidence_refs':_refs(p.get('evidence_refs'),'evidence_refs'),'claim_refs':_refs(p.get('claim_refs'),'claim_refs'),'automatic_evidence_weighting':False,'automatic_claim_status_change':False})
def provenance_panel_plan(p): return _typed_panel(p,'provenance',{'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'provenance_is_reference_first':True,'automatic_provenance_inference':False})
def model_graph_panel_plan(p): return _typed_panel(p,'model-graph',{'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'v01352_graph_bridge':True,'automatic_model_inference':False})
def data_table_panel_plan(p): return _typed_panel(p,'data-table',{'dataset_ref':p.get('dataset_ref'),'row_identity_must_be_explicit':True})
def narrative_panel_plan(p): return _typed_panel(p,'narrative',{'narrative_ref':p.get('narrative_ref'),'narrative_is_annotation_not_scientific_value':True})

def selection_normalize(p): return {'ok':True,'version':VERSION,'selection':_selection(p),'scientific_objects_mutated':False}
def selection_link(p):
    s=_selection(p.get('selection') if isinstance(p.get('selection'),dict) else p); targets=_refs(p.get('target_panel_ids'),'target_panel_ids',MAX_PANELS)
    return {'ok':True,'version':VERSION,'selection':s,'target_panel_ids':targets,'mapping_ref':p.get('mapping_ref'),'automatic_join_inference':False,'requires_explicit_mapping_for_nonidentical_ids':True,'scientific_objects_mutated':False}
def selection_clear(p): return {'ok':True,'version':VERSION,'selection_ref':p.get('selection_ref'),'cleared':True,'presentation_state_only':True,'scientific_objects_mutated':False}
def filter_normalize(p): return {'ok':True,'version':VERSION,'filter':_filter(p),'filters_mutate_source_data':False}
def _compare(v,op,target):
    try:
        if op=='eq': return v==target
        if op=='neq': return v!=target
        if op=='lt': return v<target
        if op=='lte': return v<=target
        if op=='gt': return v>target
        if op=='gte': return v>=target
        if op=='in': return v in (target if isinstance(target,(list,tuple,set)) else [target])
        if op=='contains': return str(target) in str(v)
    except Exception:return False
    return False
def filter_apply(p):
    f=_filter(p.get('filter') if isinstance(p.get('filter'),dict) else p); rows=_list(p.get('rows'),'rows',100000)
    matched=[]
    for i,row in enumerate(rows):
        if isinstance(row,dict) and _compare(row.get(f['field']),f['operator'],f['value']): matched.append(i)
    return {'ok':True,'version':VERSION,'filter':f,'matched_row_indices':matched,'matched_count':len(matched),'source_row_count':len(rows),'rows_mutated':False,'result_is_view_state':True}
def filter_share(p): return {'ok':True,'version':VERSION,'filter_refs':_refs(p.get('filter_refs'),'filter_refs',MAX_FILTERS),'target_panel_ids':_refs(p.get('target_panel_ids'),'target_panel_ids',MAX_PANELS),'automatic_field_mapping':False,'presentation_state_only':True}
def domain_sync(p): return {'ok':True,'version':VERSION,'axis':str(p.get('axis') or 'x')[:20],'domain':copy.deepcopy(p.get('domain')),'target_panel_ids':_refs(p.get('target_panel_ids'),'target_panel_ids',MAX_PANELS),'requires_compatible_declared_scale':True,'presentation_only':True}
def cursor_sync(p): return {'ok':True,'version':VERSION,'cursor':copy.deepcopy(p.get('cursor')),'source_panel':p.get('source_panel'),'target_panel_ids':_refs(p.get('target_panel_ids'),'target_panel_ids',MAX_PANELS),'presentation_only':True}
def brush_plan(p): return {'ok':True,'version':VERSION,'source_panel':p.get('source_panel'),'field_refs':_refs(p.get('field_refs'),'field_refs',128),'selection_mode':str(p.get('selection_mode') or 'replace'),'brush_is_selection_not_data_edit':True}
def focus_plan(p): return {'ok':True,'version':VERSION,'panel_id':p.get('panel_id'),'object_ref':p.get('object_ref'),'preserve_linked_context':bool(p.get('preserve_linked_context',True)),'presentation_only':True}
def annotation_plan(p): return {'ok':True,'version':VERSION,'panel_id':p.get('panel_id'),'annotation_refs':_refs(p.get('annotation_refs'),'annotation_refs',1000),'annotations_do_not_change_scientific_values':True,'automatic_scientific_interpretation':False}
def evidence_context_plan(p): return {'ok':True,'version':VERSION,'evidence_refs':_refs(p.get('evidence_refs'),'evidence_refs'),'claim_refs':_refs(p.get('claim_refs'),'claim_refs'),'automatic_evidence_weighting':False,'automatic_claim_status_change':False}
def diagnostic_context_plan(p): return {'ok':True,'version':VERSION,'diagnostic_refs':_refs(p.get('diagnostic_refs'),'diagnostic_refs'),'assumption_refs':_refs(p.get('assumption_refs'),'assumption_refs'),'automatic_validity_judgment':False,'automatic_method_rejection':False}
def uncertainty_context_plan(p): return {'ok':True,'version':VERSION,'uncertainty_refs':_refs(p.get('uncertainty_refs'),'uncertainty_refs'),'distribution_refs':_refs(p.get('distribution_refs'),'distribution_refs'),'values_must_be_bound_or_declared':True,'automatic_probability_interpretation':False}
def provenance_context_plan(p): return {'ok':True,'version':VERSION,'graph_refs':_refs(p.get('graph_refs'),'graph_refs'),'execution_refs':_refs(p.get('execution_refs'),'execution_refs'),'v01352_graph_bridge':True,'automatic_provenance_inference':False}
def build_snapshot(p):
    c=_canvas(p); body={'schema':SNAPSHOT_SCHEMA,'version':VERSION,'canvas':c,'presentation':copy.deepcopy(p.get('presentation') if isinstance(p.get('presentation'),dict) else {}),'object_refs':_refs(p.get('object_refs'),'object_refs')}; body['snapshot_hash']=_hash(body); return {'ok':True,'version':VERSION,'snapshot':body}
def revision_plan(p): return {'ok':True,'version':VERSION,'base_snapshot_ref':p.get('base_snapshot_ref'),'operations':copy.deepcopy(_list(p.get('operations'),'operations',1000)),'automatic_scientific_object_mutation':False,'requires_explicit_apply':True}
def export_plan(p): return {'ok':True,'version':VERSION,'formats':[str(x).lower() for x in _list(p.get('formats') or ['json','svg','png'],'formats',20)],'include_panel_specs':True,'include_linked_selection_state':bool(p.get('include_linked_selection_state',True)),'include_object_refs':True,'scientific_values_only_if_bound_or_declared':True}
def handoff_plan(p): return {'ok':True,'version':VERSION,'destination':str(p.get('destination') or 'platform-core')[:100],'canvas_refs':_refs(p.get('canvas_refs'),'canvas_refs'),'scientific_object_refs':_refs(p.get('scientific_object_refs'),'scientific_object_refs'),'reference_first':True,'automatic_submission':False}
def core_object_plan(p): return {'ok':True,'version':VERSION,'object_type':'multi-view-scientific-analysis-canvas','canvas_refs':_refs(p.get('canvas_refs'),'canvas_refs'),'scientific_object_refs':_refs(p.get('scientific_object_refs'),'scientific_object_refs'),'lab_owns_view_composition':True,'core_owns_canonical_research_objects':True,'automatic_core_submission':False,'reference_first':True}
def readiness_report(p):
    c=_canvas(p); warnings=[]
    if not c['panels']: warnings.append('No analysis panels are declared.')
    if c['panels'] and not any(x['panel_type']=='primary-figure' for x in c['panels']): warnings.append('No primary-figure panel is declared.')
    if any(not x['object_refs'] and not x.get('figure_ref') and not x.get('data_ref') and not x.get('graph_ref') for x in c['panels']): warnings.append('One or more panels have no bound scientific-object reference.')
    if any(not x['explicit_mapping'] and x['source_panel']!=x['target_panel'] for x in c['links']): warnings.append('One or more cross-panel links rely on shared identifiers; nonidentical identifiers require an explicit mapping_ref.')
    return {'ok':True,'version':VERSION,'ready_for_visualization':bool(c['panels']),'warnings':warnings,'scientific_validity_certified':False,'automatic_join_inference':False}
def interpretation_boundaries_report(p=None): return {'ok':True,'version':VERSION,'selection_mutates_scientific_record':False,'filters_mutate_source_data':False,'automatic_join_inference':False,'automatic_scientific_interpretation':False,'automatic_validity_judgment':False,'automatic_probability_interpretation':False,'automatic_evidence_weighting':False,'automatic_claim_status_change':False,'automatic_core_submission':False,'determine_truth':False}
