from __future__ import annotations
from copy import deepcopy

VERSION='0.135.8.1'
ENGINE_VERSION='2.6.0'
SCHEMA='sc-lab-graph-studio-canonical-runtime/0.135.8.1'
VIEWS=('figure','analysis','provenance','scene','compare','session','narrative','review')
CAPABILITIES=('binding','adaptive','scene-engine','state','linked','spatial','markup','uncertainty','provenance','gpu','webgl2','webgpu','advanced3d')

class GraphStudioCanonicalRuntimeError(ValueError):
    def __init__(self,detail:str,status_code:int=400): super().__init__(detail); self.detail=detail; self.status_code=status_code

def health():
    return {'ok':True,'status':'graph-studio-canonical-runtime-ready','version':VERSION,'engine_version':ENGINE_VERSION,'schema':SCHEMA,'canonical_view_count':len(VIEWS),'isolated_capability_panel_count':len(CAPABILITIES),'single_active_research_view':True,'legacy_capability_adapters_quarantined':True,'presentation_state_separated':True,'scientific_mutation_from_navigation':False,'api_route_count':16}

def manifest():
    return {'ok':True,'version':VERSION,'canonical_owner':'graph-studio-canonical-runtime','canonical_views':list(VIEWS),'capability_adapters':list(CAPABILITIES),'retains_visual_stack':['0.135.1','0.135.2','0.135.3','0.135.4','0.135.5','0.135.6','0.135.7','0.135.8'],'historical_controls_default_collapsed':True}

def catalog(): return {'view_count':len(VIEWS),'capability_panel_count':len(CAPABILITIES),'views':list(VIEWS),'capabilities':list(CAPABILITIES),'default_view':'figure'}
def schema_info(): return {'schema':SCHEMA,'view_state':'presentation-only','scientific_objects':'reference-first','automatic_scientific_inference':False}
def _obj(payload):
    if payload is None:return {}
    if not isinstance(payload,dict):raise GraphStudioCanonicalRuntimeError('Payload must be an object.')
    return deepcopy(payload)
def normalize_runtime(payload):
    p=_obj(payload);v=str(p.get('active_view') or 'figure').strip().lower();
    if v not in VIEWS: raise GraphStudioCanonicalRuntimeError('Unknown canonical Graph Studio view.')
    return {'ok':True,'version':VERSION,'active_view':v,'presentation_state_only':True,'mutates_science':False}
def verify_runtime(payload):
    p=_obj(payload); visible=p.get('visible_views',[])
    if not isinstance(visible,list): raise GraphStudioCanonicalRuntimeError('visible_views must be an array.')
    duplicates=[x for x in visible if visible.count(x)>1]
    return {'ok':len(visible)<=1 and not duplicates,'visible_view_count':len(visible),'single_active_view':len(visible)<=1,'duplicate_view_ids':sorted(set(duplicates))}
def normalize_view(payload): return normalize_runtime({'active_view':_obj(payload).get('view','figure')})
def activate_view(payload): return normalize_view(payload)
def lifecycle_plan(payload):
    p=_obj(payload);return {'ok':True,'from_view':p.get('from_view'),'to_view':p.get('to_view','figure'),'actions':['preserve-scientific-objects','suspend-presentation-listeners','activate-single-view','restore-presentation-state'],'destroy_scientific_objects':False}
def normalize_capability(payload):
    p=_obj(payload);cap=str(p.get('capability') or '').strip().lower()
    if cap not in CAPABILITIES: raise GraphStudioCanonicalRuntimeError('Unknown capability adapter.')
    return {'ok':True,'capability':cap,'presentation_role':'adapter','primary_renderer_owner':False}
def isolate_capability(payload):
    x=normalize_capability(payload);x.update({'isolated':True,'default_visible':False});return x
def asset_plan(payload):
    _obj(payload);return {'ok':True,'canonical_assets':['graph-studio-canonical-runtime-v013581.js','sc-lab-graph-studio-canonical-runtime-v013581.css'],'legacy_capability_assets':'retained-as-adapters','duplicate-primary-renderer_owner':False}
def asset_audit(payload):
    p=_obj(payload);owners=p.get('primary_renderer_owners',[])
    if not isinstance(owners,list): raise GraphStudioCanonicalRuntimeError('primary_renderer_owners must be an array.')
    return {'ok':len(owners)<=1,'primary_renderer_owner_count':len(owners),'owners':owners}
def identity_report(payload):
    _obj(payload);return {'ok':True,'release_version':VERSION,'runtime_subsystem_version':'0.26.3.1','display_identity':f'Lab {VERSION} · graph-studio · canonical runtime','public_release_identity_authoritative':True}
def dom_audit(payload):
    p=_obj(payload);return {'ok':True,'visible_research_views':int(p.get('visible_research_views',1)),'duplicate_primary_canvases':int(p.get('duplicate_primary_canvases',0)),'pass_single_view':int(p.get('visible_research_views',1))<=1,'pass_no_duplicate_primary_canvas':int(p.get('duplicate_primary_canvases',0))==0}
def boundaries_report(payload=None):
    _obj(payload or {});return {'presentation_state_is_scientific_record':False,'navigation_creates_claims':False,'review_ui_creates_evidence':False,'automatic_scientific_inference':False,'automatic_core_submission':False,'legacy_adapter_becomes_primary_renderer':False}
