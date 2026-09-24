from app.research_review_critique_revision_v01358 import *

def test_health_catalog():
    h=health(); c=catalog()
    assert h['version']=='0.135.8' and h['api_route_count']==60
    assert c['review_state_count']==6 and c['critique_type_count']==8 and c['response_state_count']==5
    assert c['decision_state_count']==5 and c['revision_kind_count']==5 and c['handoff_target_count']==5

def test_review_and_critique_are_non_authoritative():
    r=create_review({'title':'Review','narrative_ref':'n:1'})
    assert r['scientific_record_mutated'] is False and r['review']['review_is_scientific_certification'] is False
    c=add_critique({'critique_type':'methodology','target_ref':'finding:1','text':'Check assumption'})['critique']
    assert c['critique_is_evidence'] is False and c['critique_is_claim'] is False

def test_response_revision_boundaries():
    response=add_response({'critique_ref':'c:1','response_state':'addressed','text':'Updated methods'})['response']
    assert response['response_resolves_science_automatically'] is False
    rev=create_revision({'revision_kind':'method','parent_ref':'m:1','new_ref':'m:2'})['revision']
    assert rev['revision_upgrades_claim_status'] is False

def test_deterministic_lineage_and_diff():
    payload={'events':[{'ref':'review:1','kind':'review'},{'ref':'critique:1','kind':'critique'},{'ref':'response:1','kind':'response'}]}
    a=build_lineage(payload); b=build_lineage(payload)
    assert a['lineage_hash']==b['lineage_hash'] and a['causal_lineage_inferred'] is False
    d=revision_diff({'before':{'a':1},'after':{'a':2,'b':3}})
    assert d['changed_paths']==['a','b'] and d['diff_is_scientific_interpretation'] is False

def test_handoff_and_boundaries():
    h=handoff_core({'references':['review:1']})
    assert h['requires_explicit_submission'] is True and h['automatic_core_submission'] is False
    b=interpretation_boundaries_report()
    assert b['review_is_scientific_certification'] is False and b['automatic_acceptance'] is False and b['automatic_replication'] is False
