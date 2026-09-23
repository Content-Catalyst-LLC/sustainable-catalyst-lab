from __future__ import annotations
import copy, json
from hashlib import sha256

VERSION='0.135.7'; ENGINE_VERSION='16.7.0'
SCHEMA='sc-lab-visual-research-narrative-findings/0.135.7'
PACKAGE_SCHEMA='sc-lab-visual-research-publication-package/0.135.7'
BLOCK_TYPES={'figure','finding','method','evidence','uncertainty','limitation','provenance','comparison','scene','table','citation','appendix'}
FINDING_STATES={'draft','supported','contested','withdrawn','ready-for-review'}
HANDOFF_TARGETS={'platform-core','publication-studio','knowledge-library','workspace'}
CITATION_MODES={'reference-only','snapshot-bound','manifest-bound'}
MAX_BLOCKS=512; MAX_REFS=10000; MAX_TEXT=20000

class VisualResearchNarrativeFindingsError(ValueError):
    def __init__(self, detail, status_code=400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _meta(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v,label,limit):
    if v is None: return []
    if not isinstance(v,list): raise VisualResearchNarrativeFindingsError(f'{label} must be an array.')
    if len(v)>limit: raise VisualResearchNarrativeFindingsError(f'{label} exceeds configured maximum of {limit}.')
    return copy.deepcopy(v)
def _text(v,limit=MAX_TEXT): return str(v or '')[:limit]
def _req(v,label):
    s=str(v or '').strip()
    if not s: raise VisualResearchNarrativeFindingsError(f'{label} is required.')
    return s[:500]

def schema_info():
    return {'ok':True,'version':VERSION,'engine_version':ENGINE_VERSION,'schema':SCHEMA,'package_schema':PACKAGE_SCHEMA,
            'block_types':sorted(BLOCK_TYPES),'finding_states':sorted(FINDING_STATES),'handoff_targets':sorted(HANDOFF_TARGETS),'citation_modes':sorted(CITATION_MODES),
            'limits':{'blocks':MAX_BLOCKS,'refs':MAX_REFS,'text':MAX_TEXT}}
def catalog():
    return {'ok':True,'version':VERSION,'block_types':sorted(BLOCK_TYPES),'block_type_count':len(BLOCK_TYPES),'finding_states':sorted(FINDING_STATES),'finding_state_count':len(FINDING_STATES),
            'handoff_targets':sorted(HANDOFF_TARGETS),'handoff_target_count':len(HANDOFF_TARGETS),'citation_modes':sorted(CITATION_MODES),'citation_mode_count':len(CITATION_MODES),
            'narrative_is_not_scientific_claim':True,'finding_status_is_declared_not_certified':True,'presentation_cannot_upgrade_claim_status':True,
            'automatic_evidence_weighting':False,'automatic_truth_determination':False,'automatic_core_submission':False,'automatic_publication':False}
def manifest():
    return {'ok':True,'status':'visual-research-narrative-findings-ready','version':VERSION,'engine_version':ENGINE_VERSION,
            'governed_visual_narratives':True,'finding_reference_objects':True,'citation_binding':True,'publication_handoff':True,'reproducible_session_bridge':True,
            'v01356_session_bridge':True,'v01355_context_bridge':True,'v01354_scene_bridge':True,'v01353_canvas_bridge':True,'v01352_graph_bridge':True,
            'platform_core_reference_bridge':True,'publication_studio_bridge':True,'knowledge_library_bridge':True,'workspace_bridge':True,
            'presentation_creates_scientific_claims':False,'automatic_evidence_weighting':False,'automatic_truth_determination':False,'automatic_core_submission':False}
def health():
    return {**manifest(),'schema':SCHEMA,'block_type_count':12,'finding_state_count':5,'handoff_target_count':4,'citation_mode_count':3,'api_route_count':56}

def normalize_narrative(payload):
    if not isinstance(payload,dict): raise VisualResearchNarrativeFindingsError('payload must be an object.')
    blocks=_list(payload.get('blocks'),'blocks',MAX_BLOCKS)
    n={'narrative_ref':str(payload.get('narrative_ref') or f"visual-narrative:{_hash(payload)[:16]}")[:500],
       'title':_text(payload.get('title'),1000),'project_ref':payload.get('project_ref'),'study_ref':payload.get('study_ref'),'session_ref':payload.get('session_ref'),
       'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),'blocks':blocks,'metadata':_meta(payload.get('metadata')),
       'presentation_is_scientific_claim':False,'reference_first':True}
    n['narrative_hash']=_hash(n); return {'ok':True,'version':VERSION,'narrative':n}
def create_narrative(payload): return {**normalize_narrative(payload),'created':True,'scientific_record_mutated':False}
def clone_narrative(payload):
    n=normalize_narrative(payload)['narrative']; n['parent_narrative_ref']=n['narrative_ref']; n['narrative_ref']=str(payload.get('clone_ref') or f"visual-narrative:{_hash({'parent':n['parent_narrative_ref'],'payload':payload})[:16]}")[:500]; n['narrative_hash']=_hash(n)
    return {'ok':True,'version':VERSION,'narrative':n,'scientific_record_mutated':False}
def reorder_narrative(payload):
    refs=_list(payload.get('block_refs') if isinstance(payload,dict) else None,'block_refs',MAX_BLOCKS)
    return {'ok':True,'version':VERSION,'block_refs':refs,'presentation_order_only':True,'scientific_record_mutated':False}

def normalize_block(payload):
    if not isinstance(payload,dict): raise VisualResearchNarrativeFindingsError('payload must be an object.')
    kind=str(payload.get('block_type') or '').lower()
    if kind not in BLOCK_TYPES: raise VisualResearchNarrativeFindingsError('block_type invalid.')
    b={'block_ref':str(payload.get('block_ref') or f"narrative-block:{_hash(payload)[:16]}")[:500],'block_type':kind,'title':_text(payload.get('title'),1000),'text':_text(payload.get('text')),
       'object_ref':payload.get('object_ref'),'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),'metadata':_meta(payload.get('metadata')),
       'presentation_block':True,'scientific_assertion_created':False}; b['block_hash']=_hash(b)
    return {'ok':True,'version':VERSION,'block':b}
def add_block(payload): return {**normalize_block(payload),'operation':'add','scientific_record_mutated':False}
def update_block(payload): return {**normalize_block(payload),'operation':'update-presentation','scientific_record_mutated':False}
def remove_block(payload): return {'ok':True,'version':VERSION,'block_ref':_req(payload.get('block_ref') if isinstance(payload,dict) else None,'block_ref'),'operation':'remove-from-narrative','source_object_deleted':False}
def list_blocks(payload):
    blocks=[normalize_block(x)['block'] for x in _list(payload.get('blocks') if isinstance(payload,dict) else None,'blocks',MAX_BLOCKS)]
    return {'ok':True,'version':VERSION,'blocks':blocks,'block_count':len(blocks)}

def _ref_plan(payload,kind): return {'ok':True,'version':VERSION,'kind':kind,'reference':_meta(payload),'reference_first':True,'scientific_record_mutated':False}
def bind_figure(payload): return _ref_plan(payload,'figure-binding')
def snapshot_figure(payload):
    r=_ref_plan(payload,'figure-snapshot'); r['snapshot_hash']=_hash(r['reference']); r['snapshot_certifies_scientific_validity']=False; return r
def caption_figure(payload): return {'ok':True,'version':VERSION,'caption':_text(payload.get('caption') if isinstance(payload,dict) else ''),'caption_is_scientific_claim':False}
def alt_text_figure(payload): return {'ok':True,'version':VERSION,'alt_text':_text(payload.get('alt_text') if isinstance(payload,dict) else ''),'accessibility_text_is_scientific_claim':False}

def normalize_finding(payload):
    if not isinstance(payload,dict): raise VisualResearchNarrativeFindingsError('payload must be an object.')
    state=str(payload.get('finding_state') or 'draft').lower()
    if state not in FINDING_STATES: raise VisualResearchNarrativeFindingsError('finding_state invalid.')
    f={'finding_ref':str(payload.get('finding_ref') or f"finding:{_hash(payload)[:16]}")[:500],'finding_state':state,'statement':_text(payload.get('statement')),
       'evidence_refs':_list(payload.get('evidence_refs'),'evidence_refs',MAX_REFS),'uncertainty_refs':_list(payload.get('uncertainty_refs'),'uncertainty_refs',MAX_REFS),
       'limitation_refs':_list(payload.get('limitation_refs'),'limitation_refs',MAX_REFS),'provenance_refs':_list(payload.get('provenance_refs'),'provenance_refs',MAX_REFS),
       'status_is_declared_not_certified':True,'truth_determined':False,'evidence_weighted_automatically':False}; f['finding_hash']=_hash(f)
    return {'ok':True,'version':VERSION,'finding':f}
def create_finding(payload): return {**normalize_finding(payload),'created':True,'automatic_claim_creation':False}
def set_finding_status(payload):
    f=normalize_finding(payload)['finding']; return {'ok':True,'version':VERSION,'finding':f,'status_change_requires_explicit_user_action':True,'status_certified':False}
def link_finding_evidence(payload): return _ref_plan(payload,'finding-evidence-link')
def link_finding_uncertainty(payload): return _ref_plan(payload,'finding-uncertainty-link')
def link_finding_limitation(payload): return _ref_plan(payload,'finding-limitation-link')

def normalize_annotation(payload):
    if not isinstance(payload,dict): raise VisualResearchNarrativeFindingsError('payload must be an object.')
    a={'annotation_ref':str(payload.get('annotation_ref') or f"annotation:{_hash(payload)[:16]}")[:500],'target_ref':payload.get('target_ref'),'text':_text(payload.get('text')),
       'author_ref':payload.get('author_ref'),'metadata':_meta(payload.get('metadata')),'annotation_is_evidence':False,'annotation_is_claim':False}; a['annotation_hash']=_hash(a)
    return {'ok':True,'version':VERSION,'annotation':a}
def add_annotation(payload): return {**normalize_annotation(payload),'added':True,'scientific_record_mutated':False}
def resolve_annotation(payload): return {'ok':True,'version':VERSION,'annotation_ref':_req(payload.get('annotation_ref') if isinstance(payload,dict) else None,'annotation_ref'),'resolved_for_workflow':True,'scientific_conclusion_changed':False}

def normalize_citation(payload):
    if not isinstance(payload,dict): raise VisualResearchNarrativeFindingsError('payload must be an object.')
    mode=str(payload.get('citation_mode') or 'reference-only').lower()
    if mode not in CITATION_MODES: raise VisualResearchNarrativeFindingsError('citation_mode invalid.')
    c={'citation_ref':str(payload.get('citation_ref') or f"citation:{_hash(payload)[:16]}")[:500],'citation_mode':mode,'source_ref':payload.get('source_ref'),'snapshot_ref':payload.get('snapshot_ref'),'manifest_ref':payload.get('manifest_ref'),'metadata':_meta(payload.get('metadata')),'reference_first':True}; c['citation_hash']=_hash(c)
    return {'ok':True,'version':VERSION,'citation':c}
def citation_plan(payload): return {**normalize_citation(payload),'plan_only':True,'automatic_source_resolution':False}
def validate_citation(payload):
    c=normalize_citation(payload)['citation']; valid=bool(c.get('source_ref')) and (c['citation_mode']=='reference-only' or bool(c.get('snapshot_ref') or c.get('manifest_ref')))
    return {'ok':True,'version':VERSION,'valid':valid,'citation':c,'scientific_validity_certified':False}

def context_provenance(payload): return _ref_plan(payload,'provenance-context')
def context_evidence(payload): return _ref_plan(payload,'evidence-context')
def context_uncertainty(payload): return _ref_plan(payload,'uncertainty-context')
def context_diagnostics(payload): return _ref_plan(payload,'diagnostics-context')
def context_session(payload): return _ref_plan(payload,'v0.135.6-session-context')
def context_scene(payload): return _ref_plan(payload,'v0.135.4-scene-context')
def context_canvas(payload): return _ref_plan(payload,'v0.135.3-canvas-context')
def context_comparison(payload): return _ref_plan(payload,'v0.135.5-comparison-context')

def publication_outline(payload): return {'ok':True,'version':VERSION,'sections':_list(payload.get('sections') if isinstance(payload,dict) else None,'sections',128),'outline_is_presentation_structure':True}
def publication_section(payload): return {'ok':True,'version':VERSION,'section_ref':str(payload.get('section_ref') or f"section:{_hash(payload)[:16]}")[:500],'title':_text(payload.get('title'),1000),'block_refs':_list(payload.get('block_refs'),'block_refs',MAX_BLOCKS),'scientific_claims_created':False}
def publication_figure_table(payload): return {'ok':True,'version':VERSION,'entries':_list(payload.get('entries') if isinstance(payload,dict) else None,'entries',MAX_BLOCKS),'reference_first':True}
def publication_appendix(payload): return {'ok':True,'version':VERSION,'appendix_blocks':_list(payload.get('blocks') if isinstance(payload,dict) else None,'blocks',MAX_BLOCKS),'reference_first':True}
def publication_abstract(payload): return {'ok':True,'version':VERSION,'abstract':_text(payload.get('abstract') if isinstance(payload,dict) else ''),'abstract_is_authored_text':True,'automatic_claim_creation':False}
def publication_readiness(payload): return {'ok':True,'version':VERSION,'ready_for_handoff':bool(payload.get('explicit_review_complete',False)) if isinstance(payload,dict) else False,'requires_explicit_human_review':True,'scientific_validity_certified':False}

def handoff_plan(payload):
    target=str(payload.get('target') or 'platform-core').lower() if isinstance(payload,dict) else 'platform-core'
    if target not in HANDOFF_TARGETS: raise VisualResearchNarrativeFindingsError('target invalid.')
    return {'ok':True,'version':VERSION,'target':target,'handoff_kind':'visual-research-narrative','reference_first':True,'requires_explicit_submission':True,'automatic_handoff':False}
def handoff_core(payload): return {**handoff_plan({**(payload if isinstance(payload,dict) else {}),'target':'platform-core'}),'core_object_type':'visual-research-narrative','automatic_core_submission':False}
def handoff_publication(payload): return {**handoff_plan({**(payload if isinstance(payload,dict) else {}),'target':'publication-studio'}),'automatic_publication':False}
def handoff_library(payload): return {**handoff_plan({**(payload if isinstance(payload,dict) else {}),'target':'knowledge-library'}),'automatic_library_publication':False}
def handoff_workspace(payload): return {**handoff_plan({**(payload if isinstance(payload,dict) else {}),'target':'workspace'}),'automatic_workspace_mutation':False}

def export_plan(payload): return {'ok':True,'version':VERSION,'formats':['json','markdown','publication-handoff-json','reference-manifest-json'],'reference_first':True,'automatic_publication':False}
def export_package(payload):
    n=normalize_narrative(payload.get('narrative') if isinstance(payload,dict) and isinstance(payload.get('narrative'),dict) else {})['narrative']; pkg={'schema':PACKAGE_SCHEMA,'narrative':n,'finding_refs':_list(payload.get('finding_refs'),'finding_refs',MAX_REFS) if isinstance(payload,dict) else [],'citation_refs':_list(payload.get('citation_refs'),'citation_refs',MAX_REFS) if isinstance(payload,dict) else [],'reference_first':True,'automatic_publication':False}; pkg['package_hash']=_hash(pkg); return {'ok':True,'version':VERSION,'package':pkg}
def export_manifest(payload):
    p=export_package(payload)['package']; return {'ok':True,'version':VERSION,'manifest':{'package_hash':p['package_hash'],'narrative_ref':p['narrative']['narrative_ref'],'finding_refs':p['finding_refs'],'citation_refs':p['citation_refs'],'scientific_validity_certified':False}}

def guard_claims(payload): return {'ok':True,'version':VERSION,'presentation_creates_claims':False,'captions_create_claims':False,'annotations_create_claims':False,'finding_status_requires_explicit_declaration':True}
def guard_evidence(payload): return {'ok':True,'version':VERSION,'automatic_evidence_weighting':False,'evidence_context_is_reference_only':True,'presentation_changes_evidence_strength':False}
def guard_presentation(payload): return {'ok':True,'version':VERSION,'presentation_state_only':True,'source_science_mutated':False,'scientific_conclusion_changed':False}
def guard_references(payload):
    refs=_list(payload.get('refs') if isinstance(payload,dict) else None,'refs',MAX_REFS); return {'ok':True,'version':VERSION,'explicit_reference_count':len(refs),'implicit_reference_resolution':False,'refs':refs}
def interpretation_boundaries_report(payload=None): return {'ok':True,'version':VERSION,'narrative_is_scientific_claim':False,'caption_is_scientific_claim':False,'annotation_is_evidence':False,'presentation_can_upgrade_finding_status':False,'weight_evidence':False,'change_claim_status_automatically':False,'certify_scientific_validity':False,'determine_truth':False,'automatic_core_submission':False,'automatic_publication':False}
