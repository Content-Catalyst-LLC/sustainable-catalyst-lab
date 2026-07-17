from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.model_registry import ModelRegistryError, ScientificModelRegistry, capture_environment, normalize_model_version


def model_payload(version: str = "1.0.0") -> dict:
    return {
        "id": "heat-transfer-surrogate",
        "modelVersion": version,
        "title": "Heat-transfer surrogate",
        "projectId": "thermal-lab",
        "type": "registered-method",
        "methodId": "simulation.parameter_sweep",
        "sourceRevision": "abc123",
        "artifactIds": ["artifact-model-weights"],
        "defaultInputs": {"temperature": 350},
        "parameters": {"tolerance": 1e-8},
        "environment": {
            "id": f"env-{version.replace('.', '-')}",
            "title": "Python scientific environment",
            "runtime": {"pythonVersion": "3.12.12"},
            "system": {"os": "Linux", "machine": "x86_64"},
            "container": {"image": "sc-lab-compute", "digest": "sha256:deadbeef"},
            "dependencies": [
                {"name": "numpy", "version": "2.2.0", "hashes": ["sha256:numpy"]},
                {"name": "scipy", "version": "1.15.0", "hashes": ["sha256:scipy"]},
            ],
            "sourceRevision": "abc123",
        },
        "provenance": {"author": "Sustainable Catalyst Lab", "calibrationStudyId": "calibration-1"},
    }


def test_environment_capture_is_deterministic_for_lock_basis():
    payload = model_payload()["environment"]
    a = capture_environment(payload)
    b = capture_environment(payload)
    assert a["lockHash"] == b["lockHash"]
    assert a["recordHash"] != b["recordHash"] or a["capturedAt"] == b["capturedAt"]
    assert [d["name"] for d in a["dependencies"]] == ["numpy", "scipy"]


def test_model_normalization_requires_registered_method():
    payload = model_payload()
    payload.pop("methodId")
    with pytest.raises(ModelRegistryError):
        normalize_model_version(payload)


def test_register_versions_are_immutable_and_idempotent(tmp_path: Path):
    registry = ScientificModelRegistry(str(tmp_path / "registry.sqlite3"))
    first = registry.register(model_payload())
    assert first["created"] is True
    same = registry.register(model_payload())
    assert same["created"] is False
    changed = model_payload()
    changed["description"] = "changed without version bump"
    with pytest.raises(ModelRegistryError) as exc:
        registry.register(changed)
    assert exc.value.status_code == 409



def test_environment_ids_are_immutable(tmp_path: Path):
    registry = ScientificModelRegistry(str(tmp_path / "registry.sqlite3"))
    registry.register(model_payload())
    changed = model_payload("1.0.1")
    changed["environment"]["id"] = "env-1-0-0"
    changed["environment"]["dependencies"][0]["version"] = "9.9.9"
    with pytest.raises(ModelRegistryError) as exc:
        registry.register(changed)
    assert exc.value.status_code == 409
    assert "Environment IDs are immutable" in exc.value.detail


def test_promotion_alias_and_deprecation_history(tmp_path: Path):
    registry = ScientificModelRegistry(str(tmp_path / "registry.sqlite3"))
    registry.register(model_payload())
    promoted = registry.promote("heat-transfer-surrogate", "1.0.0", "production", "reviewer", "validated")
    assert promoted["model"]["channel"] == "production"
    assert registry.get("heat-transfer-surrogate", "production")["model"]["modelVersion"] == "1.0.0"
    deprecated = registry.deprecate("heat-transfer-surrogate", "1.0.0", "reviewer", "superseded")
    assert deprecated["model"]["channel"] == "deprecated"
    assert deprecated["model"]["deprecatedReason"] == "superseded"
    events = registry.timeline("heat-transfer-surrogate")["events"]
    assert {event["event_type"] for event in events} >= {"model-version-registered", "model-version-promoted", "model-version-deprecated"}


def test_reproduction_manifest_and_verification(tmp_path: Path):
    registry = ScientificModelRegistry(str(tmp_path / "registry.sqlite3"))
    registry.register(model_payload())
    manifest = registry.reproduction_manifest("heat-transfer-surrogate", "1.0.0")["manifest"]
    verified = registry.verify_reproduction({"manifest": manifest})
    assert verified["ok"] is True
    manifest["environment"]["lockHash"] = "tampered"
    failed = registry.verify_reproduction({"manifest": manifest})
    assert failed["ok"] is False
    assert failed["checks"]["environmentLockHash"] is False


def test_environment_comparison_reports_dependency_drift(tmp_path: Path):
    registry = ScientificModelRegistry(str(tmp_path / "registry.sqlite3"))
    left = model_payload()["environment"]
    right = model_payload()["environment"] | {
        "dependencies": [
            {"name": "numpy", "version": "2.3.0"},
            {"name": "pandas", "version": "2.3.0"},
        ]
    }
    comparison = registry.compare_environments({"left": left, "right": right})
    assert comparison["identical"] is False
    assert comparison["dependencyDiff"]["added"] == ["pandas"]
    assert comparison["dependencyDiff"]["removed"] == ["scipy"]
    assert comparison["dependencyDiff"]["changed"] == ["numpy"]


def test_health_reports_sqlite_wal_and_counts(tmp_path: Path):
    registry = ScientificModelRegistry(str(tmp_path / "registry.sqlite3"))
    registry.register(model_payload())
    health = registry.health()
    assert health["ok"] is True
    assert health["storage"] == "sqlite-wal"
    assert health["counts"]["models"] == 1
    assert health["counts"]["versions"] == 1


def test_fastapi_routes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SC_LAB_MODEL_REGISTRY_DB_PATH", str(tmp_path / "registry.sqlite3"))
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
        assert client.get("/v1/model-registry/health").status_code == 200
        unknown = model_payload("0.9.0")
        unknown["methodId"] = "unknown.unregistered_method"
        rejected = client.post("/v1/model-registry/models", json=unknown)
        assert rejected.status_code == 422
        assert "Unknown registered compute method" in rejected.text
        registered = client.post("/v1/model-registry/models", json=model_payload())
        assert registered.status_code == 200, registered.text
        promoted = client.post("/v1/model-registry/models/heat-transfer-surrogate/1.0.0/promote", json={"channel": "production", "reason": "validated"})
        assert promoted.status_code == 200
        manifest = client.get("/v1/model-registry/models/heat-transfer-surrogate/reproduction?version=production")
        assert manifest.status_code == 200
        verified = client.post("/v1/model-registry/reproduction/verify", json=manifest.json())
        assert verified.status_code == 200
        assert verified.json()["ok"] is True
        health = client.get("/health").json()
        assert health["version"] == "0.37.1"
        assert health["scientificModelRegistry"]["version"] == "0.34.0"
