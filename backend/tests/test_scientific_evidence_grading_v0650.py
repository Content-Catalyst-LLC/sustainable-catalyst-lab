import copy
import pytest

from app.scientific_evidence_grading_v0650 import (
    ScientificEvidenceGradingError,
    health,
    policies,
    normalize_assessment,
    record_boundary_review,
    evaluate_evidence,
    build_consensus_packet,
    verify_consensus_packet,
)
from app.scientific_claims_traceability_v0620 import record_claim_review
from app.scientific_literature_provenance_v0630 import record_source_review


def claim(claim_id="claim-1", decision=None):
    c = {
        "id": claim_id,
        "studyId": "study-1",
        "statement": f"Scientific claim {claim_id}",
        "claimType": "associational",
        "status": "active",
        "scopeNote": "Bounded population and context.",
        "evidenceLinks": [{"role": "supports", "sourceType": "analysis", "ref": f"analysis-{claim_id}"}],
    }
    if decision:
        c = record_claim_review({
            "claim": c,
            "review": {"decision": decision, "rationale": "Claim evidence and limitations were reviewed."},
        })["claim"]
    return c


def source(source_id, decision="include", caution=False):
    s = {
        "id": source_id,
        "sourceType": "journal-article",
        "title": f"Study {source_id}",
        "status": "active",
        "peerReviewStatus": "peer-reviewed",
        "scopeNote": "Source applicability reviewed.",
    }
    if decision:
        s = record_source_review({
            "source": s,
            "review": {
                "decision": "include-with-caution" if caution else decision,
                "rationale": "Source methods and applicability were reviewed.",
            },
        })["source"]
    return s


def link(source_id, role="supports", claim_id="claim-1"):
    return {"claimId": claim_id, "sourceId": source_id, "role": role, "note": "Human-mapped source-to-claim link."}


def synthesis(claim_id="claim-1", i2=10.0, replication_gate="directionally-consistent", gate="synthesis-reviewed"):
    return {
        "recordType": "systematic-evidence-synthesis-v0640",
        "packet": {
            "protocolId": "syn-1",
            "protocolHash": "a" * 64,
            "packetHash": "b" * 64,
            "gate": gate,
            "claimCoverage": {claim_id: 3},
            "metaAnalysis": {
                "k": 3,
                "model": "random-effects",
                "pooledEffect": 0.25,
                "ciLow": 0.10,
                "ciHigh": 0.40,
                "iSquaredPercent": i2,
                "tauSquared": 0.01,
            },
            "replicationRows": [{
                "replicationSourceId": "s3",
                "originalSourceId": "s1",
                "gate": replication_gate,
            }],
        },
    }


def assessment(**kw):
    a = {
        "id": "boundary-1",
        "title": "Evidence boundary",
        "claimIds": ["claim-1"],
        "synthesisProtocolIds": ["syn-1"],
        "scopePopulation": "Defined study population",
        "scopeContext": "Defined study context",
        "scopeOutcome": "Defined outcome",
        "boundaryStatement": "Within the stated population and context, the reviewed evidence supports a bounded conclusion.",
        "qualificationNote": "Contradictions, heterogeneity, and source limitations remain explicit.",
    }
    a.update(kw)
    return a


def payload(claim_decision="accept", **kw):
    p = {
        "assessment": assessment(),
        "claims": [claim(decision=claim_decision)],
        "sources": [source("s1"), source("s2"), source("s3")],
        "claimLinks": [link("s1"), link("s2"), link("s3", "replication")],
        "syntheses": [synthesis()],
    }
    p.update(kw)
    return p


def test_health_and_policy_boundaries_are_explicit():
    h = health(); p = policies()
    assert h["status"] == "scientific-evidence-grading-ready"
    assert p["transparentRuleBasedEvidenceGrading"] is True
    assert p["numericTruthScoreAuthorized"] is False
    assert p["automaticConsensusCertificationAuthorized"] is False
    assert p["citationCountAuthorityScoringAuthorized"] is False


def test_assessment_is_deterministic_and_hashed():
    a = normalize_assessment(assessment())
    b = normalize_assessment(assessment())
    assert a["assessmentHash"] == b["assessmentHash"]
    assert len(a["assessmentHash"]) == 64
    assert a["schema"] == "sc-lab-scientific-evidence-grading-assessment/0.65.0"


def test_raw_data_credentials_full_text_and_code_are_rejected():
    for extra in ({"rows": [1]}, {"credentials": {"token": "x"}}, {"fullText": "paper"}, {"code": "print(1)"}):
        with pytest.raises(ScientificEvidenceGradingError):
            normalize_assessment({**assessment(), **extra})


def test_no_support_is_insufficient_and_not_a_consensus_score():
    result = evaluate_evidence({"assessment": assessment(), "claims": [claim(decision="accept")], "sources": [], "claimLinks": [], "syntheses": []})
    row = result["claimGrades"][0]
    assert row["evidenceGrade"] == "limited"  # one internal governed support from the claim record
    assert result["gate"] == "needs-evidence"
    assert result["consensusBoundary"]["numericTruthScore"] is None


def test_reviewed_support_without_synthesis_is_moderate_but_not_consensus():
    result = evaluate_evidence({
        "assessment": assessment(),
        "claims": [claim(decision="accept")],
        "sources": [source("s1"), source("s2")],
        "claimLinks": [link("s1"), link("s2")],
        "syntheses": [],
    })
    assert result["claimGrades"][0]["evidenceGrade"] == "moderate"
    assert result["gate"] == "needs-review"


def test_reviewed_synthesis_and_consistent_replication_can_be_substantial():
    result = evaluate_evidence(payload())
    row = result["claimGrades"][0]
    assert row["evidenceGrade"] == "substantial"
    assert row["replicationConsistencyCount"] == 1
    assert row["consensusCandidate"] == "bounded-consensus-candidate"
    assert result["gate"] == "needs-review"


def test_direct_contradiction_is_preserved_and_contested():
    p = payload(claim_decision="accept")
    p["sources"].append(source("s4"))
    p["claimLinks"].append(link("s4", "contradicts"))
    result = evaluate_evidence(p)
    row = result["claimGrades"][0]
    assert row["evidenceGrade"] == "contested"
    assert "s4" in row["literatureContradictionSourceIds"]
    assert result["gate"] == "contested"


def test_high_heterogeneity_is_a_consensus_boundary():
    p = payload(syntheses=[synthesis(i2=82.0)])
    result = evaluate_evidence(p)
    assert result["claimGrades"][0]["highHeterogeneity"] is True
    assert result["claimGrades"][0]["evidenceGrade"] == "contested"
    assert result["gate"] == "contested"


def test_replication_disagreement_is_preserved_as_contradiction():
    p = payload(syntheses=[synthesis(replication_gate="discordant-direction")])
    result = evaluate_evidence(p)
    assert result["claimGrades"][0]["replicationDisagreementCount"] == 1
    assert result["contradictions"][0]["requiresQualifiedInterpretation"] is True
    assert result["gate"] == "contested"


def test_source_caution_prevents_unqualified_strong_boundary_candidate():
    p = payload()
    p["sources"] = [source("s1", caution=True), source("s2"), source("s3")]
    result = evaluate_evidence(p)
    row = result["claimGrades"][0]
    assert row["sourceCautionPresent"] is True
    assert row["consensusCandidate"] == "qualified-agreement-candidate"


def test_blocked_claim_propagates_to_boundary():
    result = evaluate_evidence(payload(claim_decision="block"))
    assert result["claimGrades"][0]["consensusCandidate"] == "blocked"
    assert result["gate"] == "blocked"


def test_human_boundary_review_is_required_for_consensus_and_qualified_disagreement():
    p = payload()
    assert evaluate_evidence(p)["gate"] == "needs-review"
    reviewed = record_boundary_review({
        "assessment": p["assessment"],
        "review": {"decision": "accept-boundary", "rationale": "Scope and evidence boundary were reviewed by the researcher."},
    })["assessment"]
    p["assessment"] = reviewed
    assert evaluate_evidence(p)["gate"] == "consensus-bounded"

    contested = payload(claim_decision="accept-with-qualification", syntheses=[synthesis(i2=80.0)])
    qualified = record_boundary_review({
        "assessment": contested["assessment"],
        "review": {"decision": "accept-with-qualification", "rationale": "High heterogeneity remains material and is explicitly qualified."},
    })["assessment"]
    contested["assessment"] = qualified
    assert evaluate_evidence(contested)["gate"] == "consensus-bounded-with-qualification"


def test_packet_is_metadata_only_deterministic_and_tamper_evident():
    p = payload()
    p["assessment"] = record_boundary_review({
        "assessment": p["assessment"],
        "review": {"decision": "accept-boundary", "rationale": "The bounded evidence statement was reviewed."},
    })["assessment"]
    a = build_consensus_packet(p)
    b = build_consensus_packet(p)
    assert a["packetHash"] == b["packetHash"]
    assert a["gate"] == "consensus-bounded"
    assert all(k not in a for k in ("rows", "rawData", "credentials", "fullText", "inputs"))
    assert verify_consensus_packet({"packet": a})["ok"] is True
    broken = copy.deepcopy(a); broken["gate"] = "contested"
    assert verify_consensus_packet({"packet": broken})["ok"] is False
