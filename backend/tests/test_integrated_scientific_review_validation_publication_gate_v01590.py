import json
import tempfile
from pathlib import Path
import pytest
from app.integrated_scientific_review_validation_publication_gate_v01590 import IntegratedScientificReviewValidationPublicationGateManager, ScientificReviewGateError, REQUIRED_CHECKS

class CrossStub:
    def get_workspace(self,i): return {"id":i,"projectId":"project:test","status":"frozen"}
    def synthesis(self,i): return {"ok":True,"workspaceId":i,"interpretation":"descriptive"}
    def replication_matrix(self,i): return {"ok":True,"workspaceId":i,"rows":[]}
class NetworkStub:
    def get_network(self,i): return {"id":i,"projectId":"project:test","status":"frozen"}
    def coverage(self,i): return {"ok":True,"networkId":i,"completionFraction":1.0,"interpretation":"descriptive-only"}
    def network_view(self,i): return {"ok":True,"network":{"id":i},"results":[],"reviews":[]}

def mgr(tmp): return IntegratedScientificReviewValidationPublicationGateManager(str(Path(tmp)/"review.sqlite3"),CrossStub(),NetworkStub(),True)
def payload(): return {"title":"Integrated publication review","researchObjectRef":"research:object:1","crossStudyWorkspaceId":"workspace:meta","replicationNetworkId":"network:rep","publicationTarget":"journal-or-repository","scope":"Review the complete reproducible research package."}
def ready(m,did):
    for key in REQUIRED_CHECKS: m.set_check(did,{"key":key,"state":"satisfied","evidenceRefs":["evidence:"+key],"rationale":"Human reviewer marked complete."})

def test_health_and_boundaries():
    with tempfile.TemporaryDirectory() as t:
        h=mgr(t).health(); assert h["version"]=="0.159.0"; assert h["proceduralReadinessEvaluation"] is True; assert h["automaticScientificValidity"] is False; assert h["automaticPublication"] is False

def test_dossier_seeds_required_checks():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; assert d["status"]=="draft"; assert len(d["checks"])==len(REQUIRED_CHECKS); assert {x["state"] for x in d["checks"]}=={"pending"}

def test_evidence_snapshot_reads_cross_study_and_replication_network():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; s=m.evidence_snapshot(d["id"])["snapshot"]; assert s["crossStudy"]["synthesis"]["ok"] is True; assert s["replicationNetwork"]["coverage"]["completionFraction"]==1.0

def test_checklist_state_is_explicit_not_inferred():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; out=m.set_check(d["id"],{"key":"methods-and-protocol-review","state":"satisfied","rationale":"Reviewed by methods reviewer."})["dossier"]; assert next(x for x in out["checks"] if x["key"]=="methods-and-protocol-review")["state"]=="satisfied"

def test_major_finding_blocks_procedural_readiness_until_resolved():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; ready(m,d["id"]); f=m.add_finding(d["id"],{"severity":"major","title":"Mismatch","detail":"Declared protocol mismatch."})["finding"]; assert m.evaluate_gate(d["id"])["proceduralReady"] is False; m.resolve_finding(d["id"],f["id"],{"state":"resolved","resolution":"Corrected and re-reviewed."}); assert m.evaluate_gate(d["id"])["proceduralReady"] is True

def test_review_signoff_preserves_dissent():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; r=m.record_review(d["id"],{"reviewerRef":"person:reviewer","role":"primary-reviewer","decision":"dissent","rationale":"Not ready.","dissent":"Effect interpretation remains disputed."})["review"]; assert r["humanAuthored"] is True; assert r["dissent"]

def test_publication_ready_requires_human_authorization_and_approval():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; did=d["id"]; ready(m,did); m.transition(did,{"targetState":"under-review","reason":"Begin review."}); m.record_review(did,{"reviewerRef":"person:reviewer","role":"primary-reviewer","decision":"approve","rationale":"Procedural review complete."}); m.transition(did,{"targetState":"review-complete","reason":"Checklist complete."})
        with pytest.raises(ScientificReviewGateError): m.transition(did,{"targetState":"publication-ready","reason":"Publish."})
        out=m.transition(did,{"targetState":"publication-ready","reason":"Human approved handoff.","humanAuthorization":True}); assert out["dossier"]["status"]=="publication-ready"

def test_revision_request_blocks_review_completion():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; did=d["id"]; ready(m,did); m.transition(did,{"targetState":"under-review","reason":"Begin review."}); m.record_review(did,{"reviewerRef":"person:methods","role":"methods-reviewer","decision":"revisions-required","rationale":"Clarify exclusions."}); assert m.evaluate_gate(did)["proceduralReady"] is False

def test_publication_packet_is_explicit_handoff_not_publication():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; did=d["id"]; ready(m,did); m.transition(did,{"targetState":"under-review","reason":"Begin."}); m.record_review(did,{"reviewerRef":"person:reviewer","role":"publication-reviewer","decision":"approve","rationale":"Ready for handoff."}); m.transition(did,{"targetState":"review-complete","reason":"Complete."}); m.transition(did,{"targetState":"publication-ready","reason":"Authorized.","humanAuthorization":True}); p=m.publication_packet(did)["packet"]; assert p["automaticPublication"] is False; assert p["requiresExplicitUserAction"] is True; assert p["scientificValidityDetermined"] is False

def test_manifest_tamper_detection():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; bundle=m.manifest(d["id"]); assert m.verify_manifest(bundle)["verified"] is True; bad=json.loads(json.dumps(bundle)); bad["manifest"]["dossier"]["title"]="tampered"; assert m.verify_manifest(bad)["verified"] is False

def test_invalid_transition_rejected():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; 
        with pytest.raises(ScientificReviewGateError): m.transition(d["id"],{"targetState":"publication-ready","reason":"skip" ,"humanAuthorization":True})

def test_archive_retains_dossier():
    with tempfile.TemporaryDirectory() as t:
        m=mgr(t); d=m.create_dossier("project:test",payload())["dossier"]; m.archive(d["id"]); assert m.get_dossier(d["id"])["status"]=="archived"
