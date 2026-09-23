from app.evidence_synthesis_intelligence_ii_v01340 import *

def test_catalog_and_boundaries():
    c=catalog(); b=interpretation_boundaries_report()
    assert c['synthesis_family_count']>=20 and c['figure_family_count']>=16
    assert c['automatic_truth_inference'] is False and b['determine_truth'] is False

def test_evidence_normalization_preserves_no_weight():
    r=normalize_evidence({'evidence':[{'evidence_ref':'e1','claim_refs':['c1'],'state':'supports'}]})
    assert r['evidence'][0]['automatic_evidence_weight'] is None and r['automatic_quality_scoring'] is False

def test_contradictions_preserved():
    p={'evidence':[{'evidence_ref':'a','claim_refs':['c'],'state':'supports','effect_direction':'positive'},{'evidence_ref':'b','claim_refs':['c'],'state':'challenges','effect_direction':'negative'}]}
    r=contradiction_report(p)
    assert r['contradiction_count']==1 and r['contradictions'][0]['automatic_resolution'] is False

def test_random_effects_meta_analysis_uses_existing_engine():
    r=quantitative_synthesis({'model_choice':'random-effects','effects':[{'effect_ref':'e1','effect':.2,'standard_error':.1},{'effect_ref':'e2','effect':.4,'standard_error':.12},{'effect_ref':'e3','effect':.1,'standard_error':.09}]})
    assert r['meta_analysis']['k']==3 and r['automatic_truth_inference'] is False

def test_heterogeneity_not_auto_judged():
    r=heterogeneity_report({'effects':[{'effect':.2,'standard_error':.1},{'effect':.8,'standard_error':.1}]})
    assert r['i_squared_percent']>=0 and r['automatic_heterogeneity_judgment'] is False

def test_replication_disagreement_preserved():
    r=replication_synthesis({'evidence':[{'evidence_ref':'o','state':'supports','effect_direction':'positive'},{'evidence_ref':'r','kind':'replication','replication_of_ref':'o','state':'challenges','effect_direction':'negative'}]})
    assert r['replications'][0]['direction_agreement'] is False and r['automatic_replication_certification'] is False

def test_claim_synthesis_has_no_truth_status():
    r=claim_synthesis({'claim_refs':['c1'],'evidence':[{'evidence_ref':'e1','claim_refs':['c1'],'state':'supports'}]})
    assert r['claims'][0]['automatic_claim_status'] is None and r['automatic_consensus_certification'] is False

def test_assumption_bridge_does_not_exclude_studies():
    r=assumption_diagnostic_bridge({'assumption_refs':['a1'],'diagnostic_refs':['d1']})
    assert r['v01330_reference_first'] is True and r['automatic_study_exclusion'] is False

def test_readiness_structural_not_scientific_certification():
    checks={k:True for k in ['protocol_declared','evidence_registered','scope_declared','heterogeneity_reviewed','contradictions_reviewed','researcher_adjudication_plan']}
    r=readiness_report({'checks':checks})
    assert r['structurally_ready'] is True and r['scientific_consensus_certified'] is False

def test_snapshot_deterministic():
    a=build_snapshot({'content':{'b':2,'a':1}}); b=build_snapshot({'content':{'a':1,'b':2}})
    assert a['snapshot']['snapshot_ref']==b['snapshot']['snapshot_ref']

def test_core_plan_reference_first():
    r=core_object_plan({'project_ref':'p1','claim_refs':['c1'],'evidence_refs':['e1']})
    assert r['reference_first'] is True and r['core_does_not_execute_synthesis'] is True and r['automatic_core_submission'] is False
