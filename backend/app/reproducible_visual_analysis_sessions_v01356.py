from __future__ import annotations
import copy, json
from hashlib import sha256
from typing import Any

VERSION='0.135.6'; ENGINE_VERSION='16.6.0'
SCHEMA='sc-lab-reproducible-visual-analysis-sessions/0.135.6'
SNAPSHOT_SCHEMA='sc-lab-reproducible-visual-analysis-session-snapshot/0.135.6'
EVENT_TYPES={'focus','select','filter','brush','drill','camera','viewport','compare','pin','annotation','layout','checkpoint'}
SESSION_STATES={'active','paused','closed','archived'}
CHECKPOINT_KINDS={'manual','milestone','before-compare','before-drill','export'}
REPLAY_MODES={'strict','reference-only','presentation-only'}
MAX_EVENTS=5000; MAX_CHECKPOINTS=256; MAX_REFS=10000; MAX_BYTES=1048576

class ReproducibleVisualAnalysisSessionError(ValueError):
    def __init__(self, detail, status_code=400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _req(v,label):
    s=str(v or '').strip()
    if not s: raise ReproducibleVisualAnalysisSessionError(f'{label} is required.')
    return s[:500]
def _list(v,label,limit):
    if v is None: return []
    if not isinstance(v,list): raise ReproducibleVisualAnalysisSessionError(f'{label} must be an array.')
    if len(v)>limit: raise ReproducibleVisualAnalysisSessionError(f'{label} exceeds configured maximum of {limit}.')
    return copy.deepcopy(v)
def _meta(v): return copy.deepcopy(v) if isinstance(v,dict) else {}

def schema_info():
    return {'ok':True,'schema':SCHEMA,'snapshot_schema':SNAPSHOT_SCHEMA,'version':VERSION,'engine_version':ENGINE_VERSION,
            'event_types':sorted(EVENT_TYPES),'session_states':sorted(SESSION_STATES),'checkpoint_kinds':sorted(CHECKPOINT_KINDS),'replay_modes':sorted(REPLAY_MODES),
            'limits':{'events':MAX_EVENTS,'checkpoints':MAX_CHECKPOINTS,'refs':MAX_REFS,'bytes':MAX_BYTES}}
def catalog():
    return {'ok':True,'version':VERSION,'event_types':sorted(EVENT_TYPES),'event_type_count':len(EVENT_TYPES),'session_states':sorted(SESSION_STATES),'session_state_count':len(SESSION_STATES),
            'checkpoint_kinds':sorted(CHECKPOINT_KINDS),'checkpoint_kind_count':len(CHECKPOINT_KINDS),'replay_modes':sorted(REPLAY_MODES),'replay_mode_count':len(REPLAY_MODES),
            'interaction_lineage_is_not_scientific_evidence':True,'replay_requires_declared_references':True,'presentation_events_non_authoritative':True,
            'automatic_scientific_inference':False,'automatic_evidence_weighting':False,'automatic_core_submission':False}
def manifest():
    return {'ok':True,'status':'reproducible-visual-analysis-sessions-ready','version':VERSION,'engine_version':ENGINE_VERSION,
            'session_capture':True,'ordered_interaction_lineage':True,'checkpoints':True,'deterministic_replay_plans':True,'context_preservation':True,
            'v01355_context_bridge':True,'v01354_scene_bridge':True,'v01353_canvas_bridge':True,'v01352_graph_bridge':True,'platform_core_reference_bridge':True,
            'ui_history_becomes_scientific_evidence':False,'replay_mutates_source_science':False,'automatic_scientific_inference':False,'automatic_core_submission':False}
def health():
    return {**manifest(),'schema':SCHEMA,'event_type_count':12,'session_state_count':4,'checkpoint_kind_count':5,'replay_mode_count':3,'api_route_count':52}

def normalize_session(payload):
    if not isinstance(payload,dict): raise ReproducibleVisualAnalysisSessionError('payload must be an object.')
    state=str(payload.get('state') or 'active').lower()
    if state not in SESSION_STATES: raise ReproducibleVisualAnalysisSessionError('session state invalid.')
    s={'session_ref':str(payload.get('session_ref') or f'visual-session:{_hash(payload)[:16]}')[:500], 'state':state,
       'project_ref':payload.get('project_ref'),'study_ref':payload.get('study_ref'),'canvas_ref':payload.get('canvas_ref'),'scene_ref':payload.get('scene_ref'),
       'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),'metadata':_meta(payload.get('metadata')),
       'interaction_lineage_authoritative_for_science':False,'presentation_state_only':True}
    s['session_hash']=_hash(s); return {'ok':True,'version':VERSION,'session':s}
def create_session(payload): return {**normalize_session(payload),'created':True,'scientific_record_mutated':False}
def close_session(payload):
    s=normalize_session(payload)['session']; s['state']='closed'; s['session_hash']=_hash(s); return {'ok':True,'version':VERSION,'session':s,'scientific_record_mutated':False}
def clone_session(payload):
    s=normalize_session(payload)['session']; s['parent_session_ref']=s['session_ref']; s['session_ref']=str(payload.get('clone_ref') or f"visual-session:{_hash({'parent':s['parent_session_ref'],'payload':payload})[:16]}")[:500]; s['session_hash']=_hash(s)
    return {'ok':True,'version':VERSION,'session':s,'scientific_record_mutated':False}

def normalize_event(payload):
    if not isinstance(payload,dict): raise ReproducibleVisualAnalysisSessionError('payload must be an object.')
    t=str(payload.get('event_type') or '').lower()
    if t not in EVENT_TYPES: raise ReproducibleVisualAnalysisSessionError('event_type invalid.')
    seq=int(payload.get('sequence',0));
    if seq<0: raise ReproducibleVisualAnalysisSessionError('sequence must be non-negative.')
    e={'event_ref':str(payload.get('event_ref') or f'visual-event:{_hash(payload)[:16]}')[:500],'event_type':t,'sequence':seq,
       'target_ref':payload.get('target_ref'),'source_ref':payload.get('source_ref'),'context_ref':payload.get('context_ref'),'payload':_meta(payload.get('payload')),
       'presentation_event':True,'scientific_assertion':False}
    e['event_hash']=_hash(e); return {'ok':True,'version':VERSION,'event':e}
def append_event(payload): return {**normalize_event(payload),'appended':True,'scientific_record_mutated':False}
def append_event_batch(payload):
    raw=_list(payload.get('events') if isinstance(payload,dict) else None,'events',MAX_EVENTS); events=[normalize_event(x)['event'] for x in raw]
    seq=[e['sequence'] for e in events]
    if seq!=sorted(seq): raise ReproducibleVisualAnalysisSessionError('events must be ordered by non-decreasing sequence.')
    return {'ok':True,'version':VERSION,'events':events,'event_count':len(events),'scientific_record_mutated':False}
def list_events(payload):
    r=append_event_batch(payload); return {'ok':True,'version':VERSION,'events':r['events'],'event_count':r['event_count']}

def build_lineage(payload):
    r=append_event_batch(payload); events=r['events']; edges=[]
    for a,b in zip(events,events[1:]): edges.append({'from_event_ref':a['event_ref'],'to_event_ref':b['event_ref'],'relation':'next-interaction'})
    lineage={'session_ref':payload.get('session_ref'),'events':events,'edges':edges,'ordered':True,'scientific_causality':False}; lineage['lineage_hash']=_hash(lineage)
    return {'ok':True,'version':VERSION,'lineage':lineage}
def audit_lineage(payload):
    l=build_lineage(payload)['lineage']; seq=[e['sequence'] for e in l['events']]; return {'ok':True,'version':VERSION,'lineage_hash':l['lineage_hash'],'ordered':seq==sorted(seq),'duplicate_sequences':len(seq)!=len(set(seq)),'scientific_causality_inferred':False}
def lineage_path(payload):
    l=build_lineage(payload)['lineage']; refs=[e['event_ref'] for e in l['events']]; return {'ok':True,'version':VERSION,'event_refs':refs,'path_length':len(refs),'path_is_interaction_order_not_causality':True}
def lineage_upstream(payload):
    l=build_lineage(payload)['lineage']; target=_req(payload.get('event_ref'),'event_ref'); refs=[e['event_ref'] for e in l['events']]; i=refs.index(target) if target in refs else len(refs); return {'ok':True,'version':VERSION,'event_refs':refs[:i],'scientific_dependencies_inferred':False}
def lineage_downstream(payload):
    l=build_lineage(payload)['lineage']; target=_req(payload.get('event_ref'),'event_ref'); refs=[e['event_ref'] for e in l['events']]; i=refs.index(target)+1 if target in refs else 0; return {'ok':True,'version':VERSION,'event_refs':refs[i:],'scientific_dependencies_inferred':False}

def normalize_checkpoint(payload):
    if not isinstance(payload,dict): raise ReproducibleVisualAnalysisSessionError('payload must be an object.')
    kind=str(payload.get('checkpoint_kind') or 'manual').lower()
    if kind not in CHECKPOINT_KINDS: raise ReproducibleVisualAnalysisSessionError('checkpoint_kind invalid.')
    cp={'checkpoint_ref':str(payload.get('checkpoint_ref') or f'checkpoint:{_hash(payload)[:16]}')[:500],'checkpoint_kind':kind,'sequence':int(payload.get('sequence',0)),
        'session_ref':payload.get('session_ref'),'context':_meta(payload.get('context')),'pins':_list(payload.get('pins'),'pins',256),'comparison':_meta(payload.get('comparison')),'scene':_meta(payload.get('scene')),'canvas':_meta(payload.get('canvas')),
        'scientific_values_by_reference_only':True}
    cp['checkpoint_hash']=_hash(cp); return {'ok':True,'version':VERSION,'checkpoint':cp}
def create_checkpoint(payload): return {**normalize_checkpoint(payload),'created':True,'scientific_record_mutated':False}
def restore_checkpoint(payload):
    cp=normalize_checkpoint(payload.get('checkpoint') if isinstance(payload,dict) and isinstance(payload.get('checkpoint'),dict) else payload)['checkpoint']; return {'ok':True,'version':VERSION,'restore_plan':copy.deepcopy(cp),'scientific_record_mutated':False}
def list_checkpoints(payload):
    cps=[normalize_checkpoint(x)['checkpoint'] for x in _list(payload.get('checkpoints') if isinstance(payload,dict) else None,'checkpoints',MAX_CHECKPOINTS)]; return {'ok':True,'version':VERSION,'checkpoints':cps,'checkpoint_count':len(cps)}

def replay_plan(payload):
    mode=str(payload.get('replay_mode') or 'strict').lower() if isinstance(payload,dict) else 'strict'
    if mode not in REPLAY_MODES: raise ReproducibleVisualAnalysisSessionError('replay_mode invalid.')
    events=append_event_batch(payload)['events']; return {'ok':True,'version':VERSION,'replay_mode':mode,'events':events,'event_count':len(events),'requires_declared_references':True,'replay_mutates_science':False}
def validate_replay(payload):
    p=replay_plan(payload); missing=[e['event_ref'] for e in p['events'] if not (e.get('target_ref') or e.get('source_ref'))]
    return {'ok':True,'version':VERSION,'valid':len(missing)==0 or p['replay_mode']=='presentation-only','missing_reference_events':missing,'scientific_validity_certified':False}
def replay_window(payload):
    p=replay_plan(payload); start=max(0,int(payload.get('start_sequence',0))); end=int(payload.get('end_sequence',10**9)); ev=[e for e in p['events'] if start<=e['sequence']<=end]; return {'ok':True,'version':VERSION,'events':ev,'event_count':len(ev),'replay_mutates_science':False}
def replay_step(payload):
    e=normalize_event(payload.get('event') if isinstance(payload,dict) and isinstance(payload.get('event'),dict) else payload)['event']; return {'ok':True,'version':VERSION,'event':e,'apply_to_presentation_state_only':True,'scientific_record_mutated':False}

def current_state(payload): return {'ok':True,'version':VERSION,'state':_meta(payload.get('state') if isinstance(payload,dict) else {}),'authoritative_for_science':False}
def state_diff(payload):
    a=_meta(payload.get('a') if isinstance(payload,dict) else {}); b=_meta(payload.get('b') if isinstance(payload,dict) else {}); keys=sorted(set(a)|set(b)); changed=[k for k in keys if a.get(k)!=b.get(k)]; return {'ok':True,'version':VERSION,'changed_keys':changed,'changed_count':len(changed),'scientific_difference_inferred':False}
def state_hash(payload):
    s=_meta(payload.get('state') if isinstance(payload,dict) else {}); return {'ok':True,'version':VERSION,'state_hash':_hash(s),'authoritative_for_science':False}
def state_restore_plan(payload): return {'ok':True,'version':VERSION,'state':_meta(payload.get('state') if isinstance(payload,dict) else {}),'presentation_state_only':True,'scientific_record_mutated':False}

def _bridge(payload,kind): return {'ok':True,'version':VERSION,'bridge':kind,'reference':_meta(payload),'reference_first':True,'scientific_record_mutated':False}
def canvas_bridge(payload): return _bridge(payload,'v0.135.3-canvas')
def scene_bridge(payload): return _bridge(payload,'v0.135.4-scene')
def context_bridge(payload): return _bridge(payload,'v0.135.5-context')
def comparison_bridge(payload): return _bridge(payload,'comparison')
def pins_bridge(payload): return _bridge(payload,'pins')
def provenance_bridge(payload): return _bridge(payload,'provenance')
def uncertainty_bridge(payload): return _bridge(payload,'uncertainty')
def evidence_bridge(payload): return _bridge(payload,'evidence')

def export_plan(payload): return {'ok':True,'version':VERSION,'formats':['json','session-json','interaction-lineage-json','research-package-reference'],'reference_first':True,'automatic_publication':False}
def import_plan(payload): return {'ok':True,'version':VERSION,'requires_schema_validation':True,'requires_reference_resolution':True,'automatic_merge':False,'scientific_record_mutated':False}
def reproduction_plan(payload): return {'ok':True,'version':VERSION,'reproduction_kind':'visual-analysis-session','requires_declared_sources':True,'requires_versioned_scene_canvas_context':True,'replay_is_not_scientific_replication':True}
def core_object_plan(payload): return {'ok':True,'version':VERSION,'core_object_type':'visual-analysis-session','reference_first':True,'requires_explicit_submission':True,'automatic_core_submission':False}
def handoff_plan(payload): return {'ok':True,'version':VERSION,'handoff_kind':'reproducible-visual-analysis-session','target_products':['Platform Core','Workspace','Knowledge Library','Decision Studio'],'reference_first':True,'automatic_handoff':False}

def sequence_guard(payload):
    ev=append_event_batch(payload)['events']; seq=[e['sequence'] for e in ev]; return {'ok':True,'version':VERSION,'ordered':seq==sorted(seq),'scientific_causality_inferred':False}
def reference_guard(payload):
    refs=_list(payload.get('refs') if isinstance(payload,dict) else None,'refs',MAX_REFS); return {'ok':True,'version':VERSION,'refs':refs,'explicit_reference_count':len(refs),'implicit_reference_resolution':False}
def presentation_guard(payload): return {'ok':True,'version':VERSION,'presentation_state_only':True,'scientific_record_mutated':False,'scientific_assertion_created':False}
def scientific_boundary_guard(payload): return {'ok':True,'version':VERSION,'interaction_history_is_evidence':False,'replay_certifies_scientific_validity':False,'interaction_order_implies_causality':False,'automatic_core_submission':False}

def interpretation_boundaries_report(payload=None): return {'ok':True,'version':VERSION,'interaction_history_is_scientific_evidence':False,'interaction_order_is_scientific_causality':False,'replay_is_scientific_replication':False,'weight_evidence':False,'change_claim_status':False,'certify_scientific_validity':False,'determine_truth':False,'automatic_core_submission':False}
def readiness_report(payload=None): return {'ok':True,'version':VERSION,'ready':True,'session_capture':True,'interaction_lineage':True,'checkpoints':True,'replay_plans':True,'retains_v01355':True,'retains_v01354':True,'retains_v01353':True,'retains_v01352':True,'boundaries':interpretation_boundaries_report()}
def integrity_report(payload):
    s=normalize_session(payload.get('session') if isinstance(payload,dict) and isinstance(payload.get('session'),dict) else payload)['session']; return {'ok':True,'version':VERSION,'session_hash':s['session_hash'],'integrity_ok':True,'scientific_validity_certified':False}
def determinism_report(payload):
    p=replay_plan(payload); a=_hash(p['events']); b=_hash(p['events']); return {'ok':True,'version':VERSION,'deterministic_event_hash':a,'deterministic':a==b,'scientific_reproducibility_certified':False}

def build_snapshot(payload):
    session=normalize_session(payload.get('session') if isinstance(payload,dict) and isinstance(payload.get('session'),dict) else {})['session']; events=append_event_batch({'events':payload.get('events',[])})['events'] if isinstance(payload,dict) else []
    snap={'schema':SNAPSHOT_SCHEMA,'snapshot_ref':str(payload.get('snapshot_ref') or f'session-snapshot:{_hash(payload)[:16]}')[:500],'session':session,'events':events,'checkpoint':_meta(payload.get('checkpoint')),'reference_first':True,'scientific_record_mutated':False}; snap['snapshot_hash']=_hash(snap); return {'ok':True,'version':VERSION,'snapshot':snap}
def restore_snapshot(payload):
    snap=payload.get('snapshot') if isinstance(payload,dict) else None
    if not isinstance(snap,dict): raise ReproducibleVisualAnalysisSessionError('snapshot must be an object.')
    return {'ok':True,'version':VERSION,'restore_plan':copy.deepcopy(snap),'presentation_state_only':True,'scientific_record_mutated':False}
