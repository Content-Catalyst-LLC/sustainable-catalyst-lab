from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any

LAB_RELEASE_VERSION = "0.99.0"
DOMAIN_VERSION = "0.16.0"
ENGINE_VERSION = "1.0.0"
LEDGER_VERSION = "1.0.0"
ENTRY_SCHEMA = "sc-carbon-nature-mrv-verification-evidence-entry/0.16.0"
LEDGER_SCHEMA = "sc-carbon-nature-mrv-verification-evidence-ledger/0.16.0"
VALIDATION_SCHEMA = "sc-carbon-nature-mrv-verification-evidence-validation/0.16.0"
CHAIN_SCHEMA = "sc-carbon-nature-mrv-verification-evidence-chain-check/0.16.0"
PROJECT_PACKET_SCHEMA = "sc-carbon-project-packet/1.0"
MAX_ENTRIES = 500
MAX_REFS = 100
MAX_REQUIREMENTS = 200
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

EVIDENCE_TYPES = (
    "field-observation",
    "sample-record",
    "chain-of-custody",
    "laboratory-result",
    "quality-control",
    "calculation-output",
    "model-run",
    "monitoring-record",
    "protocol",
    "methodology-reference",
    "document",
    "image",
    "other",
)
REVIEW_STATES = ("unreviewed", "accepted-for-internal-review", "flagged", "rejected-for-internal-review")


class CarbonMRVVerificationLedgerV01600Error(ValueError):
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
            raise CarbonMRVVerificationLedgerV01600Error(f"{label} is required")
        return None
    out = str(value).strip()
    if not out:
        if required:
            raise CarbonMRVVerificationLedgerV01600Error(f"{label} is required")
        return None
    if len(out) > max_len:
        raise CarbonMRVVerificationLedgerV01600Error(f"{label} exceeds {max_len} characters")
    return out


def _refs(value: Any, label: str, limit: int = MAX_REFS) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVVerificationLedgerV01600Error(f"{label} must be an array")
    if len(value) > limit:
        raise CarbonMRVVerificationLedgerV01600Error(f"{label} may contain at most {limit} values")
    out: list[str] = []
    for i, item in enumerate(value):
        ref = _text(item, f"{label}[{i}]", True, 240)
        assert ref is not None
        if ref not in out:
            out.append(ref)
    return out


def _guardrails() -> dict[str, bool]:
    return {
        "ledger_integrity_is_not_external_verification": True,
        "internal_review_state_is_not_certification": True,
        "no_methodology_eligibility_determination": True,
        "no_credit_eligibility_determination": True,
        "no_automatic_evidence_acceptance": True,
        "no_hidden_required_evidence_types": True,
        "no_evidence_content_is_fabricated": True,
        "external_file_digest_must_be_explicit_when_claimed": True,
        "tamper_check_only_recomputes_declared_chain": True,
    }


def _sha256(value: Any, label: str) -> str | None:
    digest = _text(value, label, False, 64)
    if digest is None:
        return None
    digest = digest.lower()
    if not SHA256_RE.fullmatch(digest):
        raise CarbonMRVVerificationLedgerV01600Error(f"{label} must be a 64-character lowercase/uppercase hexadecimal SHA-256 digest")
    return digest


def normalize_evidence_entry(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVVerificationLedgerV01600Error("evidence-entry request must be an object")
    evidence_id = _text(payload.get("evidence_id"), "evidence_id", True, 240)
    evidence_type = _text(payload.get("evidence_type"), "evidence_type", True, 80)
    source_ref = _text(payload.get("source_ref"), "source_ref", True, 600)
    assert evidence_id and evidence_type and source_ref
    if evidence_type not in EVIDENCE_TYPES:
        raise CarbonMRVVerificationLedgerV01600Error(f"evidence_type must be one of: {', '.join(EVIDENCE_TYPES)}")
    review_state = _text(payload.get("review_state") or "unreviewed", "review_state", True, 80)
    assert review_state
    if review_state not in REVIEW_STATES:
        raise CarbonMRVVerificationLedgerV01600Error(f"review_state must be one of: {', '.join(REVIEW_STATES)}")
    source_sha256 = _sha256(payload.get("source_sha256"), "source_sha256")
    requirement_keys = _refs(payload.get("requirement_keys"), "requirement_keys", MAX_REQUIREMENTS)
    normalized = {
        "schema": ENTRY_SCHEMA,
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "title": _text(payload.get("title"), "title", False, 300),
        "source_ref": source_ref,
        "source_sha256": source_sha256,
        "captured_at": _text(payload.get("captured_at"), "captured_at", False, 80),
        "actor_ref": _text(payload.get("actor_ref"), "actor_ref", False, 240),
        "subject_ref": _text(payload.get("subject_ref"), "subject_ref", False, 240),
        "requirement_keys": requirement_keys,
        "review_state": review_state,
        "review_note": _text(payload.get("review_note"), "review_note", False, 1200),
        "methodology_refs": _refs(payload.get("methodology_refs"), "methodology_refs"),
        "provenance_refs": _refs(payload.get("provenance_refs"), "provenance_refs"),
        "metadata": payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        "guardrails": _guardrails(),
    }
    normalized["content_fingerprint"] = _hash({k: v for k, v in normalized.items() if k not in {"content_fingerprint", "chain"}})
    return normalized


def _requirements(value: Any) -> list[dict[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise CarbonMRVVerificationLedgerV01600Error("requirements must be an array")
    if len(value) > MAX_REQUIREMENTS:
        raise CarbonMRVVerificationLedgerV01600Error(f"requirements may contain at most {MAX_REQUIREMENTS} values")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise CarbonMRVVerificationLedgerV01600Error(f"requirements[{i}] must be an object")
        key = _text(item.get("requirement_key"), f"requirements[{i}].requirement_key", True, 120)
        desc = _text(item.get("description"), f"requirements[{i}].description", True, 600)
        assert key and desc
        if key in seen:
            raise CarbonMRVVerificationLedgerV01600Error(f"duplicate requirement_key: {key}")
        seen.add(key)
        allowed = item.get("accepted_evidence_types") or []
        if not isinstance(allowed, list):
            raise CarbonMRVVerificationLedgerV01600Error(f"requirements[{i}].accepted_evidence_types must be an array")
        normalized_allowed: list[str] = []
        for j, evidence_type in enumerate(allowed):
            et = _text(evidence_type, f"requirements[{i}].accepted_evidence_types[{j}]", True, 80)
            assert et
            if et not in EVIDENCE_TYPES:
                raise CarbonMRVVerificationLedgerV01600Error(f"unsupported accepted evidence type: {et}")
            if et not in normalized_allowed:
                normalized_allowed.append(et)
        out.append({"requirement_key": key, "description": desc, "accepted_evidence_types": normalized_allowed, "required": bool(item.get("required", True))})
    return out


def build_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVVerificationLedgerV01600Error("verification-evidence-ledger request must be an object")
    project_id = _text(payload.get("project_id"), "project_id", False, 240)
    title = _text(payload.get("title"), "title", False, 300)
    protocol_ref = _text(payload.get("protocol_ref"), "protocol_ref", False, 240)
    monitoring_plan_ref = _text(payload.get("monitoring_plan_ref"), "monitoring_plan_ref", False, 240)
    uncertainty_assessment_ref = _text(payload.get("uncertainty_assessment_ref"), "uncertainty_assessment_ref", False, 240)
    requirements = _requirements(payload.get("requirements"))
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list):
        raise CarbonMRVVerificationLedgerV01600Error("entries must be an array")
    if len(raw_entries) > MAX_ENTRIES:
        raise CarbonMRVVerificationLedgerV01600Error(f"entries may contain at most {MAX_ENTRIES} values")
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    previous_hash: str | None = None
    for i, raw in enumerate(raw_entries):
        entry = normalize_evidence_entry(raw)
        if entry["evidence_id"] in seen_ids:
            raise CarbonMRVVerificationLedgerV01600Error(f"duplicate evidence_id: {entry['evidence_id']}")
        seen_ids.add(entry["evidence_id"])
        chain_input = {
            "sequence": i + 1,
            "previous_entry_hash": previous_hash,
            "content_fingerprint": entry["content_fingerprint"],
        }
        entry["chain"] = {
            "sequence": i + 1,
            "previous_entry_hash": previous_hash,
            "entry_hash": _hash(chain_input),
        }
        previous_hash = entry["chain"]["entry_hash"]
        entries.append(entry)
    ledger_id = _text(payload.get("ledger_id") or f"verification-ledger:{_hash([project_id,title,protocol_ref,monitoring_plan_ref])[:16]}", "ledger_id", True, 240)
    assert ledger_id
    ledger_core = {
        "schema": LEDGER_SCHEMA,
        "ledger_id": ledger_id,
        "ledger_version": LEDGER_VERSION,
        "status": "draft",
        "project_id": project_id,
        "title": title,
        "protocol_ref": protocol_ref,
        "monitoring_plan_ref": monitoring_plan_ref,
        "uncertainty_assessment_ref": uncertainty_assessment_ref,
        "requirements": requirements,
        "entries": entries,
        "methodology_refs": _refs(payload.get("methodology_refs"), "methodology_refs"),
        "source_refs": _refs(payload.get("source_refs"), "source_refs"),
        "guardrails": _guardrails(),
    }
    ledger_core["ledger_root_hash"] = _hash({"ledger_id": ledger_id, "entry_hashes": [e["chain"]["entry_hash"] for e in entries], "requirements": requirements})
    validation = _validation_from_ledger(ledger_core)
    ledger_core["status"] = "ready-for-internal-review" if validation["ready_for_internal_review"] else "draft"
    ledger_core["ledger_fingerprint"] = _hash({k: v for k, v in ledger_core.items() if k != "ledger_fingerprint"})
    validation = _validation_from_ledger(ledger_core)
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "ledger": ledger_core, "validation": validation}


def _validation_from_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    missing_core = [field for field in ("project_id", "title", "protocol_ref", "monitoring_plan_ref") if not ledger.get(field)]
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), list) else []
    if not entries:
        missing_core.append("entries")
    requirements = ledger.get("requirements") if isinstance(ledger.get("requirements"), list) else []
    covered: set[str] = set()
    wrong_type: list[dict[str, str]] = []
    req_by_key = {r.get("requirement_key"): r for r in requirements if isinstance(r, dict) and r.get("requirement_key")}
    for entry in entries:
        for key in entry.get("requirement_keys") or []:
            req = req_by_key.get(key)
            if not req:
                continue
            allowed = req.get("accepted_evidence_types") or []
            if allowed and entry.get("evidence_type") not in allowed:
                wrong_type.append({"requirement_key": key, "evidence_id": entry.get("evidence_id"), "evidence_type": entry.get("evidence_type")})
                continue
            covered.add(key)
    missing_required = [r["requirement_key"] for r in requirements if r.get("required", True) and r.get("requirement_key") not in covered]
    unreviewed = [e.get("evidence_id") for e in entries if e.get("review_state") == "unreviewed"]
    flagged = [e.get("evidence_id") for e in entries if e.get("review_state") in {"flagged", "rejected-for-internal-review"}]
    missing_digests = [e.get("evidence_id") for e in entries if e.get("evidence_type") in {"document", "image", "laboratory-result"} and not e.get("source_sha256")]
    chain = verify_chain({"ledger": ledger})
    ready = not missing_core and not missing_required and not wrong_type and not flagged and chain["chain_valid"] and bool(entries)
    result = {
        "ok": True,
        "schema": VALIDATION_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "ledger_id": ledger.get("ledger_id"),
        "ledger_readiness": "ready-for-internal-review" if ready else "draft-incomplete",
        "ready_for_internal_review": ready,
        "missing_core_fields": missing_core,
        "missing_required_evidence": missing_required,
        "evidence_type_mismatches": wrong_type,
        "unreviewed_evidence_ids": unreviewed,
        "flagged_or_rejected_evidence_ids": flagged,
        "external_artifacts_without_sha256": missing_digests,
        "chain_valid": chain["chain_valid"],
        "external_verification_status": None,
        "certification_status": None,
        "methodology_compliance": None,
        "credit_eligibility": None,
        "interpretation": "Internal-review readiness means the declared evidence requirements are linked, the ledger chain recomputes, and no evidence is flagged/rejected. Unreviewed entries and missing external-file digests are surfaced but do not silently create an external verification conclusion.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def verify_chain(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("ledger"), dict):
        raise CarbonMRVVerificationLedgerV01600Error("chain-check request requires ledger object")
    ledger = payload["ledger"]
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise CarbonMRVVerificationLedgerV01600Error("ledger.entries must be an array")
    issues: list[str] = []
    previous_hash: str | None = None
    recomputed_hashes: list[str] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            issues.append(f"entry {index} is not an object")
            continue
        chain = entry.get("chain") if isinstance(entry.get("chain"), dict) else {}
        content = {k: v for k, v in entry.items() if k not in {"content_fingerprint", "chain"}}
        expected_content = _hash(content)
        if entry.get("content_fingerprint") != expected_content:
            issues.append(f"entry {index} content_fingerprint mismatch")
        expected_entry = _hash({"sequence": index, "previous_entry_hash": previous_hash, "content_fingerprint": expected_content})
        if chain.get("sequence") != index:
            issues.append(f"entry {index} sequence mismatch")
        if chain.get("previous_entry_hash") != previous_hash:
            issues.append(f"entry {index} previous_entry_hash mismatch")
        if chain.get("entry_hash") != expected_entry:
            issues.append(f"entry {index} entry_hash mismatch")
        recomputed_hashes.append(expected_entry)
        previous_hash = expected_entry
    expected_root = _hash({"ledger_id": ledger.get("ledger_id"), "entry_hashes": recomputed_hashes, "requirements": ledger.get("requirements") or []})
    if ledger.get("ledger_root_hash") != expected_root:
        issues.append("ledger_root_hash mismatch")
    result = {
        "ok": True,
        "schema": CHAIN_SCHEMA,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "ledger_id": ledger.get("ledger_id"),
        "entry_count": len(entries),
        "chain_valid": not issues,
        "tamper_detected": bool(issues),
        "issues": issues,
        "recomputed_ledger_root_hash": expected_root,
        "interpretation": "This check recomputes the declared hash chain and ledger root. A valid chain shows internal record integrity for the supplied ledger representation; it does not prove source authenticity or external verification.",
        "guardrails": _guardrails(),
    }
    result["result_fingerprint"] = _hash({k: v for k, v in result.items() if k != "result_fingerprint"})
    return result


def validate_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVVerificationLedgerV01600Error("validation request must be an object")
    if isinstance(payload.get("ledger"), dict):
        ledger = payload["ledger"]
        if ledger.get("schema") != LEDGER_SCHEMA:
            raise CarbonMRVVerificationLedgerV01600Error(f"ledger.schema must be {LEDGER_SCHEMA}")
        return _validation_from_ledger(ledger)
    return build_ledger(payload)["validation"]


def build_project_packet(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CarbonMRVVerificationLedgerV01600Error("project packet request must be an object")
    source = payload.get("ledger") if isinstance(payload.get("ledger"), dict) else payload
    if isinstance(source, dict) and source.get("schema") == LEDGER_SCHEMA:
        ledger = source
        validation = _validation_from_ledger(ledger)
    else:
        built = build_ledger(source)
        ledger, validation = built["ledger"], built["validation"]
    if not ledger.get("project_id"):
        raise CarbonMRVVerificationLedgerV01600Error("project_id is required for a project packet")
    actor_ref = _text(payload.get("actor_ref") or "actor:lab-user", "actor_ref", True, 240)
    object_id = _text(payload.get("object_id") or f"verification-record:mrv-evidence-{ledger['ledger_root_hash'][:16]}", "object_id", True, 240)
    assert actor_ref and object_id
    provenance_id = f"provenance:mrv-evidence-{ledger['ledger_root_hash'][:16]}"
    obj = {
        "object_id": object_id,
        "object_type": "verification-record",
        "project_id": ledger["project_id"],
        "version": "1.0.0",
        "status": "draft",
        "payload": {
            "record_type": "mrv-verification-evidence-ledger",
            "lab_release_version": LAB_RELEASE_VERSION,
            "domain_version": DOMAIN_VERSION,
            "ledger_id": ledger["ledger_id"],
            "ledger_root_hash": ledger["ledger_root_hash"],
            "entry_count": len(ledger.get("entries") or []),
            "ready_for_internal_review": validation["ready_for_internal_review"],
            "external_verification_status": None,
            "ledger_fingerprint": ledger.get("ledger_fingerprint"),
            "validation_fingerprint": validation["result_fingerprint"],
            "guardrails": ledger["guardrails"],
        },
        "source_refs": sorted(set((ledger.get("source_refs") or []) + [e.get("source_ref") for e in ledger.get("entries") or [] if e.get("source_ref")])),
    }
    provenance = {
        "provenance_id": provenance_id,
        "event_type": "created",
        "actor_ref": actor_ref,
        "object_ref": object_id,
        "source_refs": obj["source_refs"],
        "note": "Created a draft MRV verification-evidence ledger record. This ledger does not constitute external verification or certification; it records internal evidence integrity and review readiness only.",
    }
    packet = {
        "schema": PROJECT_PACKET_SCHEMA,
        "packet_type": "carbon-project-object-packet",
        "project_id": ledger["project_id"],
        "objects": [obj],
        "provenance": [provenance],
    }
    packet["packet_fingerprint"] = _hash({k: v for k, v in packet.items() if k != "packet_fingerprint"})
    return {"ok": True, "domain_version": DOMAIN_VERSION, "lab_release_version": LAB_RELEASE_VERSION, "packet": packet, "validation": validation}


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "Sustainable Catalyst Lab Carbon & Nature MRV Verification Evidence Ledger",
        "lab_release_version": LAB_RELEASE_VERSION,
        "domain_version": DOMAIN_VERSION,
        "engine_version": ENGINE_VERSION,
        "status": "verification-evidence-ledger-ready",
        "evidence_types": list(EVIDENCE_TYPES),
        "review_states": list(REVIEW_STATES),
    }


def schema() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "schemas": {
            "entry": ENTRY_SCHEMA,
            "ledger": LEDGER_SCHEMA,
            "validation": VALIDATION_SCHEMA,
            "chain_check": CHAIN_SCHEMA,
            "project_packet": PROJECT_PACKET_SCHEMA,
        },
        "evidence_types": list(EVIDENCE_TYPES),
        "review_states": list(REVIEW_STATES),
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "domain_version": DOMAIN_VERSION,
        "lab_release_version": LAB_RELEASE_VERSION,
        "ledger_policy": {
            "entry_order": "caller-supplied order; normalized into a deterministic SHA-256 chain",
            "external_artifact_digest": "explicit SHA-256 supported; never inferred from an inaccessible external artifact",
            "requirement_model": "requirements are explicit caller inputs inherited from governing protocol/monitoring documents; no hidden evidence requirements",
            "review_boundary": "review states are internal workflow labels only",
        },
        "guardrails": _guardrails(),
    }
