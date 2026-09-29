from app import training_curves_metrics_checkpoint_visualization_v01412 as m

PAYLOAD={"experimentId":"exp-1","workspaceResult":{"runs":[
 {"runId":"r1","metrics":[
  {"name":"loss","split":"train","step":1,"value":1.0},{"name":"loss","split":"validation","step":1,"value":1.2},
  {"name":"loss","split":"train","step":2,"value":0.8},{"name":"loss","split":"validation","step":2,"value":0.95},
  {"name":"loss","split":"train","step":3,"value":0.7},{"name":"loss","split":"validation","step":3,"value":0.9}],
  "checkpoints":[{"id":"c1","step":1,"artifactHash":"a"},{"id":"c2","step":3,"artifactHash":"b"}]},
 {"runId":"r2","metrics":[{"name":"loss","split":"validation","step":1,"value":1.1},{"name":"loss","split":"validation","step":2,"value":0.88}],"checkpoints":[]} ]}}

def test_health_and_policy():
    h=m.health(); assert h["version"]=="0.141.2" and h["api_route_count"]==29 and h["automaticCheckpointPromotion"] is False
    assert m.policy()["rawTelemetryImmutable"] is True

def test_curve_preserves_raw_and_smoothing_is_derived():
    raw=m.training_curve_spec({**PAYLOAD,"name":"loss","split":"validation","method":"none"}); assert raw["ok"] and raw["visualSpec"]["smoothing"]=="none"
    sm=m.smooth_series({**PAYLOAD,"name":"loss","split":"validation","method":"ema","alpha":0.5}); assert sm["derivedVisualization"] is True and all("rawValue" in x for x in sm["points"])

def test_checkpoint_candidate_is_not_promotion():
    x=m.checkpoint_candidate({**PAYLOAD,"name":"loss","split":"validation","runId":"r1","direction":"min"}); assert x["ok"] and x["candidateOnly"] and x["automaticPromotion"] is False

def test_gap_and_diagnostics_are_descriptive():
    g=m.train_validation_gap({**PAYLOAD,"name":"loss","runId":"r1"}); assert len(g["points"])==3 and g["overfittingInferred"] is False
    d=m.convergence_diagnostics({**PAYLOAD,"name":"loss","split":"validation"}); assert d["descriptiveHeuristicOnly"] and d["convergenceCertified"] is False

def test_dashboard_and_core_handoff():
    d=m.dashboard_spec(PAYLOAD); assert d["dashboard"]["automaticModelRanking"] is False
    h=m.core_visual_handoff(PAYLOAD); assert h["handoff"]["canonicalVisualObjectAuthority"]=="platform-core"

def test_snapshot_deterministic():
    a=m.snapshot(PAYLOAD)["snapshot"]; b=m.snapshot(PAYLOAD)["snapshot"]; assert a["fingerprint"]==b["fingerprint"] and a["snapshotId"]==b["snapshotId"]

def test_no_objective_direction_no_candidate():
    x=m.checkpoint_candidate({**PAYLOAD,"name":"loss","split":"validation"}); assert x["ok"] is False
