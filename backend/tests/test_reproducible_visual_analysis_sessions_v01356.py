from app.reproducible_visual_analysis_sessions_v01356 import *

def test_health_catalog():
    h=health(); c=catalog()
    assert h['version']=='0.135.6' and h['api_route_count']==52
    assert c['event_type_count']==12 and c['session_state_count']==4 and c['checkpoint_kind_count']==5 and c['replay_mode_count']==3
    assert c['interaction_lineage_is_not_scientific_evidence'] is True

def test_ordered_lineage_is_not_causality():
    p={'events':[{'event_type':'focus','sequence':0,'target_ref':'figure:1'},{'event_type':'drill','sequence':1,'target_ref':'model:1'}]}
    l=build_lineage(p)['lineage']
    assert len(l['edges'])==1 and l['scientific_causality'] is False
    assert audit_lineage(p)['scientific_causality_inferred'] is False

def test_checkpoint_and_replay_are_non_destructive():
    cp=create_checkpoint({'checkpoint_kind':'manual','sequence':2,'context':{'focus':'model:1'}})
    assert cp['scientific_record_mutated'] is False
    rp=replay_plan({'replay_mode':'strict','events':[{'event_type':'focus','sequence':0,'target_ref':'model:1'}]})
    assert rp['replay_mutates_science'] is False

def test_deterministic_snapshot():
    p={'session':{'project_ref':'p:1'},'events':[{'event_type':'focus','sequence':0,'target_ref':'x'}]}
    a=build_snapshot(p)['snapshot']; b=build_snapshot(p)['snapshot']
    assert a['snapshot_hash']==b['snapshot_hash']

def test_boundaries():
    b=interpretation_boundaries_report()
    assert b['interaction_history_is_scientific_evidence'] is False
    assert b['replay_is_scientific_replication'] is False and b['determine_truth'] is False and b['automatic_core_submission'] is False
