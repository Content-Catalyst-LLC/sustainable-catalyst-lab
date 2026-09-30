from app import scientific_model_validation_benchmark_laboratory_v01490 as m

BENCH={"benchmarkId":"b1","title":"benchmark","taskType":"classification","protocol":{"taskDefinition":"binary","evaluationSplit":"heldout","metricDefinitions":["accuracy"]},"metrics":[{"name":"accuracy","definition":"fraction correct"}],"provenance":{"source":"lab"}}

def test_health_and_policy_boundaries():
    h=m.health(); assert h["version"]=="0.149.0" and h["api_route_count"]==78 and h["scientificModelValidationBenchmarkLaboratory"] is True
    assert h["labExecutesBenchmarkCompute"] is False and h["benchmarkPerformanceIsScientificValidity"] is False and h["automaticDeploymentReadiness"] is False

def test_benchmark_normalization_deterministic():
    a=m.normalize_benchmark_suite(BENCH); b=m.normalize_benchmark_suite(BENCH); assert a["fingerprint"]==b["fingerprint"] and a["automaticWinnerSelection"] is False

def test_reference_standard_never_infallible():
    r=m.normalize_reference_standard({"referenceId":"r1","referenceType":"expert-adjudicated","definition":"panel label","provenance":{"panel":"x"},"infallibleGroundTruth":True}); assert r["infallibleGroundTruth"] is False

def test_split_integrity_and_leakage_audits():
    s=m.split_integrity_audit({"trainIds":["a","b"],"validationIds":["c"],"testIds":["b","d"]}); assert s["clean"] is False and s["overlaps"]["trainTest"]==["b"]
    l=m.benchmark_leakage_audit({"trainingRefs":["x","z"],"benchmarkRefs":["z","q"]}); assert l["leakageRisk"] is True and l["overlap"]==["z"]

def test_baseline_delta_does_not_establish_superiority():
    x=m.baseline_comparison_matrix({"baseline":{"metrics":{"accuracy":0.8}},"candidates":[{"id":"c1","metrics":{"accuracy":0.9}}]}); assert abs(x["rows"][0]["deltas"]["accuracy"]-0.1)<1e-9 and x["rows"][0]["scientificSuperiorityEstablished"] is False and x["automaticWinnerSelection"] is False

def test_external_validation_stays_scoped():
    r=m.normalize_external_validation_record({"validationId":"v1","modelRef":"m1","benchmarkRef":"b1","metricResults":[{"metric":"accuracy","value":0.9}],"universalValidityCertified":True}); assert r["validationType"]=="external" and r["universalValidityCertified"] is False
    s=m.external_validation_summary({"records":[r]}); assert s["universalValidityCertified"] is False

def test_failure_taxonomy_no_root_cause_inference():
    t=m.failure_taxonomy({"failures":[{"failureId":"f1","failureType":"domain-shift"},{"failureId":"f2","failureType":"domain-shift"}]}); assert t["byType"]["domain-shift"]==2 and t["rootCauseEstablished"] is False

def test_metric_and_regression_summaries():
    ms=m.metric_summary({"metric":"accuracy","values":[0.7,0.8,0.9]}); assert ms["summary"]["count"]==3 and round(ms["summary"]["mean"],3)==0.8
    rs=m.regression_summary({"actual":[1,2],"predicted":[1,4]}); assert rs["count"]==2 and rs["mae"]==1.0

def test_reproducibility_and_snapshot_determinism():
    a=m.workspace_snapshot({"benchmark":BENCH,"submission":{"submissionId":"s1","modelRef":"m1"}})["snapshot"]
    b=m.workspace_snapshot({"benchmark":BENCH,"submission":{"submissionId":"s1","modelRef":"m1"}})["snapshot"]
    assert a["fingerprint"]==b["fingerprint"]
    p=m.reproducibility_package({"benchmark":BENCH,"submission":{"submissionId":"s1","modelRef":"m1"}})["package"]
    assert p["reproductionCertified"] is False and p["replicationCertified"] is False and p["scientificValidityCertified"] is False

def test_handoffs_do_not_certify_validity_or_deployment():
    for fn in (m.workspace_execution_handoff,m.workbench_handoff,m.core_handoff,m.research_os_handoff,m.integrated_neural_handoff,m.graph_ml_handoff,m.multimodal_handoff):
        h=fn({"benchmarkRef":"b1","submissionRef":"s1"})["handoff"]; assert h["scientificValidityCertified"] is False and h["deploymentReadinessCertified"] is False

def test_release_gates_and_acceptance():
    g=m.release_gates(); assert all(g["gates"].values())
    a=m.acceptance_report(); assert a["accepted"]["failureAnalysis"] is True and a["scientificValidityCertified"] is False and a["deploymentReadinessCertified"] is False
