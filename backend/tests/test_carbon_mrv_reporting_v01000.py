from copy import deepcopy
import pytest

from app.carbon_mrv_verification_ledger_v0990 import build_ledger
from app.carbon_mrv_reporting_v01000 import (
    LAB_RELEASE_VERSION, DOMAIN_VERSION, REPORT_SCHEMA, AUDIT_PACKET_SCHEMA,
    CarbonMRVReportingV01700Error, report_template, build_report, validate_report,
    build_audit_packet, build_project_packet, health, schema, policies,
)


def verification_ledger():
    return build_ledger({
        "project_id": "project:fixture",
        "title": "SOC evidence ledger",
        "protocol_ref": "mrv-protocol:fixture",
        "monitoring_plan_ref": "monitoring-plan:fixture",
        "uncertainty_assessment_ref": "mrv-uncertainty:fixture",
        "requirements": [
            {"requirement_key": "sampling", "description": "Sampling evidence", "accepted_evidence_types": ["sample-record"]},
            {"requirement_key": "laboratory", "description": "Laboratory evidence", "accepted_evidence_types": ["laboratory-result"]},
        ],
        "entries": [
            {"evidence_id": "sample-001", "evidence_type": "sample-record", "source_ref": "sample:001", "requirement_keys": ["sampling"], "review_state": "accepted-for-internal-review"},
            {"evidence_id": "lab-001", "evidence_type": "laboratory-result", "source_ref": "lab:001", "source_sha256": "0" * 64, "requirement_keys": ["laboratory"], "review_state": "accepted-for-internal-review"},
        ],
    })["ledger"]


def sections():
    return [
        {"section_key": "project-boundary", "title": "Project boundary and reporting period", "content": "Project parcel and reporting period are explicitly identified.", "source_refs": ["project:fixture"]},
        {"section_key": "methodology", "title": "Methods and assumptions", "content": "Methods are linked to the governing internal protocol.", "source_refs": ["mrv-protocol:fixture"]},
        {"section_key": "monitoring", "title": "Monitoring activities", "content": "Monitoring followed the declared sampling plan.", "source_refs": ["monitoring-plan:fixture"]},
        {"section_key": "quantification", "title": "Quantification", "content": "Reported quantities are preserved from referenced model runs.", "source_refs": ["model-run:soc-change"]},
        {"section_key": "uncertainty", "title": "Uncertainty", "content": "Uncertainty is linked to the explicit assessment.", "source_refs": ["mrv-uncertainty:fixture"]},
        {"section_key": "evidence", "title": "Evidence", "content": "Evidence is indexed through the verification ledger.", "source_refs": ["verification-ledger:fixture"]},
        {"section_key": "deviations", "title": "Deviations", "content": "No unresolved deviations are declared for this fixture.", "source_refs": []},
        {"section_key": "summary", "title": "Internal review summary", "content": "Packet is prepared for internal review only.", "source_refs": []},
    ]


def complete_payload():
    ledger = verification_ledger()
    return {
        "report_type": "monitoring-report",
        "project_id": "project:fixture",
        "title": "2026 SOC monitoring report",
        "reporting_period": {"start": "2026-01-01", "end": "2026-12-31"},
        "protocol_ref": "mrv-protocol:fixture",
        "monitoring_plan_ref": "monitoring-plan:fixture",
        "uncertainty_assessment_ref": "mrv-uncertainty:fixture",
        "verification_ledger_ref": ledger["ledger_id"],
        "verification_ledger": ledger,
        "sections": sections(),
        "reported_metrics": [
            {"metric_id": "soc-change", "name": "SOC stock change", "value": 7.8, "unit": "Mg C/ha", "source_ref": "model-run:soc-change", "uncertainty_ref": "mrv-uncertainty:fixture"}
        ],
        "deviations": [],
        "methodology_refs": ["library-methodology:soc-direct-measurement"],
        "source_refs": ["project:fixture", "model-run:soc-change"],
        "prepared_by": "actor:lab-user",
    }


def test_identity_and_metadata():
    assert LAB_RELEASE_VERSION == "0.100.0"
    assert DOMAIN_VERSION == "0.17.0"
    assert health()["status"] == "mrv-reporting-audit-packets-ready"
    assert len(schema()["internal_sections"]) == 8
    assert policies()["guardrails"]["audit_packet_is_not_auditor_approval"] is True


def test_template_is_internal_only():
    t = report_template("monitoring-report")
    assert len(t["sections"]) == 8
    assert "not an external methodology" in t["template_scope"]


def test_unknown_report_type_rejected():
    with pytest.raises(CarbonMRVReportingV01700Error):
        report_template("credit-issuance-report")


def test_complete_report_ready_for_internal_review():
    r = build_report(complete_payload())
    assert r["report"]["schema"] == REPORT_SCHEMA
    assert r["report"]["status"] == "ready-for-internal-review"
    assert r["validation"]["ready_for_internal_review"] is True
    assert r["validation"]["external_verification_status"] is None
    assert r["validation"]["external_audit_status"] is None
    assert r["report"]["verification_evidence"]["chain_valid"] is True


def test_report_without_full_ledger_can_be_internal_review_ready_if_reference_exists():
    p = complete_payload()
    p.pop("verification_ledger")
    r = build_report(p)
    assert r["validation"]["ready_for_internal_review"] is True
    assert r["validation"]["evidence_chain_checked"] is False
    assert r["validation"]["evidence_chain_valid"] is None


def test_report_missing_section_is_incomplete():
    p = complete_payload()
    p["sections"] = p["sections"][:-1]
    r = build_report(p)
    assert r["validation"]["ready_for_internal_review"] is False
    assert "summary" in r["validation"]["missing_internal_sections"]


def test_open_deviation_blocks_internal_review():
    p = complete_payload()
    p["deviations"] = [{"deviation_id": "dev-1", "description": "Lab rerun pending", "state": "open"}]
    r = build_report(p)
    assert r["validation"]["ready_for_internal_review"] is False
    assert r["validation"]["unresolved_deviation_ids"] == ["dev-1"]


def test_resolved_deviation_does_not_block_internal_review():
    p = complete_payload()
    p["deviations"] = [{"deviation_id": "dev-1", "description": "Lab rerun completed", "state": "resolved", "resolution_note": "Replacement result linked."}]
    r = build_report(p)
    assert r["validation"]["ready_for_internal_review"] is True


def test_invalid_reporting_period_rejected():
    p = complete_payload(); p["reporting_period"] = {"start": "2026-12-31", "end": "2026-01-01"}
    with pytest.raises(CarbonMRVReportingV01700Error):
        build_report(p)


def test_metric_is_preserved_not_recomputed():
    r = build_report(complete_payload())
    metric = r["report"]["reported_metrics"][0]
    assert metric["value"] == 7.8
    assert metric["calculation_reperformed"] is False


def test_validate_existing_report():
    report = build_report(complete_payload())["report"]
    v = validate_report({"report": report})
    assert v["ready_for_internal_review"] is True


def test_audit_packet_requires_checked_valid_chain_for_ready_status():
    p = complete_payload()
    r = build_report(p)["report"]
    audit = build_audit_packet({"report": r, "artifacts": [
        {"artifact_id": "lab-result", "artifact_type": "laboratory-result", "source_ref": "lab:001", "sha256": "1" * 64, "role": "supporting evidence"}
    ]})
    packet = audit["audit_packet"]
    assert packet["schema"] == AUDIT_PACKET_SCHEMA
    assert packet["status"] == "ready-for-internal-audit-preparation"
    assert packet["external_audit_status"] is None
    assert packet["external_verification_status"] is None


def test_audit_packet_with_reference_only_stays_draft():
    p = complete_payload(); p.pop("verification_ledger")
    report = build_report(p)["report"]
    audit = build_audit_packet({"report": report})
    assert audit["audit_packet"]["status"] == "draft"


def test_tampered_ledger_blocks_audit_packet_ready_status():
    p = complete_payload()
    ledger = deepcopy(p["verification_ledger"])
    ledger["entries"][0]["source_ref"] = "sample:tampered"
    p["verification_ledger"] = ledger
    report = build_report(p)["report"]
    assert report["verification_evidence"]["chain_valid"] is False
    audit = build_audit_packet({"report": report})
    assert audit["audit_packet"]["status"] == "draft"


def test_missing_artifact_digest_is_surfaced_not_fabricated():
    report = build_report(complete_payload())["report"]
    audit = build_audit_packet({"report": report, "artifacts": [
        {"artifact_id": "doc-1", "artifact_type": "document", "source_ref": "doc:1"}
    ]})
    assert audit["audit_packet"]["missing_artifact_digests"] == ["doc-1"]


def test_project_packet_uses_verification_record_without_claiming_audit_approval():
    p = complete_payload()
    p["artifacts"] = [{"artifact_id": "doc-1", "artifact_type": "document", "source_ref": "doc:1", "sha256": "2" * 64}]
    result = build_project_packet(p)
    obj = result["packet"]["objects"][0]
    prov = result["packet"]["provenance"][0]
    assert obj["object_type"] == "verification-record"
    assert obj["payload"]["external_audit_status"] is None
    assert obj["payload"]["external_verification_status"] is None
    assert "not external audit approval" in prov["note"]
