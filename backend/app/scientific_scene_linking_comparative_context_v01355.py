from __future__ import annotations
import copy, json
from hashlib import sha256
from typing import Any

VERSION='0.135.5'; ENGINE_VERSION='16.5.0'
SCHEMA='sc-lab-scientific-scene-linking-comparative-context/0.135.5'
SNAPSHOT_SCHEMA='sc-lab-scientific-scene-linking-comparative-context-snapshot/0.135.5'
MAX_LINKS=1024; MAX_PINS=256; MAX_COMPARE=64; MAX_REFS=10000; MAX_CONTEXT_BYTES=262144
LINK_TYPES={'same-object','derived-from','parent-child','input-output','figure-reference','model-reference','evidence-reference','provenance-reference','spatial-reference','temporal-reference'}
COMPARE_MODES={'side-by-side','overlay','synchronized','small-multiple','difference-metadata','provenance'}
CONTEXT_FAMILIES={'selection','focus','drill-path','camera','viewport','time','spatial','uncertainty','diagnostics','evidence','provenance','annotation'}
PIN_STATES={'active','reference','hidden'}

class ScientificSceneLinkingComparativeContextError(ValueError):
    def __init__(self, detail, status_code=400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _req(v,label):
    s=str(v or '').strip()
    if not s: raise ScientificSceneLinkingComparativeContextError(f'{label} is required.')
    return s[:500]
def _list(v,label,limit):
    if v is None: return []
    if not isinstance(v,list): raise ScientificSceneLinkingComparativeContextError(f'{label} must be an array.')
    if len(v)>limit: raise ScientificSceneLinkingComparativeContextError(f'{label} exceeds configured maximum of {limit}.')
    return v
def _refs(v,label,limit=MAX_REFS): return [str(x)[:500] for x in _list(v,label,limit)]
def _meta(v): return copy.deepcopy(v) if isinstance(v,dict) else {}

def schema_info():
    return {'ok':True,'schema':SCHEMA,'snapshot_schema':SNAPSHOT_SCHEMA,'version':VERSION,'engine_version':ENGINE_VERSION,
            'link_types':sorted(LINK_TYPES),'compare_modes':sorted(COMPARE_MODES),'context_families':sorted(CONTEXT_FAMILIES),'pin_states':sorted(PIN_STATES),
            'limits':{'links':MAX_LINKS,'pins':MAX_PINS,'compare':MAX_COMPARE,'refs':MAX_REFS,'context_bytes':MAX_CONTEXT_BYTES}}
def catalog():
    return {'ok':True,'version':VERSION,'link_types':sorted(LINK_TYPES),'link_type_count':len(LINK_TYPES),'compare_modes':sorted(COMPARE_MODES),'compare_mode_count':len(COMPARE_MODES),
            'context_families':sorted(CONTEXT_FAMILIES),'context_family_count':len(CONTEXT_FAMILIES),'pin_states':sorted(PIN_STATES),'pin_state_count':len(PIN_STATES),
            'links_must_be_explicit':True,'cross_object_equivalence_must_be_explicit':True,'context_is_non_authoritative':True,'comparison_is_not_causal_inference':True,
            'automatic_equivalence_inference':False,'automatic_join_inference':False,'automatic_evidence_weighting':False,'automatic_core_submission':False}
def manifest():
    return {'ok':True,'status':'scientific-scene-linking-comparative-context-ready','version':VERSION,'engine_version':ENGINE_VERSION,
            'cross_scene_linking':True,'comparative_inspection':True,'context_preservation':True,'pinned_inspection':True,'context_capsules':True,
            'v01354_scene_bridge':True,'v01353_canvas_bridge':True,'v01352_graph_bridge':True,'platform_core_reference_bridge':True,
            'presentation_state_mutates_scientific_record':False,'automatic_equivalence_inference':False,'automatic_join_inference':False,'automatic_causal_interpretation':False,'automatic_core_submission':False}
def health():
    return {**manifest(),'schema':SCHEMA,'link_type_count':10,'compare_mode_count':6,'context_family_count':12,'pin_state_count':3,'api_route_count':48}

def normalize_link(payload):
    if not isinstance(payload,dict): raise ScientificSceneLinkingComparativeContextError('payload must be an object.')
    t=str(payload.get('link_type') or 'same-object').lower()
    if t not in LINK_TYPES: raise ScientificSceneLinkingComparativeContextError('link_type invalid.')
    src=_req(payload.get('source_ref'),'source_ref'); dst=_req(payload.get('target_ref'),'target_ref')
    link={'link_ref':str(payload.get('link_ref') or f'link:{_hash(payload)[:16]}')[:500],'link_type':t,'source_ref':src,'target_ref':dst,
          'mapping_ref':payload.get('mapping_ref'),'declared':bool(payload.get('declared',True)),'bidirectional':bool(payload.get('bidirectional',False)),
          'metadata':_meta(payload.get('metadata')),'equivalence_asserted':bool(payload.get('equivalence_asserted',False))}
    if t=='same-object' and src!=dst and not link['equivalence_asserted']:
        raise ScientificSceneLinkingComparativeContextError('same-object links across nonidentical refs require equivalence_asserted=true.')
    link['link_hash']=_hash(link)
    return {'ok':True,'version':VERSION,'link':link,'automatic_equivalence_inference':False}
def validate_link(payload):
    r=normalize_link(payload)['link']
    return {'ok':True,'version':VERSION,'valid':True,'link':r,'warnings':([] if r['declared'] else ['link is not declared authoritative metadata']),'scientific_values_mutated':False}

def normalize_context_capsule(payload):
    if not isinstance(payload,dict): raise ScientificSceneLinkingComparativeContextError('payload must be an object.')
    fams={}
    raw=payload.get('context') if isinstance(payload.get('context'),dict) else {}
    for k,v in raw.items():
        key=str(k).lower()
        if key not in CONTEXT_FAMILIES: continue
        fams[key]=copy.deepcopy(v)
    cap={'capsule_ref':str(payload.get('capsule_ref') or f'context:{_hash(payload)[:16]}')[:500],'source_ref':payload.get('source_ref'),'scene_ref':payload.get('scene_ref'),'canvas_ref':payload.get('canvas_ref'),
         'context':fams,'context_families':sorted(fams),'authoritative':False,'presentation_or_reference_state_only':True,'created_from_declared_context':True}
    if len(_stable(cap).encode())>MAX_CONTEXT_BYTES: raise ScientificSceneLinkingComparativeContextError('context capsule exceeds maximum serialized size.')
    cap['context_hash']=_hash(cap)
    return {'ok':True,'version':VERSION,'capsule':cap}
def preserve_context(payload):
    cap=normalize_context_capsule(payload)['capsule']
    return {'ok':True,'version':VERSION,'capsule':cap,'preserved':True,'scientific_record_mutated':False}
def restore_context(payload):
    cap=normalize_context_capsule(payload.get('capsule') if isinstance(payload,dict) and isinstance(payload.get('capsule'),dict) else payload)['capsule']
    return {'ok':True,'version':VERSION,'restored_context':cap['context'],'restored_families':cap['context_families'],'scientific_record_mutated':False}

def normalize_pin(payload):
    if not isinstance(payload,dict): raise ScientificSceneLinkingComparativeContextError('payload must be an object.')
    ref=_req(payload.get('object_ref') or payload.get('target_ref'),'object_ref'); state=str(payload.get('state') or 'active').lower()
    if state not in PIN_STATES: raise ScientificSceneLinkingComparativeContextError('pin state invalid.')
    pin={'pin_ref':str(payload.get('pin_ref') or f'pin:{_hash(payload)[:16]}')[:500],'object_ref':ref,'state':state,'label':str(payload.get('label') or ref)[:500],
         'scene_ref':payload.get('scene_ref'),'canvas_ref':payload.get('canvas_ref'),'context_ref':payload.get('context_ref'),'metadata':_meta(payload.get('metadata'))}
    pin['pin_hash']=_hash(pin); return {'ok':True,'version':VERSION,'pin':pin}
def pin_object(payload): return {**normalize_pin(payload),'pinned':True,'scientific_record_mutated':False}
def unpin_object(payload):
    return {'ok':True,'version':VERSION,'object_ref':_req(payload.get('object_ref') if isinstance(payload,dict) else None,'object_ref'),'pinned':False,'scientific_record_mutated':False}
def pin_set(payload):
    pins=[normalize_pin(x)['pin'] for x in _list(payload.get('pins') if isinstance(payload,dict) else None,'pins',MAX_PINS)]
    return {'ok':True,'version':VERSION,'pins':pins,'pin_count':len(pins),'scientific_record_mutated':False}

def normalize_comparison_set(payload):
    if not isinstance(payload,dict): raise ScientificSceneLinkingComparativeContextError('payload must be an object.')
    mode=str(payload.get('compare_mode') or 'side-by-side').lower()
    if mode not in COMPARE_MODES: raise ScientificSceneLinkingComparativeContextError('compare_mode invalid.')
    refs=_refs(payload.get('object_refs'),'object_refs',MAX_COMPARE)
    if len(refs)<2: raise ScientificSceneLinkingComparativeContextError('comparison requires at least two object_refs.')
    links=[normalize_link(x)['link'] for x in _list(payload.get('links'),'links',MAX_LINKS)]
    comp={'comparison_ref':str(payload.get('comparison_ref') or f'compare:{_hash(payload)[:16]}')[:500],'compare_mode':mode,'object_refs':refs,'links':links,
          'baseline_ref':payload.get('baseline_ref'),'synchronized_context':bool(payload.get('synchronized_context',True)),'metadata':_meta(payload.get('metadata')),
          'equivalence_inferred':False,'causal_interpretation':False}
    comp['comparison_hash']=_hash(comp)
    return {'ok':True,'version':VERSION,'comparison':comp}
def comparison_plan(payload):
    c=normalize_comparison_set(payload)['comparison']
    return {'ok':True,'version':VERSION,'comparison':c,'linked_object_count':len(c['object_refs']),'automatic_equivalence_inference':False,'automatic_causal_interpretation':False}
def _compare_mode(payload,mode):
    p=dict(payload or {}); p['compare_mode']=mode; return comparison_plan(p)
def side_by_side_plan(payload): return _compare_mode(payload,'side-by-side')
def overlay_plan(payload): return _compare_mode(payload,'overlay')
def synchronized_plan(payload): return _compare_mode(payload,'synchronized')
def provenance_compare_plan(payload): return _compare_mode(payload,'provenance')
def difference_metadata_plan(payload):
    r=_compare_mode(payload,'difference-metadata'); r['numeric_difference_inference']=False; r['metadata_difference_only']=True; return r
def small_multiple_plan(payload): return _compare_mode(payload,'small-multiple')
def synchronized_focus_plan(payload):
    refs=_refs(payload.get('object_refs') if isinstance(payload,dict) else None,'object_refs',MAX_COMPARE)
    return {'ok':True,'version':VERSION,'focus_ref':payload.get('focus_ref') if isinstance(payload,dict) else None,'object_refs':refs,'synchronize_presentation_state_only':True,'scientific_record_mutated':False}

def context_bridge(payload):
    cap=normalize_context_capsule(payload)['capsule']; return {'ok':True,'version':VERSION,'capsule':cap,'bridge':'generic','scientific_record_mutated':False}
def canvas_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'v0.135.3-multi-view-canvas','v01353_canvas_bridge':True}); return r
def scene_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'v0.135.4-interactive-scene','v01354_scene_bridge':True}); return r
def provenance_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'v0.135.2-provenance-graph','v01352_graph_bridge':True,'automatic_provenance_inference':False}); return r
def uncertainty_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'uncertainty','automatic_probability_interpretation':False}); return r
def evidence_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'evidence','automatic_evidence_weighting':False,'automatic_claim_status_change':False}); return r
def diagnostics_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'diagnostics','automatic_validity_certification':False}); return r
def spatial_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'spatial','crs_must_be_declared':True,'automatic_reprojection':False}); return r
def temporal_bridge(payload):
    r=context_bridge(payload); r.update({'bridge':'temporal','time_semantics_must_be_declared':True,'automatic_interpolation':False}); return r

def mapping_validation(payload):
    mappings=_list(payload.get('mappings') if isinstance(payload,dict) else None,'mappings',MAX_LINKS); out=[]
    for i,m in enumerate(mappings):
        if not isinstance(m,dict): raise ScientificSceneLinkingComparativeContextError(f'mappings[{i}] must be an object.')
        out.append({'mapping_ref':_req(m.get('mapping_ref'),f'mappings[{i}].mapping_ref'),'source_ref':_req(m.get('source_ref'),f'mappings[{i}].source_ref'),'target_ref':_req(m.get('target_ref'),f'mappings[{i}].target_ref'),'declared':True})
    return {'ok':True,'version':VERSION,'mappings':out,'mapping_count':len(out),'automatic_join_inference':False}
def equivalence_guard(payload):
    src=_req(payload.get('source_ref') if isinstance(payload,dict) else None,'source_ref'); dst=_req(payload.get('target_ref') if isinstance(payload,dict) else None,'target_ref')
    explicit=bool(payload.get('equivalence_asserted')) if isinstance(payload,dict) else False
    return {'ok':True,'version':VERSION,'source_ref':src,'target_ref':dst,'same_literal_ref':src==dst,'equivalence_asserted':explicit,'equivalence_usable':src==dst or explicit,'automatic_equivalence_inference':False}
def compare_target_guard(payload):
    refs=_refs(payload.get('object_refs') if isinstance(payload,dict) else None,'object_refs',MAX_COMPARE)
    return {'ok':True,'version':VERSION,'object_refs':refs,'distinct_count':len(set(refs)),'comparison_allowed':len(set(refs))>=2,'comparison_implies_equivalence':False,'comparison_implies_causality':False}
def cross_scene_link_plan(payload):
    l=normalize_link(payload)['link']; return {'ok':True,'version':VERSION,'link':l,'source_scene_ref':payload.get('source_scene_ref'),'target_scene_ref':payload.get('target_scene_ref'),'cross_scene':True,'scientific_record_mutated':False}
def navigation_context_plan(payload): return {'ok':True,'version':VERSION,'context':normalize_context_capsule(payload)['capsule'],'navigation_state_is_presentation':True}
def drill_context_plan(payload): return {'ok':True,'version':VERSION,'context':normalize_context_capsule(payload)['capsule'],'drill_path_must_be_explicit':True,'scientific_record_mutated':False}
def breadcrumb_context_plan(payload):
    path=_refs(payload.get('path') if isinstance(payload,dict) else None,'path',256); return {'ok':True,'version':VERSION,'path':path,'depth':len(path),'presentation_state_only':True}
def context_diff(payload):
    a=normalize_context_capsule(payload.get('a') if isinstance(payload,dict) and isinstance(payload.get('a'),dict) else {})['capsule']; b=normalize_context_capsule(payload.get('b') if isinstance(payload,dict) and isinstance(payload.get('b'),dict) else {})['capsule']
    fam=sorted(set(a['context'])|set(b['context'])); changed=[k for k in fam if a['context'].get(k)!=b['context'].get(k)]
    return {'ok':True,'version':VERSION,'changed_families':changed,'changed_count':len(changed),'scientific_difference_inferred':False}
def context_snapshot(payload):
    cap=normalize_context_capsule(payload)['capsule']; return {'ok':True,'version':VERSION,'snapshot':{'schema':SNAPSHOT_SCHEMA,'snapshot_ref':f'context-snapshot:{_hash(cap)[:16]}','capsule':cap,'immutable_reference_snapshot':True}}
def build_snapshot(payload):
    comp=normalize_comparison_set(payload.get('comparison'))['comparison'] if isinstance(payload,dict) and isinstance(payload.get('comparison'),dict) else None
    cap=normalize_context_capsule(payload.get('context') if isinstance(payload,dict) and isinstance(payload.get('context'),dict) else {})['capsule']
    snap={'schema':SNAPSHOT_SCHEMA,'snapshot_ref':str(payload.get('snapshot_ref') or f'snapshot:{_hash(payload)[:16]}')[:500],'comparison':comp,'context':cap,'pins':_list(payload.get('pins'),'pins',MAX_PINS) if isinstance(payload,dict) else [],'scientific_record_mutated':False}
    snap['snapshot_hash']=_hash(snap); return {'ok':True,'version':VERSION,'snapshot':snap}
def restore_snapshot(payload):
    snap=payload.get('snapshot') if isinstance(payload,dict) else None
    if not isinstance(snap,dict): raise ScientificSceneLinkingComparativeContextError('snapshot must be an object.')
    return {'ok':True,'version':VERSION,'snapshot_ref':snap.get('snapshot_ref'),'restore_plan':{'comparison':copy.deepcopy(snap.get('comparison')),'context':copy.deepcopy(snap.get('context')),'pins':copy.deepcopy(snap.get('pins') or [])},'scientific_record_mutated':False}
def audit_context_integrity(payload):
    cap=normalize_context_capsule(payload)['capsule']; return {'ok':True,'version':VERSION,'context_hash':cap['context_hash'],'family_count':len(cap['context_families']),'authoritative':False,'integrity_ok':True}
def export_plan(payload): return {'ok':True,'version':VERSION,'formats':['json','snapshot-json','research-package-reference'],'include_scientific_values_by_reference_only':True,'automatic_publication':False}
def handoff_plan(payload): return {'ok':True,'version':VERSION,'handoff_kind':'scientific-scene-comparative-context','target_products':['Platform Core','Workspace','Decision Studio'],'reference_first':True,'automatic_handoff':False}
def core_object_plan(payload): return {'ok':True,'version':VERSION,'core_object_type':'visual-research-context','reference_first':True,'requires_explicit_submission':True,'automatic_core_submission':False}
def interpretation_boundaries_report(payload=None):
    return {'ok':True,'version':VERSION,'infer_equivalence':False,'infer_joins':False,'infer_causality':False,'weight_evidence':False,'change_claim_status':False,'certify_scientific_validity':False,'determine_truth':False,'automatic_core_submission':False}
def readiness_report(payload=None):
    return {'ok':True,'version':VERSION,'ready':True,'cross_scene_linking':True,'comparative_inspection':True,'context_preservation':True,'retains_v01354':True,'retains_v01353':True,'retains_v01352':True,'boundaries':interpretation_boundaries_report()}
