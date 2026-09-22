from __future__ import annotations

import copy
import json
import re
from hashlib import sha256
from typing import Any
from urllib.parse import quote

from .platform_core_v3_adapter_v01040 import (
    CORE_REQUIRED_RELEASE,
    CORE_RUNTIME_CONTRACT,
    CORE_UNIFIED_RUNTIME_CONTRACT,
    PRODUCT_REF,
)

LAB_VERSION = "0.105.0"
FEATURE_VERSION = "0.105.0"
MAPPING_SCHEMA = "sc-lab-platform-core-v3-object-mapping/0.105.0"
OBJECT_SCHEMA = "sc-lab-canonical-research-object/0.105.0"
BINDING_SCHEMA = "sc-lab-platform-core-v3-object-binding/0.105.0"
BATCH_SCHEMA = "sc-lab-platform-core-v3-object-binding-batch/0.105.0"
LEGACY_BRIDGE_SCHEMA = "sc-lab-platform-core-v3-legacy-object-bridge/0.105.0"
CORE_OBJECT_BINDING_PATH = "/v1/research/unified-runtime/object-bindings"

# Lab remains authoritative. These mappings describe reference identity only;
# they never copy scientific payloads into Core and never submit remote writes.
_OBJECT_SPECS: dict[str, dict[str, Any]] = {
    "dataset": {"core_type": "dataset", "contract": "sc-research-dataset/1.0"},
    "observation-set": {"core_type": "observation-set", "contract": "sc-research-observation-set/1.0"},
    "workflow": {"core_type": "workflow", "contract": "sc-research-workflow/1.0"},
    "workflow-run": {"core_type": "workflow-run", "contract": "sc-research-workflow-run/1.0", "later_binding": "execution"},
    "experiment": {"core_type": "experiment", "contract": "sc-research-experiment/1.0", "later_binding": "execution"},
    "campaign": {"core_type": "campaign", "contract": "sc-research-campaign/1.0"},
    "model": {"core_type": "model", "contract": "sc-research-model/1.0", "core_foundation_type": "model"},
    "surrogate-model": {"core_type": "surrogate-model", "contract": "sc-research-surrogate-model/1.0"},
    "artifact": {"core_type": "artifact", "contract": "sc-research-artifact/1.0"},
    "evidence-record": {"core_type": "evidence", "contract": "sc-research-evidence/1.0"},
    "citation-set": {"core_type": "citation-set", "contract": "sc-research-citation-set/1.0"},
    "publication": {"core_type": "publication", "contract": "sc-research-publication/1.0", "later_binding": "package"},
    "reproducibility-package": {"core_type": "reproducibility-package", "contract": "sc-research-reproducibility-package/1.0", "later_binding": "package"},
    "manuscript": {"core_type": "manuscript", "contract": "sc-research-manuscript/1.0", "later_binding": "package"},
    "decision-packet": {"core_type": "decision-packet", "contract": "sc-decision-packet/1.0"},
    "scenario": {"core_type": "scenario", "contract": "sc-decision-scenario/1.0", "core_foundation_type": "scenario"},
    "indicator-set": {"core_type": "indicator-set", "contract": "sc-research-indicator-set/1.0"},
    "research-brief": {"core_type": "research-brief", "contract": "sc-research-brief/1.0"},
    "workspace-snapshot": {"core_type": "workspace-snapshot", "contract": "sc-research-workspace-snapshot/1.0"},
    "scientific-figure": {"core_type": "scientific-figure", "contract": "sc-lab-scientific-figure/*", "later_binding": "visual"},
}

_ALIASES = {
    "evidence": "evidence-record",
    "evidence_record": "evidence-record",
    "observations": "observation-set",
    "observation_set": "observation-set",
    "workflow_run": "workflow-run",
    "surrogate_model": "surrogate-model",
    "citation_set": "citation-set",
    "reproducibility_package": "reproducibility-package",
    "decision_packet": "decision-packet",
    "indicator_set": "indicator-set",
    "research_brief": "research-brief",
    "workspace_snapshot": "workspace-snapshot",
    "figure": "scientific-figure",
    "scientific_figure": "scientific-figure",
}


class PlatformCoreV3ObjectMappingError(ValueError):
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
        raise PlatformCoreV3ObjectMappingError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3ObjectMappingError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3ObjectMappingError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _visibility(value: Any) -> str:
    visibility = _text(value or "internal", "visibility", 20)
    if visibility == "private":
        # Core v3 unified runtime persists internal/public. Treat Lab private as
        # internal in the Core reference layer without changing Lab visibility.
        return "internal"
    if visibility not in {"internal", "public"}:
        raise PlatformCoreV3ObjectMappingError("visibility must be private, internal, or public.")
    return visibility


def _object_type(value: Any) -> str:
    raw = _text(value, "object_type", 180).lower().replace(" ", "-")
    raw = _ALIASES.get(raw, raw)
    if raw not in _OBJECT_SPECS:
        raise PlatformCoreV3ObjectMappingError(
            f"Unsupported Lab research object type '{raw}'.",
            422,
        )
    return raw


def _local_id(payload: dict[str, Any]) -> str:
    for key in ("local_id", "localId", "object_id", "objectId", "id"):
        if payload.get(key) not in (None, ""):
            return _text(payload.get(key), key, 1000)
    raise PlatformCoreV3ObjectMappingError("local_id (or id/object_id) is required when object_ref is not supplied.")


def _canonical_ref(object_type: str, local_id: str) -> str:
    return f"lab:{object_type}:{quote(local_id, safe='-._~')}"


def _content_hash(payload: dict[str, Any]) -> str | None:
    value = payload.get("content_hash") or payload.get("contentHash") or payload.get("sha256")
    if value not in (None, ""):
        digest = _text(value, "content_hash", 128).lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise PlatformCoreV3ObjectMappingError("content_hash must be a lowercase SHA-256 digest.")
        return digest
    if "content" in payload:
        return _hash(payload["content"])
    return None


def catalog() -> dict[str, Any]:
    mappings = []
    for lab_type, spec in _OBJECT_SPECS.items():
        mappings.append({
            "lab_type": lab_type,
            "core_object_type": spec["core_type"],
            "source_contract": spec["contract"],
            "core_foundation_type": spec.get("core_foundation_type"),
            "later_specialized_binding": spec.get("later_binding"),
            "authority": "sustainable-catalyst-lab",
        })
    body = {
        "ok": True,
        "status": "canonical-object-mapping-ready",
        "schema": MAPPING_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "required_core_release": CORE_REQUIRED_RELEASE,
        "runtime_contract": CORE_RUNTIME_CONTRACT,
        "unified_runtime_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "core_object_binding_path": CORE_OBJECT_BINDING_PATH,
        "mapping_count": len(mappings),
        "mappings": mappings,
        "boundaries": {
            "reference_first": True,
            "lab_objects_remain_authoritative": True,
            "object_payloads_copied_to_core": False,
            "automatic_core_submission": False,
            "automatic_scientific_execution": False,
            "execution_binding_deferred_to": "Lab v0.107.0",
            "visual_binding_deferred_to": "Lab v0.109.0",
            "package_binding_deferred_to": "Lab v0.110.0",
        },
    }
    body["catalog_hash"] = _hash(body)
    return body


def health() -> dict[str, Any]:
    c = catalog()
    return {
        "ok": True,
        "status": "platform-core-v3-canonical-object-mapping-ready",
        "schema": "sc-lab-platform-core-v3-object-mapping-health/0.105.0",
        "lab_release_version": LAB_VERSION,
        "required_core_release": CORE_REQUIRED_RELEASE,
        "mapping_count": c["mapping_count"],
        "catalog_hash": c["catalog_hash"],
        "core_object_binding_path": CORE_OBJECT_BINDING_PATH,
        "reference_first": True,
        "automatic_core_submission": False,
    }


def normalize_object(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ObjectMappingError("A Lab research object descriptor is required.")
    lab_type = _object_type(payload.get("object_type") or payload.get("objectType") or payload.get("entity_type") or payload.get("entityType"))
    spec = _OBJECT_SPECS[lab_type]
    object_ref = _text(payload.get("object_ref") or payload.get("objectRef"), "object_ref", 1000, required=False)
    local_id = None
    if not object_ref:
        local_id = _local_id(payload)
        object_ref = _canonical_ref(spec["core_type"], local_id)
    else:
        local_id = _text(payload.get("local_id") or payload.get("localId"), "local_id", 1000, required=False) or None

    version_ref = _text(payload.get("version_ref") or payload.get("versionRef"), "version_ref", 1000, required=False) or None
    version = _text(payload.get("version"), "version", 240, required=False) or None
    if version_ref is None and version is not None:
        version_ref = f"{object_ref}:version:{quote(version, safe='-._~')}"

    role = _text(payload.get("role") or "context", "role", 120)
    visibility_in = _text(payload.get("visibility") or "internal", "visibility", 20)
    visibility = _visibility(visibility_in)
    metadata = _dict(payload.get("metadata"), "metadata")
    provenance = _dict(payload.get("provenance"), "provenance")
    digest = _content_hash(payload)

    canonical = {
        "schema": OBJECT_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "lab_object_type": lab_type,
        "core_object_type": spec["core_type"],
        "object_ref": object_ref,
        "local_id": local_id,
        "version_ref": version_ref,
        "content_hash": digest,
        "role": role,
        "lab_visibility": visibility_in,
        "core_visibility": visibility,
        "source_contract": _text(payload.get("source_contract") or payload.get("contractVersion") or spec["contract"], "source_contract", 1000),
        "authority": PRODUCT_REF,
        "core_foundation_type": spec.get("core_foundation_type"),
        "later_specialized_binding": spec.get("later_binding"),
        "metadata": metadata,
        "provenance": provenance,
    }
    canonical["mapping_hash"] = _hash(canonical)
    return {"ok": True, "object": canonical}


def build_core_object_binding(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ObjectMappingError("A Core object-binding mapping request is required.")
    session_id = _text(payload.get("session_id") or payload.get("sessionId"), "session_id", 100)
    object_payload = payload.get("object") if isinstance(payload.get("object"), dict) else payload
    canonical = normalize_object(object_payload)["object"]

    body = {
        "session_id": session_id,
        "object_type": canonical["core_object_type"],
        "object_ref": canonical["object_ref"],
        "version_ref": canonical["version_ref"],
        "content_hash": canonical["content_hash"],
        "role": canonical["role"],
        "visibility": canonical["core_visibility"],
        "metadata": {
            "authority": PRODUCT_REF,
            "lab_release_version": LAB_VERSION,
            "lab_object_type": canonical["lab_object_type"],
            "source_contract": canonical["source_contract"],
            "mapping_schema": MAPPING_SCHEMA,
            "mapping_hash": canonical["mapping_hash"],
            "underlying_object_remains_authoritative_in_lab": True,
            "later_specialized_binding": canonical["later_specialized_binding"],
            "lab_visibility": canonical["lab_visibility"],
            "lab_metadata": canonical["metadata"],
            "lab_provenance": canonical["provenance"],
        },
    }
    return {
        "ok": True,
        "schema": BINDING_SCHEMA,
        "target_path": CORE_OBJECT_BINDING_PATH,
        "automatic_submission": False,
        "data": body,
        "request_body": {"data": body},
        "object": canonical,
        "payload_hash": _hash(body),
    }


def build_core_object_binding_batch(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ObjectMappingError("A batch mapping request is required.")
    session_id = _text(payload.get("session_id") or payload.get("sessionId"), "session_id", 100)
    objects = payload.get("objects")
    if not isinstance(objects, list) or not objects:
        raise PlatformCoreV3ObjectMappingError("objects must be a non-empty array.")
    if len(objects) > 500:
        raise PlatformCoreV3ObjectMappingError("objects exceeds 500 entries.")
    bindings = []
    seen: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            raise PlatformCoreV3ObjectMappingError("Every batch object must be an object.")
        result = build_core_object_binding({"session_id": session_id, "object": item})
        ref = result["data"]["object_ref"]
        if ref in seen:
            raise PlatformCoreV3ObjectMappingError(f"Duplicate object_ref in batch: {ref}", 422)
        seen.add(ref)
        bindings.append(result)
    out = {
        "ok": True,
        "schema": BATCH_SCHEMA,
        "session_id": session_id,
        "count": len(bindings),
        "automatic_submission": False,
        "bindings": bindings,
    }
    out["batch_hash"] = _hash([b["payload_hash"] for b in bindings])
    return out


def map_legacy_typed_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ObjectMappingError("A typed research handoff or handoff plan is required.")
    handoff = payload.get("handoff") if isinstance(payload.get("handoff"), dict) else payload
    session_id = _text(payload.get("session_id") or payload.get("sessionId") or handoff.get("session_id"), "session_id", 100)
    entity_type = _object_type(handoff.get("entityType") or handoff.get("entity_type"))
    resource = handoff.get("resource")
    if not isinstance(resource, dict):
        raise PlatformCoreV3ObjectMappingError("handoff.resource must be an object.")
    expected_contract = _OBJECT_SPECS[entity_type]["contract"]
    observed_contract = _text(handoff.get("contractVersion") or handoff.get("contract_version") or expected_contract, "contractVersion", 1000)
    if expected_contract != "sc-lab-scientific-figure/*" and observed_contract != expected_contract:
        raise PlatformCoreV3ObjectMappingError(
            f"Typed handoff contract mismatch for {entity_type}: expected {expected_contract}.",
            409,
        )
    mapped = build_core_object_binding({
        "session_id": session_id,
        "object": {
            "object_type": entity_type,
            "local_id": resource.get("id"),
            "content_hash": resource.get("sha256"),
            "version": resource.get("version"),
            "visibility": resource.get("visibility") or "internal",
            "source_contract": observed_contract,
            "role": resource.get("role") or "context",
            "metadata": {
                **_dict(resource.get("metadata"), "resource.metadata"),
                "legacy_typed_handoff_id": handoff.get("id"),
                "legacy_source_product": handoff.get("sourceProduct"),
                "legacy_target_product": handoff.get("targetProduct"),
            },
            "provenance": _dict(handoff.get("provenance"), "handoff.provenance"),
        },
    })
    return {
        "ok": True,
        "schema": LEGACY_BRIDGE_SCHEMA,
        "legacy_contract": observed_contract,
        "legacy_entity_type": entity_type,
        "core_mapping": mapped,
        "automatic_submission": False,
        "automatic_execution": False,
    }
