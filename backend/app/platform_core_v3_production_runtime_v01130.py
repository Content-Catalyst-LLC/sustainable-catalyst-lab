from __future__ import annotations

import copy
import json
import re
from hashlib import sha256
from typing import Any, Callable

from .platform_core_v3_adapter_v01040 import PRODUCT_REF
from .platform_core_v3_object_mapping_v01050 import build_core_object_binding
from .platform_core_v3_research_context_v01060 import (
    build_contextual_handoff_binding,
    build_contextual_object_binding,
    build_core_product_context_binding,
    build_core_session_registration,
    normalize_research_context,
)
from .platform_core_v3_execution_lineage_v01070 import build_core_execution_binding
from .platform_core_v3_findings_validation_v01080 import (
    build_core_claim_binding,
    build_core_evidence_link_binding,
    build_core_finding_binding,
    build_core_replication_binding,
    build_core_validation_challenge_binding,
)
from .platform_core_v3_visual_scene_v01090 import build_core_visual_binding
from .platform_core_v3_scholarly_package_v01100 import build_core_package_binding
from .platform_core_v3_scientific_investigation_v01110 import build_core_investigation_binding
from .platform_core_v3_integration_certification_v01120 import build_full_submission_plan as build_certification_plan

LAB_VERSION = "0.113.0"
FEATURE_VERSION = "0.113.0"
MINIMUM_CORE_RELEASE = "3.0.0"
PRODUCTION_SCHEMA = "sc-lab-unified-research-session-production-runtime/0.113.0"
OPERATION_SCHEMA = "sc-lab-platform-core-v3-production-operation/0.113.0"
RECEIPT_SCHEMA = "sc-lab-platform-core-v3-production-receipt/0.113.0"
CHECKPOINT_SCHEMA = "sc-lab-platform-core-v3-production-checkpoint/0.113.0"
CORE_RUNTIME_CONTRACT = "sc.research.unified-research-scientific-investigation-runtime.v1"
CORE_CERTIFICATION_CONTRACT = "sc.research.platform-integration-certification.v1"

COMPONENTS: dict[str, dict[str, str]] = {
    "runtime-adapter": {"version": "0.104.0", "health_path": "/v1/platform-core-v3-adapter/health"},
    "object-mapping": {"version": "0.105.0", "health_path": "/v1/platform-core-v3-objects/health"},
    "research-context": {"version": "0.106.0", "health_path": "/v1/platform-core-v3-context/health"},
    "execution-lineage": {"version": "0.107.0", "health_path": "/v1/platform-core-v3-executions/health"},
    "research-intelligence": {"version": "0.108.0", "health_path": "/v1/platform-core-v3-research-intelligence/health"},
    "visual-scene": {"version": "0.109.0", "health_path": "/v1/platform-core-v3-visual-scene/health"},
    "scholarly-package": {"version": "0.110.0", "health_path": "/v1/platform-core-v3-scholarly-packages/health"},
    "scientific-investigation": {"version": "0.111.0", "health_path": "/v1/platform-core-v3-scientific-investigations/health"},
    "integration-certification": {"version": "0.112.0", "health_path": "/v1/platform-core-v3-integration-certification/health"},
}

OPERATION_CATALOG: dict[str, dict[str, Any]] = {
    "session-registration": {"builder": "session", "authority": "core-session-registry"},
    "product-context-binding": {"builder": "product-context", "authority": "core-session-registry"},
    "object-binding": {"builder": "object", "authority": "lab-object-core-reference"},
    "execution-binding": {"builder": "execution", "authority": "lab-execution-core-lineage"},
    "finding-binding": {"builder": "finding", "authority": "declared-research-intelligence"},
    "claim-binding": {"builder": "claim", "authority": "declared-research-intelligence"},
    "evidence-link-binding": {"builder": "evidence", "authority": "declared-research-intelligence"},
    "validation-challenge-binding": {"builder": "validation", "authority": "declared-validation"},
    "replication-binding": {"builder": "replication", "authority": "declared-replication"},
    "visual-binding": {"builder": "visual", "authority": "lab-rendering-core-reference"},
    "package-binding": {"builder": "package", "authority": "lab-package-core-reference"},
    "investigation-binding": {"builder": "investigation", "authority": "lab-investigation-core-reference"},
    "handoff-binding": {"builder": "handoff", "authority": "cross-product-handoff"},
    "certification-plan": {"builder": "certification", "authority": "contract-conformance-evidence"},
}

FORBIDDEN_TRUE_KEYS = {
    "automatic_submission",
    "automatic_retry",
    "automatic_recovery",
    "automatic_core_mutation",
    "automatic_execution",
    "automatic_product_invocation",
    "automatic_case_execution",
    "automatic_scientific_certification",
    "automatic_product_quality_certification",
    "automatic_truth_determination",
    "infer_success",
    "infer_scientific_validity",
}


class PlatformCoreV3ProductionRuntimeError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 4000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise PlatformCoreV3ProductionRuntimeError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3ProductionRuntimeError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3ProductionRuntimeError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum: int = 5000) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3ProductionRuntimeError(f"{label} must be an array.")
    if len(value) > maximum:
        raise PlatformCoreV3ProductionRuntimeError(f"{label} exceeds {maximum} entries.")
    return copy.deepcopy(value)


def _reject_authority(payload: dict[str, Any]) -> None:
    for key in FORBIDDEN_TRUE_KEYS:
        if payload.get(key) is True:
            raise PlatformCoreV3ProductionRuntimeError(f"{key}=true is outside the v0.113.0 production-runtime boundary.", 422)


def _context(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    try:
        return normalize_research_context(raw)["context"]
    except Exception as exc:
        raise PlatformCoreV3ProductionRuntimeError(f"Invalid research context: {exc}", getattr(exc, "status_code", 400)) from exc


def _builder(operation_type: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    builders: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
        "session-registration": build_core_session_registration,
        "product-context-binding": build_core_product_context_binding,
        "object-binding": build_contextual_object_binding,
        "execution-binding": build_core_execution_binding,
        "finding-binding": build_core_finding_binding,
        "claim-binding": build_core_claim_binding,
        "evidence-link-binding": build_core_evidence_link_binding,
        "validation-challenge-binding": build_core_validation_challenge_binding,
        "replication-binding": build_core_replication_binding,
        "visual-binding": build_core_visual_binding,
        "package-binding": build_core_package_binding,
        "investigation-binding": build_core_investigation_binding,
        "handoff-binding": build_contextual_handoff_binding,
        "certification-plan": build_certification_plan,
    }
    return builders[operation_type]


def _built_endpoint(built: dict[str, Any], operation_type: str) -> str:
    if isinstance(built.get("core_mapping"), dict):
        return _built_endpoint(built["core_mapping"], operation_type)
    for key in ("target_path", "target_endpoint", "core_endpoint", "endpoint"):
        if built.get(key):
            return str(built[key])
    if operation_type == "certification-plan":
        return "/v1/research/integration-certification"
    raise PlatformCoreV3ProductionRuntimeError(f"{operation_type} did not expose a Core target endpoint.", 500)


def _built_body(built: dict[str, Any], operation_type: str) -> dict[str, Any]:
    if isinstance(built.get("core_mapping"), dict):
        return _built_body(built["core_mapping"], operation_type)
    if isinstance(built.get("request_body"), dict):
        return copy.deepcopy(built["request_body"])
    if isinstance(built.get("data"), dict):
        return {"data": copy.deepcopy(built["data"])}
    if operation_type == "certification-plan":
        return {"plan": copy.deepcopy(built)}
    raise PlatformCoreV3ProductionRuntimeError(f"{operation_type} did not expose a request body.", 500)


def normalize_operation(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ProductionRuntimeError("A production operation descriptor is required.")
    _reject_authority(payload)
    operation = payload.get("operation") if isinstance(payload.get("operation"), dict) else payload
    operation_type = _text(operation.get("operation_type") or operation.get("operationType"), "operation_type", 120)
    if operation_type not in OPERATION_CATALOG:
        raise PlatformCoreV3ProductionRuntimeError(f"Unsupported operation_type: {operation_type}", 422)
    context = _context(operation.get("context") if isinstance(operation.get("context"), dict) else payload)
    operation_payload = _dict(operation.get("payload"), "payload")
    if "context" not in operation_payload:
        operation_payload["context"] = context
    try:
        built = _builder(operation_type)(operation_payload)
    except Exception as exc:
        raise PlatformCoreV3ProductionRuntimeError(f"Unable to build {operation_type}: {exc}", getattr(exc, "status_code", 422)) from exc
    endpoint = _built_endpoint(built, operation_type)
    request_body = _built_body(built, operation_type)
    method = _text(operation.get("method") or built.get("method") or "POST", "method", 12).upper()
    request_hash = _hash({"method": method, "endpoint": endpoint, "request_body": request_body, "context_ref": context["context_ref"]})
    supplied_key = _text(operation.get("idempotency_key") or operation.get("idempotencyKey"), "idempotency_key", 240, required=False)
    idempotency_key = supplied_key or f"sc-lab-v01130:{request_hash[:40]}"
    correlation_ref = _text(operation.get("correlation_ref") or operation.get("correlationRef"), "correlation_ref", 1000, required=False) or f"lab:correlation:{request_hash[:32]}"
    operation_ref = _text(operation.get("operation_ref") or operation.get("operationRef"), "operation_ref", 1000, required=False) or f"lab:production-operation:{request_hash[:32]}"
    attempt = int(operation.get("attempt") or 1)
    if attempt < 1 or attempt > 100:
        raise PlatformCoreV3ProductionRuntimeError("attempt must be between 1 and 100.")
    normalized = {
        "operation_ref": operation_ref,
        "operation_type": operation_type,
        "method": method,
        "target_endpoint": endpoint,
        "request_body": request_body,
        "request_hash": request_hash,
        "idempotency_key": idempotency_key,
        "correlation_ref": correlation_ref,
        "attempt": attempt,
        "context_ref": context["context_ref"],
        "project_ref": context["project_ref"],
        "session_id": context.get("session_id"),
        "authority": OPERATION_CATALOG[operation_type]["authority"],
        "builder_schema": built.get("schema"),
        "automatic_submission": False,
        "automatic_retry": False,
        "automatic_recovery": False,
        "automatic_execution": False,
        "underlying_specialist_state_remains_authoritative": True,
    }
    normalized["operation_hash"] = _hash(normalized)
    return {"ok": True, "schema": OPERATION_SCHEMA, "context": context, "operation": normalized, "built_contract": built}


def build_submission_plan(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_operation(payload)
    op = normalized["operation"]
    headers = {
        "Idempotency-Key": op["idempotency_key"],
        "X-SC-Correlation-Ref": op["correlation_ref"],
        "Content-Type": "application/json",
    }
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-explicit-submission-plan/0.113.0",
        "operation": op,
        "request": {"method": op["method"], "endpoint": op["target_endpoint"], "headers": headers, "body": op["request_body"]},
        "automatic_submission": False,
        "automatic_retry": False,
        "automatic_core_mutation": False,
        "authorization_material_included": False,
        "plan_hash": _hash({"operation": op, "headers": headers}),
    }


def check_idempotency(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_operation(payload)
    op = normalized["operation"]
    records = _list(payload.get("prior_records") or payload.get("priorRecords"), "prior_records", 10000)
    same_key = [r for r in records if isinstance(r, dict) and str(r.get("idempotency_key") or r.get("idempotencyKey") or "") == op["idempotency_key"]]
    same_hash = [r for r in same_key if str(r.get("request_hash") or r.get("requestHash") or "") == op["request_hash"]]
    conflicts = [r for r in same_key if r not in same_hash]
    if conflicts:
        state = "conflict"
    elif same_hash:
        state = "replay-safe"
    else:
        state = "new"
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-idempotency-check/0.113.0",
        "state": state,
        "operation_ref": op["operation_ref"],
        "idempotency_key": op["idempotency_key"],
        "request_hash": op["request_hash"],
        "matching_record_count": len(same_hash),
        "conflicting_record_count": len(conflicts),
        "safe_to_prepare_replay": state == "replay-safe",
        "automatic_replay": False,
        "automatic_submission": False,
        "automatic_conflict_resolution": False,
    }


def build_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ProductionRuntimeError("A production receipt descriptor is required.")
    op_value = payload.get("operation")
    if isinstance(op_value, dict) and op_value.get("operation_hash") and op_value.get("request_hash"):
        op = copy.deepcopy(op_value)
    else:
        op = normalize_operation(payload)["operation"]
    response = _dict(payload.get("response"), "response")
    outcome = _text(payload.get("declared_outcome") or payload.get("declaredOutcome"), "declared_outcome", 40)
    if outcome not in {"succeeded", "failed", "uncertain", "duplicate", "conflict", "cancelled"}:
        raise PlatformCoreV3ProductionRuntimeError("declared_outcome must be succeeded, failed, uncertain, duplicate, conflict, or cancelled.")
    status_code = payload.get("status_code") if payload.get("status_code") is not None else payload.get("statusCode")
    if status_code is not None:
        try:
            status_code = int(status_code)
        except Exception as exc:
            raise PlatformCoreV3ProductionRuntimeError("status_code must be an integer.") from exc
    core_refs = []
    for item in _list(payload.get("core_refs") or payload.get("coreRefs"), "core_refs"):
        value = _text(item, "core_ref", 1000)
        if value not in core_refs:
            core_refs.append(value)
    body_hash = _hash(response) if response else None
    data = {
        "operation_ref": op["operation_ref"],
        "operation_type": op["operation_type"],
        "idempotency_key": op["idempotency_key"],
        "request_hash": op["request_hash"],
        "correlation_ref": op["correlation_ref"],
        "attempt": op["attempt"],
        "declared_outcome": outcome,
        "status_code": status_code,
        "response_hash": body_hash,
        "core_refs": core_refs,
        "error_code": _text(payload.get("error_code") or payload.get("errorCode"), "error_code", 200, required=False) or None,
        "error_detail": _text(payload.get("error_detail") or payload.get("errorDetail"), "error_detail", 4000, required=False) or None,
        "recorded_at": _text(payload.get("recorded_at") or payload.get("recordedAt"), "recorded_at", 100, required=False) or None,
        "success_inferred_from_status_code": False,
        "scientific_validity_inferred": False,
        "automatic_retry": False,
    }
    data["receipt_hash"] = _hash(data)
    return {"ok": True, "schema": RECEIPT_SCHEMA, "receipt": data}


def build_retry_plan(payload: dict[str, Any]) -> dict[str, Any]:
    receipt = payload.get("receipt") if isinstance(payload.get("receipt"), dict) else build_receipt(payload)["receipt"]
    outcome = receipt.get("declared_outcome")
    status = receipt.get("status_code")
    error = str(receipt.get("error_code") or "").lower()
    attempt = int(receipt.get("attempt") or 1)
    max_attempts = int(payload.get("max_attempts") or payload.get("maxAttempts") or 4)
    if max_attempts < 1 or max_attempts > 20:
        raise PlatformCoreV3ProductionRuntimeError("max_attempts must be between 1 and 20.")
    retryable_transport = error in {"timeout", "transport_error", "connection_reset", "dns_error"}
    retryable_http = status == 429 or (isinstance(status, int) and 500 <= status <= 599)
    explicitly_retryable = payload.get("retryable") is True
    eligible = outcome in {"failed", "uncertain"} and attempt < max_attempts and (retryable_transport or retryable_http or explicitly_retryable)
    base = int(payload.get("base_delay_seconds") or payload.get("baseDelaySeconds") or 2)
    if base < 0 or base > 3600:
        raise PlatformCoreV3ProductionRuntimeError("base_delay_seconds must be between 0 and 3600.")
    next_delay = min(base * (2 ** max(attempt - 1, 0)), 3600) if eligible else None
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-retry-plan/0.113.0",
        "eligible_for_explicit_retry": eligible,
        "reason": "retryable-declared-failure" if eligible else "not-retryable-under-declared-policy",
        "current_attempt": attempt,
        "next_attempt": attempt + 1 if eligible else None,
        "max_attempts": max_attempts,
        "suggested_delay_seconds": next_delay,
        "reuse_idempotency_key": bool(eligible),
        "automatic_retry": False,
        "automatic_submission": False,
        "scientific_result_recomputation_implied": False,
    }


def build_recovery_plan(payload: dict[str, Any]) -> dict[str, Any]:
    receipts = _list(payload.get("receipts"), "receipts", 10000)
    steps: list[dict[str, Any]] = []
    counts = {"succeeded": 0, "failed": 0, "uncertain": 0, "duplicate": 0, "conflict": 0, "cancelled": 0, "unknown": 0}
    for raw in receipts:
        if not isinstance(raw, dict):
            raise PlatformCoreV3ProductionRuntimeError("Every receipt must be an object.")
        outcome = str(raw.get("declared_outcome") or "unknown")
        counts[outcome if outcome in counts else "unknown"] += 1
        op_ref = str(raw.get("operation_ref") or "")
        if outcome in {"failed", "uncertain"}:
            steps.append({"operation_ref": op_ref, "action": "review-and-prepare-idempotent-retry", "requires_operator_or_external_dispatcher": True})
        elif outcome == "conflict":
            steps.append({"operation_ref": op_ref, "action": "halt-and-reconcile-idempotency-conflict", "requires_operator_or_external_dispatcher": True})
        elif outcome == "duplicate":
            steps.append({"operation_ref": op_ref, "action": "reconcile-existing-core-reference", "requires_operator_or_external_dispatcher": True})
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-recovery-plan/0.113.0",
        "receipt_count": len(receipts),
        "counts": counts,
        "steps": steps,
        "recovery_required": bool(steps),
        "automatic_recovery": False,
        "automatic_retry": False,
        "automatic_submission": False,
        "conflicts_auto_resolved": False,
    }


def build_checkpoint(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    operations = _list(payload.get("operations"), "operations", 10000)
    receipts = _list(payload.get("receipts"), "receipts", 10000)
    refs = []
    for item in operations:
        if isinstance(item, dict) and item.get("operation_ref"):
            refs.append(str(item["operation_ref"]))
    receipt_refs = []
    for item in receipts:
        if isinstance(item, dict) and item.get("receipt_hash"):
            receipt_refs.append(str(item["receipt_hash"]))
    state = {
        "context_ref": context["context_ref"],
        "project_ref": context["project_ref"],
        "session_id": context.get("session_id"),
        "operation_refs": refs,
        "receipt_hashes": receipt_refs,
        "operation_count": len(operations),
        "receipt_count": len(receipts),
        "label": _text(payload.get("label"), "label", 500, required=False) or None,
    }
    checkpoint_ref = _text(payload.get("checkpoint_ref") or payload.get("checkpointRef"), "checkpoint_ref", 1000, required=False) or f"lab:production-checkpoint:{_hash(state)[:32]}"
    checkpoint = {**state, "checkpoint_ref": checkpoint_ref, "checkpoint_hash": _hash(state)}
    return {"ok": True, "schema": CHECKPOINT_SCHEMA, "checkpoint": checkpoint, "automatic_persistence": False, "automatic_core_snapshot": False}


def check_continuity(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    operations = _list(payload.get("operations"), "operations", 10000)
    mismatches = []
    for index, op in enumerate(operations):
        if not isinstance(op, dict):
            mismatches.append({"index": index, "reason": "not-an-object"})
            continue
        for key in ("context_ref", "project_ref"):
            if op.get(key) not in (None, context.get(key)):
                mismatches.append({"index": index, "field": key, "expected": context.get(key), "actual": op.get(key)})
        if context.get("session_id") and op.get("session_id") not in (None, context.get("session_id")):
            mismatches.append({"index": index, "field": "session_id", "expected": context.get("session_id"), "actual": op.get("session_id")})
    state = {"context_ref": context["context_ref"], "operation_count": len(operations), "mismatches": mismatches, "continuous": not mismatches}
    return {"ok": True, "schema": "sc-lab-platform-core-v3-production-continuity-check/0.113.0", **state, "continuity_hash": _hash(state), "automatic_repair": False}


def assess_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    components = _dict(payload.get("components"), "components")
    results = {}
    missing = []
    unhealthy = []
    version_mismatches = []
    for name, spec in COMPONENTS.items():
        value = components.get(name)
        if not isinstance(value, dict):
            missing.append(name)
            results[name] = {"present": False, "healthy": False, "expected_version": spec["version"]}
            continue
        version = str(value.get("lab_release_version") or value.get("version") or "")
        healthy = value.get("ok") is True
        results[name] = {"present": True, "healthy": healthy, "reported_version": version, "expected_version": spec["version"]}
        if not healthy:
            unhealthy.append(name)
        if version != spec["version"]:
            version_mismatches.append({"component": name, "expected": spec["version"], "actual": version})
    ready = not missing and not unhealthy and not version_mismatches
    state = {"ready": ready, "missing": missing, "unhealthy": unhealthy, "version_mismatches": version_mismatches, "components": results}
    return {"ok": True, "schema": "sc-lab-platform-core-v3-production-diagnostics/0.113.0", "status": "ready" if ready else "degraded", **state, "diagnostics_hash": _hash(state), "live_calls_performed": False, "automatic_remediation": False}


def check_readiness(payload: dict[str, Any]) -> dict[str, Any]:
    core = _dict(payload.get("core_health") or payload.get("coreHealth"), "core_health")
    version = str(core.get("version") or "0.0.0")
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    core_ok = bool(core.get("ok") is True and m and tuple(map(int, m.groups())) >= (3, 0, 0))
    diagnostics = assess_diagnostics({"components": payload.get("components") or {}})
    certification = _dict(payload.get("certification"), "certification")
    certification_ok = certification.get("declared_conformance") is True if certification else False
    production_ready = core_ok and diagnostics["ready"] and certification_ok
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-production-readiness/0.113.0",
        "status": "ready" if production_ready else "not-ready",
        "production_ready": production_ready,
        "core_compatible": core_ok,
        "detected_core_release": version,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "integration_components_ready": diagnostics["ready"],
        "declared_integration_conformance": certification_ok,
        "scientific_validity_certified": False,
        "product_quality_certified": False,
        "automatic_remediation": False,
        "automatic_submission": False,
    }


def build_roundtrip_plan(payload: dict[str, Any]) -> dict[str, Any]:
    context = _context(payload)
    requested = _list(payload.get("operations"), "operations", 1000)
    operation_plans = []
    for index, item in enumerate(requested, start=1):
        if not isinstance(item, dict):
            raise PlatformCoreV3ProductionRuntimeError("Every operations entry must be an object.")
        merged = copy.deepcopy(item)
        if "context" not in merged:
            merged["context"] = context
        operation_plans.append({"sequence": index, "submission": build_submission_plan(merged)})
    stages = [
        {"stage": 1, "name": "establish-or-confirm-core-session", "automatic": False},
        {"stage": 2, "name": "bind-lab-product-context", "automatic": False},
        {"stage": 3, "name": "prepare-declared-research-operations", "operation_count": len(operation_plans), "automatic": False},
        {"stage": 4, "name": "record-declared-receipts", "automatic": False},
        {"stage": 5, "name": "check-idempotency-and-context-continuity", "automatic": False},
        {"stage": 6, "name": "checkpoint-or-prepare-recovery", "automatic": False},
        {"stage": 7, "name": "record-certification-evidence-if-requested", "automatic": False},
    ]
    plan = {"context_ref": context["context_ref"], "project_ref": context["project_ref"], "session_id": context.get("session_id"), "stages": stages, "operations": operation_plans}
    return {"ok": True, "schema": "sc-lab-platform-core-v3-production-roundtrip-plan/0.113.0", **plan, "plan_hash": _hash(plan), "automatic_submission": False, "automatic_execution": False, "automatic_retry": False, "automatic_recovery": False}


def assess_roundtrip(payload: dict[str, Any]) -> dict[str, Any]:
    receipts = _list(payload.get("receipts"), "receipts", 10000)
    outcomes = [str(r.get("declared_outcome") or "unknown") if isinstance(r, dict) else "invalid" for r in receipts]
    conflict = any(x == "conflict" for x in outcomes)
    failed = any(x in {"failed", "cancelled", "invalid"} for x in outcomes)
    uncertain = any(x in {"uncertain", "unknown"} for x in outcomes)
    completed = bool(receipts) and not conflict and not failed and not uncertain and all(x in {"succeeded", "duplicate"} for x in outcomes)
    if conflict:
        status = "conflict"
    elif failed:
        status = "failed"
    elif uncertain:
        status = "partial-or-uncertain"
    elif completed:
        status = "declared-complete"
    else:
        status = "no-receipts"
    state = {"receipt_count": len(receipts), "outcomes": outcomes, "status": status, "declared_roundtrip_complete": completed}
    return {"ok": True, "schema": "sc-lab-platform-core-v3-production-roundtrip-assessment/0.113.0", **state, "assessment_hash": _hash(state), "scientific_validity_certified": False, "product_quality_certified": False, "truth_determined": False}


def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-production-runtime-catalog/0.113.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "component_count": len(COMPONENTS),
        "components": copy.deepcopy(COMPONENTS),
        "operation_type_count": len(OPERATION_CATALOG),
        "operation_types": copy.deepcopy(OPERATION_CATALOG),
        "receipt_outcomes": ["succeeded", "failed", "uncertain", "duplicate", "conflict", "cancelled"],
        "retryable_http_classes": [429, "5xx"],
        "retryable_transport_codes": ["timeout", "transport_error", "connection_reset", "dns_error"],
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "unified-research-session-production-runtime-ready",
        "schema": PRODUCTION_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "core_runtime_contract": CORE_RUNTIME_CONTRACT,
        "core_certification_contract": CORE_CERTIFICATION_CONTRACT,
        "component_count": len(COMPONENTS),
        "operation_type_count": len(OPERATION_CATALOG),
        "boundaries": {
            "core_remains_session_reference_authority": True,
            "lab_remains_scientific_execution_authority": True,
            "explicit_submission_plans_only": True,
            "automatic_core_submission": False,
            "automatic_retry": False,
            "automatic_recovery": False,
            "automatic_core_mutation": False,
            "automatic_scientific_execution": False,
            "automatic_scientific_certification": False,
            "automatic_product_quality_certification": False,
            "automatic_truth_determination": False,
            "status_code_success_inference": False,
        },
    }


def health() -> dict[str, Any]:
    m = manifest()
    return {
        "ok": True,
        "status": m["status"],
        "schema": "sc-lab-platform-core-v3-production-runtime-health/0.113.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "component_count": len(COMPONENTS),
        "operation_type_count": len(OPERATION_CATALOG),
        "automatic_core_submission": False,
        "automatic_retry": False,
        "automatic_recovery": False,
        "automatic_scientific_execution": False,
        "automatic_scientific_certification": False,
        "automatic_truth_determination": False,
        "serviceVersion": "1.0.0",
    }
