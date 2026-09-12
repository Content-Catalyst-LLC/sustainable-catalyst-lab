from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from typing import Any

from .carbon_mrv_verification_ledger_v0990 import verify_chain as verify_evidence_chain_v1600

LAB_RELEASE_VERSION = "0.100.0"
DOMAIN_VERSION = "0.17.0"
ENGINE_VERSION = "1.0.0"
REPORT_SCHEMA = "sc-carbon-nature-mrv-report/0.17.0"
REPORT_VALIDATION_SCHEMA = "sc-carbon-nature-mrv-report-validation/0.17.0"
AUDIT_PACKET_SCHEMA = "sc-carbon-nature-mrv-audit-packet/0.17.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_REFS = 200
MAX_SECTIONS = 50
MAX_METRICS = 250
MAX_DEVIATIONS = 100
MAX_ARTIFACTS = 500
SHA256_LEN = 64

REPORT_TYPES = (
    "monitoring-report",
    "verification-preparation-report",
    "project-period-summary",
)

INTERNAL_SECTION_CATALOG = (
    ("project-boundary", "Project boundary and reporting period"),
    ("methodology", "Methods, assumptions, and methodology references"),
    ("monitoring", "Monitoring activities and sampling implementation"),
    ("quantification", "Reported quantities and calculation lineage"),
    ("uncertainty", "Uncertainty and detection assessment"),
    ("evidence", "Verification evidence ledger and supporting records"),
    ("deviations", "Deviations, limitations, and corrective actions"),
    ("summary", "Internal review summary"),
)

ARTIFACT_TYPES = (
    "protocol",
    "monitoring-plan",
    "uncertainty-assessment",
    "verification-evidence-ledger",
    "calculation-output",
    "model-run",
    "laboratory-result",
    "field-record",
    "document",
    "image",
    "other",
)

DEVIATION_STATES = ("open", "resolved", "accepted-for-internal-review")


class CarbonMRVReportingV01700Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _text(value: Any, label: str, required: bool = False, max_len: int = 4000) -> str | None:
    if value is None:
        if required:
            raise CarbonMRVReportingV01700Error(f"{label} is required")
        return None
    out = str(value).strip()
    if not out:
        if required:
            raise CarbonMRVReportingV01700Error(f"{label} is required")
        return None
    if len(out) > max_len:
        raise CarbonMRVReportingV01700Error(f"{label} exceeds {max_len} characters")
    return out


def _refs(value: Any, label: str, limit: int = MAX_REFS) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVReportingV01700Error(f"{label} must be an array")
    if len(value) > limit:
        raise CarbonMRVReportingV01700Error(f"{label} may contain at most {limit} values")
    out: list[str] = []
    for i, item in enumerate(value):
        ref = _text(item, f"{label}[{i}]", True, 600)
        assert ref is not None
        if ref not in out:
            out.append(ref)
    return out


def _date(value: Any, label: str) -> str:
    text = _text(value, label, True, 20)
    assert text is not None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise CarbonMRVReportingV01700Error(f"{label} must be an ISO date (YYYY-MM-DD)") from exc


def _guardrails() -> dict[str, bool]:
    return {
        "internal_report_readiness_is_not_external_verification": True,
        "audit_packet_is_not_auditor_approval": True,
        "no_methodology_compliance_determination": True,
        "no_credit_eligibility_determination": True,
        "no_automatic_metric_recalculation": True,
        "no_hidden_external_reporting_requirements": True,
        "no_automatic_evidence_authenticity_claim": True,
        "ledger_chain_integrity_is_not_source_authenticity": True,
    }


def report_template(report_type: str) -> dict[str, Any]:
    report_type = _text(report_type, "report_type", True, 80)
    assert report_type is not None
    if report_type not in REPORT_TYPES:
        raise CarbonMRVReportingV01700Error(f"report_type must be one of: {', '.join(REPORT_TYPES)}", 404)
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "report_type": report_type,
        "template_scope": "Sustainable Catalyst internal reporting structure only; it is not an external methodology or program reporting template.",
        "sections": [
            {"section_key": key, "title": title, "required_for_internal_review": True}
            for key, title in INTERNAL_SECTION_CATALOG
        ],
        "guardrails": _guardrails(),
    }


def _normalize_period(payload: Any) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise CarbonMRVReportingV01700Error("reporting_period must be an object")
    start = _date(payload.get("start"), "reporting_period.start")
    end = _date(payload.get("end"), "reporting_period.end")
    if date.fromisoformat(end) < date.fromisoformat(start):
        raise CarbonMRVReportingV01700Error("reporting_period.end must be on or after reporting_period.start")
    return {"start": start, "end": end}


def _normalize_sections(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise CarbonMRVReportingV01700Error("sections must be an array")
    if len(value) > MAX_SECTIONS:
        raise CarbonMRVReportingV01700Error(f"sections may contain at most {MAX_SECTIONS} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise CarbonMRVReportingV01700Error(f"sections[{i}] must be an object")
        key = _text(raw.get("section_key"), f"sections[{i}].section_key", True, 120)
        title = _text(raw.get("title"), f"sections[{i}].title", True, 300)
        content = _text(raw.get("content"), f"sections[{i}].content", True, 12000)
        assert key and title and content
        if key in seen:
            raise CarbonMRVReportingV01700Error(f"duplicate section_key: {key}")
        seen.add(key)
        section = {
            "section_key": key,
            "title": title,
            "content": content,
            "source_refs": _refs(raw.get("source_refs"), f"sections[{i}].source_refs"),
        }
        section["section_fingerprint"] = _hash(section)
        out.append(section)
    return out


def _normalize_metrics(value: Any) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVReportingV01700Error("reported_metrics must be an array")
    if len(value) > MAX_METRICS:
        raise CarbonMRVReportingV01700Error(f"reported_metrics may contain at most {MAX_METRICS} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise CarbonMRVReportingV01700Error(f"reported_metrics[{i}] must be an object")
        metric_id = _text(raw.get("metric_id"), f"reported_metrics[{i}].metric_id", True, 120)
        name = _text(raw.get("name"), f"reported_metrics[{i}].name", True, 300)
        unit = _text(raw.get("unit"), f"reported_metrics[{i}].unit", True, 120)
        source_ref = _text(raw.get("source_ref"), f"reported_metrics[{i}].source_ref", True, 600)
        assert metric_id and name and unit and source_ref
        if metric_id in seen:
            raise CarbonMRVReportingV01700Error(f"duplicate metric_id: {metric_id}")
        seen.add(metric_id)
        value_raw = raw.get("value")
        if isinstance(value_raw, bool) or not isinstance(value_raw, (int, float)):
            raise CarbonMRVReportingV01700Error(f"reported_metrics[{i}].value must be numeric")
        out.append({
            "metric_id": metric_id,
            "name": name,
            "value": float(value_raw),
            "unit": unit,
            "source_ref": source_ref,
            "uncertainty_ref": _text(raw.get("uncertainty_ref"), f"reported_metrics[{i}].uncertainty_ref", False, 600),
            "note": _text(raw.get("note"), f"reported_metrics[{i}].note", False, 1200),
            "calculation_reperformed": False,
        })
    return out


def _normalize_deviations(value: Any) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVReportingV01700Error("deviations must be an array")
    if len(value) > MAX_DEVIATIONS:
        raise CarbonMRVReportingV01700Error(f"deviations may contain at most {MAX_DEVIATIONS} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise CarbonMRVReportingV01700Error(f"deviations[{i}] must be an object")
        deviation_id = _text(raw.get("deviation_id"), f"deviations[{i}].deviation_id", True, 120)
        description = _text(raw.get("description"), f"deviations[{i}].description", True, 2000)
        state = _text(raw.get("state") or "open", f"deviations[{i}].state", True, 80)
        assert deviation_id and description and state
        if deviation_id in seen:
            raise CarbonMRVReportingV01700Error(f"duplicate deviation_id: {deviation_id}")
        if state not in DEVIATION_STATES:
            raise CarbonMRVReportingV01700Error(f"deviations[{i}].state must be one of: {', '.join(DEVIATION_STATES)}")
        seen.add(deviation_id)
        out.append({
            "deviation_id": deviation_id,
            "description": description,
            "state": state,
            "resolution_note": _text(raw.get("resolution_note"), f"deviations[{i}].resolution_note", False, 2000),
            "source_refs": _refs(raw.get("source_refs"), f"deviations[{i}].source_refs"),
        })
    return out


def _ledger_summary(payload: dict[str, Any]) -> dict[str, Any]:
    ledger = payload.get("verification_ledger")
    ledger_ref = _text(payload.get("verification_ledger_ref"), "verification_ledger_ref", False, 600)
    if ledger is None:
        return {
            "verification_ledger_ref": ledger_ref,
            "ledger_root_hash": None,
            "entry_count": None,
            "chain_checked": False,
            "chain_valid": None,
            "tamper_detected": None,
            "external_verification_status": None,
        }
    if not isinstance(ledger, dict):
        raise CarbonMRVReportingV01700Error("verification_ledger must be an object when supplied")
    try:
        chain = verify_evidence_chain_v1600({"ledger": ledger})
    except Exception as exc:
        raise CarbonMRVReportingV01700Error(f"verification_ledger could not be chain-checked: {exc}") from exc
    return {
        "verification_ledger_ref": ledger_ref or ledger.get("ledger_id"),
        "ledger_root_hash": ledger.get("ledger_root_hash"),
        "entry_count": len(ledger.get("entries") or []) if isinstance(ledger.get("entries"), list) else None,
        "chain_checked": True,
        "chain_valid": bool(chain.get("chain_valid")),
        "tamper_detected": bool(chain.get("tamper_detected")),
        "external_verification_status": None,
    }


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVReportingV01700Error("MRV reporting request must be an object")
    report_type = _text(payload.get("report_type") or "monitoring-report", "report_type", True, 80)
    assert report_type
    if report_type not in REPORT_TYPES:
        raise CarbonMRVReportingV01700Error(f"report_type must be one of: {', '.join(REPORT_TYPES)}")
    project_id = _text(payload.get("project_id"), "project_id", True, 240)
    title = _text(payload.get("title"), "title", True, 300)
    protocol_ref = _text(payload.get("protocol_ref"), "protocol_ref", True, 600)
    monitoring_plan_ref = _text(payload.get("monitoring_plan_ref"), "monitoring_plan_ref", True, 600)
    uncertainty_assessment_ref = _text(payload.get("uncertainty_assessment_ref"), "uncertainty_assessment_ref", True, 600)
    assert project_id and title and protocol_ref and monitoring_plan_ref and uncertainty_assessment_ref
    period = _normalize_period(payload.get("reporting_period"))
    sections = _normalize_sections(payload.get("sections"))
    metrics = _normalize_metrics(payload.get("reported_metrics"))
    deviations = _normalize_deviations(payload.get("deviations"))
    ledger_summary = _ledger_summary(payload)
    report_id = _text(payload.get("report_id") or f"mrv-report:{_hash([project_id,title,period,report_type])[:16]}", "report_id", True, 240)
    assert report_id
    report = {
        "schema": REPORT_SCHEMA,
        "report_id": report_id,
        "report_type": report_type,
        "status": "draft",
        "project_id": project_id,
        "title": title,
        "reporting_period": period,
        "protocol_ref": protocol_ref,
        "monitoring_plan_ref": monitoring_plan_ref,
        "uncertainty_assessment_ref": uncertainty_assessment_ref,
        "verification_evidence": ledger_summary,
        "sections": sections,
        "reported_metrics": metrics,
        "deviations": deviations,
        "methodology_refs": _refs(payload.get("methodology_refs"), "methodology_refs"),
        "source_refs": _refs(payload.get("source_refs"), "source_refs"),
        "prepared_by": _text(payload.get("prepared_by"), "prepared_by", False, 240),
        "guardrails": _guardrails(),
    }
    report["report_fingerprint"] = _hash({k: v for k, v in report.items() if k != "report_fingerprint"})
    validation = _validation_from_report(report)
    report["status"] = "ready-for-internal-review" if validation["ready_for_internal_review"] else "draft"
    report["report_fingerprint"] = _hash({k: v for k, v in report.items() if k != "report_fingerprint"})
    validation = _validation_from_report(report)
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "report": report, "validation": validation}


def _validation_from_report(report: dict[str, Any]) -> dict[str, Any]:
    missing_core = [field for field in ("project_id", "title", "protocol_ref", "monitoring_plan_ref", "uncertainty_assessment_ref") if not report.get(field)]
    if not isinstance(report.get("reporting_period"), dict):
        missing_core.append("reporting_period")
    required_keys = [k for k, _ in INTERNAL_SECTION_CATALOG]
    section_map = {s.get("section_key"): s for s in report.get("sections") or [] if isinstance(s, dict)}
    missing_sections = [k for k in required_keys if k not in section_map or not section_map[k].get("content")]
    unresolved_deviations = [d.get("deviation_id") for d in report.get("deviations") or [] if d.get("state") == "open"]
    ledger = report.get("verification_evidence") if isinstance(report.get("verification_evidence"), dict) else {}
    missing_ledger_ref = not ledger.get("verification_ledger_ref")
    chain_checked = bool(ledger.get("chain_checked"))
    chain_valid = ledger.get("chain_valid") if chain_checked else None
    ready = not missing_core and not missing_sections and not unresolved_deviations and not missing_ledger_ref and (chain_valid is not False)
    result = {
        "ok": True,
        "schema": REPORT_VALIDATION_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "report_id": report.get("report_id"),
        "report_readiness": "ready-for-internal-review" if ready else "draft-incomplete",
        "ready_for_internal_review": ready,
        "missing_core_fields": missing_core,
        "missing_internal_sections": missing_sections,
        "unresolved_deviation_ids": unresolved_deviations,
        "missing_verification_ledger_reference": missing_ledger_ref,
        "evidence_chain_checked": chain_checked,
        "evidence_chain_valid": chain_valid,
        "external_verification_status": None,
        "external_audit_status": None,
        "methodology_compliance": None,
        "credit_eligibility": None,
        "interpretation": "Internal-report readiness checks Sustainable Catalyst's declared report structure, references, deviations, and any supplied evidence-chain result. It does not establish external verification, audit approval, methodology compliance, or credit eligibility.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def validate_report(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVReportingV01700Error("report validation request must be an object")
    if isinstance(payload.get("report"), dict):
        report = payload["report"]
        if report.get("schema") != REPORT_SCHEMA:
            raise CarbonMRVReportingV01700Error(f"report.schema must be {REPORT_SCHEMA}")
        return _validation_from_report(report)
    return build_report(payload)["validation"]


def _normalize_artifacts(value: Any) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVReportingV01700Error("artifacts must be an array")
    if len(value) > MAX_ARTIFACTS:
        raise CarbonMRVReportingV01700Error(f"artifacts may contain at most {MAX_ARTIFACTS} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise CarbonMRVReportingV01700Error(f"artifacts[{i}] must be an object")
        artifact_id = _text(raw.get("artifact_id"), f"artifacts[{i}].artifact_id", True, 240)
        artifact_type = _text(raw.get("artifact_type"), f"artifacts[{i}].artifact_type", True, 100)
        source_ref = _text(raw.get("source_ref"), f"artifacts[{i}].source_ref", True, 600)
        assert artifact_id and artifact_type and source_ref
        if artifact_id in seen:
            raise CarbonMRVReportingV01700Error(f"duplicate artifact_id: {artifact_id}")
        if artifact_type not in ARTIFACT_TYPES:
            raise CarbonMRVReportingV01700Error(f"artifacts[{i}].artifact_type must be one of: {', '.join(ARTIFACT_TYPES)}")
        digest = _text(raw.get("sha256"), f"artifacts[{i}].sha256", False, SHA256_LEN)
        if digest is not None:
            digest = digest.lower()
            if len(digest) != SHA256_LEN or any(c not in "0123456789abcdef" for c in digest):
                raise CarbonMRVReportingV01700Error(f"artifacts[{i}].sha256 must be a 64-character hexadecimal SHA-256 digest")
        seen.add(artifact_id)
        out.append({
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "source_ref": source_ref,
            "sha256": digest,
            "role": _text(raw.get("role"), f"artifacts[{i}].role", False, 240),
        })
    return out


def build_audit_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVReportingV01700Error("audit-packet request must be an object")
    if isinstance(payload.get("report"), dict):
        report = payload["report"]
        if report.get("schema") != REPORT_SCHEMA:
            raise CarbonMRVReportingV01700Error(f"report.schema must be {REPORT_SCHEMA}")
        validation = _validation_from_report(report)
    else:
        built = build_report(payload)
        report, validation = built["report"], built["validation"]
    artifacts = _normalize_artifacts(payload.get("artifacts"))
    section_index = [
        {"section_key": s.get("section_key"), "section_fingerprint": s.get("section_fingerprint"), "source_refs": s.get("source_refs") or []}
        for s in report.get("sections") or []
    ]
    missing_artifact_digests = [a["artifact_id"] for a in artifacts if a["artifact_type"] in {"laboratory-result", "document", "image"} and not a.get("sha256")]
    ledger = report.get("verification_evidence") or {}
    ready = bool(validation.get("ready_for_internal_review")) and ledger.get("chain_checked") is True and ledger.get("chain_valid") is True
    packet_id = _text(payload.get("audit_packet_id") or f"mrv-audit-packet:{_hash([report.get('report_id'),report.get('report_fingerprint')])[:16]}", "audit_packet_id", True, 240)
    assert packet_id
    packet = {
        "schema": AUDIT_PACKET_SCHEMA,
        "audit_packet_id": packet_id,
        "status": "ready-for-internal-audit-preparation" if ready else "draft",
        "project_id": report.get("project_id"),
        "report_id": report.get("report_id"),
        "report_fingerprint": report.get("report_fingerprint"),
        "reporting_period": report.get("reporting_period"),
        "component_index": {
            "protocol_ref": report.get("protocol_ref"),
            "monitoring_plan_ref": report.get("monitoring_plan_ref"),
            "uncertainty_assessment_ref": report.get("uncertainty_assessment_ref"),
            "verification_ledger_ref": ledger.get("verification_ledger_ref"),
            "verification_ledger_root_hash": ledger.get("ledger_root_hash"),
        },
        "section_index": section_index,
        "artifacts": artifacts,
        "missing_artifact_digests": missing_artifact_digests,
        "unresolved_items": {
            "missing_core_fields": validation.get("missing_core_fields") or [],
            "missing_internal_sections": validation.get("missing_internal_sections") or [],
            "unresolved_deviation_ids": validation.get("unresolved_deviation_ids") or [],
            "evidence_chain_checked": validation.get("evidence_chain_checked"),
            "evidence_chain_valid": validation.get("evidence_chain_valid"),
        },
        "external_audit_status": None,
        "external_verification_status": None,
        "methodology_compliance": None,
        "credit_eligibility": None,
        "guardrails": _guardrails(),
    }
    packet["packet_fingerprint"] = _hash({k: v for k, v in packet.items() if k != "packet_fingerprint"})
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "report": report,
        "report_validation": validation,
        "audit_packet": packet,
        "interpretation": "The audit packet is a structured internal preparation bundle. A ready status means the internal report is complete and the supplied evidence ledger hash chain validates; it is not an auditor opinion or external verification.",
    }


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    built = build_audit_packet(payload)
    report = built["report"]
    packet = built["audit_packet"]
    project_id = report.get("project_id")
    if not project_id:
        raise CarbonMRVReportingV01700Error("project_id is required for a project packet")
    actor_ref = _text(payload.get("actor_ref") or "actor:lab-user", "actor_ref", True, 240)
    object_id = _text(payload.get("object_id") or f"verification-record:mrv-report-{packet['packet_fingerprint'][:16]}", "object_id", True, 240)
    assert actor_ref and object_id
    source_refs = sorted(set((report.get("source_refs") or []) + [x for x in (
        report.get("protocol_ref"), report.get("monitoring_plan_ref"), report.get("uncertainty_assessment_ref"),
        (report.get("verification_evidence") or {}).get("verification_ledger_ref"),
    ) if x]))
    obj = {
        "object_id": object_id,
        "object_type": "verification-record",
        "project_id": project_id,
        "version": "1.0.0",
        "status": "draft",
        "payload": {
            "record_type": "mrv-reporting-audit-packet",
            "lab_release_version": LAB_RELEASE_VERSION,
            "domain_version": DOMAIN_VERSION,
            "report_id": report.get("report_id"),
            "report_fingerprint": report.get("report_fingerprint"),
            "audit_packet_id": packet.get("audit_packet_id"),
            "audit_packet_fingerprint": packet.get("packet_fingerprint"),
            "internal_audit_preparation_status": packet.get("status"),
            "external_audit_status": None,
            "external_verification_status": None,
            "guardrails": packet.get("guardrails"),
        },
        "source_refs": source_refs,
    }
    provenance = {
        "provenance_id": f"provenance:mrv-report-{packet['packet_fingerprint'][:16]}",
        "event_type": "created",
        "actor_ref": actor_ref,
        "object_ref": object_id,
        "source_refs": source_refs,
        "note": "Created a draft MRV reporting and audit-preparation record. Internal packet readiness is not external audit approval, verification, certification, methodology compliance, or credit eligibility.",
    }
    project_packet = {
        "schema": PROJECT_PACKET_SCHEMA,
        "packet_type": "carbon-project-object-packet",
        "project_id": project_id,
        "objects": [obj],
        "provenance": [provenance],
    }
    project_packet["packet_fingerprint"] = _hash({k: v for k, v in project_packet.items() if k != "packet_fingerprint"})
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "packet": project_packet, "report_validation": built["report_validation"], "audit_packet": packet}


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "Sustainable Catalyst Lab Carbon & Nature MRV Reporting & Audit Packets",
        "lab_release_version": LAB_RELEASE_VERSION,
        "domain_version": DOMAIN_VERSION,
        "engine_version": ENGINE_VERSION,
        "status": "mrv-reporting-audit-packets-ready",
        "report_types": list(REPORT_TYPES),
        "internal_section_count": len(INTERNAL_SECTION_CATALOG),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "schemas": {
            "report": REPORT_SCHEMA,
            "report_validation": REPORT_VALIDATION_SCHEMA,
            "audit_packet": AUDIT_PACKET_SCHEMA,
            "project_packet": PROJECT_PACKET_SCHEMA,
        },
        "report_types": list(REPORT_TYPES),
        "artifact_types": list(ARTIFACT_TYPES),
        "deviation_states": list(DEVIATION_STATES),
        "internal_sections": [k for k, _ in INTERNAL_SECTION_CATALOG],
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "reporting_policy": {
            "section_catalog": "Sustainable Catalyst internal report structure; external program templates are not inferred or claimed",
            "metrics": "reported values are preserved as caller-supplied declarations and are not silently recalculated",
            "evidence_chain": "a supplied v0.16 verification ledger may be chain-checked for internal integrity",
            "audit_packet": "ready-for-internal-audit-preparation requires internal report readiness plus a validated supplied evidence-ledger chain",
            "artifact_digests": "SHA-256 digests are accepted only when explicitly provided; missing digests are surfaced",
        },
        "guardrails": _guardrails(),
    }
