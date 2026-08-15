from copy import deepcopy
import pytest

from app.scientific_claims_traceability_v0620 import (
    ScientificClaimsTraceabilityError, build_traceability_packet, evaluate_matrix, health,
    normalize_claim, normalize_conclusion, policies, record_claim_review,
    record_conclusion_review, verify_traceability_packet,
)


def _study(study_type="observational"):
    return {
        "id": "wetland-resilience", "title": "Wetland resilience study", "studyType": study_type, "status": "active",
        "researchQuestion": "How is drought frequency associated with wetland resilience?",
        "methodsSummary": "Governed observational protocol.", "analysisPlan": "Fit and validate declared models.",
        "uncertaintyPlan": "Quantify interval uncertainty.", "conclusionSummary": "Bounded association.",
        "limitations": "Observational design does not establish causality.",
    }


def _project():
    return {"id": "project-one", "studyId": "wetland-resilience", "evidenceCatalog": [
        {"ref": "analysis-1", "sourceType": "analysis", "hash": "a"*64, "title": "Regression result"},
        {"ref": "uncertainty-1", "sourceType": "analysis", "hash": "b"*64, "title": "Uncertainty result"},
        {"ref": "figure-1", "sourceType": "figure", "hash": "c"*64, "title": "Primary figure"},
        {"ref": "experiment-1", "sourceType": "experiment", "hash": "d"*64, "title": "Experiment"},
    ]}


def _claim(claim_type="associational", contradiction=False):
    links = [
        {"role": "supports", "sourceType": "analysis", "ref": "analysis-1", "hash": "a"*64},
        {"role": "uncertainty", "sourceType": "analysis", "ref": "uncertainty-1", "hash": "b"*64},
        {"role": "contextualizes", "sourceType": "figure", "ref": "figure-1", "hash": "c"*64},
    ]
    if contradiction:
        links.append({"role": "contradicts", "sourceType": "external-reference", "ref": "external-study-7", "note": "Different population."})
    return {"id": "claim-1", "studyId": "wetland-resilience", "statement": "Higher drought frequency is associated with lower wetland resilience.", "claimType": claim_type, "status": "active", "scopeNote": "Observed wetland sample only.", "evidenceLinks": links}


def _conclusion():
    return {"id": "conclusion-1", "studyId": "wetland-resilience", "statement": "The study supports a bounded association between drought frequency and resilience.", "claimIds": ["claim-1"], "caveats": "Observational design, sampling, and measurement limits remain."}


def _review_claim(claim, decision="accept"):
    return record_claim_review({"claim": claim, "review": {"decision": decision, "rationale": "Evidence, uncertainty, and scope were reviewed by the researcher.", "reviewedAt": "2026-08-15T12:00:00-05:00"}})["claim"]


def _review_conclusion(conclusion):
    return record_conclusion_review({"conclusion": conclusion, "review": {"decision": "accept", "rationale": "Conclusion wording and linked claims were reviewed.", "reviewedAt": "2026-08-15T12:01:00-05:00"}})["conclusion"]


def test_health_and_policy_keep_claims_human_governed():
    h = health(); p = policies()
    assert h["status"] == "scientific-claims-traceability-ready"
    assert p["humanClaimReviewRequired"] is True
    assert p["automaticClaimInferenceAuthorized"] is False
    assert p["automaticCausalClaimAuthorized"] is False


def test_claim_normalization_is_deterministic_and_typed():
    a = normalize_claim(_claim()); b = normalize_claim(_claim())
    assert a["claimHash"] == b["claimHash"]
    assert a["schema"] == "sc-lab-scientific-claim/0.62.0"
    assert a["evidenceLinks"][0]["sourceType"] == "analysis"


def test_claim_layer_rejects_raw_data_credentials_callbacks_and_code():
    for extra in ({"rows": [{"x": 1}]}, {"credentials": {"token": "x"}}, {"callbackUrl": "https://x"}, {"code": "print(1)"}):
        with pytest.raises(ScientificClaimsTraceabilityError):
            normalize_claim({**_claim(), **extra})


def test_evidence_matrix_requires_primary_support_and_uncertainty_context():
    claim = _claim(); claim["evidenceLinks"] = [{"role": "supports", "sourceType": "figure", "ref": "figure-1"}]
    result = evaluate_matrix({"study": _study(), "project": _project(), "claims": [claim], "conclusions": [_conclusion()]})
    assert result["gate"] == "needs-evidence"
    assert "claim-1" in result["missingEvidenceClaimIds"]


def test_unresolved_internal_evidence_reference_is_not_silently_accepted():
    claim = _claim(); claim["evidenceLinks"][0]["ref"] = "missing-analysis"
    result = evaluate_matrix({"study": _study(), "project": _project(), "claims": [claim], "conclusions": [_conclusion()]})
    row = result["claimRows"][0]
    assert row["gate"] == "needs-evidence"
    assert "missing-analysis" in row["unresolvedEvidenceRefs"]


def test_contradicting_evidence_is_preserved_and_requires_qualified_review():
    claim = _review_claim(_claim(contradiction=True), "accept")
    result = evaluate_matrix({"study": _study(), "project": _project(), "claims": [claim], "conclusions": [_conclusion()]})
    assert result["claimRows"][0]["gate"] == "contested"
    qualified = _review_claim(_claim(contradiction=True), "accept-with-qualification")
    result2 = evaluate_matrix({"study": _study(), "project": _project(), "claims": [qualified], "conclusions": [_conclusion()]})
    assert result2["claimRows"][0]["gate"] == "traceable"


def test_causal_claim_is_blocked_outside_experimental_or_mixed_design():
    result = evaluate_matrix({"study": _study("observational"), "project": _project(), "claims": [_claim("causal")], "conclusions": [_conclusion()]})
    assert result["claimRows"][0]["gate"] == "blocked"
    assert result["claimRows"][0]["causalDesignCompatible"] is False


def test_claim_review_requires_rationale_and_is_hash_chained_record():
    with pytest.raises(ScientificClaimsTraceabilityError):
        record_claim_review({"claim": _claim(), "review": {"decision": "accept", "rationale": ""}})
    out = record_claim_review({"claim": _claim(), "review": {"decision": "accept", "rationale": "Reviewed supporting and uncertainty evidence."}})
    assert len(out["review"]["reviewHash"]) == 64
    assert out["claim"]["reviewHistory"][-1]["decision"] == "accept"


def test_conclusion_requires_linked_claim_context_and_human_review():
    claim = _review_claim(_claim())
    result = evaluate_matrix({"study": _study(), "project": _project(), "claims": [claim], "conclusions": [_conclusion()]})
    assert result["conclusionRows"][0]["gate"] == "needs-review"
    broken = _conclusion(); broken["claimIds"] = []
    result2 = evaluate_matrix({"study": _study(), "project": _project(), "claims": [claim], "conclusions": [broken]})
    assert result2["conclusionRows"][0]["gate"] == "needs-trace"


def test_fully_reviewed_claim_and_conclusion_reach_traceable_not_certified():
    claim = _review_claim(_claim())
    conclusion = _review_conclusion(_conclusion())
    result = evaluate_matrix({"study": _study(), "project": _project(), "claims": [claim], "conclusions": [conclusion]})
    assert result["gate"] == "traceable"
    assert result["scientificCertificationClaim"] is False
    assert result["causalValidityClaim"] is False


def test_orphan_claims_are_visible_in_matrix_instead_of_hidden():
    claim = _review_claim(_claim())
    conclusion = _review_conclusion({**_conclusion(), "claimIds": ["other-claim"]})
    result = evaluate_matrix({"study": _study(), "project": _project(), "claims": [claim], "conclusions": [conclusion]})
    assert "claim-1" in result["orphanClaimIds"]
    assert result["conclusionRows"][0]["unknownClaimIds"] == ["other-claim"]


def test_traceability_packet_is_deterministic_metadata_only_and_tamper_evident():
    claim = _review_claim(_claim())
    conclusion = _review_conclusion(_conclusion())
    payload = {"study": _study(), "project": _project(), "claims": [claim], "conclusions": [conclusion]}
    first = build_traceability_packet(payload)["packet"]; second = build_traceability_packet(payload)["packet"]
    assert first["packetHash"] == second["packetHash"]
    assert first["boundaries"]["rawScientificDataIncluded"] is False
    assert first["boundaries"]["automaticConclusionGeneration"] is False
    assert verify_traceability_packet({"packet": first})["ok"] is True
    broken = deepcopy(first); broken["gate"] = "blocked"
    assert verify_traceability_packet({"packet": broken})["ok"] is False
