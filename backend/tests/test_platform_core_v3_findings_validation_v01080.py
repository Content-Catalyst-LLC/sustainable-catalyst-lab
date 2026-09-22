import pytest

from app.platform_core_v3_findings_validation_v01080 import (
    MINIMUM_CORE_RELEASE,
    PlatformCoreV3FindingsValidationError,
    build_core_claim_binding,
    build_core_contradiction_binding,
    build_core_evidence_link_binding,
    build_core_finding_binding,
    build_core_replication_binding,
    build_core_validation_challenge_binding,
    health,
    manifest,
    map_legacy_scientific_claim,
    normalize_claim,
    normalize_finding,
)


def context(**extra):
    value = {
        "project_ref": "project:energy-study",
        "session_id": "88",
        "session_key": "energy-study-2026",
        "title": "Energy Study",
        "workflow_ref": "lab:workflow:w-energy",
        "project_state_ref": "core:project-state:88",
        "researcher_ref": "researcher:tariq",
        "visibility": "private",
    }
    value.update(extra)
    return value


def lab_claim(**extra):
    value = {
        "id": "claim-1",
        "studyId": "study-1",
        "statement": "Storage availability is associated with lower curtailment in the modeled scenario.",
        "claimType": "associational",
        "status": "active",
        "scopeNote": "Modeled regional grid scenario.",
        "evidenceLinks": [
            {"id": "ev-1", "role": "supports", "sourceType": "analysis", "ref": "lab:artifact:result-1", "note": "Primary analysis"},
            {"id": "ev-2", "role": "limitation", "sourceType": "model", "ref": "lab:model:grid-1", "note": "Scenario model limits"},
        ],
        "reviewHistory": [
            {"id": "rev-1", "decision": "accept-with-qualification", "rationale": "Association only.", "reviewerRole": "researcher", "reviewedAt": "2026-09-22T02:00:00Z"}
        ],
    }
    value.update(extra)
    return value


def test_health_and_manifest_preserve_scientific_boundaries():
    h = health(); m = manifest()
    assert h["lab_release_version"] == "0.108.0"
    assert h["minimum_core_release"] == MINIMUM_CORE_RELEASE == "3.0.0"
    assert h["automatic_claim_inference"] is False
    assert h["automatic_evidence_judgment"] is False
    assert h["automatic_replication_certification"] is False
    assert m["boundaries"]["lab_remains_authoritative_for_underlying_science"] is True
    assert m["boundaries"]["bridge_determines_truth"] is False


def test_finding_normalization_and_core_binding_are_reference_first():
    payload = {
        "context": context(),
        "finding": {
            "id": "finding-1",
            "title": "Curtailment result",
            "statement": "Curtailment declined in the declared modeled scenario.",
            "finding_type": "result",
            "status": "recorded",
            "method_ref": "lab:method:dispatch-model:v1",
            "execution_ref": "lab:execution:run-1",
            "source_refs": ["lab:artifact:result-1"],
            "uncertainty": {"interval_ref": "lab:artifact:interval-1"},
            "limitations": ["Scenario dependent"],
        },
    }
    n = normalize_finding(payload)
    assert n["finding"]["finding_key"] == "finding-1"
    assert len(n["finding"]["finding_hash"]) == 64
    b = build_core_finding_binding(payload)
    assert b["target_path"].endswith("/projects/project%3Aenergy-study/findings")
    assert b["automatic_submission"] is False
    assert b["data"]["analysis_run_ref"] == "lab:execution:run-1"
    assert b["data"]["metadata"]["underlying_finding_remains_authoritative_in_lab"] is True


def test_lab_v062_claim_maps_to_core_claim_without_inferring_support():
    out = normalize_claim({"context": context(), "claim": lab_claim()})
    c = out["claim"]
    assert c["claim_key"] == "claim-1"
    assert c["claim_type"] == "interpretive"
    assert c["status"] == "proposed"
    assert c["truth_determined_by_bridge"] is False
    b = build_core_claim_binding({"context": context(), "claim": lab_claim()})
    assert b["target_path"].endswith("/projects/project%3Aenergy-study/claims")
    assert b["data"]["claim_type"] == "interpretive"
    assert b["data"]["status"] == "proposed"
    assert b["automatic_submission"] is False


def test_structured_claim_rules_are_preserved():
    with pytest.raises(PlatformCoreV3FindingsValidationError):
        normalize_claim({"context": context(), "claim": {"statement": "x", "subject_ref": "a", "predicate": "p"}})
    with pytest.raises(PlatformCoreV3FindingsValidationError):
        normalize_claim({"context": context(), "claim": {"statement": "x", "polarity": "affirmed"}})


def test_evidence_link_maps_lab_roles_and_namespaces_assessment():
    out = build_core_evidence_link_binding({
        "context": context(),
        "evidence_link": {
            "id": "link-1",
            "evidence_ref": "lab:artifact:result-1",
            "target_type": "claim",
            "target_id": "core-claim-id-1",
            "relation": "limitation",
            "declared_strength": "moderate",
            "assessment": {"basis": "human-reviewed synthesis"},
            "lab_evidence_assessment": {
                "id": "boundary-1",
                "claimIds": ["claim-1"],
                "boundaryStatement": "Evidence applies only to the modeled system.",
            },
        },
    })
    assert out["data"]["relation"] == "qualifies"
    assert out["data"]["declared_strength"] == "moderate"
    assert "lab_evidence_boundary" in out["data"]["assessment"]
    assert out["data"]["metadata"]["evidence_strength_is_declared_not_core_judged"] is True


def test_contradiction_binding_records_declared_pair_without_resolution():
    out = build_core_contradiction_binding({
        "context": context(),
        "contradiction": {
            "id": "contra-1",
            "claim_a_id": "claim-a",
            "claim_b_id": "claim-b",
            "status": "unresolved",
            "basis_refs": ["lab:evidence:e1"],
            "rationale": "Declared inconsistency requires review.",
        },
    })
    assert out["target_path"].endswith("/contradictions")
    assert out["data"]["status"] == "unresolved"
    assert out["automatic_core_mutation"] is False


def test_validation_challenge_binding_carries_declared_evidence_boundary():
    out = build_core_validation_challenge_binding({
        "context": context(),
        "validation": {
            "id": "validation-1",
            "challenge_type": "uncertainty_challenge",
            "title": "Uncertainty boundary review",
            "description": "Review sensitivity to demand assumptions.",
            "source_ref": "lab:execution:run-1",
            "lab_evidence_assessment": {
                "id": "boundary-1",
                "claimIds": ["claim-1"],
                "boundaryStatement": "Inference is limited to modeled demand assumptions.",
            },
        },
    })
    assert out["target_path"] == "/v1/research/validation-challenges/challenges"
    assert out["data"]["challenge_type"] == "uncertainty_challenge"
    assert out["data"]["metadata"]["challenge_state_is_declared_not_core_decided"] is True
    assert out["scientific_validity_certified"] is False


def test_replication_binding_requires_existing_challenge_and_does_not_certify():
    out = build_core_replication_binding({
        "context": context(),
        "replication": {
            "id": "repl-1",
            "challenge_id": "core-challenge-id-1",
            "target_ref": "lab:claim:claim-1",
            "protocol_ref": "lab:protocol:p1",
            "execution_ref": "lab:execution:replication-1",
            "package_ref": "lab:reproducibility-package:pkg-1",
            "result_status": "recorded",
            "evidence": ["lab:artifact:replication-result-1"],
        },
    })
    assert out["target_path"] == "/v1/research/validation-challenges/replications"
    assert out["data"]["challenge_id"] == "core-challenge-id-1"
    assert out["data"]["provenance"]["replication_result_is_declared_not_core_certified"] is True
    assert out["scientific_validity_certified"] is False


def test_legacy_claim_bridge_builds_claim_and_evidence_envelopes():
    out = map_legacy_scientific_claim({"context": context(), "claim": lab_claim()})
    assert out["normalized_claim"]["claim_key"] == "claim-1"
    assert out["core_claim_binding"]["data"]["status"] == "proposed"
    assert len(out["core_evidence_bindings"]) == 2
    assert out["core_evidence_bindings"][0]["automatic_submission"] is False
    assert out["automatic_claim_inference"] is False
    assert out["automatic_scientific_certification"] is False


def test_invalid_enums_are_rejected():
    with pytest.raises(PlatformCoreV3FindingsValidationError):
        normalize_finding({"context": context(), "finding": {"statement": "x", "finding_type": "truth"}})
    with pytest.raises(PlatformCoreV3FindingsValidationError):
        build_core_validation_challenge_binding({"context": context(), "validation": {"title": "x", "challenge_type": "winner_selection"}})
    with pytest.raises(PlatformCoreV3FindingsValidationError):
        build_core_evidence_link_binding({"context": context(), "evidence_link": {"evidence_ref": "e", "target_id": "c", "target_type": "claim", "relation": "proves"}})
