from app.visual_research_narrative_findings_v01357 import *

def test_health_catalog():
    h=health(); c=catalog()
    assert h['version']=='0.135.7' and h['api_route_count']==56
    assert c['block_type_count']==12 and c['finding_state_count']==5 and c['handoff_target_count']==4 and c['citation_mode_count']==3
    assert c['narrative_is_not_scientific_claim'] is True

def test_narrative_and_blocks_are_non_authoritative():
    n=create_narrative({'title':'Study narrative','blocks':[]})
    assert n['scientific_record_mutated'] is False and n['narrative']['presentation_is_scientific_claim'] is False
    b=add_block({'block_type':'figure','object_ref':'figure:1'})
    assert b['block']['scientific_assertion_created'] is False

def test_finding_state_is_declared_not_certified():
    f=create_finding({'statement':'Observed pattern','finding_state':'supported','evidence_refs':['e:1']})['finding']
    assert f['status_is_declared_not_certified'] is True and f['truth_determined'] is False
    assert f['evidence_weighted_automatically'] is False

def test_deterministic_publication_package():
    p={'narrative':{'title':'A','blocks':[]},'finding_refs':['f:1'],'citation_refs':['c:1']}
    a=export_package(p)['package']; b=export_package(p)['package']
    assert a['package_hash']==b['package_hash']

def test_boundaries_and_handoff():
    b=interpretation_boundaries_report()
    assert b['determine_truth'] is False and b['automatic_core_submission'] is False and b['automatic_publication'] is False
    h=handoff_core({})
    assert h['requires_explicit_submission'] is True and h['automatic_core_submission'] is False
