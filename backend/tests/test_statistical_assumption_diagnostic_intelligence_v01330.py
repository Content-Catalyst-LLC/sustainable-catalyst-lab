from app.statistical_assumption_diagnostic_intelligence_v01330 import *

def test_catalog_and_boundaries():
    c=catalog(); b=interpretation_boundaries_report()
    assert c['assumption_catalog_count']>=25 and c['diagnostic_catalog_count']>=19
    assert c['automatic_method_invalidation'] is False and b['determine_truth'] is False

def test_context_is_researcher_declared():
    c=normalize_context({'project_ref':'p:1','method_refs':['linear-regression']})['context']
    assert c['researcher_declared'] is True and c['automatic_context_inference'] is False

def test_states_preserve_uncertainty_and_untested():
    r=evaluate_assumptions({'assumptions':[{'assumption_ref':'a:1','state':'uncertain'},{'assumption_ref':'a:2'}]})
    assert r['state_counts']['uncertain']==1 and r['state_counts']['untested']==1

def test_violation_does_not_auto_invalidate_method():
    r=violation_report({'assumptions':[{'assumption_ref':'a:1','method_ref':'m:1','state':'violated'}]})
    assert r['count']==1 and r['automatic_method_invalidation'] is False

def test_residual_and_distribution_diagnostics_are_descriptive():
    r=residual_diagnostics({'residuals':[-1,0,1,0]}); d=distribution_diagnostics({'values':[1,2,3,4,5]})
    assert r['automatic_model_rejection'] is False and d['automatic_normality_certification'] is False

def test_variance_and_multicollinearity_do_not_mutate_model():
    v=variance_diagnostics({'groups':[{'group_ref':'a','values':[1,2,3]},{'group_ref':'b','values':[1,3,5]}]})
    m=multicollinearity_diagnostics({'vif':[{'term':'x1','vif':6.2}]})
    assert v['automatic_homoskedasticity_certification'] is False and m['automatic_term_removal'] is False

def test_convergence_does_not_certify_sampler():
    c=convergence_diagnostics({'rhat':{'beta':1.01},'ess':{'beta':800}})
    assert c['automatic_convergence_certification'] is False

def test_causal_and_spatial_boundaries():
    c=causal_overlap_diagnostics({'treated_scores':[.2,.4,.7],'control_scores':[.1,.3,.6]})
    s=spatial_diagnostics({'weights_ref':'w:1','global_moran_i':0.3})
    assert c['automatic_causal_identification_certification'] is False and s['spatial_association_is_not_causality'] is True

def test_time_series_and_simulation_boundaries():
    t=time_series_diagnostics({'values':[1,2,2,3,4],'frequency':'monthly'})
    s=simulation_diagnostics({'checkpoints':[{'n':100,'mean':1.2}]})
    assert t['automatic_stationarity_certification'] is False and s['automatic_probability_as_truth'] is False

def test_cross_method_synthesis_has_no_winner():
    r=cross_method_synthesis({'assumptions':[{'assumption_ref':'a','method_ref':'m1','state':'satisfied'},{'assumption_ref':'b','method_ref':'m2','state':'violated'}]})
    assert r['automatic_winner'] is None and r['automatic_method_ranking'] is False

def test_researcher_adjudication_and_readiness():
    a=adjudication_record({'assumption_ref':'a:1','state':'uncertain','rationale':'mixed diagnostics'})
    checks={k:True for k in ['method_context','assumptions_registered','diagnostics_declared','untested_reviewed','researcher_adjudication_plan']}
    r=readiness_report({'checks':checks})
    assert a['adjudication']['automatic_adjudication'] is False and r['structurally_ready'] is True and r['scientific_validity_certified'] is False

def test_snapshot_and_core_are_reference_first():
    a=build_snapshot({'content':{'b':2,'a':1}}); b=build_snapshot({'content':{'a':1,'b':2}})
    c=core_object_plan({'project_ref':'p:1','method_refs':['m:1'],'assumption_refs':['a:1']})
    assert a['snapshot']['snapshot_ref']==b['snapshot']['snapshot_ref']
    assert c['automatic_core_submission'] is False and c['core_does_not_certify_assumptions'] is True
