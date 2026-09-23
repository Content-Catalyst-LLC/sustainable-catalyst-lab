import pytest
from app.scientific_research_project_studio_v01300 import *

def test_manifest_catalog_health():
    assert health()['version']=='0.130.0'; assert health()['api_route_count']==32
    assert len(catalog()['method_families'])==18 and len(catalog()['figure_families'])==16

def test_project_normalization_is_deterministic():
    p={'project_ref':'p:1','title':'Study','tags':['a','b']}
    a=normalize_project(p)['project']; b=normalize_project(p)['project']; assert a['project_hash']==b['project_hash']; assert a['boundaries']['workspace_is_source_of_truth'] is False

def test_component_registry_reference_first():
    r=component_registry({'components':[{'ref':'d:1','type':'dataset','source_product':'library'}]})
    assert r['component_count']==1 and r['components'][0]['authority_ref']=='d:1' and r['project_registry_is_not_domain_authority'] is True
    with pytest.raises(ResearchProjectStudioError): component_registry({'components':[{'ref':'x'},{'ref':'x'}]})

def test_relationships_and_dependencies_are_declared():
    g=relationship_graph({'node_refs':['a','b'],'relationships':[{'from_ref':'a','to_ref':'b','relation':'produces'}]})
    assert not g['unresolved_refs'] and g['automatic_relationship_inference'] is False
    d=dependency_graph({'dependencies':[{'from_ref':'b','requires_ref':'a','hard':True}]}); assert d['automatic_dependency_inference'] is False

def test_workstreams_milestones_state():
    w=workstream_plan({'workstreams':[{'title':'Analysis','component_refs':['m:1']}]}); assert len(w['workstreams'])==1 and w['automatic_priority_assignment'] is False
    m=milestone_plan({'milestones':[{'title':'Freeze data','status':'planned'}]}); assert m['automatic_completion_certification'] is False
    s=project_state_report({'states':{'m:1':'complete'}}); assert s['automatic_overall_grade'] is False

def test_artifact_indexes_preserve_authority():
    assert dataset_index({'datasets':[{'ref':'d:1'}]})['index_is_not_domain_authority'] is True
    assert model_index({'models':[{'ref':'m:1'}]})['items'][0]['ref']=='m:1'
    assert execution_index({'executions':[{'ref':'e:1'}]})['count']==1
    assert figure_index({'figures':[{'ref':'f:1'}]})['count']==1
    assert manuscript_index({'manuscripts':[{'ref':'ms:1'}]})['count']==1
    assert reproduction_index({'reproduction_packages':[{'ref':'r:1'}]})['count']==1
    assert investigation_index({'investigations':[{'ref':'i:1'}]})['count']==1

def test_claim_evidence_no_weighting():
    x=claim_evidence_index({'claims':[{'ref':'c:1'}],'evidence':[{'ref':'ev:1'}],'links':[{'claim_ref':'c:1','evidence_ref':'ev:1'}]})
    assert x['automatic_evidence_weighting'] is False and x['automatic_claim_status_change'] is False

def test_session_handoff_workspace():
    assert research_session_plan({'project_ref':'p','component_refs':['d']})['automatic_session_registration'] is False
    assert handoff_plan({'project_ref':'p','source_product':'lab','target_product':'workspace'})['automatic_handoff'] is False
    assert workspace_layout({'panels':[{'panel_type':'figure','object_refs':['f:1']} ]})['layout_changes_scientific_semantics'] is False

def test_timeline_provenance_readiness():
    t=research_timeline({'events':[{'time':'2026-02-01','event_ref':'b'},{'time':'2026-01-01','event_ref':'a'}]}); assert [x['event_ref'] for x in t['events']]==['a','b']
    p=provenance_aggregate({'root_refs':['x'],'records':[{'ref':'x'}]}); assert p['aggregation_does_not_replace_source_provenance'] is True
    r=readiness_report({'checks':{'project':1,'components':1,'provenance':1,'methods':1,'outputs':1}}); assert r['ready_for_project_review'] is True and r['ready_for_scientific_acceptance'] is False

def test_snapshot_revision_export():
    s=build_snapshot({'project_ref':'p','component_refs':['d:1']})['snapshot']; assert len(s['snapshot_hash'])==64
    assert revision_plan({'project_ref':'p','changes':[{'op':'add'}]})['automatic_apply'] is False
    assert export_plan({'project_ref':'p','formats':['json','pdf']})['automatic_export_execution'] is False
    with pytest.raises(ResearchProjectStudioError): export_plan({'formats':['exe']})

def test_core_publication_boundaries():
    c=core_project_plan({'project_ref':'p','session_id':'s','component_refs':['d:1']}); assert c['automatic_core_submission'] is False and c['core_becomes_domain_authority'] is False
    p=publication_package_plan({'project_ref':'p','manuscript_refs':['m:1']}); assert p['automatic_publication'] is False
    b=interpretation_boundaries_report(); assert b['scientific_validity_certified'] is False and len(b['boundaries'])>=10
