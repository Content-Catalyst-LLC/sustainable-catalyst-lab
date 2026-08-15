from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json

import pytest

from app.shared_model_handoff import (
    HANDOFF_SCHEMA,
    LAB_PRODUCT,
    LEGACY_STORAGE_KEY,
    SHARED_MODEL_SCHEMA,
    STORAGE_KEY,
    VERSION,
    WORKBENCH_PRODUCT,
    ModelHandoffError,
    build_workbench_handoff,
    health,
    import_workbench_handoff,
    normalize_shared_model,
    policies,
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def lab_model():
    return {
        "id": "model-heat-001",
        "title": "Urban heat screening model",
        "family": "declarative-expression",
        "definition": {"equation": "T = b0 + b1*C + b2*I"},
        "variables": [
            {"symbol": "C", "label": "Canopy", "unit": "%", "role": "input"},
            {"symbol": "I", "label": "Impervious", "unit": "%", "role": "input"},
            {"symbol": "T", "label": "Temperature", "unit": "C", "role": "response"},
        ],
        "parameters": [
            {"symbol": "b0", "label": "Intercept", "unit": "C", "role": "estimated", "value": 31, "bounds": {"lower": 20, "upper": 45}},
            {"symbol": "b1", "label": "Canopy coefficient", "unit": "", "role": "estimated", "value": -0.08, "bounds": {"lower": -1, "upper": 0}},
            {"symbol": "b2", "label": "Impervious coefficient", "unit": "", "role": "estimated", "value": 0.12, "bounds": {"lower": 0, "upper": 1}},
        ],
        "constants": [],
        "initialConditions": [{"symbol": "T", "value": 31, "unit": "C"}],
        "dataset": {"datasetId": "dataset-chicago-heat"},
        "datasetBindings": [
            {"column": "canopy_pct", "symbol": "C", "role": "feature", "unit": "%"},
            {"column": "impervious_pct", "symbol": "I", "role": "feature", "unit": "%"},
            {"column": "temp_c", "symbol": "T", "role": "response", "unit": "C"},
        ],
        "assumptions": ["Screening relationship over the observed urban domain."],
        "limitations": ["Does not establish causality."],
        "provenance": {"projectId": "project-heat", "sourceIds": ["dataset-chicago-heat"], "createdAt": "2026-08-15T00:00:00Z", "createdBy": "researcher"},
    }


def workbench_packet_from(outbound):
    packet = deepcopy(outbound["handoff"])
    packet["source"] = {"product": WORKBENCH_PRODUCT, "role": "interactive-compute-authority"}
    packet["target"] = {"product": LAB_PRODUCT, "role": "scientific-modeling-authority"}
    packet["intent"] = "validate-in-lab"
    packet.pop("packetHash", None)
    packet["packetHash"] = digest(packet)
    return packet


def test_health_and_policy_contract():
    h = health(); p = policies()
    assert h["ok"] is True and h["version"] == VERSION
    assert h["labToWorkbench"] is True and h["workbenchToLab"] is True
    assert h["arbitraryCode"] is False
    assert p["sharedModelSchema"] == SHARED_MODEL_SCHEMA
    assert p["handoffSchema"] == HANDOFF_SCHEMA
    assert p["transport"]["storageKey"] == STORAGE_KEY
    assert p["transport"]["legacyStorageKey"] == LEGACY_STORAGE_KEY
    assert p["boundaries"]["automaticRemoteDelivery"] is False


def test_lab_model_normalizes_to_shared_contract_and_preserves_science():
    shared = normalize_shared_model(lab_model())
    assert shared["schema"] == SHARED_MODEL_SCHEMA
    assert shared["modelKind"] == "algebraic"
    assert shared["scientificDefinition"]["equation"] == "T = b0 + b1*C + b2*I"
    assert shared["scientificDefinition"]["safeDeclarative"] is True
    assert shared["variables"][0]["unit"] == "%"
    assert shared["parameters"][0]["bounds"] == {"lower": 20.0, "upper": 45.0}
    assert shared["initialConditions"][0]["value"] == 31.0
    assert shared["dataset"]["datasetId"] == "dataset-chicago-heat"
    assert shared["dataset"]["bindings"][0]["column"] == "canopy_pct"
    assert len(shared["sharedModelHash"]) == 64


def test_outbound_packet_targets_workbench_and_declares_local_transport():
    result = build_workbench_handoff({"model": lab_model()})
    packet = result["handoff"]
    assert packet["schema"] == HANDOFF_SCHEMA
    assert packet["source"]["product"] == LAB_PRODUCT
    assert packet["target"]["product"] == WORKBENCH_PRODUCT
    assert packet["intent"] == "explore-interactively"
    assert packet["transport"]["storageKey"] == STORAGE_KEY
    assert packet["transport"]["legacyStorageKey"] == LEGACY_STORAGE_KEY
    assert packet["transport"]["automaticRemoteDelivery"] is False
    assert packet["modelHash"] == packet["model"]["sharedModelHash"]
    assert len(packet["packetHash"]) == 64


def test_workbench_round_trip_revalidates_model_for_lab():
    outbound = build_workbench_handoff({"model": lab_model()})
    inbound = import_workbench_handoff(workbench_packet_from(outbound))
    model = inbound["model"]
    assert inbound["ok"] is True and inbound["revalidated"] is True
    assert inbound["sourceProduct"] == WORKBENCH_PRODUCT
    assert inbound["targetModule"] == "model-studio"
    assert model["family"] == "declarative-expression"
    assert model["definition"]["safeExecution"] is True
    assert model["definition"]["equation"] == "T = b0 + b1*C + b2*I"
    assert model["parameters"][1]["bounds"] == {"lower": -1.0, "upper": 0.0}
    assert any(x.startswith("workbench-handoff:") for x in model["provenance"]["sourceIds"])


def test_tampered_packet_hash_is_rejected():
    outbound = build_workbench_handoff({"model": lab_model()})
    packet = workbench_packet_from(outbound)
    packet["intent"] = "tampered"
    with pytest.raises(ModelHandoffError, match="integrity"):
        import_workbench_handoff(packet)


def test_tampered_shared_model_hash_is_rejected():
    shared = normalize_shared_model(lab_model())
    shared["title"] = "Tampered title"
    with pytest.raises(ModelHandoffError, match="integrity"):
        normalize_shared_model(shared)


def test_arbitrary_code_fields_are_rejected():
    model = lab_model(); model["code"] = "import os"
    with pytest.raises(ModelHandoffError, match="Executable field"):
        normalize_shared_model(model)


def test_remote_callback_fields_are_rejected():
    model = lab_model(); model["callbackUrl"] = "https://example.invalid/hook"
    with pytest.raises(ModelHandoffError, match="Executable field"):
        normalize_shared_model(model)


def test_legacy_wrapper_with_shared_model_is_accepted():
    shared = normalize_shared_model(lab_model())
    wrapper = {"schema": "sc-lab-workbench-handoff/1.0", "release": VERSION, "source": "workbench", "sharedModel": shared}
    result = import_workbench_handoff(wrapper)
    assert result["model"]["title"] == "Urban heat screening model"
    assert result["revalidated"] is True


def test_legacy_record_reference_without_model_is_rejected_helpfully():
    wrapper = {"schema": "sc-lab-workbench-handoff/1.0", "release": "0.28.0", "source": "research-lab-global-science", "record_id": "record-1"}
    with pytest.raises(ModelHandoffError, match="only a record reference"):
        import_workbench_handoff(wrapper)


def test_registered_model_handoff_does_not_require_equation():
    model = lab_model()
    model["family"] = "registered-model"
    model["definition"] = {"registeredModelId": "registry-model-7", "equation": ""}
    shared = normalize_shared_model(model)
    assert shared["modelKind"] == "registered"
    assert shared["scientificDefinition"]["registeredModelId"] == "registry-model-7"
