from app import graph_studio_review_reproduction_v0135170 as m

BASE={
 "id":"bridge-1","threadId":"thread-1","resolutionRecordId":"res-1","auditRecordId":"audit-1","annotationId":"ann-1",
 "revisionAction":"rerun-analysis","revisionRef":"revision-2","revisionImpactRef":"impact-1","studyRef":"study-1","originalExecutionRef":"run-original",
 "environmentLockRef":"env-lock-1","methodPlanRef":"method-plan-1",
 "inputArtifacts":[{"artifactRef":"dataset-1","artifactType":"dataset","sha256":"a"*64,"available":True}],
 "expectedOutputRefs":["figure-1"],"claimRefs":["claim-1"],
}

def payload(**kw):
 x=dict(BASE); x.update(kw); return x

def execution(**kw):
 x=payload(); x.update({"execution":{"executionRef":"run-repro-1","bridgeRef":"bridge-1","sourceExecutionRef":"run-original","state":"completed","runtime":"python","runtimeVersion":"3.12","observed":[1.0,2.0],"outputArtifacts":[{"artifactType":"reproduction-result","artifactRef":"result-1","sha256":"b"*64}]}}); x.update(kw); return x

def test_normalize_validate():
 n=m.normalize_request(payload()); assert n["ok"] and n["record"]["collection"]=="graphStudioReviewReproductionBridges" and len(n["record"]["fingerprint"])==64
 v=m.validate_request(payload()); assert v["ok"] and not v["errors"]

def test_reuses_reproduction_engine():
 s=m.reproduction_study(payload()); assert s["ok"] and s["version"]=="0.129.0" and s["study"]["mode"]=="reproduction"
 inv=m.artifact_inventory(payload()); assert inv["ok"] and inv["required_available_count"]==1
 plan=m.execution_plan(payload()); assert plan["ok"] and plan["automatic_execution"] is False and plan["plan"]["study_ref"]=="study-1"

def test_impact_scope_supplied():
 a={"id":"impact-1","seedId":"method","downstream":{"affected_node_ids":["run","figure"]},"upstream":{"affected_node_ids":["dataset"]}}
 r=m.impact_scope({"revisionImpactAnalysis":a}); assert r["ok"] and r["potentially_affected_node_ids"]==["run","figure"] and r["potential_impact_only"]

def test_execution_and_comparison():
 e=m.normalize_execution(execution()); assert e["ok"] and e["record"]["externally_supplied_result"] is True
 c=m.compare_execution({**execution(),"expected":[1.0,2.0],"observed":[1.0001,2.0],"absoluteTolerance":0.001}); assert c["ok"] and c["comparison_status"]=="within-declared-tolerance" and c["scientific_claim_confirmed"] is False
 c2=m.compare_execution({**execution(),"expected":[1.0,2.0],"observed":[1.2,2.0],"absoluteTolerance":0.001}); assert c2["comparison_status"]=="outside-declared-tolerance"

def test_verification_bundle_and_audit_draft():
 p=execution(verificationEventId="verify-event-1",verificationOutcome="passed",verificationScope="rerun and compare")
 b=m.verification_bundle(p); assert b["ok"] and b["record"]["id"]=="verification-bundle-run-repro-1" and b["record"]["verification_method"]=="rerun"
 d=m.audit_verification_draft(p); assert d["ok"] and d["event"]["verificationRef"]==b["record"]["id"] and d["automatic_append"] is False

def test_bridge_packet_boundaries_and_contract():
 b=m.bridge_packet(payload()); assert b["ok"] and b["packet"]["target"]=="research-reproduction-replication-studio-v0.129.0" and b["packet"]["automatic_execution"] is False
 h=m.health(); assert h["api_route_count"]==18 and h["v01290_reproduction_engine_reused"]
 a=m.acceptance_report(); assert a["review_to_reproduction_bridge"] and not a["automatic_execution"] and not a["automatic_claim_confirmation"] and not a["truth_ranking"]
