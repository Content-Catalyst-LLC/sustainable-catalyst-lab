from app import ablation_study_framework_v01415 as m
P={"studyId":"abl-1","datasetRef":"ds-a","splitRef":"split-a","baseTrainingConfigurationRef":"train-a","environmentRef":"env-a","seedPolicyRef":"seed-policy-a",
   "factors":[{"factorId":"f-drop","component":"dropout","action":"remove"},{"factorId":"f-norm","component":"layer-norm","action":"disable"}],
   "metrics":[{"name":"loss","direction":"min","definitionRef":"loss-v1"},{"name":"accuracy","direction":"max","definitionRef":"acc-v1"}],
   "baseline":{"variantId":"baseline","modelRef":"model-a","datasetRef":"ds-a","splitRef":"split-a","baseTrainingConfigurationRef":"train-a","environmentRef":"env-a","seedPolicyRef":"seed-policy-a"},
   "variants":[
      {"variantId":"baseline","isBaseline":True,"status":"completed","metrics":{"loss":0.72,"accuracy":0.84},"metricDefinitionRef":"metrics-v1"},
      {"variantId":"no-dropout","status":"completed","factors":[{"component":"dropout","action":"remove"}],"metrics":{"loss":0.75,"accuracy":0.82},"metricDefinitionRef":"metrics-v1"},
      {"variantId":"no-norm","status":"completed","factors":[{"component":"layer-norm","action":"disable"}],"metrics":{"loss":0.79,"accuracy":0.80},"metricDefinitionRef":"metrics-v1"},
   ]}

def test_health_policy():
    h=m.health(); assert h["version"]=="0.141.5" and h["api_route_count"]==30 and h["labExecutesTraining"] is False
    assert m.policy()["causalEffectInferred"] is False and m.policy()["automaticWinnerSelection"] is False

def test_plan_and_workspace_handoff():
    p=m.normalize_plan(P); assert p["readyForExecutionHandoff"] is True and len(p["plan"]["factors"])==2
    h=m.workspace_handoff(P); assert h["handoff"]["executionAuthority"]=="workspace" and h["handoff"]["labExecutesTraining"] is False

def test_baseline_and_comparability():
    b=m.baseline_audit(P); assert b["valid"] is True and b["baseline"]["variantId"]=="baseline"
    c=m.comparability(P); assert c["allComparable"] is True
    assert all(x["causalEffectInferred"] is False for x in c["rows"])
    q={**P,"variants":[P["variants"][0],{**P["variants"][1],"environmentRef":"env-b"}]}
    qc=m.comparability(q); assert qc["allComparable"] is False and qc["rows"][0]["controlledContrast"] is False

def test_controlled_delta_not_causal():
    p={**P,"baseline":{**P["baseline"],"metricDefinitionRef":"metrics-v1"}}
    p["variants"]=[{**v,"metricDefinitionRef":"metrics-v1"} for v in P["variants"]]
    # baseline metric definition is carried on variant result, so force matching via common variant fields
    for v in p["variants"]: v["metricDefinitionRef"]="metrics-v1"
    d=m.paired_delta_matrix(p); assert d["ok"] is True and d["matrix"]["causalEffectInferred"] is False
    assert abs(d["matrix"]["rows"][0]["deltas"]["loss"]-0.03) < 1e-12

def test_component_summary_descriptive_only():
    x=m.component_effect_summary(P); assert x["descriptiveEffectOnly"] is True
    assert all(r["causalEffectInferred"] is False for r in x["rows"])

def test_interaction_guardrail():
    q={**P,"variants":P["variants"]+[{"variantId":"double","status":"completed","factors":[{"component":"dropout","action":"remove"},{"component":"layer-norm","action":"disable"}],"metrics":{"loss":0.9,"accuracy":0.7}}]}
    x=m.interaction_summary(q); assert x["interactionEstimated"] is False and len(x["rows"])==1

def test_candidate_review_never_returns_winner():
    x=m.candidate_review({**P,"metric":"loss","direction":"min"}); assert x["winner"] is None and x["automaticWinnerSelection"] is False
    bad=m.candidate_review({**P,"metric":"loss"}); assert bad["ok"] is False

def test_snapshot_deterministic_and_reproducibility_not_certified():
    a=m.snapshot(P)["snapshot"]; b=m.snapshot(P)["snapshot"]; assert a["fingerprint"]==b["fingerprint"] and a["snapshotId"]==b["snapshotId"]
    r=m.reproducibility_packet(P); assert r["reproducibilityCertified"] is False and r["reproducibilityPacket"]["causalEffectCertified"] is False

def test_core_handoff_preserves_authority():
    h=m.core_visual_handoff({**P,"view":"component-effect-summary"}); assert h["handoff"]["canonicalVisualObjectAuthority"]=="platform-core" and h["handoff"]["causalEffectInferred"] is False
