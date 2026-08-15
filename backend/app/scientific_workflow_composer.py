from __future__ import annotations

import copy
import json
import re
import secrets
import time
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Callable

from .datasets import profile_dataset
from .data_transformations import transform_dataset, join_datasets
from .model_studio import normalize_model
from .advanced_statistical_modeling import fit as statistical_fit, cross_validate as statistical_cross_validate, compare as statistical_compare
from .bayesian_inference import fit as bayesian_fit, posterior_predictive as bayesian_posterior_predictive
from .model_diagnostics import diagnose as model_diagnose, cross_validate as model_cross_validate
from .probabilistic_analysis import analyze as independent_uncertainty
from .correlated_uncertainty import analyze as correlated_uncertainty
from .dynamic_systems_v0540 import simulate as dynamic_simulate, bifurcation_scan as dynamic_bifurcation, phase_analysis as dynamic_phase
from .response_surfaces import fit as response_surface_fit, optimize as response_surface_optimize
from .advanced_experimental_design import generate_optimal_design, sequential_plan
from .graph_studio import normalize_graph, normalize_figure
from .reproducible_model_package import build_package, build_research_bundle, registry_projection

VERSION = "0.57.0"
WORKFLOW_SCHEMA = "sc-lab-scientific-workflow-composer/0.57.0"
RUN_SCHEMA = "sc-lab-scientific-workflow-run/0.57.0"
STAGE_RESULT_SCHEMA = "sc-lab-scientific-workflow-stage-result/0.57.0"
MAX_STAGES = 24
MAX_BINDINGS = 32
MAX_TEXT = 4000
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")
EXECUTABLE_KEYS = {"python", "javascript", "shell", "command", "callback", "callbackurl", "webhook", "script", "eval", "exec", "code"}


class ScientificWorkflowComposerError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = MAX_TEXT) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _safe_tree(value: Any, depth: int = 0, nodes: list[int] | None = None) -> Any:
    if nodes is None:
        nodes = [0]
    nodes[0] += 1
    if nodes[0] > 40000 or depth > 14:
        raise ScientificWorkflowComposerError("Workflow payload exceeds the bounded data-tree limit.")
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            safe_key = _text(key, 180)
            normalized_key = re.sub(r"[^a-z0-9]", "", safe_key.lower())
            if normalized_key in EXECUTABLE_KEYS:
                raise ScientificWorkflowComposerError(f"Executable field is not allowed in scientific workflows: {safe_key}")
            out[safe_key] = _safe_tree(child, depth + 1, nodes)
        return out
    if isinstance(value, list):
        if len(value) > 10000:
            raise ScientificWorkflowComposerError("Workflow array exceeds the 10,000-item limit.")
        return [_safe_tree(child, depth + 1, nodes) for child in value]
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered.startswith("javascript:") or lowered.startswith("data:text/html"):
            raise ScientificWorkflowComposerError("Executable URI content is not allowed in scientific workflows.")
        return value[:100000]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _text(value, 100000)



def _semantic_view(value: Any) -> Any:
    """Remove runtime-only fields before reproducibility hashing."""
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            low = str(key).lower()
            if low in {"generatedat", "createdat", "updatedat", "validatedat", "timestamp", "durationms", "runtimems"}:
                continue
            if low.endswith("hash"):
                continue
            out[key] = _semantic_view(child)
        return out
    if isinstance(value, list):
        return [_semantic_view(item) for item in value]
    return value

def _deep_get(value: Any, path: str) -> Any:
    current = value
    for part in [p for p in str(path or "").split(".") if p]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise ScientificWorkflowComposerError(f"Binding source path was not found: {path}")
    return copy.deepcopy(current)


def _deep_set(target: dict[str, Any], path: str, value: Any) -> None:
    parts = [p for p in str(path or "").split(".") if p]
    if not parts:
        raise ScientificWorkflowComposerError("Binding targetPath is required.")
    current = target
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        if not isinstance(current[part], dict):
            raise ScientificWorkflowComposerError(f"Binding target path crosses a non-object value: {path}")
        current = current[part]
    current[parts[-1]] = copy.deepcopy(value)


def _package_projection(payload: dict[str, Any]) -> dict[str, Any]:
    package = payload.get("package") if isinstance(payload.get("package"), dict) else payload
    return {"ok": True, "projection": registry_projection(package)}


def _stage_catalog_rows() -> list[dict[str, Any]]:
    return [
        {"kind": "dataset.profile", "label": "Dataset profile", "group": "Data", "handler": profile_dataset, "deterministic": True},
        {"kind": "data.transform", "label": "Data transformation", "group": "Data", "handler": transform_dataset, "deterministic": True},
        {"kind": "data.join", "label": "Dataset join", "group": "Data", "handler": join_datasets, "deterministic": True},
        {"kind": "model.normalize", "label": "Model definition", "group": "Model", "handler": normalize_model, "deterministic": True},
        {"kind": "statistics.fit", "label": "Statistical fit", "group": "Model", "handler": statistical_fit, "deterministic": True},
        {"kind": "statistics.cross-validate", "label": "Statistical cross-validation", "group": "Validate", "handler": statistical_cross_validate, "deterministic": True},
        {"kind": "statistics.compare", "label": "Statistical model comparison", "group": "Validate", "handler": statistical_compare, "deterministic": True},
        {"kind": "diagnostics.run", "label": "Model diagnostics", "group": "Validate", "handler": model_diagnose, "deterministic": True},
        {"kind": "diagnostics.cross-validate", "label": "Model cross-validation", "group": "Validate", "handler": model_cross_validate, "deterministic": True},
        {"kind": "bayesian.fit", "label": "Bayesian inference", "group": "Model", "handler": bayesian_fit, "deterministic": True},
        {"kind": "bayesian.posterior-predictive", "label": "Posterior predictive", "group": "Validate", "handler": bayesian_posterior_predictive, "deterministic": True},
        {"kind": "uncertainty.independent", "label": "Independent uncertainty", "group": "Uncertainty", "handler": independent_uncertainty, "deterministic": True},
        {"kind": "uncertainty.correlated", "label": "Correlated uncertainty", "group": "Uncertainty", "handler": correlated_uncertainty, "deterministic": True},
        {"kind": "dynamic.simulate", "label": "Dynamic-system simulation", "group": "Model", "handler": dynamic_simulate, "deterministic": True},
        {"kind": "dynamic.bifurcation", "label": "Bifurcation scan", "group": "Validate", "handler": dynamic_bifurcation, "deterministic": True},
        {"kind": "dynamic.phase", "label": "Phase analysis", "group": "Validate", "handler": dynamic_phase, "deterministic": True},
        {"kind": "response-surface.fit", "label": "Response-surface fit", "group": "Model", "handler": response_surface_fit, "deterministic": True},
        {"kind": "response-surface.optimize", "label": "Response-surface optimization", "group": "Model", "handler": response_surface_optimize, "deterministic": True},
        {"kind": "experiment.design", "label": "Advanced experiment design", "group": "Experiment", "handler": generate_optimal_design, "deterministic": True, "proposalOnly": True},
        {"kind": "experiment.sequential", "label": "Sequential experiment proposal", "group": "Experiment", "handler": sequential_plan, "deterministic": True, "proposalOnly": True},
        {"kind": "graph.normalize", "label": "Scientific graph", "group": "Figure", "handler": normalize_graph, "deterministic": True},
        {"kind": "figure.normalize", "label": "Scientific figure", "group": "Figure", "handler": normalize_figure, "deterministic": True},
        {"kind": "model.package", "label": "Reproducible model package", "group": "Record", "handler": build_package, "deterministic": True},
        {"kind": "registry.project", "label": "Registry projection", "group": "Record", "handler": _package_projection, "deterministic": True, "proposalOnly": True},
        {"kind": "report.bundle", "label": "Research bundle", "group": "Record", "handler": build_research_bundle, "deterministic": True},
    ]


CATALOG = {row["kind"]: row for row in _stage_catalog_rows()}


def catalog() -> dict[str, Any]:
    stages = [{k: v for k, v in row.items() if k != "handler"} for row in _stage_catalog_rows()]
    return {"ok": True, "version": VERSION, "schema": WORKFLOW_SCHEMA, "stages": stages, "stageCount": len(stages)}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "architecture": "bounded-scientific-workflow-composer",
        "maximumStages": MAX_STAGES,
        "explicitBindings": True,
        "acyclicGraphRequired": True,
        "deterministicRunHash": True,
        "projectSavedDefinitions": True,
        "projectSavedRuns": True,
        "legacyOperationalOrchestrator": "workflow-orchestration-v0321",
        "boundaries": {
            "arbitraryCode": False,
            "arbitraryCallbacks": False,
            "automaticExperimentExecution": False,
            "automaticRegistryPromotion": False,
            "automaticPublication": False,
            "automaticWorkflowScheduling": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "scientific-workflow-composer-ready",
        "version": VERSION,
        "schema": WORKFLOW_SCHEMA,
        "runSchema": RUN_SCHEMA,
        "stageKinds": len(CATALOG),
        "legacyOrchestrationCompatible": True,
        "automaticExecutionOfExternalSystems": False,
        "arbitraryCode": False,
    }


def _normalize_binding(raw: Any, stage_id: str, known_ids: set[str]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ScientificWorkflowComposerError(f"Stage {stage_id} contains an invalid binding.")
    from_stage = _text(raw.get("fromStage") or raw.get("from"), 160)
    source_path = _text(raw.get("sourcePath") or raw.get("source"), 500)
    target_path = _text(raw.get("targetPath") or raw.get("target"), 500)
    if not from_stage or not source_path or not target_path:
        raise ScientificWorkflowComposerError(f"Stage {stage_id} binding requires fromStage, sourcePath, and targetPath.")
    if from_stage != "$run" and from_stage not in known_ids:
        raise ScientificWorkflowComposerError(f"Stage {stage_id} binding references unknown stage: {from_stage}")
    return {"fromStage": from_stage, "sourcePath": source_path, "targetPath": target_path}


def _topological(stages: list[dict[str, Any]]) -> list[str]:
    deps = {stage["id"]: set(stage["dependsOn"]) for stage in stages}
    out: list[str] = []
    ready = sorted([sid for sid, values in deps.items() if not values])
    while ready:
        sid = ready.pop(0)
        out.append(sid)
        for other in sorted(deps):
            if sid in deps[other]:
                deps[other].remove(sid)
                if not deps[other] and other not in out and other not in ready:
                    ready.append(other)
                    ready.sort()
    if len(out) != len(stages):
        raise ScientificWorkflowComposerError("Scientific workflow must be acyclic.")
    return out


def normalize_workflow(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("workflow") if isinstance(payload.get("workflow"), dict) else payload
    if not isinstance(source, dict):
        raise ScientificWorkflowComposerError("A workflow object is required.")
    workflow_id = _text(source.get("id"), 160) or f"scientific-workflow-{secrets.token_hex(6)}"
    if not ID_RE.match(workflow_id):
        raise ScientificWorkflowComposerError("Workflow ID may contain only letters, numbers, dots, underscores, and hyphens.")
    raw_stages = source.get("stages")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise ScientificWorkflowComposerError("A scientific workflow requires at least one stage.")
    if len(raw_stages) > MAX_STAGES:
        raise ScientificWorkflowComposerError(f"A scientific workflow may contain at most {MAX_STAGES} stages.")

    prelim: list[dict[str, Any]] = []
    ids: set[str] = set()
    previous: str | None = None
    for index, raw in enumerate(raw_stages):
        if not isinstance(raw, dict):
            raise ScientificWorkflowComposerError(f"Workflow stage {index + 1} must be an object.")
        stage_id = _text(raw.get("id"), 160) or f"stage-{index + 1}"
        if not ID_RE.match(stage_id) or stage_id in ids:
            raise ScientificWorkflowComposerError(f"Workflow stage ID is invalid or duplicated: {stage_id}")
        kind = _text(raw.get("kind") or raw.get("type"), 100)
        if kind not in CATALOG:
            raise ScientificWorkflowComposerError(f"Unsupported scientific workflow stage kind: {kind}")
        if "dependsOn" in raw:
            dep_raw = raw.get("dependsOn")
            if not isinstance(dep_raw, list):
                raise ScientificWorkflowComposerError(f"Stage {stage_id} dependsOn must be an array.")
            depends = [_text(v, 160) for v in dep_raw if _text(v, 160)]
        else:
            depends = [previous] if previous else []
        request = _safe_tree(raw.get("request") or {})
        prelim.append({
            "id": stage_id,
            "title": _text(raw.get("title"), 260) or CATALOG[kind]["label"],
            "kind": kind,
            "enabled": bool(raw.get("enabled", True)),
            "dependsOn": list(dict.fromkeys(depends)),
            "request": request,
            "bindingsRaw": raw.get("bindings") or [],
            "notes": _text(raw.get("notes"), 1200),
        })
        ids.add(stage_id)
        previous = stage_id

    for stage in prelim:
        for dep in stage["dependsOn"]:
            if dep not in ids or dep == stage["id"]:
                raise ScientificWorkflowComposerError(f"Stage {stage['id']} has an invalid dependency: {dep}")
        raw_bindings = stage.pop("bindingsRaw")
        if not isinstance(raw_bindings, list) or len(raw_bindings) > MAX_BINDINGS:
            raise ScientificWorkflowComposerError(f"Stage {stage['id']} has too many or invalid bindings.")
        stage["bindings"] = [_normalize_binding(item, stage["id"], ids) for item in raw_bindings]
        for binding in stage["bindings"]:
            source_stage = binding["fromStage"]
            if source_stage != "$run" and source_stage not in stage["dependsOn"]:
                stage["dependsOn"].append(source_stage)

    order = _topological(prelim)
    workflow = {
        "schema": WORKFLOW_SCHEMA,
        "version": VERSION,
        "id": workflow_id,
        "title": _text(source.get("title"), 300) or "Scientific workflow",
        "description": _text(source.get("description"), 1200),
        "projectId": _text(source.get("projectId") or source.get("project_id"), 180),
        "stages": prelim,
        "order": order,
        "governance": {
            "arbitraryCode": False,
            "automaticExperimentExecution": False,
            "automaticRegistryPromotion": False,
            "automaticPublication": False,
            "humanReviewRequired": True,
        },
    }
    workflow["workflowHash"] = _hash({k: v for k, v in workflow.items() if k != "workflowHash"})
    return workflow


def _resolve_stage_request(stage: dict[str, Any], run_inputs: dict[str, Any], stage_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    request = copy.deepcopy(stage["request"])
    for binding in stage["bindings"]:
        if binding["fromStage"] == "$run":
            root = run_inputs
        else:
            root = stage_results[binding["fromStage"]]["result"]
        value = _deep_get(root, binding["sourcePath"])
        _deep_set(request, binding["targetPath"], value)
    return request


def _call_stage(kind: str, request: dict[str, Any]) -> Any:
    row = CATALOG[kind]
    handler: Callable[[dict[str, Any]], Any] = row["handler"]
    return handler(request)


def run_workflow(payload: dict[str, Any]) -> dict[str, Any]:
    workflow = normalize_workflow(payload.get("workflow") if isinstance(payload.get("workflow"), dict) else payload)
    run_inputs = _safe_tree(payload.get("inputs") or {})
    stage_by_id = {stage["id"]: stage for stage in workflow["stages"]}
    results: dict[str, dict[str, Any]] = {}
    timeline: list[dict[str, Any]] = []
    started = time.perf_counter()
    for stage_id in workflow["order"]:
        stage = stage_by_id[stage_id]
        if not stage["enabled"]:
            record = {"schema": STAGE_RESULT_SCHEMA, "version": VERSION, "stageId": stage_id, "kind": stage["kind"], "status": "skipped", "reason": "disabled", "durationMs": 0.0, "result": None, "outputHash": _hash(None)}
            results[stage_id] = record
            timeline.append({"stageId": stage_id, "status": "skipped"})
            continue
        failed_dep = next((dep for dep in stage["dependsOn"] if results.get(dep, {}).get("status") not in {"completed", "skipped"}), None)
        if failed_dep:
            raise ScientificWorkflowComposerError(f"Stage {stage_id} cannot run because dependency {failed_dep} did not complete.")
        request = _resolve_stage_request(stage, run_inputs, results)
        request_hash = _hash(request)
        stage_start = time.perf_counter()
        try:
            value = _call_stage(stage["kind"], request)
        except Exception as exc:
            raise ScientificWorkflowComposerError(f"Stage {stage_id} ({stage['kind']}) failed: {exc}") from exc
        duration = round((time.perf_counter() - stage_start) * 1000.0, 3)
        output_hash = _hash(_semantic_view(value))
        record = {
            "schema": STAGE_RESULT_SCHEMA,
            "version": VERSION,
            "stageId": stage_id,
            "title": stage["title"],
            "kind": stage["kind"],
            "status": "completed",
            "requestHash": request_hash,
            "outputHash": output_hash,
            "durationMs": duration,
            "proposalOnly": bool(CATALOG[stage["kind"]].get("proposalOnly")),
            "result": value,
        }
        results[stage_id] = record
        timeline.append({"stageId": stage_id, "kind": stage["kind"], "status": "completed", "requestHash": request_hash, "outputHash": output_hash, "durationMs": duration})

    deterministic = {
        "workflowHash": workflow["workflowHash"],
        "inputs": run_inputs,
        "stages": [{"stageId": sid, "status": results[sid]["status"], "outputHash": results[sid]["outputHash"]} for sid in workflow["order"]],
    }
    run = {
        "schema": RUN_SCHEMA,
        "version": VERSION,
        "id": f"workflow-run-{secrets.token_hex(8)}",
        "workflowId": workflow["id"],
        "workflowHash": workflow["workflowHash"],
        "projectId": workflow["projectId"],
        "status": "completed",
        "createdAt": _now(),
        "durationMs": round((time.perf_counter() - started) * 1000.0, 3),
        "inputsHash": _hash(run_inputs),
        "stageCount": len(workflow["stages"]),
        "completedStageCount": sum(1 for row in results.values() if row["status"] == "completed"),
        "results": results,
        "timeline": timeline,
        "runHash": _hash(deterministic),
        "governance": workflow["governance"],
    }
    return {"ok": True, "workflow": workflow, "run": run}


def compare_runs(payload: dict[str, Any]) -> dict[str, Any]:
    left = payload.get("left") or payload.get("baseline")
    right = payload.get("right") or payload.get("candidate")
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ScientificWorkflowComposerError("Two workflow run records are required for comparison.")
    left_results = left.get("results") if isinstance(left.get("results"), dict) else {}
    right_results = right.get("results") if isinstance(right.get("results"), dict) else {}
    stage_ids = sorted(set(left_results) | set(right_results))
    stages = []
    for sid in stage_ids:
        lh = (left_results.get(sid) or {}).get("outputHash")
        rh = (right_results.get(sid) or {}).get("outputHash")
        stages.append({"stageId": sid, "leftHash": lh, "rightHash": rh, "unchanged": bool(lh and rh and lh == rh)})
    same = left.get("runHash") == right.get("runHash")
    return {"ok": True, "version": VERSION, "sameRunHash": same, "workflowHashMatch": left.get("workflowHash") == right.get("workflowHash"), "stageComparisons": stages, "changedStageCount": sum(1 for row in stages if not row["unchanged"])}


def templates() -> dict[str, Any]:
    rows = [
        {
            "id": "data-to-model",
            "title": "Data → transformation → statistical model",
            "workflow": {
                "id": "data-to-model",
                "title": "Data to statistical model",
                "stages": [
                    {"id": "profile", "kind": "dataset.profile", "request": {}, "bindings": [{"fromStage": "$run", "sourcePath": "dataset.rows", "targetPath": "rows"}]},
                    {"id": "transform", "kind": "data.transform", "request": {"plan": {"operations": []}}, "bindings": [{"fromStage": "$run", "sourcePath": "dataset.rows", "targetPath": "rows"}]},
                    {"id": "fit", "kind": "statistics.fit", "request": {"family": "gaussian", "estimator": "ols", "features": ["x"], "response": "y"}, "bindings": [{"fromStage": "transform", "sourcePath": "result.rows", "targetPath": "rows"}]},
                ],
            },
        },
        {
            "id": "model-validation",
            "title": "Fit → cross-validation",
            "workflow": {
                "id": "model-validation",
                "title": "Statistical model validation",
                "stages": [
                    {"id": "fit", "kind": "statistics.fit", "request": {"family": "gaussian", "estimator": "ols", "features": ["x"], "response": "y"}, "bindings": [{"fromStage": "$run", "sourcePath": "dataset.rows", "targetPath": "rows"}]},
                    {"id": "cross-validation", "kind": "statistics.cross-validate", "request": {"study": {"family": "gaussian", "estimator": "ols", "features": ["x"], "response": "y"}, "folds": 5, "repeats": 1, "seed": 42}, "bindings": [{"fromStage": "$run", "sourcePath": "dataset.rows", "targetPath": "rows"}]},
                ],
            },
        },
        {
            "id": "uncertainty-evidence",
            "title": "Uncertainty → figure-ready evidence",
            "workflow": {
                "id": "uncertainty-evidence",
                "title": "Probabilistic uncertainty evidence",
                "stages": [
                    {"id": "uncertainty", "kind": "uncertainty.independent", "request": {}, "bindings": [{"fromStage": "$run", "sourcePath": "uncertaintyStudy", "targetPath": "study"}]},
                ],
            },
        },
        {
            "id": "experimental-design",
            "title": "Advanced design → sequential proposal",
            "workflow": {
                "id": "experimental-design",
                "title": "Sequential experimental design",
                "stages": [
                    {"id": "design", "kind": "experiment.design", "request": {}, "bindings": [{"fromStage": "$run", "sourcePath": "designSpec", "targetPath": "spec"}]},
                ],
            },
        },
    ]
    return {"ok": True, "version": VERSION, "templates": rows}
