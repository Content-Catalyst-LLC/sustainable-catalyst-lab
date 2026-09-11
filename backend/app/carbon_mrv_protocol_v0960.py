from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from typing import Any

from .carbon_mrv_registry_v0950 import METHODS, assess_readiness

LAB_RELEASE_VERSION = "0.96.0"
DOMAIN_VERSION = "0.13.0"
ENGINE_VERSION = "1.0.0"
PROTOCOL_VERSION = "1.0.0"
PROTOCOL_SCHEMA = "sc-carbon-nature-mrv-protocol/0.13.0"
VALIDATION_SCHEMA = "sc-carbon-nature-mrv-protocol-validation/0.13.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_REFS = 100
MAX_LIST_ITEMS = 100
MAX_STEP_LENGTH = 1200


class CarbonMRVProtocolV01300Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _text(value: Any, label: str, required: bool = False, max_len: int = 1200) -> str | None:
    if value is None:
        if required:
            raise CarbonMRVProtocolV01300Error(f"{label} is required")
        return None
    out = str(value).strip()
    if not out:
        if required:
            raise CarbonMRVProtocolV01300Error(f"{label} is required")
        return None
    if len(out) > max_len:
        raise CarbonMRVProtocolV01300Error(f"{label} exceeds {max_len} characters")
    return out


def _refs(value: Any, label: str) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVProtocolV01300Error(f"{label} must be an array")
    if len(value) > MAX_REFS:
        raise CarbonMRVProtocolV01300Error(f"{label} may contain at most {MAX_REFS} values")
    out: list[str] = []
    for i, item in enumerate(value):
        ref = _text(item, f"{label}[{i}]", True, 240)
        assert ref is not None
        if ref not in out:
            out.append(ref)
    return out


def _steps(value: Any, label: str) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVProtocolV01300Error(f"{label} must be an array")
    if len(value) > MAX_LIST_ITEMS:
        raise CarbonMRVProtocolV01300Error(f"{label} may contain at most {MAX_LIST_ITEMS} values")
    out: list[str] = []
    for i, item in enumerate(value):
        step = _text(item, f"{label}[{i}]", True, MAX_STEP_LENGTH)
        assert step is not None
        if step not in out:
            out.append(step)
    return out


def _date(value: Any, label: str) -> str | None:
    raw = _text(value, label, False, 32)
    if raw is None:
        return None
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError as exc:
        raise CarbonMRVProtocolV01300Error(f"{label} must be an ISO date (YYYY-MM-DD)") from exc


def _roles(value: Any) -> list[dict[str, str | None]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVProtocolV01300Error("responsible_roles must be an array")
    if len(value) > 50:
        raise CarbonMRVProtocolV01300Error("responsible_roles may contain at most 50 values")
    out: list[dict[str, str | None]] = []
    seen: set[tuple[str, str | None]] = set()
    for i, item in enumerate(value):
        if isinstance(item, str):
            role = _text(item, f"responsible_roles[{i}]", True, 120)
            actor = None
            responsibility = None
        elif isinstance(item, dict):
            role = _text(item.get("role"), f"responsible_roles[{i}].role", True, 120)
            actor = _text(item.get("actor_ref"), f"responsible_roles[{i}].actor_ref", False, 240)
            responsibility = _text(item.get("responsibility"), f"responsible_roles[{i}].responsibility", False, 600)
        else:
            raise CarbonMRVProtocolV01300Error(f"responsible_roles[{i}] must be a string or object")
        assert role is not None
        key = (role.lower(), actor)
        if key not in seen:
            seen.add(key)
            out.append({"role": role, "actor_ref": actor, "responsibility": responsibility})
    return out


def _guardrails() -> dict[str, bool]:
    return {
        "protocol_is_not_external_methodology": True,
        "no_automatic_method_selection": True,
        "no_methodology_eligibility_determination": True,
        "no_verification_determination": True,
        "no_credit_eligibility_determination": True,
        "no_current_program_rule_assertion": True,
        "no_hidden_measurement_or_sampling_defaults": True,
        "no_hidden_emission_or_gwp_factors": True,
        "no_causal_attribution_inference": True,
        "no_uncertainty_inference_without_inputs": True,
    }


SECTION_DEFINITIONS = [
    ("objective_and_scope", "Objective & scope", "State the monitoring objective, system boundary, spatial unit, temporal scope, pools/gases, and exclusions."),
    ("measurement_and_sampling_plan", "Measurement & sampling plan", "Document field, laboratory, inventory, flux, activity-data, or modeling procedures appropriate to the selected foundation method."),
    ("calculation_plan", "Calculation plan", "Describe equations/models, versions, factors, transformations, aggregation, units, and reproducible computation steps."),
    ("uncertainty_plan", "Uncertainty plan", "Identify sampling, analytical, model, parameter, factor, temporal, and spatial uncertainty components that will be quantified or explicitly left unresolved."),
    ("quality_control_plan", "QA/QC plan", "Document identity checks, calibration/controls, review steps, chain of custody, duplicate handling, validation, and exception handling."),
    ("data_management_plan", "Data & provenance plan", "Define identifiers, source references, custody, versioning, storage, lineage, access, and change tracking."),
    ("monitoring_schedule", "Monitoring schedule", "State when monitoring occurs, its explicit frequency or event trigger, and how departures from schedule are recorded."),
    ("reporting_plan", "Reporting plan", "Define outputs, review/signoff path, evidence packet contents, and what is reported without implying external verification."),
    ("change_control_plan", "Change-control plan", "Define how protocol revisions, method changes, exceptions, superseded records, and approvals are versioned and justified."),
]


def protocol_template(method_key: str) -> dict[str, Any]:
    key = _text(method_key, "method_key", True, 120)
    assert key is not None
    if key not in METHODS:
        raise CarbonMRVProtocolV01300Error(f"unknown MRV method: {key}", 404)
    method = METHODS[key]
    template = {
        "ok": True,
        "schema": "sc-carbon-nature-mrv-protocol-template/0.13.0",
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "method_key": key,
        "method_title": method["title"],
        "library_methodology_key": method["library_methodology_key"],
        "required_inputs": list(method["required_inputs"]),
        "required_evidence": list(method["required_evidence"]),
        "uncertainty_expectations": list(method["uncertainty_expectations"]),
        "quality_controls": list(method["quality_controls"]),
        "sections": [
            {"section_key": key_, "title": title, "prompt": prompt, "content": None}
            for key_, title, prompt in SECTION_DEFINITIONS
        ],
        "interpretation": "This is a Sustainable Catalyst protocol scaffold derived from a foundation method profile. It is not an external methodology, verifier-approved protocol, or current-program compliance determination.",
        "guardrails": _guardrails(),
    }
    template["template_fingerprint"] = _hash({k: v for k, v in template.items() if k != "template_fingerprint"})
    return template


def _normalize_sections(value: Any) -> dict[str, str | None]:
    if value in (None, ""):
        value = {}
    if not isinstance(value, dict):
        raise CarbonMRVProtocolV01300Error("sections must be an object")
    known = {key for key, _, _ in SECTION_DEFINITIONS}
    unknown = sorted(set(value) - known)
    if unknown:
        raise CarbonMRVProtocolV01300Error("unknown protocol sections: " + ", ".join(unknown))
    return {key: _text(value.get(key), f"sections.{key}", False, 8000) for key, _, _ in SECTION_DEFINITIONS}


def _validation_from_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    missing_core: list[str] = []
    for field in ("project_id", "title", "objective", "spatial_boundary_ref", "monitoring_frequency"):
        if not protocol.get(field):
            missing_core.append(field)
    period = protocol.get("monitoring_period") or {}
    if not period.get("start_date"):
        missing_core.append("monitoring_period.start_date")
    if not period.get("end_date"):
        missing_core.append("monitoring_period.end_date")
    if not protocol.get("responsible_roles"):
        missing_core.append("responsible_roles")

    missing_sections = [key for key, _, _ in SECTION_DEFINITIONS if not protocol["sections"].get(key)]
    readiness = protocol["method_documentation_readiness"]
    missing_references = []
    if not protocol.get("methodology_refs"):
        missing_references.append("methodology_refs")
    if not protocol.get("source_refs"):
        missing_references.append("source_refs")

    structural_complete = not missing_core and not missing_sections and not missing_references
    documentation_complete = readiness["documentation_ready"]
    protocol_ready = structural_complete and documentation_complete

    result = {
        "ok": True,
        "schema": VALIDATION_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "protocol_id": protocol["protocol_id"],
        "method_key": protocol["method_key"],
        "structural_status": "complete" if structural_complete else "incomplete",
        "documentation_status": readiness["documentation_readiness"],
        "protocol_readiness": "ready-for-internal-review" if protocol_ready else "draft-incomplete",
        "ready_for_internal_review": protocol_ready,
        "missing_core_fields": missing_core,
        "missing_sections": missing_sections,
        "missing_references": missing_references,
        "missing_method_inputs": list(readiness["missing_inputs"]),
        "missing_method_evidence": list(readiness["missing_evidence"]),
        "external_methodology_compliance": None,
        "verification_status": None,
        "credit_eligibility": None,
        "interpretation": "Ready-for-internal-review means the Sustainable Catalyst scaffold and named foundation-method documentation are populated. It does not establish external methodology compliance, verification, certification, or credit eligibility.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def build_protocol(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVProtocolV01300Error("protocol request must be an object")
    method_key = _text(payload.get("method_key"), "method_key", True, 120)
    assert method_key is not None
    if method_key not in METHODS:
        raise CarbonMRVProtocolV01300Error(f"unknown MRV method: {method_key}", 404)

    start = _date((payload.get("monitoring_period") or {}).get("start_date") if isinstance(payload.get("monitoring_period"), dict) else None, "monitoring_period.start_date")
    end = _date((payload.get("monitoring_period") or {}).get("end_date") if isinstance(payload.get("monitoring_period"), dict) else None, "monitoring_period.end_date")
    if start and end and end < start:
        raise CarbonMRVProtocolV01300Error("monitoring_period.end_date must be on or after start_date")

    method_readiness = assess_readiness({
        "method_key": method_key,
        "available_inputs": _refs(payload.get("available_inputs"), "available_inputs"),
        "available_evidence": _refs(payload.get("available_evidence"), "available_evidence"),
        "methodology_refs": _refs(payload.get("methodology_refs"), "methodology_refs"),
        "source_refs": _refs(payload.get("source_refs"), "source_refs"),
    })
    sections = _normalize_sections(payload.get("sections"))
    project_id = _text(payload.get("project_id"), "project_id", False, 240)
    title = _text(payload.get("title"), "title", False, 240)
    objective = _text(payload.get("objective"), "objective", False, 3000)
    boundary = _text(payload.get("spatial_boundary_ref"), "spatial_boundary_ref", False, 240)
    frequency = _text(payload.get("monitoring_frequency"), "monitoring_frequency", False, 600)
    protocol_seed = [project_id, method_key, title, objective, boundary, start, end]
    protocol_id = _text(payload.get("protocol_id") or f"mrv-protocol:{_hash(protocol_seed)[:16]}", "protocol_id", True, 240)
    assert protocol_id is not None

    protocol = {
        "schema": PROTOCOL_SCHEMA,
        "protocol_id": protocol_id,
        "protocol_version": PROTOCOL_VERSION,
        "status": "draft",
        "project_id": project_id,
        "title": title,
        "objective": objective,
        "method_key": method_key,
        "method_title": METHODS[method_key]["title"],
        "library_methodology_key": METHODS[method_key]["library_methodology_key"],
        "spatial_boundary_ref": boundary,
        "monitoring_period": {"start_date": start, "end_date": end},
        "monitoring_frequency": frequency,
        "responsible_roles": _roles(payload.get("responsible_roles")),
        "available_inputs": method_readiness["available_inputs"],
        "available_evidence": method_readiness["available_evidence"],
        "methodology_refs": method_readiness["methodology_refs"],
        "source_refs": method_readiness["source_refs"],
        "sections": sections,
        "method_documentation_readiness": method_readiness,
        "method_requirements": {
            "required_inputs": list(METHODS[method_key]["required_inputs"]),
            "required_evidence": list(METHODS[method_key]["required_evidence"]),
            "uncertainty_expectations": list(METHODS[method_key]["uncertainty_expectations"]),
            "quality_controls": list(METHODS[method_key]["quality_controls"]),
        },
        "interpretation": "Draft Sustainable Catalyst MRV protocol scaffold. Protocol content remains user- and evidence-supplied and must be checked against authoritative external methodology and program requirements when applicable.",
        "guardrails": _guardrails(),
    }
    protocol["protocol_fingerprint"] = _hash({k: v for k, v in protocol.items() if k != "protocol_fingerprint"})
    validation = _validation_from_protocol(protocol)
    protocol["status"] = "ready-for-internal-review" if validation["ready_for_internal_review"] else "draft"
    protocol["protocol_fingerprint"] = _hash({k: v for k, v in protocol.items() if k != "protocol_fingerprint"})
    validation = _validation_from_protocol(protocol)
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "protocol": protocol, "validation": validation}


def validate_protocol(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVProtocolV01300Error("validation request must be an object")
    if isinstance(payload.get("protocol"), dict):
        protocol = payload["protocol"]
        if protocol.get("schema") != PROTOCOL_SCHEMA:
            raise CarbonMRVProtocolV01300Error(f"protocol.schema must be {PROTOCOL_SCHEMA}")
        # Rebuild from the editable/source fields so validation cannot trust a caller-supplied readiness result.
        source = {
            "protocol_id": protocol.get("protocol_id"),
            "project_id": protocol.get("project_id"),
            "title": protocol.get("title"),
            "objective": protocol.get("objective"),
            "method_key": protocol.get("method_key"),
            "spatial_boundary_ref": protocol.get("spatial_boundary_ref"),
            "monitoring_period": protocol.get("monitoring_period"),
            "monitoring_frequency": protocol.get("monitoring_frequency"),
            "responsible_roles": protocol.get("responsible_roles"),
            "available_inputs": protocol.get("available_inputs"),
            "available_evidence": protocol.get("available_evidence"),
            "methodology_refs": protocol.get("methodology_refs"),
            "source_refs": protocol.get("source_refs"),
            "sections": protocol.get("sections"),
        }
        return build_protocol(source)["validation"]
    return build_protocol(payload)["validation"]


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVProtocolV01300Error("project packet request must be an object")
    source = payload.get("protocol") if isinstance(payload.get("protocol"), dict) else payload
    built = build_protocol(source)
    protocol = built["protocol"]
    validation = built["validation"]
    project_id = protocol.get("project_id")
    if not project_id:
        raise CarbonMRVProtocolV01300Error("project_id is required for a project packet")
    actor = _text(payload.get("actor_ref") or "actor:lab-user", "actor_ref", True, 240)
    assert actor is not None
    object_id = _text(payload.get("object_id") or f"monitoring-record:protocol-{protocol['protocol_fingerprint'][:16]}", "object_id", True, 240)
    assert object_id is not None
    refs: list[str] = []
    for ref in protocol["source_refs"] + protocol["methodology_refs"] + METHODS[protocol["method_key"]]["source_refs"]:
        if ref not in refs:
            refs.append(ref)
    provenance_id = f"provenance:mrv-protocol-{protocol['protocol_fingerprint'][:16]}"
    obj = {
        "object_id": object_id,
        "object_type": "monitoring-record",
        "project_id": project_id,
        "version": "1.0.0",
        "status": "draft",
        "payload": {
            "record_type": "mrv-protocol",
            "protocol_version": PROTOCOL_VERSION,
            "lab_release_version": LAB_RELEASE_VERSION,
            "domain_version": DOMAIN_VERSION,
            "protocol_id": protocol["protocol_id"],
            "method_key": protocol["method_key"],
            "protocol_status": protocol["status"],
            "ready_for_internal_review": validation["ready_for_internal_review"],
            "protocol_fingerprint": protocol["protocol_fingerprint"],
            "validation_fingerprint": validation["result_fingerprint"],
            "guardrails": protocol["guardrails"],
        },
        "source_refs": refs,
        "evidence_refs": protocol["source_refs"],
        "methodology_refs": protocol["methodology_refs"],
        "provenance_refs": [provenance_id],
    }
    event = {
        "provenance_id": provenance_id,
        "event_type": "created",
        "object_id": object_id,
        "actor_ref": actor,
        "details": {
            "record_type": "mrv-protocol",
            "protocol_id": protocol["protocol_id"],
            "method_key": protocol["method_key"],
            "ready_for_internal_review": validation["ready_for_internal_review"],
        },
    }
    packet = {"schema": PROJECT_PACKET_SCHEMA, "objects": [obj], "provenance": [event], "links": []}
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "packet": packet,
        "protocol": protocol,
        "validation": validation,
        "packet_fingerprint": _hash(packet),
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "capabilities": {
            "method_derived_protocol_templates": True,
            "draft_protocol_builder": True,
            "structural_validation": True,
            "method_documentation_gap_analysis": True,
            "responsibility_assignment": True,
            "monitoring_period_and_frequency": True,
            "qa_qc_uncertainty_data_and_reporting_sections": True,
            "library_methodology_crosswalk": True,
            "carbon_project_monitoring_record_handoff": True,
            "deterministic_fingerprints": True,
        },
        "limits": {"max_refs_per_field": MAX_REFS, "max_list_items": MAX_LIST_ITEMS, "max_roles": 50},
        "guardrails": _guardrails(),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "protocol_schema": PROTOCOL_SCHEMA,
        "validation_schema": VALIDATION_SCHEMA,
        "section_keys": [key for key, _, _ in SECTION_DEFINITIONS],
        "method_keys": list(METHODS),
        "protocol_status_values": ["draft", "ready-for-internal-review"],
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "mrv-protocol-builder-ready",
        "service": "Sustainable Catalyst Lab MRV Protocol Builder",
        "lab_release_version": LAB_RELEASE_VERSION,
        "domain_version": DOMAIN_VERSION,
        "engine_version": ENGINE_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "method_registry_count": len(METHODS),
        "section_count": len(SECTION_DEFINITIONS),
        "guardrails": _guardrails(),
    }
