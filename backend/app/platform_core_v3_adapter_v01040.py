from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

LAB_VERSION = "0.104.0"
CORE_REQUIRED_RELEASE = "3.0.0"
ADAPTER_VERSION = "1.0.0"
PRODUCT_REF = "product:sustainable-catalyst-lab"
PRODUCT_ID = "sustainable-catalyst-lab"
ADAPTER_REF = "lab:adapter:platform-core-v3:0.104.0"
RUNTIME_BINDING_REF = "lab:runtime:scientific-compute:0.104.0"
CORE_RUNTIME_CONTRACT = "sc.research.unified-runtime-contract.v1"
CORE_UNIFIED_RUNTIME_CONTRACT = "sc.research.unified-research-scientific-investigation-runtime.v1"
ADAPTER_SCHEMA = "sc-lab-platform-core-v3-runtime-adapter/0.104.0"
CONTEXT_SCHEMA = "sc-lab-platform-core-v3-runtime-context/0.104.0"
HANDOFF_SCHEMA = "sc-lab-platform-core-v3-handoff-validation/0.104.0"
COMPATIBILITY_SCHEMA = "sc-lab-platform-core-v3-compatibility/0.104.0"

CORE_CAPABILITIES = (
    "object:read",
    "provenance:trace",
    "context:handoff",
    "package:export",
    "validation:record",
    "workflow:state",
)

SPECIALIST_CAPABILITIES = (
    "scientific-compute",
    "registered-method-execution",
    "workflow-execution",
    "experiment-design",
    "statistical-modeling",
    "bayesian-inference",
    "causal-inference",
    "monte-carlo",
    "sensitivity-analysis",
    "model-registry",
    "reproducibility",
    "scientific-visualization",
    "scientific-scene-rendering",
    "webgl2-rendering",
    "webgpu-rendering",
    "carbon-mrv",
    "energy-modeling",
)

REQUIRED_CORE_READINESS_FLAGS = (
    "reference_first_runtime_by_core",
    "unified_session_registry_by_core",
    "research_object_binding_by_core",
    "product_context_binding_by_core",
    "computation_execution_binding_by_core",
    "investigation_binding_by_core",
    "visual_reasoning_binding_by_core",
    "validation_challenge_binding_by_core",
    "research_package_binding_by_core",
    "cross_product_handoff_binding_by_core",
    "milestone_registry_by_core",
    "revision_history_by_core",
    "immutable_runtime_snapshots_by_core",
    "underlying_objects_remain_authoritative_in_specialist_layers",
)

REQUIRED_CORE_FALSE_BOUNDARIES = (
    "execute_scientific_work_by_core",
    "execute_code_by_core",
    "run_investigation_by_core",
    "infer_findings_by_core",
    "infer_causality_by_core",
    "select_hypothesis_by_core",
    "rank_evidence_by_core",
    "render_visuals_by_core",
    "publish_research_by_core",
    "authorize_access_by_core",
    "certify_scientific_validity_by_core",
    "determine_truth_by_core",
)


class PlatformCoreV3AdapterError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 1000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise PlatformCoreV3AdapterError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3AdapterError(f"{label} exceeds {maximum} characters.")
    return text


def _string_list(value: Any, label: str, maximum_items: int = 500) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3AdapterError(f"{label} must be an array.")
    if len(value) > maximum_items:
        raise PlatformCoreV3AdapterError(f"{label} exceeds {maximum_items} entries.")
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = _text(item, label, 1000)
        if text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _metadata(value: Any, label: str = "metadata") -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3AdapterError(f"{label} must be an object.")
    # Deep-copy so validation/normalization never mutates caller state.
    return copy.deepcopy(value)


def boundaries() -> dict[str, bool]:
    return {
        "core_is_reference_first_orchestrator": True,
        "lab_is_scientific_execution_authority": True,
        "underlying_lab_objects_remain_authoritative": True,
        "core_executes_specialist_work": False,
        "lab_mutates_core_state_automatically": False,
        "lab_calls_core_automatically": False,
        "adapter_auto_routes_research_requests": False,
        "adapter_infers_scientific_truth": False,
        "adapter_certifies_scientific_validity": False,
        "adapter_changes_access_authorization": False,
        "arbitrary_code_enabled_by_adapter": False,
    }


def manifest() -> dict[str, Any]:
    body: dict[str, Any] = {
        "ok": True,
        "status": "ready",
        "schema": ADAPTER_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "product_id": PRODUCT_ID,
        "product_ref": PRODUCT_REF,
        "role": "scientific-execution-authority",
        "adapter_ref": ADAPTER_REF,
        "runtime_binding_ref": RUNTIME_BINDING_REF,
        "required_core_release": CORE_REQUIRED_RELEASE,
        "contracts": {
            "runtime_contract": CORE_RUNTIME_CONTRACT,
            "unified_runtime": CORE_UNIFIED_RUNTIME_CONTRACT,
            "legacy_typed_handoff": "sc-typed-research-handoff-plan/0.38.1",
        },
        "core_capabilities": list(CORE_CAPABILITIES),
        "specialist_capabilities": list(SPECIALIST_CAPABILITIES),
        "supported_core_bindings": [
            "product",
            "execution",
            "handoff",
            "object-reference",
            "investigation-reference",
            "visual-reference",
            "validation-reference",
            "package-reference",
        ],
        "boundaries": boundaries(),
    }
    body["adapter_hash"] = _hash(body)
    return body


def health() -> dict[str, Any]:
    m = manifest()
    return {
        "ok": True,
        "status": "platform-core-v3-adapter-ready",
        "schema": "sc-lab-platform-core-v3-adapter-health/0.104.0",
        "lab_release_version": LAB_VERSION,
        "required_core_release": CORE_REQUIRED_RELEASE,
        "runtime_contract": CORE_RUNTIME_CONTRACT,
        "unified_runtime_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "product_ref": PRODUCT_REF,
        "adapter_ref": ADAPTER_REF,
        "runtime_binding_ref": RUNTIME_BINDING_REF,
        "capability_count": len(CORE_CAPABILITIES) + len(SPECIALIST_CAPABILITIES),
        "adapter_hash": m["adapter_hash"],
        "boundaries": boundaries(),
    }


def build_contract_product_registration(payload: dict[str, Any]) -> dict[str, Any]:
    """Build the exact Core v2.96 product-binding body retained by Core v3.

    Core owns the registry write. Lab only constructs and validates the payload;
    it never performs the remote mutation automatically in v0.104.0.
    """
    if not isinstance(payload, dict):
        raise PlatformCoreV3AdapterError("A registration request object is required.")
    contract_id = _text(payload.get("contract_id"), "contract_id", 100)
    visibility = _text(payload.get("visibility", "internal"), "visibility", 20)
    if visibility not in {"private", "internal", "public"}:
        raise PlatformCoreV3AdapterError("visibility must be private, internal, or public.")
    body = {
        "binding_key": _text(payload.get("binding_key") or f"lab-core-v3-{LAB_VERSION}", "binding_key", 240),
        "contract_id": contract_id,
        "product_ref": PRODUCT_REF,
        "product_version": LAB_VERSION,
        "adapter_ref": ADAPTER_REF,
        "supported_capabilities": list(CORE_CAPABILITIES),
        "supported_object_types": _string_list(payload.get("supported_object_types"), "supported_object_types"),
        "status": _text(payload.get("status", "declared"), "status", 60),
        "visibility": visibility,
        "metadata": {
            "runtime_binding_ref": RUNTIME_BINDING_REF,
            "unified_runtime_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
            "role": "scientific-execution-authority",
            "specialist_capabilities": list(SPECIALIST_CAPABILITIES),
            "lab_adapter_hash": manifest()["adapter_hash"],
            **_metadata(payload.get("metadata")),
        },
        "provenance": {
            "source": "sustainable-catalyst-lab",
            "lab_release_version": LAB_VERSION,
            "adapter_ref": ADAPTER_REF,
            **_metadata(payload.get("provenance"), "provenance"),
        },
    }
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-contract-registration/0.104.0",
        "target_path": "/v1/research/runtime-contract/product-bindings",
        "automatic_submission": False,
        "data": body,
        "payload_hash": _hash(body),
    }


def build_session_product_binding(payload: dict[str, Any]) -> dict[str, Any]:
    """Build the Core v3 per-session product-binding body."""
    if not isinstance(payload, dict):
        raise PlatformCoreV3AdapterError("A session product-binding request object is required.")
    session_id = _text(payload.get("session_id"), "session_id", 100)
    visibility = _text(payload.get("visibility", "internal"), "visibility", 20)
    if visibility not in {"private", "internal", "public"}:
        raise PlatformCoreV3AdapterError("visibility must be private, internal, or public.")
    body = {
        "session_id": session_id,
        "product_ref": PRODUCT_REF,
        "product_version": LAB_VERSION,
        "runtime_binding_ref": RUNTIME_BINDING_REF,
        "context_ref": _text(payload.get("context_ref"), "context_ref", 1000, required=False) or None,
        "declared_capabilities": list(SPECIALIST_CAPABILITIES),
        "visibility": visibility,
        "metadata": {
            "adapter_ref": ADAPTER_REF,
            "runtime_contract": CORE_RUNTIME_CONTRACT,
            "unified_runtime_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
            "reference_first": True,
            **_metadata(payload.get("metadata")),
        },
    }
    return {
        "ok": True,
        "schema": "sc-lab-platform-core-v3-session-product-binding/0.104.0",
        "target_path": "/v1/research/unified-runtime/product-bindings",
        "automatic_submission": False,
        "data": body,
        "payload_hash": _hash(body),
    }


def normalize_runtime_context(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3AdapterError("A Core v3 runtime context object is required.")
    session_id = _text(payload.get("session_id") or payload.get("id"), "session_id", 100)
    project_ref = _text(payload.get("project_ref"), "project_ref", 1000)
    runtime_contract_ref = _text(
        payload.get("runtime_contract_ref") or CORE_RUNTIME_CONTRACT,
        "runtime_contract_ref",
        1000,
    )
    if runtime_contract_ref != CORE_RUNTIME_CONTRACT:
        raise PlatformCoreV3AdapterError(
            f"Unsupported runtime contract '{runtime_contract_ref}'. Expected {CORE_RUNTIME_CONTRACT}.",
            409,
        )
    status = _text(payload.get("status", "active"), "status", 60)
    context = {
        "schema": CONTEXT_SCHEMA,
        "session_id": session_id,
        "project_ref": project_ref,
        "workflow_ref": _text(payload.get("workflow_ref"), "workflow_ref", 1000, required=False) or None,
        "project_state_ref": _text(payload.get("project_state_ref"), "project_state_ref", 1000, required=False) or None,
        "runtime_contract_ref": runtime_contract_ref,
        "certification_suite_ref": _text(payload.get("certification_suite_ref"), "certification_suite_ref", 1000, required=False) or None,
        "status": status,
        "visibility": _text(payload.get("visibility", "internal"), "visibility", 20),
        "metadata": _metadata(payload.get("metadata")),
        "provenance": _metadata(payload.get("provenance"), "provenance"),
        "lab_product_ref": PRODUCT_REF,
        "lab_runtime_binding_ref": RUNTIME_BINDING_REF,
    }
    if context["visibility"] not in {"private", "internal", "public"}:
        raise PlatformCoreV3AdapterError("visibility must be private, internal, or public.")
    context["context_hash"] = _hash(context)
    return {"ok": True, "context": context, "boundaries": boundaries()}


def validate_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3AdapterError("A Core v3 handoff binding object is required.")
    session_id = _text(payload.get("session_id"), "session_id", 100)
    handoff_ref = _text(payload.get("handoff_ref"), "handoff_ref", 1000)
    source_product_ref = _text(payload.get("source_product_ref"), "source_product_ref", 1000)
    target_product_ref = _text(payload.get("target_product_ref"), "target_product_ref", 1000)
    if target_product_ref not in {PRODUCT_REF, PRODUCT_ID, "lab"}:
        raise PlatformCoreV3AdapterError("This adapter only accepts handoffs targeted to Sustainable Catalyst Lab.", 409)
    normalized = {
        "schema": HANDOFF_SCHEMA,
        "session_id": session_id,
        "handoff_ref": handoff_ref,
        "source_product_ref": source_product_ref,
        "target_product_ref": PRODUCT_REF,
        "context_ref": _text(payload.get("context_ref"), "context_ref", 1000, required=False) or None,
        "status": _text(payload.get("status", "declared"), "status", 60),
        "metadata": _metadata(payload.get("metadata")),
        "provenance": _metadata(payload.get("provenance"), "provenance"),
    }
    normalized["handoff_hash"] = _hash(normalized)
    return {
        "ok": True,
        "status": "accepted-for-lab-context-binding",
        "handoff": normalized,
        "automatic_execution": False,
        "automatic_core_mutation": False,
        "legacy_typed_handoff_bridge": {
            "available": True,
            "contract": "sc-typed-research-handoff-plan/0.38.1",
            "object_mapping_available": True,
            "object_mapping_contract": "sc-lab-platform-core-v3-object-mapping/0.105.0",
            "object_mapping_path": "/v1/platform-core-v3-objects/legacy-handoff/map",
        },
    }


def compatibility_report(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3AdapterError("A Platform Core readiness object is required.")
    release = _text(payload.get("release"), "release", 40)
    contract = _text(payload.get("contract"), "contract", 1000)
    checks: dict[str, bool] = {
        "core_release": release == CORE_REQUIRED_RELEASE,
        "unified_runtime_contract": contract == CORE_UNIFIED_RUNTIME_CONTRACT,
    }
    for key in REQUIRED_CORE_READINESS_FLAGS:
        checks[key] = payload.get(key) is True
    for key in REQUIRED_CORE_FALSE_BOUNDARIES:
        checks[key] = payload.get(key) is False
    compatible = all(checks.values())
    missing = [key for key, passed in checks.items() if not passed]
    report = {
        "ok": compatible,
        "status": "compatible" if compatible else "incompatible",
        "schema": COMPATIBILITY_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "required_core_release": CORE_REQUIRED_RELEASE,
        "observed_core_release": release,
        "required_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "observed_contract": contract,
        "checks": checks,
        "failed_checks": missing,
        "automatic_registration": False,
        "automatic_remote_calls": False,
    }
    report["report_hash"] = _hash(report)
    return report
