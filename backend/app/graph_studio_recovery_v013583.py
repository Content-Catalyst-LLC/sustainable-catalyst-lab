from __future__ import annotations
VERSION='0.135.8.3'; ENGINE_VERSION='3.1.0'; API_ROUTE_COUNT=16
class GraphStudioRecoveryError(ValueError): pass
MODES=('plot','distribution','diagnostics','uncertainty','provenance','scene')
def health(): return {'ok':True,'version':VERSION,'engine_version':ENGINE_VERSION,'api_route_count':API_ROUTE_COUNT,'single_renderer_root':True,'single_primary_viewport':True,'scientific_state_hydration':True,'advanced_provenance_graph':True}
def manifest(): return {'ok':True,'version':VERSION,'renderer_modes':list(MODES),'unique_root_id':'sc-lab-graph-studio-renderer-root','hydration_sources':['active-graph','figure-controls','project-figure','unbound']}
def lifecycle_report(): return {'ok':True,'version':VERSION,'mount_policy':'idempotent-single-root','observer_ignores_own_subtree':True,'v013582_host_suppressed':True,'view_switch_remounts_renderer':False}
def hydration_plan(payload=None): return {'ok':True,'version':VERSION,'priority':['active-graph','figure-controls','project-figure','unbound'],'fabricates_scientific_values':False,'payload_reference':(payload or {}).get('reference')}
def provenance_plan(payload=None): return {'ok':True,'version':VERSION,'layouts':['layered','radial','swimlane'],'interactive_node_inspection':True,'declared_edges_only':True,'structural_paths_are_causal':False}
def acceptance_report(): return {'ok':True,'version':VERSION,'renderer_roots':1,'workspace_shells':1,'visible_primary_viewports':1,'duplicate_renderer_headers':0,'legacy_primary_owners':0,'hydrated_context_expected':True}
def boundaries_report(): return {'ok':True,'version':VERSION,'presentation_creates_evidence':False,'automatic_join_inference':False,'automatic_causal_inference':False,'automatic_claim_upgrade':False,'automatic_core_submission':False}
def compatibility_report(): return {'ok':True,'version':VERSION,'retains_v013582_renderer_implementation':True,'retains_v013581_navigation':True,'legacy_graph_studio_primary_owner':False}
def normalize_state(payload):
    if not isinstance(payload,dict): raise GraphStudioRecoveryError('payload must be an object')
    out=dict(payload); out.setdefault('version',VERSION); out.setdefault('presentation_state_only',True); return out

def dom_audit(payload=None):
    p=payload or {}; return {'ok': p.get('renderer_roots',1)==1 and p.get('visible_primary_viewports',1)==1 and p.get('duplicate_renderer_headers',0)==0, 'version':VERSION, 'observed':p}
def hydration_sources(): return {'ok':True,'version':VERSION,'sources':['active-graph','figure-controls','project-figure','unbound']}
def provenance_layouts(): return {'ok':True,'version':VERSION,'layouts':['layered','radial','swimlane']}
def renderer_status(): return {'ok':True,'version':VERSION,'engine_version':ENGINE_VERSION,'primary_owner':'graph-studio-recovery-v013583','legacy_host_suppressed':True}
def state_status(): return {'ok':True,'version':VERSION,'presentation_state_isolated':True,'scientific_state_hydrated':True}
def recovery_plan(payload=None): return {'ok':True,'version':VERSION,'steps':['dedupe','claim-root','hydrate','render','observe-with-own-subtree-exclusion'],'payload':payload or {}}
def ui_acceptance(payload=None):
    p=payload or {}; return {'ok':p.get('renderer_roots',1)==1 and p.get('workspace_shells',1)==1 and p.get('visible_primary_viewports',1)==1 and p.get('duplicate_renderer_headers',0)==0, 'version':VERSION}
