import copy
import pytest

from app.scientific_argumentation_v0660 import (
    ScientificArgumentationError,
    health,
    policies,
    normalize_case,
    normalize_hypothesis,
    normalize_evidence_link,
    normalize_discriminating_test,
    record_hypothesis_review,
    record_case_review,
    evaluate_argumentation,
    build_argumentation_packet,
    verify_argumentation_packet,
)


def claim(cid="claim-1"):
    return {
        "id": cid,
        "studyId": "study-1",
        "statement": f"Scientific claim {cid}",
        "claimType": "associational",
        "status": "active",
        "scopeNote": "Bounded claim scope.",
        "evidenceLinks": [{"role": "supports", "sourceType": "analysis", "ref": f"analysis-{cid}"}],
    }


def hypothesis(hid, decision=None, test_id="test-1", outcome="increase"):
    h = {
        "id": hid,
        "title": f"Hypothesis {hid}",
        "statement": f"Mechanism proposed by {hid}",
        "mechanism": "A bounded explanatory mechanism.",
        "linkedClaimIds": ["claim-1"],
        "scopeNote": "Applies to the active study scope.",
        "predictions": [{"id": f"pred-{hid}", "statement": f"Prediction for {hid}", "expectedOutcome": outcome, "testId": test_id}],
    }
    if decision:
        h = record_hypothesis_review({"hypothesis": h, "review": {"decision": decision, "rationale": "Hypothesis reviewed against the available evidence."}})["hypothesis"]
    return h


def case(decision=None):
    c = {
        "id": "argument-1",
        "title": "Competing explanations",
        "researchQuestion": "Which explanation best accounts for the observed pattern?",
        "claimIds": ["claim-1"],
        "evidenceBoundaryAssessmentIds": ["boundary-1"],
        "scopeNote": "Bounded to the active study population and context.",
        "decisionBoundary": "Alternative explanations remain provisional and bounded by the current evidence record.",
    }
    if decision:
        c = record_case_review({"case": c, "review": {"decision": decision, "rationale": "The argument map and unresolved alternatives were explicitly reviewed."}})["case"]
    return c


def discriminating_test():
    return {
        "id": "test-1",
        "title": "Discriminating observation",
        "methodRef": "method-1",
        "evidenceRef": "evidence-test",
        "status": "observed",
        "expectations": [
            {"hypothesisId": "h1", "expectedOutcome": "increase", "predictionId": "pred-h1"},
            {"hypothesisId": "h2", "expectedOutcome": "no-effect", "predictionId": "pred-h2"},
        ],
    }


def evidence_catalog():
    return [
        {"id": "evidence-a", "type": "claim-evidence", "hash": "a" * 64, "gate": "traceable", "claimIds": ["claim-1"]},
        {"id": "evidence-b", "type": "literature", "hash": "b" * 64, "gate": "traceable", "claimIds": ["claim-1"]},
        {"id": "evidence-test", "type": "experiment", "hash": "c" * 64, "gate": "reviewed", "claimIds": ["claim-1"]},
    ]


def links(falsify_h2=False):
    rows = [
        {"id": "l1", "hypothesisId": "h1", "evidenceRef": "evidence-a", "relation": "supports"},
        {"id": "l2", "hypothesisId": "h2", "evidenceRef": "evidence-b", "relation": "supports"},
    ]
    if falsify_h2:
        rows.append({"id": "l3", "hypothesisId": "h2", "evidenceRef": "evidence-test", "relation": "falsifying-candidate", "testId": "test-1"})
    else:
        rows.append({"id": "l3", "hypothesisId": "h1", "evidenceRef": "evidence-test", "relation": "discriminates-for", "testId": "test-1"})
    return rows


def payload(h1_decision="retain", h2_decision="retain", case_decision=None, falsify_h2=False):
    return {
        "case": case(case_decision),
        "hypotheses": [hypothesis("h1", h1_decision, outcome="increase"), hypothesis("h2", h2_decision, outcome="no-effect")],
        "evidenceLinks": links(falsify_h2),
        "tests": [discriminating_test()],
        "evidenceCatalog": evidence_catalog(),
        "claims": [claim()],
    }


def test_health_and_policy_boundaries_are_explicit():
    h = health(); p = policies()
    assert h["status"] == "scientific-argumentation-ready"
    assert p["competingHypothesesSupported"] is True
    assert p["automaticHypothesisProofAuthorized"] is False
    assert p["automaticWinnerSelectionAuthorized"] is False
    assert p["automaticFalsificationAuthorized"] is False


def test_case_and_hypothesis_are_deterministic_and_hashed():
    c1 = normalize_case(case()); c2 = normalize_case(case())
    h1 = normalize_hypothesis(hypothesis("h1")); h2 = normalize_hypothesis(hypothesis("h1"))
    assert c1["caseHash"] == c2["caseHash"] and len(c1["caseHash"]) == 64
    assert h1["hypothesisHash"] == h2["hypothesisHash"] and len(h1["hypothesisHash"]) == 64


def test_raw_data_credentials_full_text_and_code_are_rejected():
    for extra in ({"rows": [1]}, {"credentials": {"token": "x"}}, {"fullText": "paper"}, {"code": "print(1)"}):
        with pytest.raises(ScientificArgumentationError):
            normalize_case({**case(), **extra})


def test_evidence_and_discriminating_test_normalization_require_governed_refs():
    link = normalize_evidence_link({"hypothesisId": "h1", "evidenceRef": "e1", "relation": "supports"})
    test = normalize_discriminating_test(discriminating_test())
    assert link["schema"] == "sc-lab-hypothesis-evidence-link/0.66.0"
    assert test["schema"] == "sc-lab-discriminating-test/0.66.0"
    with pytest.raises(ScientificArgumentationError):
        normalize_evidence_link({"hypothesisId": "h1", "evidenceRef": "e1", "relation": "winner"})


def test_single_hypothesis_requires_competing_alternative():
    p = payload(); p["hypotheses"] = p["hypotheses"][:1]
    result = evaluate_argumentation(p)
    assert result["gate"] == "needs-alternatives"
    assert result["automaticWinnerSelection"] is False


def test_missing_predictions_are_not_silently_filled():
    p = payload(); p["hypotheses"][1]["predictions"] = []
    result = evaluate_argumentation(p)
    assert result["gate"] == "needs-predictions"
    assert any(r["state"] == "needs-predictions" for r in result["hypothesisRows"])


def test_discriminating_test_requires_distinct_predictions_for_multiple_hypotheses():
    p = payload(); p["tests"][0]["expectations"][1]["expectedOutcome"] = "increase"
    result = evaluate_argumentation(p)
    assert result["gate"] == "needs-discriminating-test"
    assert result["discriminatingTestCount"] == 0


def test_unresolved_evidence_reference_is_visible_and_blocks_progression():
    p = payload(); p["evidenceLinks"][0]["evidenceRef"] = "missing-evidence"
    result = evaluate_argumentation(p)
    assert result["gate"] == "needs-evidence"
    assert "missing-evidence" in result["unresolvedEvidenceRefs"]


def test_falsifying_candidate_is_preserved_but_does_not_auto_reject():
    p = payload(h2_decision=None, falsify_h2=True)
    result = evaluate_argumentation(p)
    h2 = next(r for r in result["hypothesisRows"] if r["hypothesisId"] == "h2")
    assert h2["falsificationChallenge"] is True
    assert h2["state"] == "falsification-challenge"
    assert result["gate"] == "falsification-challenge"
    assert h2["automaticFalsification"] is False


def test_unresolved_alternatives_require_explicit_case_review_boundary():
    result = evaluate_argumentation(payload())
    assert result["gate"] == "alternatives-unresolved"
    reviewed = evaluate_argumentation(payload(case_decision="accept-with-unresolved-alternatives"))
    assert reviewed["gate"] == "argument-bounded-with-unresolved-alternatives"
    assert reviewed["unresolvedAlternatives"] is True


def test_single_provisional_preference_is_reviewable_but_never_proven():
    result = evaluate_argumentation(payload(h1_decision="provisionally-prefer", h2_decision="retain", case_decision="accept-argument-map"))
    assert result["gate"] == "provisional-preference-reviewed"
    assert result["provisionallyPreferredHypothesisIds"] == ["h1"]
    assert result["automaticHypothesisProof"] is False
    assert result["numericTruthScore"] is None


def test_rejected_alternative_can_leave_bounded_argument_without_proof_claim():
    result = evaluate_argumentation(payload(h1_decision="retain", h2_decision="reject", case_decision="accept-argument-map"))
    assert result["gate"] == "argument-bounded"
    assert result["activeHypothesisIds"] == ["h1"]
    assert result["automaticHypothesisProof"] is False


def test_packet_is_metadata_only_deterministic_and_tamper_evident():
    p = payload(case_decision="accept-with-unresolved-alternatives")
    a = build_argumentation_packet(p); b = build_argumentation_packet(p)
    assert a["packetHash"] == b["packetHash"]
    assert a["gate"] == "argument-bounded-with-unresolved-alternatives"
    assert all(k not in a for k in ("rows", "rawData", "credentials", "fullText", "inputs"))
    assert verify_argumentation_packet({"packet": a})["ok"] is True
    broken = copy.deepcopy(a); broken["gate"] = "argument-bounded"
    assert verify_argumentation_packet({"packet": broken})["ok"] is False
