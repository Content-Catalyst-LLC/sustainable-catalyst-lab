from __future__ import annotations

import copy
import json
import re
from hashlib import sha256
from typing import Any
from urllib.parse import quote

from .platform_core_v3_adapter_v01040 import PRODUCT_REF
from .platform_core_v3_object_mapping_v01050 import normalize_object
from .platform_core_v3_research_context_v01060 import normalize_research_context

LAB_VERSION = "0.107.0"
FEATURE_VERSION = "0.107.0"
MINIMUM_CORE_RELEASE = "3.0.0"
EXECUTION_SCHEMA = "sc-lab-scientific-execution-lineage/0.107.0"
BINDING_SCHEMA = "sc-lab-platform-core-v3-execution-binding/0.107.0"
BATCH_SCHEMA = "sc-lab-platform-core-v3-execution-binding-batch/0.107.0"
LINEAGE_CHECK_SCHEMA = "sc-lab-scientific-execution-lineage-check/0.107.0"
LEGACY_BRIDGE_SCHEMA = "sc-lab-scientific-execution-legacy-bridge/0.107.0"
CORE_EXECUTION_BINDING_PATH = "/v1/research/unified-runtime/execution-bindings"


class PlatformCoreV3ExecutionLineageError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, label: str, maximum: int = 2000, required: bool = True) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise PlatformCoreV3ExecutionLineageError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3ExecutionLineageError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3ExecutionLineageError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum_items: int = 1000) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3ExecutionLineageError(f"{label} must be an array.")
    if len(value) > maximum_items:
        raise PlatformCoreV3ExecutionLineageError(f"{label} exceeds {maximum_items} entries.")
    return copy.deepcopy(value)


def _visibility(value: Any) -> tuple[str, str]:
    lab = _text(value or "internal", "visibility", 20)
    if lab not in {"private", "internal", "public"}:
        raise PlatformCoreV3ExecutionLineageError("visibility must be private, internal, or public.")
    return lab, "internal" if lab == "private" else lab


def _digest(value: Any, label: str) -> str | None:
    if value in (None, ""):
        return None
    digest = _text(value, label, 128).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise PlatformCoreV3ExecutionLineageError(f"{label} must be a lowercase SHA-256 digest.")
    return digest


def _canonical_object_ref(item: Any, label: str) -> str:
    if isinstance(item, str):
        return _text(item, label, 1000)
    if not isinstance(item, dict):
        raise PlatformCoreV3ExecutionLineageError(f"Every {label} entry must be a reference string or object descriptor.")
    for key in ("object_ref", "objectRef", "ref"):
        if item.get(key) not in (None, ""):
            return _text(item[key], label, 1000)
    try:
        return normalize_object(item)["object"]["object_ref"]
    except Exception as exc:
        raise PlatformCoreV3ExecutionLineageError(f"Unable to normalize {label} object: {exc}", 422) from exc


def _canonical_refs(value: Any, label: str) -> list[str]:
    items = _list(value, label)
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        ref = _canonical_object_ref(item, label)
        if ref not in seen:
            out.append(ref)
            seen.add(ref)
    return out


def _execution_payload(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("execution")
    return value if isinstance(value, dict) else payload


def _context_from(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    try:
        return normalize_research_context(raw)["context"]
    except Exception as exc:
        raise PlatformCoreV3ExecutionLineageError(f"Invalid research context: {exc}", getattr(exc, "status_code", 400)) from exc


def normalize_execution(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ExecutionLineageError("A scientific execution descriptor is required.")
    context = _context_from(payload)
    execution = _execution_payload(payload)
    runtime = _text(execution.get("runtime") or execution.get("runtime_name") or execution.get("runtimeName"), "runtime", 120)
    environment_ref = _text(execution.get("environment_ref") or execution.get("environmentRef"), "environment_ref", 1000)
    method_ref = _text(execution.get("method_ref") or execution.get("methodRef"), "method_ref", 1000)
    execution_ref = _text(execution.get("execution_ref") or execution.get("executionRef") or execution.get("run_ref") or execution.get("runRef"), "execution_ref", 1000, required=False)
    local_id = _text(execution.get("id") or execution.get("run_id") or execution.get("runId"), "execution id", 1000, required=False)
    if not execution_ref:
        if local_id:
            execution_ref = f"lab:execution:{quote(local_id, safe='-._~')}"
        else:
            seed = {
                "context_ref": context["context_ref"],
                "runtime": runtime,
                "environment_ref": environment_ref,
                "method_ref": method_ref,
                "inputs": execution.get("input_refs") or execution.get("inputRefs") or execution.get("inputs") or [],
                "parameters": execution.get("parameters") or {},
            }
            execution_ref = f"lab:execution:{_hash(seed)[:32]}"

    input_refs = _canonical_refs(execution.get("input_refs") or execution.get("inputRefs") or execution.get("inputs"), "input_refs")
    output_refs = _canonical_refs(execution.get("output_refs") or execution.get("outputRefs") or execution.get("outputs"), "output_refs")
    parameters = _dict(execution.get("parameters"), "parameters")
    assumptions = _dict(execution.get("assumptions"), "assumptions")
    environment = _dict(execution.get("environment"), "environment")
    provenance = _dict(execution.get("provenance"), "provenance")
    metadata = _dict(execution.get("metadata"), "metadata")
    status = _text(execution.get("status") or "recorded", "status", 80)
    started_at = _text(execution.get("started_at") or execution.get("startedAt"), "started_at", 100, required=False) or None
    completed_at = _text(execution.get("completed_at") or execution.get("completedAt"), "completed_at", 100, required=False) or None
    software_ref = _text(execution.get("software_ref") or execution.get("softwareRef"), "software_ref", 1000, required=False) or None
    code_ref = _text(execution.get("code_ref") or execution.get("codeRef"), "code_ref", 1000, required=False) or None
    seed_ref = _text(execution.get("seed_ref") or execution.get("seedRef"), "seed_ref", 1000, required=False) or None
    declared_execution_hash = _digest(execution.get("execution_hash") or execution.get("executionHash"), "execution_hash")
    lab_visibility, core_visibility = _visibility(execution.get("visibility") or context.get("lab_visibility"))

    input_manifest_hash = _hash(input_refs)
    parameter_hash = _hash(parameters)
    assumption_hash = _hash(assumptions)
    environment_hash = _hash({"environment_ref": environment_ref, "environment": environment})
    output_manifest_hash = _hash(output_refs)
    lineage_material = {
        "execution_ref": execution_ref,
        "context_ref": context["context_ref"],
        "project_ref": context["project_ref"],
        "session_id": context["session_id"],
        "runtime": runtime,
        "environment_ref": environment_ref,
        "method_ref": method_ref,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "input_manifest_hash": input_manifest_hash,
        "parameter_hash": parameter_hash,
        "assumption_hash": assumption_hash,
        "environment_hash": environment_hash,
        "output_manifest_hash": output_manifest_hash,
        "software_ref": software_ref,
        "code_ref": code_ref,
        "seed_ref": seed_ref,
    }
    lineage_hash = _hash(lineage_material)
    if declared_execution_hash and declared_execution_hash != lineage_hash:
        raise PlatformCoreV3ExecutionLineageError("execution_hash does not match the normalized lineage hash.", 409)

    normalized = {
        "schema": EXECUTION_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "execution_ref": execution_ref,
        "local_id": local_id,
        "runtime": runtime,
        "environment_ref": environment_ref,
        "method_ref": method_ref,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "parameters": parameters,
        "assumptions": assumptions,
        "environment": environment,
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "software_ref": software_ref,
        "code_ref": code_ref,
        "seed_ref": seed_ref,
        "lab_visibility": lab_visibility,
        "core_visibility": core_visibility,
        "metadata": metadata,
        "provenance": provenance,
        "input_manifest_hash": input_manifest_hash,
        "parameter_hash": parameter_hash,
        "assumption_hash": assumption_hash,
        "environment_hash": environment_hash,
        "output_manifest_hash": output_manifest_hash,
        "lineage_hash": lineage_hash,
        "authority": PRODUCT_REF,
        "scientific_execution_performed_by_core": False,
        "underlying_execution_remains_authoritative_in_lab": True,
    }
    return {"ok": True, "context": context, "execution": normalized}


def build_core_execution_binding(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_execution(payload)
    context = normalized["context"]
    execution = normalized["execution"]
    if not context.get("session_id"):
        raise PlatformCoreV3ExecutionLineageError("session_id is required to build a Core execution binding.")
    body = {
        "session_id": context["session_id"],
        "execution_ref": execution["execution_ref"],
        "runtime": execution["runtime"],
        "environment_ref": execution["environment_ref"],
        "method_ref": execution["method_ref"],
        "input_refs": execution["input_refs"],
        "output_refs": execution["output_refs"],
        "visibility": execution["core_visibility"],
        "metadata": {
            "authority": PRODUCT_REF,
            "lab_release_version": LAB_VERSION,
            "context_ref": context["context_ref"],
            "project_ref": context["project_ref"],
            "workflow_ref": context.get("workflow_ref"),
            "project_state_ref": context.get("project_state_ref"),
            "status": execution["status"],
            "started_at": execution["started_at"],
            "completed_at": execution["completed_at"],
            "software_ref": execution["software_ref"],
            "code_ref": execution["code_ref"],
            "seed_ref": execution["seed_ref"],
            "input_manifest_hash": execution["input_manifest_hash"],
            "parameter_hash": execution["parameter_hash"],
            "assumption_hash": execution["assumption_hash"],
            "environment_hash": execution["environment_hash"],
            "output_manifest_hash": execution["output_manifest_hash"],
            "lineage_hash": execution["lineage_hash"],
            "parameters": execution["parameters"],
            "assumptions": execution["assumptions"],
            "environment": execution["environment"],
            "lab_visibility": execution["lab_visibility"],
            "lab_metadata": execution["metadata"],
            "lab_provenance": execution["provenance"],
            "underlying_execution_remains_authoritative_in_lab": True,
            "core_records_execution_lineage_only": True,
        },
    }
    return {
        "ok": True,
        "schema": BINDING_SCHEMA,
        "target_path": CORE_EXECUTION_BINDING_PATH,
        "automatic_submission": False,
        "automatic_execution": False,
        "automatic_core_mutation": False,
        "data": body,
        "request_body": {"data": body},
        "context": context,
        "execution": execution,
        "payload_hash": _hash(body),
    }


def build_core_execution_binding_batch(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ExecutionLineageError("A batch execution-binding request is required.")
    context = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    executions = payload.get("executions")
    if not isinstance(executions, list) or not executions:
        raise PlatformCoreV3ExecutionLineageError("executions must be a non-empty array.")
    if len(executions) > 500:
        raise PlatformCoreV3ExecutionLineageError("executions exceeds 500 entries.")
    bindings = []
    seen: set[str] = set()
    for item in executions:
        if not isinstance(item, dict):
            raise PlatformCoreV3ExecutionLineageError("Every executions entry must be an object.")
        result = build_core_execution_binding({"context": context, "execution": item})
        ref = result["data"]["execution_ref"]
        if ref in seen:
            raise PlatformCoreV3ExecutionLineageError(f"Duplicate execution_ref in batch: {ref}", 422)
        seen.add(ref)
        bindings.append(result)
    out = {
        "ok": True,
        "schema": BATCH_SCHEMA,
        "count": len(bindings),
        "automatic_submission": False,
        "automatic_execution": False,
        "bindings": bindings,
    }
    out["batch_hash"] = _hash([b["payload_hash"] for b in bindings])
    return out


def map_legacy_execution(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ExecutionLineageError("A legacy Lab run/execution descriptor is required.")
    context = payload.get("context") if isinstance(payload.get("context"), dict) else payload
    run = payload.get("run") if isinstance(payload.get("run"), dict) else payload.get("execution") if isinstance(payload.get("execution"), dict) else payload
    execution = {
        "id": run.get("id") or run.get("run_id") or run.get("runId") or run.get("execution_id") or run.get("executionId"),
        "execution_ref": run.get("execution_ref") or run.get("executionRef"),
        "runtime": run.get("runtime") or run.get("engine") or run.get("language") or "python",
        "environment_ref": run.get("environment_ref") or run.get("environmentRef") or run.get("environment_id") or run.get("environmentId") or "lab:environment:unspecified",
        "method_ref": run.get("method_ref") or run.get("methodRef") or run.get("method") or run.get("operation") or "lab:method:unspecified",
        "inputs": run.get("input_refs") or run.get("inputRefs") or run.get("inputs") or [],
        "outputs": run.get("output_refs") or run.get("outputRefs") or run.get("outputs") or [],
        "parameters": run.get("parameters") or run.get("params") or {},
        "assumptions": run.get("assumptions") or {},
        "environment": run.get("environment") or {},
        "status": run.get("status") or "recorded",
        "started_at": run.get("started_at") or run.get("startedAt"),
        "completed_at": run.get("completed_at") or run.get("completedAt") or run.get("finished_at") or run.get("finishedAt"),
        "software_ref": run.get("software_ref") or run.get("softwareRef"),
        "code_ref": run.get("code_ref") or run.get("codeRef") or run.get("source_ref") or run.get("sourceRef"),
        "seed_ref": run.get("seed_ref") or run.get("seedRef"),
        "metadata": {"legacy_bridge": True, **_dict(run.get("metadata"), "metadata")},
        "provenance": _dict(run.get("provenance"), "provenance"),
        "visibility": run.get("visibility") or context.get("visibility") or "internal",
    }
    binding = build_core_execution_binding({"context": context, "execution": execution})
    return {
        "ok": True,
        "schema": LEGACY_BRIDGE_SCHEMA,
        "automatic_submission": False,
        "automatic_execution": False,
        "source_execution": copy.deepcopy(run),
        "core_binding": binding,
    }


def check_execution_lineage(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ExecutionLineageError("An execution-lineage check request is required.")
    normalized = normalize_execution(payload)
    context = normalized["context"]
    execution = normalized["execution"]
    errors: list[str] = []
    warnings: list[str] = []
    if not context.get("session_id"):
        errors.append("session_id is missing")
    if not execution["input_refs"]:
        warnings.append("execution has no declared input_refs")
    if not execution["output_refs"]:
        warnings.append("execution has no declared output_refs")
    if execution["completed_at"] and not execution["started_at"]:
        warnings.append("completed_at is declared without started_at")
    result = {
        "ok": not errors,
        "status": "lineage-valid" if not errors else "lineage-invalid",
        "schema": LINEAGE_CHECK_SCHEMA,
        "context_ref": context["context_ref"],
        "project_ref": context["project_ref"],
        "session_id": context.get("session_id"),
        "execution_ref": execution["execution_ref"],
        "input_count": len(execution["input_refs"]),
        "output_count": len(execution["output_refs"]),
        "errors": errors,
        "warnings": warnings,
        "lineage_hash": execution["lineage_hash"],
        "lineage_is_declared_not_inferred": True,
        "scientific_validity_certified": False,
        "automatic_execution": False,
        "automatic_core_mutation": False,
    }
    result["check_hash"] = _hash(result)
    return result


def manifest() -> dict[str, Any]:
    body = {
        "ok": True,
        "status": "scientific-execution-lineage-bridge-ready",
        "schema": "sc-lab-platform-core-v3-scientific-execution-lineage-manifest/0.107.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "core_execution_binding_path": CORE_EXECUTION_BINDING_PATH,
        "capabilities": [
            "scientific-execution-normalization",
            "core-execution-binding-envelope",
            "batch-execution-binding-envelope",
            "input-output-reference-lineage",
            "parameter-assumption-environment-hashing",
            "context-preserving-execution-lineage",
            "legacy-lab-run-bridge",
            "execution-lineage-continuity-check",
        ],
        "boundaries": {
            "lab_is_scientific_execution_authority": True,
            "core_records_execution_references_and_lineage": True,
            "underlying_execution_remains_authoritative_in_lab": True,
            "automatic_core_submission": False,
            "automatic_scientific_execution": False,
            "core_executes_scientific_work": False,
            "scientific_validity_certified_by_bridge": False,
            "findings_claims_validation_bridge_deferred_to": "Lab v0.108.0",
        },
    }
    body["manifest_hash"] = _hash(body)
    return body


def health() -> dict[str, Any]:
    m = manifest()
    return {
        "ok": True,
        "status": "platform-core-v3-scientific-execution-lineage-ready",
        "schema": "sc-lab-platform-core-v3-scientific-execution-lineage-health/0.107.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "capability_count": len(m["capabilities"]),
        "core_execution_binding_path": CORE_EXECUTION_BINDING_PATH,
        "manifest_hash": m["manifest_hash"],
        "automatic_core_submission": False,
        "automatic_scientific_execution": False,
    }
