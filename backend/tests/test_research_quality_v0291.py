from fastapi.testclient import TestClient
from app.main import app
from app.research_quality import compare_reviews, evaluate_review, normalize_review, verify_review

client = TestClient(app)


def standard_payload():
    return {
        "methodId": "numerical.root.bracketed_polynomial",
        "title": "Bracketed polynomial root",
        "methodVersion": "0.27.0",
        "riskTier": "standard",
        "status": "under-review",
        "benchmarkIds": ["root.sqrt2.brent"],
        "benchmarkCoverage": {"passed": 1, "total": 1},
        "validationEvidenceIds": ["ev-1"],
        "sourceIds": ["src-1"],
        "evidenceIds": ["ev-1"],
        "reproducibleRunIds": ["run-1"],
        "provenanceIds": ["prov-1"],
        "limitations": ["Bracket must contain a sign change."],
        "calibration": {"status": "not-required"},
        "reviewer": {"name": "Reviewer", "role": "Method reviewer", "independent": True},
        "reviewerNotes": "Known-answer fixture and convergence behavior reviewed.",
    }


def test_normalize_and_verify():
    review = normalize_review(standard_payload())
    assert review["version"] == "0.29.1"
    assert review["benchmarkCoverage"]["percent"] == 100.0
    assert verify_review({"review": review})["ok"] is True


def test_standard_review_ready():
    result = evaluate_review(standard_payload())
    assert result["evaluation"]["readyForApproval"] is True
    assert result["evaluation"]["score"] >= 70


def test_high_consequence_requires_independent_reviewer_and_more_evidence():
    payload = standard_payload()
    payload["riskTier"] = "high-consequence"
    payload["reviewer"]["independent"] = False
    result = evaluate_review(payload)
    assert result["evaluation"]["readyForApproval"] is False
    assert any("independent reviewer" in item for item in result["evaluation"]["issues"])


def test_compare_review_revisions():
    left = normalize_review(standard_payload())
    changed = standard_payload(); changed["status"] = "approved"; changed["decision"] = "approve"
    right = normalize_review(changed)
    result = compare_reviews({"left": left, "right": right})
    assert result["comparison"]["status"] == "changed"
    assert any(item["field"] == "status" for item in result["comparison"]["differences"])


def test_research_quality_api():
    health = client.get('/v1/research-quality/health').json()
    assert health["version"] == "0.29.1"
    policies = client.get('/v1/research-quality/policies').json()
    assert "high-consequence" in policies["requirements"]
    normalized = client.post('/v1/research-quality/reviews/normalize', json=standard_payload()).json()
    assert normalized["ok"] is True
    evaluated = client.post('/v1/research-quality/reviews/evaluate', json=standard_payload()).json()
    assert evaluated["evaluation"]["readyForApproval"] is True
    verified = client.post('/v1/research-quality/reviews/verify', json={"review": normalized["review"]}).json()
    assert verified["ok"] is True
