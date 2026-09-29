from app import model_comparison_experiment_matrix_v01413 as m
P={"experiments":[
 {"experimentId":"e1","runId":"r1","datasetRef":"ds-a","splitRef":"split-a","architectureRef":"arch-a","trainingConfigurationRef":"cfg-a","environmentRef":"env-a","provenanceRef":"prov-a","metrics":[{"name":"loss","split":"validation","value":0.8,"definitionRef":"metric-loss-v1"},{"name":"accuracy","split":"validation","value":0.82,"definitionRef":"metric-acc-v1"}],"checkpoints":[{"id":"c1"}]},
 {"experimentId":"e2","runId":"r2","datasetRef":"ds-a","splitRef":"split-a","architectureRef":"arch-b","trainingConfigurationRef":"cfg-b","environmentRef":"env-a","provenanceRef":"prov-b","metrics":[{"name":"loss","split":"validation","value":0.7,"definitionRef":"metric-loss-v1"},{"name":"accuracy","split":"validation","value":0.84,"definitionRef":"metric-acc-v1"}],"checkpoints":[{"id":"c2"},{"id":"c3"}]}]}

def test_health_policy():
    h=m.health(); assert h["version"]=="0.141.3" and h["api_route_count"]==30 and h["automaticWinnerSelection"] is False
    assert m.policy()["explicitComparability"] is True

def test_comparability_is_explicit():
    c=m.comparability({**P,"metric":"loss","split":"validation"}); assert len(c["pairs"])==1
    dims=c["pairs"][0]["dimensions"]; assert dims["dataset"]["same"] is True and dims["architecture"]["same"] is False

def test_matrices_do_not_rank():
    e=m.experiment_matrix({**P,"metric":"loss","split":"validation"}); assert e["matrix"]["automaticRanking"] is False and len(e["matrix"]["rows"])==2
    mm=m.metric_matrix(P); assert mm["matrix"]["automaticRanking"] is False
    dm=m.delta_matrix({**P,"metric":"loss","split":"validation"}); assert dm["matrix"]["winnerInferred"] is False

def test_pairwise_has_no_winner():
    x=m.pairwise_metric_comparison({**P,"metric":"loss","split":"validation"}); assert x["pairs"][0]["winner"] is None and x["pairs"][0]["difference"] is not None

def test_metric_definition_audit():
    x=m.metric_definition_audit(P); assert all(r["definitionMismatch"] is False for r in x["rows"])

def test_snapshot_deterministic():
    a=m.snapshot(P)["snapshot"]; b=m.snapshot(P)["snapshot"]; assert a["fingerprint"]==b["fingerprint"] and a["snapshotId"]==b["snapshotId"]

def test_core_handoff_and_repro():
    h=m.core_visual_handoff({**P,"view":"experiment-matrix"}); assert h["handoff"]["canonicalVisualObjectAuthority"]=="platform-core"
    r=m.reproducibility_packet(P); assert r["reproducibilityCertified"] is False
