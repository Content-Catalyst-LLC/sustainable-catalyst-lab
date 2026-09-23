from app.research_question_hypothesis_workspace_v01310 import *

def test_question_and_hypothesis_registry():
    q=normalize_question({'question':'Does intervention X alter outcome Y?','population':'P'})
    assert q['question']['researcher_declared'] is True
    h=hypothesis_registry({'hypotheses':[{'statement':'X increases Y','type':'primary'},{'statement':'X does not increase Y','type':'null'}]})
    assert h['hypothesis_count']==2 and h['automatic_hypothesis_selection'] is False

def test_competing_set_requires_two():
    s=competing_hypothesis_set({'hypothesis_refs':['h:1','h:2']})
    assert s['competing_set']['researcher_selection_required'] is True and s['competing_set']['automatic_winner'] is None

def test_operationalization_and_observables():
    v=operationalize_variables({'variables':[{'variable_ref':'v:y','name':'Outcome','role':'outcome','unit':'kg'}]})
    o=observable_registry({'observables':[{'observable_ref':'o:1','variable_ref':'v:y','expected_only':True}]})
    assert v['automatic_operationalization'] is False and o['expected_observation_equals_evidence'] is False

def test_expectations_do_not_score_hypotheses():
    m=expected_observation_matrix({'expectations':[{'hypothesis_ref':'h:1','observable_ref':'o:1','expected_pattern':'increase'}]})
    assert m['automatic_hypothesis_scoring'] is False

def test_falsification_and_rivals():
    f=falsification_criteria({'criteria':[{'hypothesis_ref':'h:1','criterion':'No measurable change'}]})
    r=rival_explanations({'rivals':[{'statement':'Confounding mechanism','target_hypothesis_refs':['h:1']}]})
    assert f['automatic_hypothesis_rejection'] is False and r['automatic_dismissal'] is False

def test_preregistration_is_immutable():
    p=preregistration_lock({'content':{'question':'q','hypotheses':['h1']}})
    d=preregistration_deviation({'deviations':[{'lock_ref':p['preregistration']['lock_ref'],'field':'method','reason':'instrument failure'}]})
    assert p['preregistration']['locked'] is True and d['deviations_hidden'] is False

def test_method_and_decision_boundaries():
    m=method_eligibility_plan({'methods':[{'method_ref':'m:1','declared_eligible':True}]})
    b=decision_boundary_plan({'boundaries':[{'metric':'effect','threshold':1.0}]})
    assert m['automatic_method_selection'] is False and b['automatic_decision'] is False

def test_readiness_not_validity():
    r=readiness_report({'checks':{k:1 for k in ['question','hypotheses','variables','observables','assumptions','expected_observations','falsification','scope']}})
    assert r['structurally_ready'] is True and r['ready_for_scientific_acceptance'] is False

def test_core_reference_first():
    c=core_object_plan({'project_ref':'p:1','question_refs':['q:1'],'hypothesis_refs':['h:1']})
    assert c['automatic_core_submission'] is False and c['core_does_not_select_hypotheses'] is True

def test_snapshot_deterministic():
    a=build_snapshot({'content':{'b':2,'a':1}}); b=build_snapshot({'content':{'a':1,'b':2}})
    assert a['snapshot']['snapshot_ref']==b['snapshot']['snapshot_ref']

def test_boundaries():
    b=interpretation_boundaries_report()
    assert b['determine_truth'] is False and b['scientific_validity_certified'] is False and b['researcher_selection_required'] is True
