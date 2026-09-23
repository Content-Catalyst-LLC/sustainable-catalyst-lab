from app.method_selection_intelligence_v01320 import *

def test_context_and_profiles_are_researcher_declared():
    c=normalize_research_context({'question_refs':['q:1'],'research_goal':'causal'})
    d=data_profile({'outcome_type':'continuous','row_count':100})
    assert c['context']['researcher_declared'] is True and c['context']['automatic_context_inference'] is False
    assert d['automatic_imputation'] is False

def test_catalog_has_cross_lab_methods():
    c=catalog()
    assert c['method_catalog_count'] >= 20
    assert 'time-series-forecasting' in c['method_catalog'] and 'causal-matching-weighting' in c['method_catalog']
    assert c['automatic_method_selection'] is False

def test_candidate_engine_is_unranked():
    r=method_candidates({'research_goal':'causal','outcome_type':'continuous','design_type':'observational','causal':True})
    assert r['automatic_method_ranking'] is False and r['input_order_preserved'] is True
    assert all(x['automatic_rank'] is None for x in r['candidates'])

def test_eligibility_exposes_missing_requirements():
    e=eligibility_matrix({'method_refs':['bayesian-regression'],'outcome_type':'continuous','design_type':'observational','satisfied_requirements':[]})
    row=e['eligibility'][0]
    assert row['status']=='needs-information' and 'priors-declared' in row['missing']

def test_incompatible_outcome_is_explained_not_auto_rejected():
    c=method_candidates({'method_refs':['linear-regression'],'outcome_type':'binary','design_type':'observational'})
    assert c['candidates'][0]['status']=='incompatible'
    i=incompatibility_report({'candidates':c['candidates']})
    assert i['count']==1 and i['automatic_method_rejection'] is False

def test_assumptions_not_certified():
    m=assumption_matrix({'method_refs':['linear-regression'],'assumptions':[{'assumption_ref':'a:1','state':'unknown'}]})
    assert m['matrix'][0]['automatic_assumption_satisfaction'] is False and m['automatic_method_rejection'] is False

def test_comparison_has_no_winner():
    c=method_comparison({'methods':[{'method_ref':'m:1','strengths':['transparent']},{'method_ref':'m:2','limitations':['data hungry']}]})
    assert c['automatic_winner'] is None and c['automatic_ranking'] is False and c['selected_method_ref'] is None

def test_shortlist_and_decision_are_researcher_declared():
    s=researcher_shortlist({'method_refs':['linear-regression','bayesian-regression'],'rationale':'compare paradigms'})
    d=method_decision_record({'selected_method_ref':'bayesian-regression','alternatives_considered':['linear-regression'],'rationale':'prior knowledge available'})
    assert s['shortlist']['automatic_shortlisting'] is False and d['decision']['automatic_decision'] is False and d['decision']['researcher_declared'] is True

def test_readiness_is_not_validity():
    checks={k:True for k in ['question','estimand','data_profile','design_profile','candidate_methods','assumptions','diagnostics','validation']}
    r=readiness_report({'checks':checks})
    assert r['structurally_ready'] is True and r['ready_for_scientific_acceptance'] is False and r['method_validity_certified'] is False

def test_snapshot_and_core_are_reference_first():
    a=build_snapshot({'content':{'b':2,'a':1}}); b=build_snapshot({'content':{'a':1,'b':2}})
    c=core_object_plan({'project_ref':'p:1','candidate_method_refs':['m:1'],'selected_method_ref':'m:1'})
    assert a['snapshot']['snapshot_ref']==b['snapshot']['snapshot_ref']
    assert c['automatic_core_submission'] is False and c['core_does_not_select_method'] is True

def test_interpretation_boundaries():
    b=interpretation_boundaries_report()
    assert b['determine_truth'] is False and b['automatic_method_selection'] is False and b['eligible_does_not_mean_valid'] is True
