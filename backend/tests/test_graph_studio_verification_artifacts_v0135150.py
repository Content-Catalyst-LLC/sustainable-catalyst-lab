from app import graph_studio_verification_artifacts_v0135150 as m

SHA = "a" * 64

def bundle(sha=SHA):
    return {
        "id": "vb1",
        "threadId": "t1",
        "resolutionRecordId": "rr1",
        "auditRecordId": "au1",
        "annotationId": "a1",
        "verificationEventId": "e1",
        "verificationOutcome": "passed",
        "verificationMethod": "method-check",
        "verificationScope": "Confirm revised method and rerun outputs",
        "artifacts": [
            {"id": "x1", "artifactType": "method", "artifactRef": "method-rev-2", "versionRef": "rev2", "sha256": sha},
            {"id": "x2", "artifactType": "execution", "artifactRef": "run-7", "executionRef": "run-7"},
        ],
    }

def audit(ref="vb1"):
    return {"id":"au1","events":[{"id":"e1","annotationId":"a1","eventType":"verification-recorded","outcome":"passed","verificationMethod":"method-check","verificationRef":ref}]}

def payload():
    return {"bundle": bundle(), "auditRecord": audit()}

def test_normalize_bundle_and_summary():
    n=m.normalize_bundle(payload()); assert n["ok"] and n["artifact_count"]==2
    s=m.summarize(payload()); assert s["artifact_count"]==2 and s["by_type"]["method"]==1 and s["sha256_count"]==1

def test_audit_binding_is_explicit():
    v=m.validate_bundle(payload()); assert v["ok"] and v["binding_valid"] is True
    bad={"bundle":bundle(),"auditRecord":audit("some-other-ref")}; v2=m.validate_bundle(bad); assert v2["ok"] is False and v2["binding_valid"] is False

def test_sha256_validation():
    bad=bundle("not-a-digest"); n=m.normalize_bundle({"bundle":bad}); assert n["ok"] is False and "sha256" in n["error"]

def test_integrity_and_fingerprint():
    i=m.integrity(payload()); assert i["ok"] and len(i["bundle_fingerprint"])==64
    f=m.fingerprint(payload()); assert f["ok"] and len(f["fingerprint"])==64

def test_compare_detects_changed_artifact():
    left=bundle(); right=bundle(); right["id"]="vb2"; right["verificationEventId"]="e2"; right["artifacts"][0]["versionRef"]="rev3"
    c=m.compare({"left":left,"right":right}); assert c["ok"] and "method-rev-2" in c["changed_artifact_refs"] and "run-7" in c["unchanged_artifact_refs"]

def test_packet_and_contract():
    p=m.verification_packet(payload()); assert p["ok"] and p["target"]=="project-workspace" and p["validation"]["binding_valid"] is True
    h=m.health(); assert h["api_route_count"]==13 and h["typed_verification_artifacts"] and h["backward_compatible_v0135140"]
    a=m.acceptance_report(); assert a["multi_artifact_evidence_bundles"] and not a["audit_history_mutation"] and not a["truth_ranking"]
