import pytest
from app.research_reproduction_replication_studio_v01290 import *


def test_health_catalog_schema():
    assert health()['version']=='0.129.0'; assert len(METHOD_FAMILIES)==15; assert len(FIGURE_FAMILIES)==14
    assert catalog()['automatic_claim_confirmation'] is False


def test_normalize_and_inventory():
    s=normalize_study({'mode':'reproduction','study_ref':'study:1','artifact_refs':['a']})['study']; assert len(s['study_hash'])==64
    inv=artifact_inventory({'artifacts':[{'ref':'data:1','type':'dataset','required':True,'available':True,'sha256':'a'*64}]})
    assert inv['availability_fraction']==1 and inv['hash_coverage_fraction']==1


def test_integrity_and_environment():
    h='a'*64
    r=input_integrity_report({'checks':[{'artifact_ref':'x','expected_sha256':h,'observed_sha256':h}]}); assert r['all_declared_inputs_match'] is True
    e=environment_lock_plan({'environment':{'runtime':'python','runtime_version':'3.12','environment_variables':{'A':'x'}}}); assert len(e['lock_hash'])==64


def test_method_execution_and_tolerance():
    m=method_reconstruction_plan({'steps':[{'method_ref':'m:1','input_refs':['d:1'],'output_refs':['o:1'],'parameters':{'x':1},'seed':4}]}); assert len(m['method_plan_hash'])==64
    p=execution_reproduction_plan({'study_ref':'s','method_plan_ref':'m'}); assert p['automatic_execution'] is False
    t=tolerance_profile({'absolute_tolerance':.01,'relative_tolerance':.001}); assert t['profile']['absolute_tolerance']==.01


def test_result_comparison():
    r=result_comparison({'expected':[1,2,3],'observed':[1.0,2.001,2.99],'absolute_tolerance':.02}); assert r['all_within_tolerance'] is True
    assert r['numerical_match_confirms_claim'] is False


def test_figure_provenance_deviation():
    f=figure_reproduction_plan({'figures':[{'figure_ref':'fig:1','source_data_refs':['d:1']}]}); assert f['automatic_rendering'] is False
    p=provenance_reconstruction({'nodes':[{'ref':'d:1'},{'ref':'o:1'}],'edges':[{'from':'d:1','to':'o:1'}]}); assert p['provenance_complete'] is True
    d=deviation_register({'deviations':[{'category':'runtime','original':'3.11','reproduction':'3.12'}]}); assert d['deviation_count']==1


def test_replication_protocol_result():
    p=replication_protocol({'claim_refs':['c:1'],'independent_data':True}); assert p['automatic_success_criteria_selection'] is False
    q=independent_replication_plan({'protocol_ref':'p:1','dataset_refs':['d:2']}); assert q['automatic_replication_judgment'] is False
    r=replication_result_record({'replication_ref':'r:1','outcomes':[{'metric':'m','value':1.2}]}); assert r['automatic_success_label'] is False


def test_claim_matrix_package():
    c=claim_linkage_report({'links':[{'claim_ref':'c:1','original_evidence_refs':['e:1'],'replication_output_refs':['o:2']}]}); assert c['automatic_claim_status_change'] is False
    m=reproducibility_matrix({'dimensions':{'inputs':'available','environment':'available'}}); assert m['automatic_grade'] is False
    p=package_manifest({'items':[{'ref':'d:1','sha256':'a'*64}]}); assert len(p['package_hash'])==64 and p['scientific_validity_certified'] is False


def test_visual_studio_snapshot_core():
    assert build_visualization_plan({})['figure_count']==14
    st=build_studio({'study_ref':'s:1','mode':'replication'})['studio']; assert len(st['studio_hash'])==64
    snap=build_snapshot({'studio':st,'study_ref':'s:1'}); assert len(snap['snapshot_hash'])==64
    assert build_export_plan({})['automatic_publication'] is False
    assert build_core_object_plan({'session_id':'sess','analysis_id':'rr1'})['automatic_core_submission'] is False
    assert build_execution_lineage_plan({'session_id':'sess'})['automatic_execution'] is False


def test_readiness_and_boundaries():
    r=readiness_report({'artifact_inventory_ref':'i','environment_lock_ref':'e','method_plan_ref':'m','expected_output_refs':['o'],'tolerance_profile_ref':'t','provenance_ref':'p'})
    assert r['ready_for_execution_review'] is True and r['ready_for_scientific_acceptance'] is False
    assert reproduction_status_report({'status':{'artifacts':'complete'}})['automatic_overall_grade'] is False
    b=interpretation_boundaries_report(); assert b['scientific_validity_certified'] is False and len(b['boundaries'])>=10


def test_errors():
    with pytest.raises(ReproductionReplicationError): normalize_study({'mode':'other'})
    with pytest.raises(ReproductionReplicationError): tolerance_profile({'absolute_tolerance':-1})
    with pytest.raises(ReproductionReplicationError): result_comparison({'expected':[1],'observed':[1,2]})
