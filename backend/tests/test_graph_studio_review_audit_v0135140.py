from app import graph_studio_review_audit_v0135140 as m

def payload(events=None, action="revise-method", disposition="addressed"):
    return {"thread":{"annotations":[{"id":"a1"},{"id":"a2"}]},"resolutionRecord":{"id":"rr1","resolutions":[{"id":"r1","annotationId":"a1","disposition":disposition,"action":action,"response":"done","revisionRef":"rev2"}]},"auditRecord":{"id":"au1","threadId":"t1","resolutionRecordId":"rr1","events":events or []}}

def test_state_requires_verification_for_revision_action(): assert m.state_for(payload(),"a1")=="action-required"
def test_no_action_ready_to_resolve(): assert m.state_for(payload(action="none"),"a1")=="ready-to-resolve"
def test_verification_pass_then_resolution():
    ev=[{"id":"e1","annotationId":"a1","eventType":"verification-recorded","outcome":"passed","verificationMethod":"method-check","verificationRef":"method-rev-2","note":"checked","previousEventId":None},{"id":"e2","annotationId":"a1","eventType":"resolution-confirmed","note":"confirmed","previousEventId":"e1"}]
    p=payload(ev); assert m.state_for(p,"a1")=="resolved"; assert m.integrity(p)["chain_valid"] is True; assert m.audit_trail(p)["event_count"]==2

def test_failed_verification_not_ready():
    ev=[{"id":"e1","annotationId":"a1","eventType":"verification-recorded","outcome":"failed","verificationMethod":"rerun","verificationRef":"run-7","note":"mismatch","previousEventId":None}]
    p=payload(ev); assert m.state_for(p,"a1")=="verification-failed"; assert m.resolution_readiness(p)["ready_count"]==0

def test_invalid_verification_rejected():
    p=payload(); p.update({"annotationId":"a1","outcome":"passed","verificationMethod":"method-check","verificationRef":""}); assert m.verify_action(p)["ok"] is False

def test_deferred_can_reopen():
    p=payload(action="follow-up",disposition="deferred"); p.update({"annotationId":"a1","eventType":"reopened"}); assert m.transition(p)["allowed"] is True

def test_integrity_detects_bad_link():
    ev=[{"id":"e1","annotationId":"a1","eventType":"action-started","note":"start","previousEventId":"wrong"}]; assert m.integrity(payload(ev))["ok"] is False

def test_contracts():
    assert m.health()["api_route_count"]==13; a=m.acceptance_report(); assert a["review_state_machine"] and a["action_verification"] and a["append_only_resolution_audit"] and not a["resolution_mutation"] and not a["truth_ranking"]
