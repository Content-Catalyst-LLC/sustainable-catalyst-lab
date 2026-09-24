from __future__ import annotations
import copy, json
from hashlib import sha256

VERSION='0.135.8'; ENGINE_VERSION='16.8.0'
SCHEMA='sc-lab-research-review-critique-revision-lineage/0.135.8'
PACKAGE_SCHEMA='sc-lab-review-revision-package/0.135.8'
REVIEW_STATES={'draft','open','response-requested','revision-requested','resolved','closed'}
CRITIQUE_TYPES={'question','critique','suggestion','limitation','evidence-request','reproducibility','methodology','interpretation'}
RESPONSE_STATES={'draft','addressed','partially-addressed','disputed','deferred'}
DECISION_STATES={'no-decision','accept-for-handoff','revise','contested','withdraw'}
REVISION_KINDS={'narrative','figure','finding-reference','method','package'}
HANDOFF_TARGETS={'platform-core','publication-studio','knowledge-library','workspace','replication-studio'}
MAX_ITEMS=1024; MAX_REFS=10000; MAX_TEXT=20000

class ResearchReviewCritiqueRevisionError(ValueError):
    def __init__(self, detail, status_code=400):
        super().__init__(detail); self.detail=detail; self.status_code=status_code

def _stable(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _meta(v): return copy.deepcopy(v) if isinstance(v,dict) else {}
def _list(v,label,limit=MAX_ITEMS):
    if v is None: return []
    if not isinstance(v,list): raise ResearchReviewCritiqueRevisionError(f'{label} must be an array.')
    if len(v)>limit: raise ResearchReviewCritiqueRevisionError(f'{label} exceeds configured maximum of {limit}.')
    return copy.deepcopy(v)
def _text(v,limit=MAX_TEXT): return str(v or '')[:limit]
def _req(v,label):
    s=str(v or '').strip()
    if not s: raise ResearchReviewCritiqueRevisionError(f'{label} is required.')
    return s[:500]

def schema_info():
    return {'ok':True,'version':VERSION,'engine_version':ENGINE_VERSION,'schema':SCHEMA,'package_schema':PACKAGE_SCHEMA,
            'review_states':sorted(REVIEW_STATES),'critique_types':sorted(CRITIQUE_TYPES),'response_states':sorted(RESPONSE_STATES),
            'decision_states':sorted(DECISION_STATES),'revision_kinds':sorted(REVISION_KINDS),'handoff_targets':sorted(HANDOFF_TARGETS),
            'limits':{'items':MAX_ITEMS,'refs':MAX_REFS,'text':MAX_TEXT}}
def catalog():
    return {'ok':True,'version':VERSION,'review_states':sorted(REVIEW_STATES),'review_state_count':len(REVIEW_STATES),
            'critique_types':sorted(CRITIQUE_TYPES),'critique_type_count':len(CRITIQUE_TYPES),
            'response_states':sorted(RESPONSE_STATES),'response_state_count':len(RESPONSE_STATES),
            'decision_states':sorted(DECISION_STATES),'decision_state_count':len(DECISION_STATES),
            'revision_kinds':sorted(REVISION_KINDS),'revision_kind_count':len(REVISION_KINDS),
            'handoff_targets':sorted(HANDOFF_TARGETS),'handoff_target_count':len(HANDOFF_TARGETS),
            'review_is_not_scientific_certification':True,'reviewer_comments_are_not_evidence':True,'revision_does_not_upgrade_claim_status':True,
            'automatic_acceptance':False,'automatic_evidence_weighting':False,'automatic_truth_determination':False,'automatic_core_submission':False}
def manifest():
    return {'ok':True,'status':'research-review-critique-revision-lineage-ready','version':VERSION,'engine_version':ENGINE_VERSION,
            'governed_review_packages':True,'critique_response_lineage':True,'revision_diff_lineage':True,'replication_reference_bridge':True,
            'v01357_narrative_bridge':True,'v01356_session_bridge':True,'workspace_review_bridge':True,'replication_studio_bridge':True,
            'platform_core_reference_bridge':True,'publication_studio_bridge':True,'knowledge_library_bridge':True,
            'review_creates_scientific_certification':False,'automatic_acceptance':False,'automatic_core_submission':False}
def health():
    return {**manifest(),'schema':SCHEMA,'review_state_count':6,'critique_type_count':8,'response_state_count':5,
            'decision_state_count':5,'revision_kind_count':5,'handoff_target_count':5,'api_route_count':60}

def normalize_review(payload):
    if not isinstance(payload,dict): raise ResearchReviewCritiqueRevisionError('payload must be an object.')
    state=str(payload.get('review_state') or 'draft').lower()
    if state not in REVIEW_STATES: raise ResearchReviewCritiqueRevisionError('review_state invalid.')
    r={'review_ref':str(payload.get('review_ref') or f"review:{_hash(payload)[:16]}")[:500],
       'review_state':state,'title':_text(payload.get('title'),1000),'narrative_ref':payload.get('narrative_ref'),
       'package_ref':payload.get('package_ref'),'reviewer_refs':_list(payload.get('reviewer_refs'),'reviewer_refs',MAX_REFS),
       'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),'metadata':_meta(payload.get('metadata')),
       'review_is_scientific_certification':False,'reference_first':True}
    r['review_hash']=_hash(r); return {'ok':True,'version':VERSION,'review':r}
def create_review(payload): return {**normalize_review(payload),'created':True,'scientific_record_mutated':False}
def clone_review(payload):
    r=normalize_review(payload)['review']; r['parent_review_ref']=r['review_ref']; r['review_ref']=str(payload.get('clone_ref') or f"review:{_hash({'parent':r['parent_review_ref'],'payload':payload})[:16]}")[:500]; r['review_hash']=_hash(r)
    return {'ok':True,'version':VERSION,'review':r,'scientific_record_mutated':False}
def open_review(payload):
    r=normalize_review({**payload,'review_state':'open'})['review']; return {'ok':True,'version':VERSION,'review':r,'opened_for_workflow':True,'scientific_certification_created':False}
def close_review(payload):
    r=normalize_review({**payload,'review_state':'closed'})['review']; return {'ok':True,'version':VERSION,'review':r,'closed_for_workflow':True,'scientific_conclusion_changed':False}

def normalize_item(payload):
    if not isinstance(payload,dict): raise ResearchReviewCritiqueRevisionError('payload must be an object.')
    item={'item_ref':str(payload.get('item_ref') or f"review-item:{_hash(payload)[:16]}")[:500],
          'target_ref':payload.get('target_ref'),'text':_text(payload.get('text')),'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),
          'metadata':_meta(payload.get('metadata')),'review_item_is_evidence':False,'scientific_assertion_created':False}; item['item_hash']=_hash(item)
    return {'ok':True,'version':VERSION,'item':item}
def add_item(payload): return {**normalize_item(payload),'operation':'add','scientific_record_mutated':False}
def update_item(payload): return {**normalize_item(payload),'operation':'update-review-workflow','scientific_record_mutated':False}
def resolve_item(payload): return {'ok':True,'version':VERSION,'item_ref':_req(payload.get('item_ref') if isinstance(payload,dict) else None,'item_ref'),'resolved_for_workflow':True,'scientific_conclusion_changed':False}
def list_items(payload):
    items=[normalize_item(x)['item'] for x in _list(payload.get('items') if isinstance(payload,dict) else None,'items')]
    return {'ok':True,'version':VERSION,'items':items,'item_count':len(items)}

def normalize_critique(payload):
    if not isinstance(payload,dict): raise ResearchReviewCritiqueRevisionError('payload must be an object.')
    kind=str(payload.get('critique_type') or 'critique').lower()
    if kind not in CRITIQUE_TYPES: raise ResearchReviewCritiqueRevisionError('critique_type invalid.')
    c={'critique_ref':str(payload.get('critique_ref') or f"critique:{_hash(payload)[:16]}")[:500],'critique_type':kind,
       'target_ref':payload.get('target_ref'),'text':_text(payload.get('text')),'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),
       'reviewer_ref':payload.get('reviewer_ref'),'metadata':_meta(payload.get('metadata')),'critique_is_evidence':False,'critique_is_claim':False}
    c['critique_hash']=_hash(c); return {'ok':True,'version':VERSION,'critique':c}
def add_critique(payload): return {**normalize_critique(payload),'added':True,'scientific_record_mutated':False}
def classify_critique(payload): return {**normalize_critique(payload),'classification_declared_not_inferred':True}
def link_critique_target(payload): return _ref_plan(payload,'critique-target-link')
def resolve_critique(payload): return {'ok':True,'version':VERSION,'critique_ref':_req(payload.get('critique_ref') if isinstance(payload,dict) else None,'critique_ref'),'resolved_for_workflow':True,'truth_determined':False}

def normalize_response(payload):
    if not isinstance(payload,dict): raise ResearchReviewCritiqueRevisionError('payload must be an object.')
    state=str(payload.get('response_state') or 'draft').lower()
    if state not in RESPONSE_STATES: raise ResearchReviewCritiqueRevisionError('response_state invalid.')
    r={'response_ref':str(payload.get('response_ref') or f"response:{_hash(payload)[:16]}")[:500],'response_state':state,
       'critique_ref':payload.get('critique_ref'),'text':_text(payload.get('text')),'revision_refs':_list(payload.get('revision_refs'),'revision_refs',MAX_REFS),
       'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),'metadata':_meta(payload.get('metadata')),
       'response_resolves_science_automatically':False}; r['response_hash']=_hash(r)
    return {'ok':True,'version':VERSION,'response':r}
def add_response(payload): return {**normalize_response(payload),'added':True,'scientific_record_mutated':False}
def update_response(payload): return {**normalize_response(payload),'operation':'update-review-response','scientific_record_mutated':False}
def set_response_status(payload): return {**normalize_response(payload),'status_requires_explicit_user_action':True,'scientific_conclusion_changed':False}

def normalize_revision(payload):
    if not isinstance(payload,dict): raise ResearchReviewCritiqueRevisionError('payload must be an object.')
    kind=str(payload.get('revision_kind') or 'package').lower()
    if kind not in REVISION_KINDS: raise ResearchReviewCritiqueRevisionError('revision_kind invalid.')
    r={'revision_ref':str(payload.get('revision_ref') or f"revision:{_hash(payload)[:16]}")[:500],'revision_kind':kind,
       'parent_ref':payload.get('parent_ref'),'new_ref':payload.get('new_ref'),'response_refs':_list(payload.get('response_refs'),'response_refs',MAX_REFS),
       'changed_paths':_list(payload.get('changed_paths'),'changed_paths',MAX_ITEMS),'metadata':_meta(payload.get('metadata')),
       'revision_upgrades_claim_status':False}; r['revision_hash']=_hash(r)
    return {'ok':True,'version':VERSION,'revision':r}
def create_revision(payload): return {**normalize_revision(payload),'created':True,'scientific_record_mutated':False}
def revision_diff(payload):
    before=_meta(payload.get('before') if isinstance(payload,dict) else None); after=_meta(payload.get('after') if isinstance(payload,dict) else None)
    keys=sorted(set(before)|set(after)); changed=[k for k in keys if before.get(k)!=after.get(k)]
    return {'ok':True,'version':VERSION,'changed_paths':changed,'before_hash':_hash(before),'after_hash':_hash(after),'diff_is_scientific_interpretation':False}
def link_revision_response(payload): return _ref_plan(payload,'revision-response-link')
def supersede_revision(payload): return {'ok':True,'version':VERSION,'revision_ref':_req(payload.get('revision_ref') if isinstance(payload,dict) else None,'revision_ref'),'superseded_by_ref':payload.get('superseded_by_ref'),'history_rewritten':False}
def list_revisions(payload):
    revs=[normalize_revision(x)['revision'] for x in _list(payload.get('revisions') if isinstance(payload,dict) else None,'revisions')]
    return {'ok':True,'version':VERSION,'revisions':revs,'revision_count':len(revs)}

def normalize_decision(payload):
    if not isinstance(payload,dict): raise ResearchReviewCritiqueRevisionError('payload must be an object.')
    state=str(payload.get('decision_state') or 'no-decision').lower()
    if state not in DECISION_STATES: raise ResearchReviewCritiqueRevisionError('decision_state invalid.')
    d={'decision_ref':str(payload.get('decision_ref') or f"review-decision:{_hash(payload)[:16]}")[:500],'decision_state':state,
       'review_ref':payload.get('review_ref'),'rationale':_text(payload.get('rationale')),'source_refs':_list(payload.get('source_refs'),'source_refs',MAX_REFS),
       'metadata':_meta(payload.get('metadata')),'decision_is_scientific_truth':False,'decision_is_peer_review_certification':False}; d['decision_hash']=_hash(d)
    return {'ok':True,'version':VERSION,'decision':d}
def record_decision(payload): return {**normalize_decision(payload),'recorded':True,'automatic_acceptance':False}

def _ref_plan(payload,kind): return {'ok':True,'version':VERSION,'kind':kind,'reference':_meta(payload),'reference_first':True,'scientific_record_mutated':False}
def link_replication_study(payload): return _ref_plan(payload,'replication-study-link')
def link_replication_run(payload): return _ref_plan(payload,'replication-run-link')
def link_replication_result(payload): return _ref_plan(payload,'replication-result-link')
def replication_plan(payload):
    return {'ok':True,'version':VERSION,'plan':_meta(payload),'requires_explicit_replication_execution':True,'replication_success_inferred':False}

def context_narrative(payload): return _ref_plan(payload,'narrative-context')
def context_finding(payload): return _ref_plan(payload,'finding-context')
def context_evidence(payload): return _ref_plan(payload,'evidence-context')
def context_uncertainty(payload): return _ref_plan(payload,'uncertainty-context')
def context_method(payload): return _ref_plan(payload,'method-context')
def context_session(payload): return _ref_plan(payload,'session-context')
def context_scene(payload): return _ref_plan(payload,'scene-context')
def context_provenance(payload): return _ref_plan(payload,'provenance-context')

def build_lineage(payload):
    events=_list(payload.get('events') if isinstance(payload,dict) else None,'events')
    nodes=[]; edges=[]
    for i,e in enumerate(events):
        ref=str(e.get('ref') or f'event:{i}') if isinstance(e,dict) else f'event:{i}'; nodes.append({'ref':ref,'kind':str(e.get('kind') or 'event') if isinstance(e,dict) else 'event'})
        if i: edges.append({'from':nodes[i-1]['ref'],'to':ref,'kind':'review-sequence'})
    return {'ok':True,'version':VERSION,'nodes':nodes,'edges':edges,'lineage_hash':_hash({'nodes':nodes,'edges':edges}),'causal_lineage_inferred':False}
def audit_lineage(payload):
    g=build_lineage(payload); refs=[n['ref'] for n in g['nodes']]; return {'ok':True,'version':VERSION,'node_count':len(refs),'duplicate_refs':sorted({r for r in refs if refs.count(r)>1}),'audit_certifies_scientific_validity':False}
def lineage_path(payload): return _ref_plan(payload,'lineage-path')
def lineage_upstream(payload): return _ref_plan(payload,'lineage-upstream')
def lineage_downstream(payload): return _ref_plan(payload,'lineage-downstream')

def handoff_plan(payload):
    if not isinstance(payload,dict): raise ResearchReviewCritiqueRevisionError('payload must be an object.')
    target=str(payload.get('target') or 'platform-core').lower()
    if target not in HANDOFF_TARGETS: raise ResearchReviewCritiqueRevisionError('target invalid.')
    return {'ok':True,'version':VERSION,'target':target,'references':_list(payload.get('references'),'references',MAX_REFS),
            'requires_explicit_submission':True,'automatic_submission':False,'handoff_certifies_scientific_validity':False}
def handoff_core(payload): return {**handoff_plan({**_meta(payload),'target':'platform-core'}),'automatic_core_submission':False}
def handoff_publication(payload): return {**handoff_plan({**_meta(payload),'target':'publication-studio'}),'automatic_publication':False}
def handoff_library(payload): return handoff_plan({**_meta(payload),'target':'knowledge-library'})
def handoff_workspace(payload): return handoff_plan({**_meta(payload),'target':'workspace'})
def handoff_replication(payload): return {**handoff_plan({**_meta(payload),'target':'replication-studio'}),'automatic_replication':False}

def guard_claims(payload): return {'ok':True,'version':VERSION,'review_comments_create_claims':False,'review_decisions_upgrade_claim_status':False,'revision_upgrades_claim_status':False}
def guard_evidence(payload): return {'ok':True,'version':VERSION,'reviewer_comments_are_evidence':False,'automatic_evidence_weighting':False,'evidence_strength_mutated':False}
def guard_review(payload): return {'ok':True,'version':VERSION,'review_is_scientific_certification':False,'automatic_acceptance':False,'reviewer_identity_confers_authority':False}
def guard_presentation(payload): return {'ok':True,'version':VERSION,'presentation_state_only':True,'scientific_record_mutated':False}
def guard_references(payload):
    refs=_list(payload.get('refs') if isinstance(payload,dict) else None,'refs',MAX_REFS); return {'ok':True,'version':VERSION,'explicit_reference_count':len(refs),'implicit_reference_resolution':False,'refs':refs}
def interpretation_boundaries_report(payload=None):
    return {'ok':True,'version':VERSION,'review_is_scientific_certification':False,'critique_is_evidence':False,'response_determines_truth':False,
            'revision_upgrades_claim_status':False,'decision_is_scientific_truth':False,'automatic_evidence_weighting':False,'automatic_acceptance':False,
            'automatic_core_submission':False,'automatic_publication':False,'automatic_replication':False}
