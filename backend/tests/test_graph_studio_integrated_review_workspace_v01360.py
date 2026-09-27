
from app import graph_studio_integrated_scientific_review_reproducibility_v01360 as integrated

def sample_payload():
    return {
        "projectId": "demo-project",
        "reviewThreads": [{"id":"rt-1","status":"closed"}],
        "resolutionRecords": [{"id":"res-1","thread_id":"rt-1"}],
        "auditRecords": [{"id":"audit-1","verification_event_id":"ver-1"}],
        "verificationBundles": [{"id":"vb-1","integrity_ok": True}],
        "impactAnalyses": [{"id":"imp-1"}],
        "reproductionBridges": [{"id":"rep-1","state":"completed"}],
        "reviewerPanels": [{"id":"panel-1","thread_id":"rt-1","dissents": []}],
        "crossReviewSyntheses": []
    }

def test_integration_normalizes():
    out = integrated.normalize_workspace(sample_payload())
    assert out["ok"] is True
    assert out["workspace"]["projectId"] == "demo-project"
    assert out["workspace"]["workspace"]["fullGraphRedraw"] is False

def test_digest_present():
    out = integrated.workspace_digest(sample_payload())
    assert out["ok"] is True
    assert out["workspaceDigest"]
    assert out["integrationDigest"]
