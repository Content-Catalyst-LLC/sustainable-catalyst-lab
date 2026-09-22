import pytest

from app.platform_core_v3_execution_lineage_v01070 import (
    CORE_EXECUTION_BINDING_PATH,
    MINIMUM_CORE_RELEASE,
    PlatformCoreV3ExecutionLineageError,
    build_core_execution_binding,
    build_core_execution_binding_batch,
    check_execution_lineage,
    health,
    manifest,
    map_legacy_execution,
    normalize_execution,
)


def context(**extra):
    value = {
        "project_ref": "project:energy-study",
        "session_id": "77",
        "session_key": "energy-study-2026",
        "title": "Energy Study",
        "workflow_ref": "lab:workflow:w-energy",
        "project_state_ref": "core:project-state:77",
        "researcher_ref": "researcher:tariq",
        "visibility": "private",
    }
    value.update(extra)
    return value


def execution(**extra):
    value = {
        "id": "run-1",
        "runtime": "python",
        "environment_ref": "lab:environment:python-3.12",
        "method_ref": "lab:method:monte-carlo:v1",
        "inputs": [
            {"object_type": "dataset", "id": "weather-1"},
            {"object_type": "model", "id": "grid-model-1"},
        ],
        "outputs": [
            {"object_type": "artifact", "id": "result-1"},
            {"object_type": "scientific-figure", "id": "figure-1"},
        ],
        "parameters": {"iterations": 10000, "seed": 42},
        "assumptions": {"independent_draws": True},
        "environment": {"python": "3.12", "numpy": "declared"},
        "status": "completed",
        "started_at": "2026-09-22T01:00:00Z",
        "completed_at": "2026-09-22T01:01:00Z",
        "code_ref": "git:lab@abc123",
        "seed_ref": "seed:42",
        "metadata": {"purpose": "test"},
        "provenance": {"source": "pytest"},
    }
    value.update(extra)
    return value


def test_health_and_manifest_define_execution_boundary():
    h = health(); m = manifest()
    assert h["lab_release_version"] == "0.107.0"
    assert h["minimum_core_release"] == MINIMUM_CORE_RELEASE == "3.0.0"
    assert h["core_execution_binding_path"] == CORE_EXECUTION_BINDING_PATH
    assert m["boundaries"]["lab_is_scientific_execution_authority"] is True
    assert m["boundaries"]["core_records_execution_references_and_lineage"] is True
    assert m["boundaries"]["automatic_core_submission"] is False
    assert m["boundaries"]["automatic_scientific_execution"] is False


def test_normalize_execution_builds_stable_reference_hashes_and_context():
    a = normalize_execution({"context": context(), "execution": execution()})
    b = normalize_execution({"context": context(), "execution": execution()})
    x = a["execution"]
    assert x["execution_ref"] == "lab:execution:run-1"
    assert x["input_refs"] == ["lab:dataset:weather-1", "lab:model:grid-model-1"]
    assert x["output_refs"] == ["lab:artifact:result-1", "lab:scientific-figure:figure-1"]
    assert len(x["lineage_hash"]) == 64
    assert x["lineage_hash"] == b["execution"]["lineage_hash"]
    assert a["context"]["project_ref"] == "project:energy-study"
    assert x["underlying_execution_remains_authoritative_in_lab"] is True


def test_core_execution_binding_matches_core_v3_shape_and_namespaces_lab_details():
    out = build_core_execution_binding({"context": context(), "execution": execution()})
    assert out["target_path"] == CORE_EXECUTION_BINDING_PATH
    assert out["automatic_submission"] is False
    assert out["automatic_execution"] is False
    assert out["request_body"] == {"data": out["data"]}
    data = out["data"]
    assert data["session_id"] == "77"
    assert data["execution_ref"] == "lab:execution:run-1"
    assert data["runtime"] == "python"
    assert data["environment_ref"] == "lab:environment:python-3.12"
    assert data["method_ref"] == "lab:method:monte-carlo:v1"
    assert data["input_refs"] == ["lab:dataset:weather-1", "lab:model:grid-model-1"]
    assert data["output_refs"] == ["lab:artifact:result-1", "lab:scientific-figure:figure-1"]
    assert data["metadata"]["parameters"] == {"iterations": 10000, "seed": 42}
    assert data["metadata"]["project_ref"] == "project:energy-study"
    assert data["metadata"]["underlying_execution_remains_authoritative_in_lab"] is True


def test_batch_binding_preserves_one_context_and_rejects_duplicates():
    out = build_core_execution_binding_batch({
        "context": context(),
        "executions": [execution(id="r1"), execution(id="r2", method_ref="lab:method:sobol:v1")],
    })
    assert out["count"] == 2
    assert out["automatic_submission"] is False
    assert all(x["data"]["session_id"] == "77" for x in out["bindings"])
    with pytest.raises(PlatformCoreV3ExecutionLineageError):
        build_core_execution_binding_batch({"context": context(), "executions": [execution(id="same"), execution(id="same")]})


def test_legacy_run_bridge_maps_common_lab_run_fields():
    out = map_legacy_execution({
        "context": context(),
        "run": {
            "runId": "legacy-1",
            "engine": "python",
            "environmentId": "env:legacy",
            "method": "lab:method:legacy",
            "inputs": [{"object_type": "dataset", "id": "d1"}],
            "outputs": [{"object_type": "artifact", "id": "a1"}],
            "params": {"alpha": 0.05},
        },
    })
    binding = out["core_binding"]
    assert binding["data"]["execution_ref"] == "lab:execution:legacy-1"
    assert binding["data"]["runtime"] == "python"
    assert binding["data"]["metadata"]["parameters"] == {"alpha": 0.05}
    assert out["automatic_execution"] is False


def test_lineage_check_is_declared_not_scientific_validation():
    out = check_execution_lineage({"context": context(), "execution": execution(outputs=[])})
    assert out["ok"] is True
    assert "execution has no declared output_refs" in out["warnings"]
    assert out["lineage_is_declared_not_inferred"] is True
    assert out["scientific_validity_certified"] is False
    assert out["automatic_execution"] is False


def test_execution_hash_mismatch_is_rejected():
    with pytest.raises(PlatformCoreV3ExecutionLineageError):
        normalize_execution({"context": context(), "execution": execution(execution_hash="0" * 64)})


def test_required_context_runtime_environment_and_method_are_enforced():
    with pytest.raises(PlatformCoreV3ExecutionLineageError):
        normalize_execution({"execution": execution()})
    with pytest.raises(PlatformCoreV3ExecutionLineageError):
        normalize_execution({"context": context(), "execution": execution(runtime="")})
    with pytest.raises(PlatformCoreV3ExecutionLineageError):
        normalize_execution({"context": context(), "execution": execution(environment_ref="")})
    with pytest.raises(PlatformCoreV3ExecutionLineageError):
        normalize_execution({"context": context(), "execution": execution(method_ref="")})
