from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any

from .model_studio import ModelStudioError, normalize_model as normalize_lab_model

VERSION = "0.49.0"
SHARED_MODEL_SCHEMA = "sc-catalyst-computational-model/0.49.0"
HANDOFF_SCHEMA = "sc-catalyst-model-handoff/0.49.0"
TYPED_RESEARCH_MODEL_CONTRACT = "sc-research-model/1.0"
LAB_PRODUCT = "sustainable-catalyst-lab"
WORKBENCH_PRODUCT = "sustainable-catalyst-workbench"
LEGACY_STORAGE_KEY = "sc_workbench_handoff"
STORAGE_KEY = "sc_catalyst_model_handoff_v0490"
LEGACY_EVENT = "sc:workbench-handoff"
HANDOFF_EVENT = "sc:catalyst-model-handoff"
MAX_PACKET_BYTES = 2 * 1024 * 1024

# These keys represent executable payload surfaces. Equations are deliberately not
# included: declarative equations are revalidated by Model Studio's v0.42 grammar.
FORBIDDEN_EXECUTABLE_KEYS = {
    "code", "script", "command", "shell", "python", "javascript", "callback",
    "callbackurl", "callback_url", "webhook", "webhookurl", "webhook_url",
    "binary", "subprocess", "eval", "exec", "import",
}


class ModelHandoffError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _packet_size(value: Any) -> int:
    try:
        return len(_canonical(value).encode("utf-8"))
    except (TypeError, ValueError) as exc:
        raise ModelHandoffError("Model handoff payload must be JSON-serializable.") from exc


def _scan_for_executable_payload(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = str(key).replace("-", "").replace("_", "").lower()
            forbidden = {k.replace("-", "").replace("_", "").lower() for k in FORBIDDEN_EXECUTABLE_KEYS}
            if normalized_key in forbidden:
                raise ModelHandoffError(f"Executable field is not permitted in a model handoff: {path}.{key}.")
            _scan_for_executable_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_executable_payload(child, f"{path}[{index}]")


def _verify_hash(record: dict[str, Any], field: str, label: str) -> None:
    expected = str(record.get(field) or "").strip()
    if not expected:
        return
    copy = deepcopy(record)
    copy.pop(field, None)
    actual = _digest(copy)
    if actual != expected:
        raise ModelHandoffError(f"{label} integrity verification failed.")


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "sharedModelSchema": SHARED_MODEL_SCHEMA,
        "handoffSchema": HANDOFF_SCHEMA,
        "typedResearchContract": TYPED_RESEARCH_MODEL_CONTRACT,
        "products": {"lab": LAB_PRODUCT, "workbench": WORKBENCH_PRODUCT},
        "directions": ["lab-to-workbench", "workbench-to-lab"],
        "transport": {
            "primary": "same-origin-local-storage",
            "storageKey": STORAGE_KEY,
            "legacyStorageKey": LEGACY_STORAGE_KEY,
            "event": HANDOFF_EVENT,
            "legacyEvent": LEGACY_EVENT,
            "deepLinkParameter": "sc_model_handoff",
            "automaticRemoteDelivery": False,
        },
        "preserves": [
            "equation-or-registered-model-reference", "variables", "units", "parameters",
            "parameter-bounds", "constants", "initial-conditions", "dataset-bindings",
            "assumptions", "limitations", "provenance", "model-integrity-hash",
        ],
        "boundaries": {
            "arbitraryCode": False,
            "arbitraryPython": False,
            "arbitraryJavaScript": False,
            "shellExecution": False,
            "remoteCallbacks": False,
            "automaticRemoteDelivery": False,
            "safeDeclarativeEquationsOnly": True,
            "modelStudioRevalidationOnImport": True,
            "packetIntegrityVerification": True,
            "maximumPacketBytes": MAX_PACKET_BYTES,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "bidirectional-model-contract-ready",
        "version": VERSION,
        "sharedModelSchema": SHARED_MODEL_SCHEMA,
        "handoffSchema": HANDOFF_SCHEMA,
        "labToWorkbench": True,
        "workbenchToLab": True,
        "legacyWorkbenchTransportCompatibility": True,
        "typedResearchModelContract": TYPED_RESEARCH_MODEL_CONTRACT,
        "automaticRemoteDelivery": False,
        "arbitraryCode": False,
    }


def _shared_from_lab_model(model: dict[str, Any]) -> dict[str, Any]:
    try:
        lab_model = normalize_lab_model(model)
    except ModelStudioError as exc:
        raise ModelHandoffError(str(exc)) from exc

    family = lab_model.get("family") or "declarative-expression"
    definition = lab_model.get("definition") or {}
    if family == "declarative-expression":
        kind = "algebraic"
    elif family == "registered-model":
        kind = "registered"
    else:
        kind = "statistical"

    shared = {
        "schema": SHARED_MODEL_SCHEMA,
        "version": VERSION,
        "recordType": "computational-model",
        "id": lab_model["id"],
        "title": lab_model["title"],
        "status": lab_model.get("status") or "draft",
        "modelKind": kind,
        "scientificDefinition": {
            "family": family,
            "equation": definition.get("equation") or "",
            "registeredModelId": definition.get("registeredModelId") or "",
            "outputSymbol": definition.get("outputSymbol") or "",
            "functions": list(definition.get("functions") or []),
            "safeDeclarative": bool(definition.get("safeExecution") is True),
        },
        "variables": deepcopy(lab_model.get("variables") or []),
        "parameters": deepcopy(lab_model.get("parameters") or []),
        "constants": deepcopy(lab_model.get("constants") or []),
        "initialConditions": deepcopy(lab_model.get("initialConditions") or []),
        "dataset": deepcopy(lab_model.get("dataset") or {"datasetId": "", "bindings": []}),
        "assumptions": deepcopy(lab_model.get("assumptions") or []),
        "limitations": deepcopy(lab_model.get("limitations") or []),
        "provenance": deepcopy(lab_model.get("provenance") or {}),
        "source": {
            "product": LAB_PRODUCT,
            "release": VERSION,
            "modelStudioSchema": lab_model.get("schema"),
            "modelStudioVersion": lab_model.get("version"),
            "sourceModelHash": lab_model.get("modelHash"),
        },
        "compatibility": {
            "typedResearchContract": TYPED_RESEARCH_MODEL_CONTRACT,
            "consumerRoles": ["interactive-compute-authority", "scientific-modeling-authority"],
            "capabilities": [
                "safe-declarative-equation", "unit-aware-parameters", "parameter-bounds",
                "initial-conditions", "dataset-bindings", "provenance",
            ],
        },
    }
    hashable = deepcopy(shared)
    shared["sharedModelHash"] = _digest(hashable)
    return shared


def _normalize_existing_shared(payload: dict[str, Any]) -> dict[str, Any]:
    _verify_hash(payload, "sharedModelHash", "Shared model")
    definition = payload.get("scientificDefinition") or {}
    family = str(definition.get("family") or "").strip()
    lab_payload = {
        "id": payload.get("id"),
        "title": payload.get("title"),
        "status": payload.get("status") or "draft",
        "family": family,
        "definition": {
            "equation": definition.get("equation") or "",
            "registeredModelId": definition.get("registeredModelId") or "",
        },
        "variables": payload.get("variables") or [],
        "parameters": payload.get("parameters") or [],
        "constants": payload.get("constants") or [],
        "initialConditions": payload.get("initialConditions") or [],
        "dataset": payload.get("dataset") or {},
        "datasetBindings": (payload.get("dataset") or {}).get("bindings") or [],
        "assumptions": payload.get("assumptions") or [],
        "limitations": payload.get("limitations") or [],
        "provenance": payload.get("provenance") or {},
    }
    # Round-trip through the governed Lab normalizer to enforce symbols, bounds,
    # units, and safe declarative equation validation before accepting the model.
    return _shared_from_lab_model(lab_payload)


def normalize_shared_model(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelHandoffError("Computational model must be an object.")
    if _packet_size(payload) > MAX_PACKET_BYTES:
        raise ModelHandoffError("Computational model exceeds the handoff size limit.")
    _scan_for_executable_payload(payload)
    if payload.get("schema") == SHARED_MODEL_SCHEMA:
        return _normalize_existing_shared(payload)
    return _shared_from_lab_model(payload)


def build_workbench_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelHandoffError("Handoff payload must be an object.")
    candidate = payload.get("model") if isinstance(payload.get("model"), dict) else payload
    model = normalize_shared_model(candidate)
    packet = {
        "schema": HANDOFF_SCHEMA,
        "version": VERSION,
        "recordType": "computational-model-handoff",
        "id": f"handoff-{_digest({'model': model['sharedModelHash'], 'time': _now()})[:20]}",
        "createdAt": _now(),
        "source": {"product": LAB_PRODUCT, "role": "scientific-modeling-authority"},
        "target": {"product": WORKBENCH_PRODUCT, "role": "interactive-compute-authority"},
        "intent": "explore-interactively",
        "typedResearchContract": TYPED_RESEARCH_MODEL_CONTRACT,
        "transport": {
            "mode": "same-origin-local-storage",
            "storageKey": STORAGE_KEY,
            "legacyStorageKey": LEGACY_STORAGE_KEY,
            "event": HANDOFF_EVENT,
            "legacyEvent": LEGACY_EVENT,
            "automaticRemoteDelivery": False,
        },
        "model": model,
        "modelHash": model["sharedModelHash"],
        "provenance": {
            "labProjectId": (model.get("provenance") or {}).get("projectId") or "",
            "sourceModelId": model.get("id") or "",
            "sourceModelHash": (model.get("source") or {}).get("sourceModelHash") or "",
        },
    }
    packet["packetHash"] = _digest(packet)
    if _packet_size(packet) > MAX_PACKET_BYTES:
        raise ModelHandoffError("Model handoff exceeds the handoff size limit.")
    return {"ok": True, "handoff": packet, "model": model, "policies": policies()["transport"]}


def _extract_inbound_packet(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ModelHandoffError("Inbound Workbench handoff must be an object.")
    packet = payload.get("handoff") if isinstance(payload.get("handoff"), dict) else payload
    # Modern packet.
    if packet.get("schema") == HANDOFF_SCHEMA:
        _verify_hash(packet, "packetHash", "Handoff packet")
        source = str((packet.get("source") or {}).get("product") or "").strip()
        if source not in {WORKBENCH_PRODUCT, "workbench"}:
            raise ModelHandoffError("Inbound handoff source must be Sustainable Catalyst Workbench.")
        model = packet.get("model")
        if not isinstance(model, dict):
            raise ModelHandoffError("Inbound Workbench handoff does not contain a computational model.")
        declared_model_hash = str(packet.get("modelHash") or "").strip()
        if declared_model_hash and declared_model_hash != str(model.get("sharedModelHash") or ""):
            raise ModelHandoffError("Inbound model hash does not match the handoff packet.")
        return packet, model

    # Compatibility wrapper generated by Lab/Workbench browser transports.
    embedded = packet.get("sharedModel") if isinstance(packet.get("sharedModel"), dict) else packet.get("model")
    if isinstance(embedded, dict):
        source = str(packet.get("source") or packet.get("product") or WORKBENCH_PRODUCT).strip()
        if source not in {WORKBENCH_PRODUCT, "workbench", "research-lab-global-science"}:
            raise ModelHandoffError("Unsupported legacy model handoff source.")
        return packet, embedded

    if packet.get("schema") == "sc-lab-workbench-handoff/1.0" and packet.get("record_id"):
        raise ModelHandoffError(
            "Legacy Workbench handoff contains only a record reference and no computational model payload. "
            "Open or export the model from Workbench using the v0.49 shared computational contract."
        )
    raise ModelHandoffError("No computational model was found in the inbound Workbench handoff.")


def import_workbench_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    if _packet_size(payload) > MAX_PACKET_BYTES:
        raise ModelHandoffError("Inbound Workbench handoff exceeds the size limit.")
    _scan_for_executable_payload(payload)
    packet, incoming_model = _extract_inbound_packet(payload)
    shared = normalize_shared_model(incoming_model)
    definition = shared.get("scientificDefinition") or {}
    lab_payload = {
        "id": shared.get("id"),
        "title": shared.get("title"),
        "status": "draft",
        "family": definition.get("family"),
        "definition": {
            "equation": definition.get("equation") or "",
            "registeredModelId": definition.get("registeredModelId") or "",
        },
        "variables": shared.get("variables") or [],
        "parameters": shared.get("parameters") or [],
        "constants": shared.get("constants") or [],
        "initialConditions": shared.get("initialConditions") or [],
        "dataset": shared.get("dataset") or {},
        "datasetBindings": (shared.get("dataset") or {}).get("bindings") or [],
        "assumptions": shared.get("assumptions") or [],
        "limitations": shared.get("limitations") or [],
        "provenance": {
            **(shared.get("provenance") or {}),
            "sourceIds": list(dict.fromkeys([
                *((shared.get("provenance") or {}).get("sourceIds") or []),
                f"workbench-handoff:{packet.get('id') or packet.get('record_id') or 'legacy'}",
            ])),
        },
    }
    try:
        lab_model = normalize_lab_model(lab_payload)
    except ModelStudioError as exc:
        raise ModelHandoffError(str(exc)) from exc
    return {
        "ok": True,
        "model": lab_model,
        "sharedModel": shared,
        "sourceProduct": WORKBENCH_PRODUCT,
        "targetModule": "model-studio",
        "importedAt": _now(),
        "revalidated": True,
        "arbitraryCodeAccepted": False,
    }
