from app.scientific_scene_linking_comparative_context_v01355 import *

def test_health_catalog():
    h=health(); c=catalog()
    assert h['version']=='0.135.5' and h['api_route_count']==48
    assert c['link_type_count']==10 and c['compare_mode_count']==6 and c['context_family_count']==12 and c['pin_state_count']==3
    assert c['automatic_equivalence_inference'] is False and c['automatic_join_inference'] is False

def test_explicit_same_object_equivalence_guard():
    try:
        normalize_link({'link_type':'same-object','source_ref':'a','target_ref':'b'})
        assert False
    except ScientificSceneLinkingComparativeContextError:
        pass
    r=normalize_link({'link_type':'same-object','source_ref':'a','target_ref':'b','equivalence_asserted':True})
    assert r['link']['equivalence_asserted'] is True

def test_context_is_non_authoritative_and_deterministic():
    p={'source_ref':'row:1','context':{'focus':{'ref':'row:1'},'camera':{'x':1},'evidence':{'refs':['e:1']}}}
    a=normalize_context_capsule(p)['capsule']; b=normalize_context_capsule(p)['capsule']
    assert a['context_hash']==b['context_hash'] and a['authoritative'] is False
    assert preserve_context(p)['scientific_record_mutated'] is False

def test_comparison_never_implies_causality():
    r=comparison_plan({'object_refs':['model:a','model:b'],'compare_mode':'side-by-side'})
    assert r['comparison']['causal_interpretation'] is False
    assert r['automatic_equivalence_inference'] is False

def test_snapshot_and_boundaries():
    r=build_snapshot({'comparison':{'object_refs':['a','b']},'context':{'context':{'focus':{'ref':'a'}}},'pins':[]})
    assert r['snapshot']['scientific_record_mutated'] is False
    b=interpretation_boundaries_report(); assert b['determine_truth'] is False and b['automatic_core_submission'] is False
