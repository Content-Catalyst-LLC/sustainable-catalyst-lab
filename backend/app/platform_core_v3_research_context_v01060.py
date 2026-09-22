from __future__ import annotations

import copy
import json
from hashlib import sha256
from typing import Any

from .platform_core_v3_adapter_v01040 import (
    CORE_RUNTIME_CONTRACT,
    CORE_UNIFIED_RUNTIME_CONTRACT,
    PRODUCT_REF,
    RUNTIME_BINDING_REF,
    SPECIALIST_CAPABILITIES,
)
from .platform_core_v3_object_mapping_v01050 import build_core_object_binding

LAB_VERSION = "0.106.0"
FEATURE_VERSION = "0.106.0"
MINIMUM_CORE_RELEASE = "3.0.0"
CONTEXT_SCHEMA = "sc-lab-platform-core-v3-research-context/0.106.0"
SESSION_BUILD_SCHEMA = "sc-lab-platform-core-v3-session-registration/0.106.0"
PRODUCT_CONTEXT_SCHEMA = "sc-lab-platform-core-v3-product-context-binding/0.106.0"
OBJECT_CONTEXT_SCHEMA = "sc-lab-platform-core-v3-contextual-object-binding/0.106.0"
HANDOFF_CONTEXT_SCHEMA = "sc-lab-platform-core-v3-contextual-handoff-binding/0.106.0"
CONTINUITY_SCHEMA = "sc-lab-platform-core-v3-context-continuity/0.106.0"
CORE_SESSION_PATH = "/v1/research/unified-runtime/sessions"
CORE_PRODUCT_BINDING_PATH = "/v1/research/unified-runtime/product-bindings"
CORE_OBJECT_BINDING_PATH = "/v1/research/unified-runtime/object-bindings"
CORE_HANDOFF_BINDING_PATH = "/v1/research/unified-runtime/handoff-bindings"


class PlatformCoreV3ResearchContextError(ValueError):
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
        raise PlatformCoreV3ResearchContextError(f"{label} is required.")
    if len(text) > maximum:
        raise PlatformCoreV3ResearchContextError(f"{label} exceeds {maximum} characters.")
    return text


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PlatformCoreV3ResearchContextError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum_items: int = 500) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PlatformCoreV3ResearchContextError(f"{label} must be an array.")
    if len(value) > maximum_items:
        raise PlatformCoreV3ResearchContextError(f"{label} exceeds {maximum_items} entries.")
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        v = _text(item, label, 1000)
        if v not in seen:
            out.append(v)
            seen.add(v)
    return out


def _visibility(value: Any) -> tuple[str, str]:
    lab = _text(value or "internal", "visibility", 20)
    if lab not in {"private", "internal", "public"}:
        raise PlatformCoreV3ResearchContextError("visibility must be private, internal, or public.")
    return lab, "internal" if lab == "private" else lab


def _context_payload(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("context")
    return value if isinstance(value, dict) else payload


def normalize_research_context(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ResearchContextError("A project/session context object is required.")
    p = _context_payload(payload)
    project_ref = _text(p.get("project_ref") or p.get("projectRef"), "project_ref", 1000)
    session_id = _text(p.get("session_id") or p.get("sessionId"), "session_id", 100, required=False) or None
    session_key = _text(p.get("session_key") or p.get("sessionKey"), "session_key", 240, required=False) or None
    title = _text(p.get("title"), "title", 500, required=False) or None
    workflow_ref = _text(p.get("workflow_ref") or p.get("workflowRef"), "workflow_ref", 1000, required=False) or None
    project_state_ref = _text(p.get("project_state_ref") or p.get("projectStateRef"), "project_state_ref", 1000, required=False) or None
    certification_suite_ref = _text(p.get("certification_suite_ref") or p.get("certificationSuiteRef"), "certification_suite_ref", 1000, required=False) or None
    researcher_ref = _text(p.get("researcher_ref") or p.get("researcherRef"), "researcher_ref", 1000, required=False) or None
    agent_ref = _text(p.get("agent_ref") or p.get("agentRef"), "agent_ref", 1000, required=False) or None
    contributor_refs = _list(p.get("contributor_refs") or p.get("contributorRefs"), "contributor_refs")
    lab_visibility, core_visibility = _visibility(p.get("visibility"))
    metadata = _dict(p.get("metadata"), "metadata")
    provenance = _dict(p.get("provenance"), "provenance")
    runtime_contract_ref = _text(p.get("runtime_contract_ref") or p.get("runtimeContractRef") or CORE_RUNTIME_CONTRACT, "runtime_contract_ref", 1000)
    supplied_ref = _text(p.get("context_ref") or p.get("contextRef"), "context_ref", 1000, required=False)
    identity = {
        "project_ref": project_ref,
        "session_id": session_id,
        "session_key": session_key,
        "workflow_ref": workflow_ref,
        "project_state_ref": project_state_ref,
        "runtime_contract_ref": runtime_contract_ref,
        "researcher_ref": researcher_ref,
        "agent_ref": agent_ref,
        "contributor_refs": contributor_refs,
    }
    context_ref = supplied_ref or f"lab:research-context:{_hash(identity)[:32]}"
    context = {
        "schema": CONTEXT_SCHEMA,
        "lab_release_version": LAB_VERSION,
        "context_ref": context_ref,
        "project_ref": project_ref,
        "session_id": session_id,
        "session_key": session_key,
        "title": title,
        "workflow_ref": workflow_ref,
        "project_state_ref": project_state_ref,
        "runtime_contract_ref": runtime_contract_ref,
        "certification_suite_ref": certification_suite_ref,
        "researcher_ref": researcher_ref,
        "agent_ref": agent_ref,
        "contributor_refs": contributor_refs,
        "lab_visibility": lab_visibility,
        "core_visibility": core_visibility,
        "metadata": metadata,
        "provenance": provenance,
        "authority": PRODUCT_REF,
    }
    context["context_hash"] = _hash(context)
    return {"ok": True, "context": context}


def build_core_session_registration(payload: dict[str, Any]) -> dict[str, Any]:
    context = normalize_research_context(payload)["context"]
    if not context["session_key"]:
        raise PlatformCoreV3ResearchContextError("session_key is required to build a Core session registration.")
    if not context["title"]:
        raise PlatformCoreV3ResearchContextError("title is required to build a Core session registration.")
    body = {
        "session_key": context["session_key"],
        "title": context["title"],
        "project_ref": context["project_ref"],
        "workflow_ref": context["workflow_ref"],
        "project_state_ref": context["project_state_ref"],
        "runtime_contract_ref": context["runtime_contract_ref"],
        "certification_suite_ref": context["certification_suite_ref"],
        "visibility": context["core_visibility"],
        "metadata": {
            "context_ref": context["context_ref"],
            "authority": PRODUCT_REF,
            "lab_release_version": LAB_VERSION,
            "researcher_ref": context["researcher_ref"],
            "agent_ref": context["agent_ref"],
            "contributor_refs": context["contributor_refs"],
            "lab_visibility": context["lab_visibility"],
            "lab_metadata": context["metadata"],
        },
        "provenance": {
            "source": "sustainable-catalyst-lab",
            "context_hash": context["context_hash"],
            "lab_provenance": context["provenance"],
        },
    }
    return {
        "ok": True,
        "schema": SESSION_BUILD_SCHEMA,
        "target_path": CORE_SESSION_PATH,
        "automatic_submission": False,
        "data": body,
        "request_body": {"data": body},
        "context": context,
        "payload_hash": _hash(body),
    }


def build_core_product_context_binding(payload: dict[str, Any]) -> dict[str, Any]:
    context = normalize_research_context(payload)["context"]
    if not context["session_id"]:
        raise PlatformCoreV3ResearchContextError("session_id is required to build a Core product-context binding.")
    capabilities = _list(payload.get("declared_capabilities"), "declared_capabilities") or list(SPECIALIST_CAPABILITIES)
    body = {
        "session_id": context["session_id"],
        "product_ref": PRODUCT_REF,
        "product_version": LAB_VERSION,
        "runtime_binding_ref": RUNTIME_BINDING_REF,
        "context_ref": context["context_ref"],
        "declared_capabilities": capabilities,
        "visibility": context["core_visibility"],
        "metadata": {
            "project_ref": context["project_ref"],
            "workflow_ref": context["workflow_ref"],
            "project_state_ref": context["project_state_ref"],
            "researcher_ref": context["researcher_ref"],
            "agent_ref": context["agent_ref"],
            "contributor_refs": context["contributor_refs"],
            "context_hash": context["context_hash"],
            "underlying_lab_state_remains_authoritative": True,
        },
    }
    return {
        "ok": True,
        "schema": PRODUCT_CONTEXT_SCHEMA,
        "target_path": CORE_PRODUCT_BINDING_PATH,
        "automatic_submission": False,
        "data": body,
        "request_body": {"data": body},
        "context": context,
        "payload_hash": _hash(body),
    }


def build_contextual_object_binding(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ResearchContextError("A contextual object-binding request is required.")
    context = normalize_research_context(payload.get("context") if isinstance(payload.get("context"), dict) else payload)["context"]
    if not context["session_id"]:
        raise PlatformCoreV3ResearchContextError("session_id is required to bind an object to a Core research session.")
    object_payload = payload.get("object")
    if not isinstance(object_payload, dict):
        raise PlatformCoreV3ResearchContextError("object must be an object descriptor.")
    enriched = copy.deepcopy(object_payload)
    source_meta = _dict(enriched.get("metadata"), "object.metadata")
    source_prov = _dict(enriched.get("provenance"), "object.provenance")
    enriched["metadata"] = {
        **source_meta,
        "project_ref": context["project_ref"],
        "context_ref": context["context_ref"],
        "session_key": context["session_key"],
        "workflow_ref": context["workflow_ref"],
        "project_state_ref": context["project_state_ref"],
        "researcher_ref": context["researcher_ref"],
        "agent_ref": context["agent_ref"],
        "contributor_refs": context["contributor_refs"],
    }
    enriched["provenance"] = {
        **source_prov,
        "context_hash": context["context_hash"],
        "context_authority": PRODUCT_REF,
    }
    mapped = build_core_object_binding({"session_id": context["session_id"], "object": enriched})
    return {
        "ok": True,
        "schema": OBJECT_CONTEXT_SCHEMA,
        "context": context,
        "core_mapping": mapped,
        "automatic_submission": False,
        "automatic_execution": False,
    }


def build_contextual_handoff_binding(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ResearchContextError("A contextual handoff request is required.")
    context = normalize_research_context(payload.get("context") if isinstance(payload.get("context"), dict) else payload)["context"]
    if not context["session_id"]:
        raise PlatformCoreV3ResearchContextError("session_id is required to build a Core handoff binding.")
    handoff = payload.get("handoff") if isinstance(payload.get("handoff"), dict) else payload
    handoff_ref = _text(handoff.get("handoff_ref") or handoff.get("handoffRef") or handoff.get("id"), "handoff_ref", 1000)
    source = _text(handoff.get("source_product_ref") or handoff.get("sourceProductRef") or handoff.get("sourceProduct") or PRODUCT_REF, "source_product_ref", 1000)
    target = _text(handoff.get("target_product_ref") or handoff.get("targetProductRef") or handoff.get("targetProduct"), "target_product_ref", 1000)
    status = _text(handoff.get("status") or "declared", "status", 60)
    body = {
        "session_id": context["session_id"],
        "handoff_ref": handoff_ref,
        "source_product_ref": source,
        "target_product_ref": target,
        "context_ref": context["context_ref"],
        "status": status,
        "visibility": context["core_visibility"],
        "metadata": {
            "project_ref": context["project_ref"],
            "workflow_ref": context["workflow_ref"],
            "project_state_ref": context["project_state_ref"],
            "context_hash": context["context_hash"],
            "handoff_metadata": _dict(handoff.get("metadata"), "handoff.metadata"),
            "lab_release_version": LAB_VERSION,
        },
    }
    return {
        "ok": True,
        "schema": HANDOFF_CONTEXT_SCHEMA,
        "target_path": CORE_HANDOFF_BINDING_PATH,
        "automatic_submission": False,
        "automatic_execution": False,
        "automatic_core_mutation": False,
        "data": body,
        "request_body": {"data": body},
        "context": context,
        "payload_hash": _hash(body),
    }


def check_context_continuity(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PlatformCoreV3ResearchContextError("A context continuity request is required.")
    context = normalize_research_context(payload.get("context") if isinstance(payload.get("context"), dict) else payload)["context"]
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise PlatformCoreV3ResearchContextError("entries must be a non-empty array.")
    if len(entries) > 1000:
        raise PlatformCoreV3ResearchContextError("entries exceeds 1000 entries.")
    fields = ("project_ref", "session_id", "context_ref", "workflow_ref", "project_state_ref")
    mismatches: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise PlatformCoreV3ResearchContextError("Every continuity entry must be an object.")
        for field in fields:
            expected = context.get(field)
            observed = entry.get(field) if field in entry else entry.get("".join([field.split("_")[0]] + [x.title() for x in field.split("_")[1:]]))
            if observed in (None, "") or expected in (None, ""):
                continue
            if str(observed) != str(expected):
                mismatches.append({"index": index, "field": field, "expected": expected, "observed": observed})
    result = {
        "ok": not mismatches,
        "status": "continuous" if not mismatches else "context-mismatch",
        "schema": CONTINUITY_SCHEMA,
        "context_ref": context["context_ref"],
        "project_ref": context["project_ref"],
        "session_id": context["session_id"],
        "checked_entries": len(entries),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "continuity_is_declared_not_inferred": True,
        "automatic_core_mutation": False,
    }
    result["continuity_hash"] = _hash(result)
    return result


def manifest() -> dict[str, Any]:
    body = {
        "ok": True,
        "status": "unified-project-research-session-context-ready",
        "schema": "sc-lab-platform-core-v3-project-session-context-manifest/0.106.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "runtime_contract": CORE_RUNTIME_CONTRACT,
        "unified_runtime_contract": CORE_UNIFIED_RUNTIME_CONTRACT,
        "product_ref": PRODUCT_REF,
        "paths": {
            "sessions": CORE_SESSION_PATH,
            "product_bindings": CORE_PRODUCT_BINDING_PATH,
            "object_bindings": CORE_OBJECT_BINDING_PATH,
            "handoff_bindings": CORE_HANDOFF_BINDING_PATH,
        },
        "capabilities": [
            "project-context-normalization",
            "research-session-registration-envelope",
            "product-context-binding-envelope",
            "contextual-object-binding-envelope",
            "contextual-handoff-binding-envelope",
            "context-continuity-validation",
        ],
        "boundaries": {
            "core_owns_session_registry": True,
            "lab_owns_scientific_workspace_state": True,
            "automatic_core_submission": False,
            "automatic_scientific_execution": False,
            "execution_lineage_deferred_to": "Lab v0.107.0",
        },
    }
    body["manifest_hash"] = _hash(body)
    return body


def health() -> dict[str, Any]:
    m = manifest()
    return {
        "ok": True,
        "status": "platform-core-v3-project-session-context-ready",
        "schema": "sc-lab-platform-core-v3-project-session-context-health/0.106.0",
        "lab_release_version": LAB_VERSION,
        "minimum_core_release": MINIMUM_CORE_RELEASE,
        "product_ref": PRODUCT_REF,
        "capability_count": len(m["capabilities"]),
        "manifest_hash": m["manifest_hash"],
        "automatic_core_submission": False,
        "automatic_scientific_execution": False,
    }
