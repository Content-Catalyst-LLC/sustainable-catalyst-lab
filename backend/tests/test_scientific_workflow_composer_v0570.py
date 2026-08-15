from __future__ import annotations

import copy
import pytest

from app.scientific_workflow_composer import (
    ScientificWorkflowComposerError, catalog, compare_runs, health, normalize_workflow, policies, run_workflow, templates,
)


def rows():
    return [{"x": float(i), "y": 1.0 + 2.0 * i} for i in range(20)]


def workflow():
    return {
        "id": "linear-pipeline",
        "title": "Linear research pipeline",
        "stages": [
            {"id": "profile", "kind": "dataset.profile", "request": {}, "bindings": [{"fromStage": "$run", "sourcePath": "dataset.rows", "targetPath": "rows"}]},
            {"id": "transform", "kind": "data.transform", "request": {"plan": {"operations": [{"type": "derive", "name": "x2", "expression": "x * x"}]}}, "bindings": [{"fromStage": "$run", "sourcePath": "dataset.rows", "targetPath": "rows"}]},
            {"id": "fit", "kind": "statistics.fit", "request": {"family": "gaussian", "estimator": "ols", "features": ["x"], "response": "y"}, "bindings": [{"fromStage": "transform", "sourcePath": "result.rows", "targetPath": "rows"}]},
            {"id": "cv", "kind": "statistics.cross-validate", "request": {"study": {"family": "gaussian", "estimator": "ols", "features": ["x"], "response": "y"}, "folds": 4, "repeats": 1, "seed": 7}, "bindings": [{"fromStage": "transform", "sourcePath": "result.rows", "targetPath": "rows"}]},
        ],
    }


def test_health_catalog_and_policies():
    assert health()["version"] == "0.57.0"
    assert catalog()["stageCount"] >= 20
    p = policies()
    assert p["acyclicGraphRequired"] is True
    assert p["boundaries"]["arbitraryCode"] is False
    assert p["legacyOperationalOrchestrator"] == "workflow-orchestration-v0321"


def test_normalize_adds_dependency_from_binding_and_hash():
    out = normalize_workflow(workflow())
    fit = next(row for row in out["stages"] if row["id"] == "fit")
    assert "transform" in fit["dependsOn"]
    assert len(out["workflowHash"]) == 64
    assert out["order"].index("transform") < out["order"].index("fit")


def test_pipeline_executes_and_is_reproducible():
    payload = {"workflow": workflow(), "inputs": {"dataset": {"rows": rows()}}}
    a = run_workflow(payload)["run"]
    b = run_workflow(payload)["run"]
    assert a["status"] == "completed"
    assert a["completedStageCount"] == 4
    assert a["results"]["fit"]["result"]["result"]["metrics"]["rSquared"] > .999999
    assert a["runHash"] == b["runHash"]
    comparison = compare_runs({"left": a, "right": b})
    assert comparison["sameRunHash"] is True
    assert comparison["changedStageCount"] == 0


def test_changed_input_changes_run_hash():
    payload = {"workflow": workflow(), "inputs": {"dataset": {"rows": rows()}}}
    a = run_workflow(payload)["run"]
    changed = copy.deepcopy(payload)
    changed["inputs"]["dataset"]["rows"][0]["y"] = 99
    b = run_workflow(changed)["run"]
    assert a["runHash"] != b["runHash"]
    assert compare_runs({"left": a, "right": b})["changedStageCount"] >= 1


def test_cycles_are_rejected():
    w = workflow()
    w["stages"][0]["dependsOn"] = ["fit"]
    with pytest.raises(ScientificWorkflowComposerError, match="acyclic"):
        normalize_workflow(w)


def test_unknown_stage_and_missing_binding_are_rejected():
    w = workflow(); w["stages"][0]["kind"] = "unknown.stage"
    with pytest.raises(ScientificWorkflowComposerError, match="Unsupported"):
        normalize_workflow(w)
    w = workflow(); w["stages"][1]["bindings"] = [{"fromStage": "missing", "sourcePath": "x", "targetPath": "rows"}]
    with pytest.raises(ScientificWorkflowComposerError, match="unknown stage"):
        normalize_workflow(w)


def test_executable_fields_are_rejected():
    w = workflow(); w["stages"][0]["request"] = {"python": "print('no')"}
    with pytest.raises(ScientificWorkflowComposerError, match="Executable field"):
        normalize_workflow(w)


def test_disabled_stage_is_skipped_without_execution():
    w = {"id": "skip-test", "stages": [{"id": "skip", "kind": "dataset.profile", "enabled": False, "request": {}}]}
    run = run_workflow({"workflow": w})["run"]
    assert run["results"]["skip"]["status"] == "skipped"


def test_templates_are_governed_and_normalizable():
    result = templates()
    assert len(result["templates"]) >= 4
    for row in result["templates"]:
        normalized = normalize_workflow(row["workflow"])
        assert normalized["schema"].endswith("/0.57.0")
