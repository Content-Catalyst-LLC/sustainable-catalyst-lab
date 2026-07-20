from __future__ import annotations

import importlib
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.ensemble_uncertainty import (
    EnsembleError,
    EnsembleStudyManager,
    analyze_results,
    generate_design,
    normalize_definition,
)
from app.model_registry import ScientificModelRegistry
from app.persistent_dispatch_queue import PersistentDistributedDispatcher


def model_payload(model_id: str = "ensemble-model-a", version: str = "1.0.0", weight: float = 1.0) -> dict:
    return {
        "id": model_id,
        "modelVersion": version,
        "title": model_id,
        "projectId": "ensemble-project",
        "type": "registered-method",
        "methodId": "simulation.parameter_sweep",
        "defaultInputs": {"model": "logistic_growth", "parameter": "rate", "values": [0.2], "fixed": {"initial": 10, "carryingCapacity": 100, "time": 10}},
        "parameters": {},
        "environment": {"id": f"env-{model_id}-{version}", "dependencies": [{"name": "numpy", "version": "2.2.0"}]},
        "metadata": {"weight": weight},
    }


def study_payload(model_ids: list[str] | None = None, method: str = "latin-hypercube", samples: int = 8) -> dict:
    ids = model_ids or ["ensemble-model-a"]
    return {
        "id": "climate-ensemble",
        "title": "Climate ensemble",
        "projectId": "ensemble-project",
        "members": [{"modelId": item, "modelVersion": "1.0.0", "weight": index + 1} for index, item in enumerate(ids)],
        "variables": [
            {"name": "rate", "path": "fixed.rate", "distribution": "uniform", "low": 0.1, "high": 0.5},
            {"name": "capacity", "path": "fixed.carryingCapacity", "distribution": "normal", "mean": 100, "stdDev": 5},
        ],
        "design": {"method": method, "samples": samples, "seed": 42},
        "output": {"path": "result.value", "label": "Outcome", "unit": "index"},
        "analysis": {"confidence": 0.9, "thresholds": [50, 100]},
    }


def build_manager(tmp_path: Path, model_ids: list[str] | None = None) -> tuple[EnsembleStudyManager, ScientificModelRegistry, PersistentDistributedDispatcher]:
    registry = ScientificModelRegistry(str(tmp_path / "models.sqlite3"))
    for model_id in model_ids or ["ensemble-model-a"]:
        registry.register(model_payload(model_id))
    dispatcher = PersistentDistributedDispatcher(str(tmp_path / "dispatcher.sqlite3"))
    manager = EnsembleStudyManager(str(tmp_path / "ensemble.sqlite3"), registry, dispatcher, max_studies=50, max_evaluations=10000)
    return manager, registry, dispatcher


def test_latin_hypercube_design_is_seeded_and_bounded(tmp_path: Path):
    manager, registry, _ = build_manager(tmp_path)
    definition = normalize_definition(study_payload(), registry)
    first = generate_design(definition)
    second = generate_design(definition)
    assert first == second
    assert len(first) == 8
    assert all(0.1 <= row["values"]["rate"] <= 0.5 for row in first)
    assert len({round(row["values"]["rate"], 8) for row in first}) == 8
    assert manager.health()["ok"] is True


def test_saltelli_design_expands_for_global_sensitivity(tmp_path: Path):
    _, registry, _ = build_manager(tmp_path)
    definition = normalize_definition(study_payload(method="saltelli-sobol", samples=4), registry)
    design = generate_design(definition)
    assert len(design) == 4 * (2 + 2)
    assert sum(row["role"] == "A" for row in design) == 4
    assert sum(row["role"] == "B" for row in design) == 4
    assert sum(row["role"] == "AB" for row in design) == 8


def test_definition_requires_registered_method_models(tmp_path: Path):
    registry = ScientificModelRegistry(str(tmp_path / "models.sqlite3"))
    payload = model_payload()
    payload["type"] = "external-artifact"
    payload.pop("methodId")
    registry.register(payload)
    with pytest.raises(EnsembleError) as exc:
        normalize_definition(study_payload(), registry)
    assert "registered-method" in exc.value.detail


def test_study_start_queues_every_member_and_sample(tmp_path: Path):
    manager, _, dispatcher = build_manager(tmp_path, ["ensemble-model-a", "ensemble-model-b"])
    created = manager.create(study_payload(["ensemble-model-a", "ensemble-model-b"], samples=4))
    assert created["created"] is True
    started = manager.start("climate-ensemble")
    study = started["study"]
    assert study["status"] in {"queued", "running"}
    assert len(study["evaluations"]) == 8
    assert dispatcher.status()["counts"]["queued"] == 8
    assert {item["modelId"] for item in study["evaluations"]} == {"ensemble-model-a", "ensemble-model-b"}


def test_manual_results_complete_weighted_ensemble_analysis(tmp_path: Path):
    manager, _, _ = build_manager(tmp_path, ["ensemble-model-a", "ensemble-model-b"])
    manager.create(study_payload(["ensemble-model-a", "ensemble-model-b"], samples=6))
    started = manager.start("climate-ensemble")["study"]
    for evaluation in started["evaluations"]:
        sample = evaluation["sampleValues"]
        model_offset = 10 if evaluation["modelId"].endswith("b") else 0
        value = 2 * float(sample["rate"]) + 0.5 * float(sample["capacity"]) + model_offset
        manager.record_result("climate-ensemble", evaluation["id"], {"outputValue": value, "result": {"manual": True}})
    completed = manager.get("climate-ensemble", reconcile=False)["study"]
    assert completed["status"] == "completed"
    assert completed["analysis"]["completeEnsembleSamples"] == 6
    assert completed["analysis"]["uncertainty"]["count"] == 6
    assert len(completed["analysis"]["members"]) == 2
    sensitivity = {item["name"]: item for item in completed["analysis"]["sensitivity"]["variables"]}
    assert sensitivity["capacity"]["pearson"] > 0.9
    assert completed["analysis"]["analysisHash"]


def test_saltelli_analysis_reports_first_and_total_indices(tmp_path: Path):
    _, registry, _ = build_manager(tmp_path)
    definition = normalize_definition(study_payload(method="saltelli-sobol", samples=16), registry)
    design = generate_design(definition)
    evaluations = []
    for row in design:
        rate = float(row["values"]["rate"])
        capacity = float(row["values"]["capacity"])
        evaluations.append({
            "status": "completed", "outputValue": 10 * rate + 0.01 * capacity,
            "memberIndex": 0, "role": row["role"], "baseIndex": row["baseIndex"],
            "parameterName": row.get("parameterName"), "sampleValues": row["values"],
        })
    analysis = analyze_results(definition, evaluations)
    assert analysis["sensitivity"]["method"] == "saltelli-sobol"
    by_name = {item["name"]: item for item in analysis["sensitivity"]["variables"]}
    assert set(by_name) == {"rate", "capacity"}
    assert by_name["rate"]["totalOrder"] > by_name["capacity"]["totalOrder"]


def test_completed_manual_results_are_immutable(tmp_path: Path):
    manager, _, dispatcher = build_manager(tmp_path)
    manager.create(study_payload(samples=4))
    evaluation = manager.start("climate-ensemble")["study"]["evaluations"][0]
    manager.record_result("climate-ensemble", evaluation["id"], {"outputValue": 1.0})
    assert dispatcher.queue_item(evaluation["queueId"])["queueItem"]["status"] == "cancelled"
    same = manager.record_result("climate-ensemble", evaluation["id"], {"outputValue": 1.0})
    assert same.get("idempotent") is True
    with pytest.raises(EnsembleError) as exc:
        manager.record_result("climate-ensemble", evaluation["id"], {"outputValue": 2.0})
    assert exc.value.status_code == 409


def test_cancel_preserves_timeline(tmp_path: Path):
    manager, _, _ = build_manager(tmp_path)
    manager.create(study_payload(samples=4))
    manager.start("climate-ensemble")
    cancelled = manager.cancel("climate-ensemble", "reviewer", "unsafe assumptions")
    assert cancelled["study"]["status"] == "cancelled"
    events = manager.timeline("climate-ensemble")["events"]
    assert {item["eventType"] for item in events} >= {"study-created", "study-started", "study-cancelled"}


def test_capacity_and_evaluation_limits_are_enforced(tmp_path: Path):
    manager, registry, _ = build_manager(tmp_path)
    payload = study_payload(method="saltelli-sobol", samples=100)
    payload["maximumEvaluations"] = 10
    with pytest.raises(EnsembleError) as exc:
        normalize_definition(payload, registry)
    assert exc.value.status_code == 409
    assert "evaluations" in exc.value.detail


def test_fastapi_routes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SC_LAB_MODEL_REGISTRY_DB_PATH", str(tmp_path / "models.sqlite3"))
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
        model = client.post("/v1/model-registry/models", json=model_payload())
        assert model.status_code == 200, model.text
        health = client.get("/v1/ensemble-studies/health")
        assert health.status_code == 200
        assert health.json()["version"] == "0.34.1"
        validated = client.post("/v1/ensemble-studies/validate", json=study_payload(samples=4))
        assert validated.status_code == 200, validated.text
        created = client.post("/v1/ensemble-studies", json=study_payload(samples=4))
        assert created.status_code == 200, created.text
        started = client.post("/v1/ensemble-studies/climate-ensemble/start")
        assert started.status_code == 200, started.text
        listed = client.get("/v1/ensemble-studies")
        assert listed.status_code == 200
        assert listed.json()["count"] == 1
        service_health = client.get("/health").json()
        assert service_health["version"] == "0.39.2"
        assert service_health["ensembleSimulation"]["version"] == "0.34.1"
