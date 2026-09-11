from copy import deepcopy
import pytest

from app.carbon_mrv_verification_ledger_v0990 import (
    LAB_RELEASE_VERSION, DOMAIN_VERSION, ENTRY_SCHEMA, LEDGER_SCHEMA,
    CarbonMRVVerificationLedgerV01600Error,
    normalize_evidence_entry, build_ledger, validate_ledger, verify_chain,
    build_project_packet, health, schema, policies,
)


def complete_payload():
    return {
        "project_id": "project:fixture",
        "title": "SOC verification evidence ledger",
        "protocol_ref": "mrv-protocol:fixture",
        "monitoring_plan_ref": "monitoring-plan:fixture",
        "uncertainty_assessment_ref": "mrv-uncertainty:fixture",
        "requirements": [
            {"requirement_key": "sampling", "description": "Sampling evidence", "accepted_evidence_types": ["sample-record"]},
            {"requirement_key": "laboratory", "description": "Laboratory evidence", "accepted_evidence_types": ["laboratory-result"]},
            {"requirement_key": "uncertainty", "description": "Uncertainty assessment", "accepted_evidence_types": ["model-run"]},
        ],
        "entries": [
            {"evidence_id": "sample-001", "evidence_type": "sample-record", "source_ref": "sample:001", "requirement_keys": ["sampling"], "review_state": "accepted-for-internal-review"},
            {"evidence_id": "lab-001", "evidence_type": "laboratory-result", "source_ref": "lab:001", "source_sha256": "0" * 64, "requirement_keys": ["laboratory"], "review_state": "accepted-for-internal-review"},
            {"evidence_id": "unc-001", "evidence_type": "model-run", "source_ref": "mrv-uncertainty:fixture", "requirement_keys": ["uncertainty"], "review_state": "accepted-for-internal-review"},
        ],
        "methodology_refs": ["library-methodology:soc-direct-measurement"],
        "source_refs": ["mrv-protocol:fixture", "monitoring-plan:fixture"],
    }


def test_identity_and_metadata():
    assert LAB_RELEASE_VERSION == "0.99.0"
    assert DOMAIN_VERSION == "0.16.0"
    assert health()["ok"] is True
    assert "laboratory-result" in schema()["evidence_types"]
    assert policies()["guardrails"]["ledger_integrity_is_not_external_verification"] is True


def test_normalize_evidence_entry():
    entry = normalize_evidence_entry({"evidence_id":"e1","evidence_type":"document","source_ref":"doc:1","source_sha256":"a"*64})
    assert entry["schema"] == ENTRY_SCHEMA
    assert len(entry["content_fingerprint"]) == 64
    assert entry["review_state"] == "unreviewed"


def test_invalid_digest_rejected():
    with pytest.raises(CarbonMRVVerificationLedgerV01600Error):
        normalize_evidence_entry({"evidence_id":"e1","evidence_type":"document","source_ref":"doc:1","source_sha256":"bad"})


def test_build_complete_ledger_and_chain():
    result = build_ledger(complete_payload())
    ledger = result["ledger"]
    assert ledger["schema"] == LEDGER_SCHEMA
    assert ledger["status"] == "ready-for-internal-review"
    assert result["validation"]["ready_for_internal_review"] is True
    assert result["validation"]["external_verification_status"] is None
    assert len(ledger["entries"]) == 3
    assert ledger["entries"][0]["chain"]["previous_entry_hash"] is None
    assert ledger["entries"][1]["chain"]["previous_entry_hash"] == ledger["entries"][0]["chain"]["entry_hash"]
    checked = verify_chain({"ledger": ledger})
    assert checked["chain_valid"] is True and checked["tamper_detected"] is False


def test_chain_detects_tampering():
    ledger = build_ledger(complete_payload())["ledger"]
    tampered = deepcopy(ledger)
    tampered["entries"][1]["source_ref"] = "lab:tampered"
    checked = verify_chain({"ledger": tampered})
    assert checked["chain_valid"] is False
    assert checked["tamper_detected"] is True
    assert any("content_fingerprint mismatch" in x for x in checked["issues"])


def test_duplicate_evidence_id_rejected():
    payload = complete_payload()
    payload["entries"].append(dict(payload["entries"][0]))
    with pytest.raises(CarbonMRVVerificationLedgerV01600Error):
        build_ledger(payload)


def test_required_evidence_gap_is_reported():
    payload = complete_payload()
    payload["entries"] = payload["entries"][:-1]
    result = build_ledger(payload)
    assert result["ledger"]["status"] == "draft"
    assert "uncertainty" in result["validation"]["missing_required_evidence"]


def test_evidence_type_mismatch_is_reported():
    payload = complete_payload()
    payload["entries"][0]["evidence_type"] = "document"
    result = build_ledger(payload)
    assert result["validation"]["ready_for_internal_review"] is False
    assert result["validation"]["evidence_type_mismatches"][0]["requirement_key"] == "sampling"


def test_flagged_evidence_blocks_internal_review():
    payload = complete_payload()
    payload["entries"][0]["review_state"] = "flagged"
    result = build_ledger(payload)
    assert result["validation"]["ready_for_internal_review"] is False
    assert "sample-001" in result["validation"]["flagged_or_rejected_evidence_ids"]


def test_unreviewed_is_surfaced_but_not_silently_verification():
    payload = complete_payload()
    payload["entries"][0]["review_state"] = "unreviewed"
    result = build_ledger(payload)
    assert "sample-001" in result["validation"]["unreviewed_evidence_ids"]
    assert result["validation"]["external_verification_status"] is None


def test_missing_external_digest_is_surfaced():
    payload = complete_payload()
    payload["entries"][1].pop("source_sha256")
    result = build_ledger(payload)
    assert "lab-001" in result["validation"]["external_artifacts_without_sha256"]


def test_validate_existing_ledger():
    ledger = build_ledger(complete_payload())["ledger"]
    validation = validate_ledger({"ledger": ledger})
    assert validation["chain_valid"] is True
    assert validation["ready_for_internal_review"] is True


def test_project_packet_uses_verification_record_without_claiming_verification():
    ledger = build_ledger(complete_payload())["ledger"]
    packet = build_project_packet({"ledger": ledger})
    obj = packet["packet"]["objects"][0]
    prov = packet["packet"]["provenance"][0]
    assert obj["object_type"] == "verification-record"
    assert obj["payload"]["external_verification_status"] is None
    assert prov["event_type"] == "created"
    assert "does not constitute external verification" in prov["note"]


def test_project_packet_requires_project_id():
    payload = complete_payload(); payload["project_id"] = None
    ledger = build_ledger(payload)["ledger"]
    with pytest.raises(CarbonMRVVerificationLedgerV01600Error):
        build_project_packet({"ledger": ledger})
