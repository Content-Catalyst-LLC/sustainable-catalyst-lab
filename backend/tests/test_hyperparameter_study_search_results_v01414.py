from app import hyperparameter_study_search_results_v01414 as m
P={"studyId":"study-1","datasetRef":"ds-a","splitRef":"split-a","architectureRef":"arch-a","environmentRef":"env-a","strategy":"random","seed":42,"maxTrials":4,
   "parameters":[{"name":"lr","type":"float","low":0.0001,"high":0.1,"scale":"log"},{"name":"depth","type":"integer","low":2,"high":6}],
   "objectives":[{"name":"loss","direction":"min","definitionRef":"loss-v1"},{"name":"accuracy","direction":"max","definitionRef":"acc-v1"}],
   "trials":[
    {"trialId":"t1","number":1,"status":"completed","parameters":{"lr":0.01,"depth":3},"objectives":{"loss":0.8,"accuracy":0.82},"runId":"r1"},
    {"trialId":"t2","number":2,"status":"completed","parameters":{"lr":0.005,"depth":4},"objectives":{"loss":0.7,"accuracy":0.84},"runId":"r2"},
    {"trialId":"t3","number":3,"status":"pruned","parameters":{"lr":0.08,"depth":6},"objectives":{"loss":1.1,"accuracy":0.72},"reason":"pruning rule"},
   ]}

def test_health_policy():
    h=m.health(); assert h["version"]=="0.141.4" and h["api_route_count"]==31 and h["labExecutesSearch"] is False
    assert m.policy()["automaticWinnerSelection"] is False and m.policy()["objectiveDirectionInferred"] is False

def test_study_and_workspace_handoff():
    s=m.study_spec(P); assert s["readyForExecutionHandoff"] is True and s["study"]["searchStrategy"]=="random"
    h=m.workspace_handoff(P); assert h["handoff"]["executionAuthority"]=="workspace" and h["handoff"]["labExecutesSearch"] is False

def test_trial_matrices_do_not_rank():
    p=m.parameter_value_matrix(P); assert len(p["matrix"]["rows"])==3 and p["matrix"]["automaticRanking"] is False
    o=m.objective_result_matrix(P); assert o["matrix"]["automaticWinnerSelection"] is False

def test_candidate_set_requires_explicit_direction():
    bad=m.single_objective_candidate_set({**P,"objective":"loss","direction":""}); assert bad["ok"] is False
    good=m.single_objective_candidate_set({**P,"objective":"loss","direction":"min"}); assert good["winner"] is None and good["candidateSet"][0]["trialId"]=="t2"

def test_pareto_is_candidate_set_not_ranking():
    x=m.pareto_frontier(P); assert x["ok"] is True and x["winner"] is None and x["automaticRanking"] is False
    assert any(r["trialId"]=="t2" for r in x["nondominatedCandidateSet"])

def test_descriptive_association_not_causal():
    x=m.parameter_effect_summary({**P,"objective":"loss"}); assert x["descriptiveAssociationOnly"] is True
    assert all(r["causalEffectInferred"] is False for r in x["rows"])

def test_snapshot_deterministic():
    a=m.snapshot(P)["snapshot"]; b=m.snapshot(P)["snapshot"]
    assert a["fingerprint"]==b["fingerprint"] and a["snapshotId"]==b["snapshotId"]

def test_core_handoff_and_reproducibility():
    h=m.core_visual_handoff({**P,"view":"search-progress"}); assert h["handoff"]["canonicalVisualObjectAuthority"]=="platform-core"
    r=m.reproducibility_packet(P); assert r["reproducibilityCertified"] is False
