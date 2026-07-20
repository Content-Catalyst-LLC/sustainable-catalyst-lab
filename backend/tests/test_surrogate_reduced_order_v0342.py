from __future__ import annotations

import importlib
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.model_registry import ScientificModelRegistry
from app.surrogate_reduced_order import (
    SurrogateROMError,
    SurrogateReducedOrderManager,
    normalize_definition,
    train_definition,
)


def surrogate_payload(study_id: str = "thermal-surrogate", algorithm: str = "polynomial-ridge") -> dict:
    x = [[float(i), float(i % 3)] for i in range(12)]
    y = [2.0 * row[0] - 0.5 * row[1] + 3.0 for row in x]
    return {
        "id": study_id,
        "title": "Thermal response surrogate",
        "projectId": "thermal-lab",
        "mode": "surrogate",
        "data": {"features": ["temperature", "flow"], "inputs": x, "outputs": y},
        "training": {"algorithm": algorithm, "degree": 2, "ridge": 1e-9, "kernel": "matern52"},
        "validation": {"holdoutFraction": 0.25, "randomSeed": 42, "maximumNormalizedRmse": 0.1, "minimumR2": 0.9},
        "provenance": {"datasetId": "thermal-training-v1"},
    }


def rom_payload(study_id: str = "flow-rom", mode: str = "reduced-order") -> dict:
    t = np.linspace(0, 2 * np.pi, 16)
    snapshots = np.column_stack([np.sin(t), np.cos(t), 2 * np.sin(t), 2 * np.cos(t)]).tolist()
    payload = {
        "id": study_id,
        "title": "Flow field reduced-order model",
        "projectId": "fluid-lab",
        "mode": mode,
        "data": {"snapshots": snapshots, "stateLabels": ["u1", "v1", "u2", "v2"]},
        "reducedOrder": {"energyThreshold": 0.99, "maxRank": 3, "center": True},
        "validation": {"maximumNormalizedRmse": 0.05},
    }
    if mode == "hybrid-rom":
        payload["data"]["features"] = ["phase"]
        payload["data"]["inputs"] = [[float(value)] for value in t]
        payload["training"] = {"algorithm": "radial-basis", "rbfGamma": 0.8, "ridge": 1e-8}
    return payload


def manager(tmp_path: Path) -> SurrogateReducedOrderManager:
    registry = ScientificModelRegistry(str(tmp_path / "registry.sqlite3"))
    return SurrogateReducedOrderManager(str(tmp_path / "surrogate.sqlite3"), registry, max_studies=20, max_training_rows=1000, max_snapshot_dimensions=100)


def test_polynomial_surrogate_training_is_reproducible_and_accurate():
    definition = normalize_definition(surrogate_payload())
    first = train_definition(definition)
    second = train_definition(definition)
    assert first["modelHash"] == second["modelHash"]
    assert first["validation"]["passed"] is True
    assert first["trainingMetrics"]["r2"] > 0.999999


def test_gaussian_process_reports_predictive_uncertainty(tmp_path: Path):
    mgr = manager(tmp_path)
    payload = surrogate_payload("gp-surrogate", "gaussian-process")
    payload["validation"]["maximumNormalizedRmse"] = 1.0
    mgr.train(payload)
    predicted = mgr.predict("gp-surrogate", {"inputs": {"temperature": 5.5, "flow": 1.0}})
    assert np.isfinite(predicted["prediction"]["value"])
    assert predicted["prediction"]["standardDeviation"] >= 0
    assert predicted["predictionHash"]


def test_pod_retains_energy_and_reconstructs(tmp_path: Path):
    mgr = manager(tmp_path)
    trained = mgr.train(rom_payload())
    model = trained["study"]["model"]["reducedOrder"]
    assert model["retainedRank"] <= 3
    assert model["retainedEnergy"] >= 0.99
    coefficients = model["trainingCoefficients"][0]
    predicted = mgr.predict("flow-rom", {"coefficients": coefficients})
    assert len(predicted["prediction"]["state"]) == 4


def test_hybrid_rom_maps_parameters_to_reconstructed_state(tmp_path: Path):
    mgr = manager(tmp_path)
    trained = mgr.train(rom_payload("hybrid-flow", "hybrid-rom"))
    assert trained["study"]["model"]["validation"]["passed"] is True
    predicted = mgr.predict("hybrid-flow", {"inputs": {"phase": 1.2}})
    assert len(predicted["prediction"]["state"]) == 4
    assert len(predicted["prediction"]["coefficients"]) == trained["study"]["model"]["reducedOrder"]["retainedRank"]


def test_studies_are_immutable_and_idempotent(tmp_path: Path):
    mgr = manager(tmp_path)
    first = mgr.train(surrogate_payload())
    assert first["created"] is True
    same = mgr.train(surrogate_payload())
    assert same["created"] is False
    changed = surrogate_payload()
    changed["description"] = "changed without new study ID"
    with pytest.raises(SurrogateROMError) as exc:
        mgr.train(changed)
    assert exc.value.status_code == 409


def test_surrogate_can_publish_immutable_registry_version(tmp_path: Path):
    mgr = manager(tmp_path)
    mgr.train(surrogate_payload())
    published = mgr.register_model("thermal-surrogate", {"id": "thermal-rom-model", "modelVersion": "1.0.0", "channel": "candidate"}, "reviewer")
    model = published["registration"]["model"]["model"]
    assert model["type"] == "surrogate"
    assert model["channel"] == "candidate"
    assert model["provenance"]["surrogateStudyId"] == "thermal-surrogate"
    assert mgr.get("thermal-surrogate")["study"]["status"] == "registered"


def test_validation_rejects_mismatched_hybrid_rows():
    payload = rom_payload("bad-hybrid", "hybrid-rom")
    payload["data"]["inputs"] = payload["data"]["inputs"][:-1]
    with pytest.raises(SurrogateROMError):
        normalize_definition(payload)


def test_timeline_and_health_are_durable(tmp_path: Path):
    mgr = manager(tmp_path)
    mgr.train(surrogate_payload())
    timeline = mgr.timeline("thermal-surrogate")
    assert timeline["events"][0]["event_type"] == "surrogate-study-trained"
    health = mgr.health()
    assert health["ok"] is True
    assert health["storage"] == "sqlite-wal"
    assert health["counts"]["studies"] == 1


def test_fastapi_routes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SC_LAB_MODEL_REGISTRY_DB_PATH", str(tmp_path / "registry.sqlite3"))
    monkeypatch.setenv("SC_LAB_SURROGATE_ROM_DB_PATH", str(tmp_path / "surrogate.sqlite3"))
    monkeypatch.setenv("SC_LAB_ENSEMBLE_STUDY_DB_PATH", str(tmp_path / "ensemble.sqlite3"))
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(tmp_path / "jobs.sqlite3"))
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_DB_PATH", str(tmp_path / "workflows.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_SCHEDULE_DB_PATH", str(tmp_path / "schedules.sqlite3"))
    monkeypatch.setenv("SC_LAB_EXPERIMENT_CAMPAIGN_DB_PATH", str(tmp_path / "campaigns.sqlite3"))
    monkeypatch.setenv("SC_LAB_CLOSED_LOOP_DB_PATH", str(tmp_path / "closed-loop.sqlite3"))
    monkeypatch.setenv("SC_LAB_LOAD_LEGACY_EXTENSIONS", "0")
    import app.config as config_module
    import app.main as main_module
    importlib.reload(config_module)
    main_module = importlib.reload(main_module)
    with TestClient(main_module.app) as client:
        health = client.get("/v1/surrogate-rom/health")
        assert health.status_code == 200
        assert health.json()["version"] == "0.34.2"
        validated = client.post("/v1/surrogate-rom/validate", json=surrogate_payload())
        assert validated.status_code == 200, validated.text
        trained = client.post("/v1/surrogate-rom/studies", json=surrogate_payload())
        assert trained.status_code == 200, trained.text
        predicted = client.post("/v1/surrogate-rom/studies/thermal-surrogate/predict", json={"inputs": {"temperature": 4.0, "flow": 1.0}})
        assert predicted.status_code == 200, predicted.text
        registered = client.post("/v1/surrogate-rom/studies/thermal-surrogate/register", json={"id": "thermal-surrogate-published", "modelVersion": "1.0.0"})
        assert registered.status_code == 200, registered.text
        listed = client.get("/v1/surrogate-rom/studies")
        assert listed.status_code == 200
        assert listed.json()["count"] == 1
        service = client.get("/health").json()
        assert service["version"] == "0.40.1"
        assert service["surrogateReducedOrder"]["version"] == "0.34.2"


def test_surrogate_routes_accept_governed_training_payloads_above_global_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SC_LAB_MODEL_REGISTRY_DB_PATH", str(tmp_path / "registry-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_SURROGATE_ROM_DB_PATH", str(tmp_path / "surrogate-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_ENSEMBLE_STUDY_DB_PATH", str(tmp_path / "ensemble-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_JOB_DB_PATH", str(tmp_path / "jobs-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_DISPATCHER_DB_PATH", str(tmp_path / "dispatcher-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_ARTIFACT_ROOT", str(tmp_path / "artifacts-large"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_DB_PATH", str(tmp_path / "workflows-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_WORKFLOW_SCHEDULE_DB_PATH", str(tmp_path / "schedules-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_EXPERIMENT_CAMPAIGN_DB_PATH", str(tmp_path / "campaigns-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_CLOSED_LOOP_DB_PATH", str(tmp_path / "closed-loop-large.sqlite3"))
    monkeypatch.setenv("SC_LAB_LOAD_LEGACY_EXTENSIONS", "0")
    monkeypatch.setenv("SC_LAB_MAX_REQUEST_BYTES", "262144")
    monkeypatch.setenv("SC_LAB_SURROGATE_ROM_MAX_REQUEST_BYTES", "16777216")
    payload = surrogate_payload("large-training-payload")
    payload["data"]["inputs"] = [[float(i), float(i % 7)] for i in range(14000)]
    payload["data"]["outputs"] = [2.0 * row[0] - 0.5 * row[1] + 3.0 for row in payload["data"]["inputs"]]
    import json
    assert len(json.dumps(payload).encode("utf-8")) > 262144
    import app.config as config_module
    import app.main as main_module
    importlib.reload(config_module)
    main_module = importlib.reload(main_module)
    with TestClient(main_module.app) as client:
        response = client.post("/v1/surrogate-rom/validate", json=payload)
        assert response.status_code == 200, response.text
        assert response.json()["definition"]["id"] == "large-training-payload"
