from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from . import scientific_research_operating_system_v01400 as research_os

VERSION = "0.141.0"
ROUTE_COUNT = 27
SCHEMA = "sc-lab-machine-learning-experiment-workspace/0.141.0"
SNAPSHOT_SCHEMA = "sc-lab-machine-learning-experiment-snapshot/0.141.0"
WORKSPACE_HANDOFF_SCHEMA = "sc-workspace-neural-execution-request/1.0"
WORKSPACE_RESULT_SCHEMA = "sc-workspace-neural-execution-result/1.0"
CORE_CONTRACT = "sc-platform-core-neural-research-objects/1.0"
BOUNDARY = (
    "Machine Learning Experiment Workspace governs experiment design, declared inputs, execution handoffs, returned run "
    "artifacts, comparison, provenance, and reproducibility. Lab does not execute neural training itself, silently mutate "
    "source datasets, infer scientific validity, select a best model automatically, convert predictions into evidence, "
    "or treat learned relationships as established facts. Workspace computes; Platform Core defines governed neural objects; "
    "Lab experiments and interprets under explicit human control."
)

EXPERIMENT_STATES = (
    "draft", "designed", "ready-for-execution", "submitted", "running", "completed", "failed", "cancelled", "archived"
)
RUN_STATES = ("queued", "running", "completed", "failed", "cancelled")
COMPUTE_TARGETS = ("cpu", "mps", "cuda", "remote_gpu")
TASK_TYPES = (
    "classification", "regression", "ranking", "embedding", "sequence", "forecasting", "vision", "multimodal", "graph"
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _txt(value: Any, limit: int = 4096) -> str:
    return str(value or "").strip()[:limit]


def _dict(value: Any) -> dict:
    return copy.deepcopy(value) if isinstance(value, dict) else {}


def _list(value: Any) -> list:
    return copy.deepcopy(value) if isinstance(value, list) else []


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _fp(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def _get(obj: dict, *names: str, default=None):
    if not isinstance(obj, dict):
        return default
    for name in names:
        if name in obj and obj[name] is not None:
            return obj[name]
    return default


def normalize(payload: dict) -> dict:
    raw = payload.get("experiment") if isinstance(payload, dict) and isinstance(payload.get("experiment"), dict) else (payload if isinstance(payload, dict) else {})
    project_id = _txt(_get(raw, "projectId", "project_id", "studyId", "study_id"), 512)
    experiment_id = _txt(_get(raw, "experimentId", "experiment_id", "id"), 512)
    title = _txt(_get(raw, "title", "name"), 1024)
    if not experiment_id and not title:
        return {"ok": False, "version": VERSION, "error": "experimentId, id, or title is required", "boundary": BOUNDARY}
    if not experiment_id:
        experiment_id = f"ml-exp-{_fp({'title': title, 'projectId': project_id})[:20]}"
    state = _txt(_get(raw, "state", "status"), 128) or "draft"
    if state not in EXPERIMENT_STATES:
        state = "draft"
    task_type = _txt(_get(raw, "taskType", "task_type"), 128) or "classification"
    if task_type not in TASK_TYPES:
        task_type = "classification"
    compute_target = _txt(_get(raw, "computeTarget", "compute_target"), 128) or "cpu"
    if compute_target not in COMPUTE_TARGETS:
        compute_target = "cpu"
    record = {
        "schema": SCHEMA,
        "version": VERSION,
        "recordType": "machine-learning-experiment",
        "collection": "machineLearningExperiments",
        "id": experiment_id,
        "experimentId": experiment_id,
        "projectId": project_id or experiment_id,
        "studyId": _txt(_get(raw, "studyId", "study_id"), 512) or project_id or experiment_id,
        "title": title or experiment_id,
        "state": state,
        "taskType": task_type,
        "objective": copy.deepcopy(_get(raw, "objective", "researchObjective", "research_objective")),
        "hypotheses": _list(raw.get("hypotheses")),
        "datasets": _list(raw.get("datasets")),
        "features": _list(raw.get("features")),
        "transformations": _list(raw.get("transformations")),
        "modelSpecification": _dict(_get(raw, "modelSpecification", "model_specification", "model")),
        "trainingConfiguration": _dict(_get(raw, "trainingConfiguration", "training_configuration", "training")),
        "evaluationPlan": _dict(_get(raw, "evaluationPlan", "evaluation_plan", "evaluation")),
        "computeTarget": compute_target,
        "runtime": _dict(raw.get("runtime")),
        "runs": _list(raw.get("runs")),
        "checkpoints": _list(raw.get("checkpoints")),
        "metrics": _list(raw.get("metrics")),
        "predictions": _list(raw.get("predictions")),
        "interpretations": _list(raw.get("interpretations")),
        "artifacts": _list(raw.get("artifacts")),
        "comparators": _list(_get(raw, "comparators", "baselines", default=[])),
        "notes": _list(raw.get("notes")),
        "limitations": _list(raw.get("limitations")),
        "provenance": _dict(raw.get("provenance")),
        "researchOS": _dict(_get(raw, "researchOS", "research_os")),
        "createdAt": _txt(_get(raw, "createdAt", "created_at"), 128) or _now(),
        "createdBy": _txt(_get(raw, "createdBy", "created_by"), 256) or "user",
        "workspaceExecutes": True,
        "labExecutesTraining": False,
        "coreDefinesNeuralObjects": True,
        "predictionIsEvidence": False,
        "automaticBestModelSelection": False,
        "automaticScientificValidity": False,
        "boundary": BOUNDARY,
    }
    record["fingerprint"] = _fp({k: v for k, v in record.items() if k not in {"fingerprint", "createdAt"}})
    return {"ok": True, "version": VERSION, "record": record, "boundary": BOUNDARY}


def validate(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    warnings = []
    errors = []
    if not r["objective"]:
        warnings.append("no experiment objective is declared")
    if not r["datasets"]:
        warnings.append("no dataset references are declared")
    if not r["modelSpecification"]:
        warnings.append("no model specification is declared")
    if not r["trainingConfiguration"]:
        warnings.append("no training configuration is declared")
    if not r["evaluationPlan"]:
        warnings.append("no evaluation plan is declared")
    return {"ok": not errors, "version": VERSION, "record": r, "errors": errors, "warnings": warnings, "boundary": BOUNDARY}


def lifecycle(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    stages = [
        ("objective", bool(r["objective"] or r["hypotheses"])),
        ("data", bool(r["datasets"])),
        ("representation", bool(r["features"] or r["transformations"])),
        ("model", bool(r["modelSpecification"])),
        ("training-plan", bool(r["trainingConfiguration"])),
        ("evaluation-plan", bool(r["evaluationPlan"])),
        ("execution", bool(r["runs"])),
        ("checkpoint", bool(r["checkpoints"])),
        ("evaluation", bool(r["metrics"])),
        ("prediction", bool(r["predictions"])),
        ("interpretation", bool(r["interpretations"])),
        ("reproducibility", bool(r["artifacts"] and r["provenance"])),
    ]
    return {"ok": True, "version": VERSION, "experimentId": r["experimentId"], "declaredState": r["state"], "stages": [{"stage": n, "declaredArtifactsPresent": p, "stateInferred": False} for n, p in stages], "automaticStateAdvance": False, "boundary": BOUNDARY}


def dataset_lineage(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    rows = []
    for i, item in enumerate(r["datasets"]):
        d = item if isinstance(item, dict) else {"ref": item}
        rows.append({
            "index": i,
            "datasetRef": _txt(_get(d, "datasetRef", "id", "ref"), 1024),
            "version": _txt(_get(d, "version", "datasetVersion"), 256),
            "role": _txt(_get(d, "role", "split"), 128) or "declared-input",
            "sourceHash": _txt(_get(d, "sourceHash", "hash", "sha256"), 256),
            "coreGovernedObjectExpected": True,
        })
    return {"ok": True, "version": VERSION, "experimentId": r["experimentId"], "datasets": rows, "transformations": r["transformations"], "silentDatasetMutation": False, "boundary": BOUNDARY}


def model_specification(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    model = copy.deepcopy(r["modelSpecification"])
    return {"ok": True, "version": VERSION, "experimentId": r["experimentId"], "modelSpecification": model, "coreContract": CORE_CONTRACT, "frameworkNeutralAuthority": "platform-core", "labMayAnnotateExperimentUse": True, "boundary": BOUNDARY}


def training_plan(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    cfg = copy.deepcopy(r["trainingConfiguration"])
    return {
        "ok": True, "version": VERSION, "experimentId": r["experimentId"], "computeTarget": r["computeTarget"],
        "configuration": cfg, "executionAuthority": "workspace", "labExecutesTraining": False,
        "deterministicSeedDeclared": _get(cfg, "seed", "randomSeed") is not None,
        "boundary": BOUNDARY,
    }


def workspace_handoff(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    request = {
        "schema": WORKSPACE_HANDOFF_SCHEMA,
        "requestedBy": "sustainable-catalyst-lab",
        "labRelease": VERSION,
        "experimentId": r["experimentId"],
        "projectId": r["projectId"],
        "taskType": r["taskType"],
        "datasets": r["datasets"],
        "features": r["features"],
        "transformations": r["transformations"],
        "modelSpecification": r["modelSpecification"],
        "trainingConfiguration": r["trainingConfiguration"],
        "evaluationPlan": r["evaluationPlan"],
        "computeTarget": r["computeTarget"],
        "runtime": r["runtime"],
        "sourceFingerprint": r["fingerprint"],
        "automaticExecution": False,
    }
    request["fingerprint"] = _fp(request)
    return {"ok": True, "version": VERSION, "handoff": request, "executionAuthority": "workspace", "automaticExecution": False, "boundary": BOUNDARY}


def ingest_workspace_result(payload: dict) -> dict:
    raw = payload if isinstance(payload, dict) else {}
    exp = normalize(raw)
    if not exp.get("ok"):
        return exp
    result = _dict(_get(raw, "workspaceResult", "workspace_result", "result"))
    run_id = _txt(_get(result, "runId", "run_id", "id"), 512)
    accepted = bool(run_id and (_get(result, "experimentId", "experiment_id") in (None, "", exp["record"]["experimentId"])))
    normalized = {
        "schema": WORKSPACE_RESULT_SCHEMA,
        "experimentId": exp["record"]["experimentId"],
        "runId": run_id,
        "state": _txt(_get(result, "state", "status"), 128) or "completed",
        "environment": _dict(result.get("environment")),
        "metrics": _list(result.get("metrics")),
        "checkpoints": _list(result.get("checkpoints")),
        "predictions": _list(result.get("predictions")),
        "artifacts": _list(result.get("artifacts")),
        "provenance": _dict(result.get("provenance")),
        "workspaceFingerprint": _txt(_get(result, "fingerprint", "resultFingerprint"), 256),
        "predictionIsEvidence": False,
    }
    normalized["ingestFingerprint"] = _fp(normalized)
    return {"ok": accepted, "version": VERSION, "accepted": accepted, "result": normalized, "scientificValidityCertified": False, "boundary": BOUNDARY}


def run_registry(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    rows = []
    for i, item in enumerate(out["record"]["runs"]):
        r = item if isinstance(item, dict) else {"id": item}
        state = _txt(_get(r, "state", "status"), 128) or "queued"
        if state not in RUN_STATES:
            state = "queued"
        rows.append({"index": i, "runId": _txt(_get(r, "runId", "id"), 512), "state": state, "checkpointCount": len(_list(r.get("checkpoints"))), "metricCount": len(_list(r.get("metrics"))), "declared": True})
    return {"ok": True, "version": VERSION, "experimentId": out["record"]["experimentId"], "runs": rows, "count": len(rows), "boundary": BOUNDARY}


def checkpoint_index(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    rows = []
    for i, item in enumerate(out["record"]["checkpoints"]):
        c = item if isinstance(item, dict) else {"ref": item}
        rows.append({"index": i, "checkpointRef": _txt(_get(c, "checkpointRef", "id", "ref"), 1024), "runId": _txt(_get(c, "runId", "run_id"), 512), "epoch": _get(c, "epoch", "step"), "artifactHash": _txt(_get(c, "artifactHash", "hash", "sha256"), 256), "promotedToEvidence": False})
    return {"ok": True, "version": VERSION, "checkpoints": rows, "count": len(rows), "boundary": BOUNDARY}


def metric_series(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    rows = []
    for i, item in enumerate(out["record"]["metrics"]):
        m = item if isinstance(item, dict) else {"value": item}
        rows.append({"index": i, "name": _txt(_get(m, "name", "metric"), 256), "value": _get(m, "value"), "split": _txt(_get(m, "split", "partition"), 128), "step": _get(m, "step", "epoch"), "higherIsBetterDeclared": _get(m, "higherIsBetter", "higher_is_better")})
    return {"ok": True, "version": VERSION, "metrics": rows, "count": len(rows), "automaticModelRanking": False, "boundary": BOUNDARY}


def comparison_matrix(payload: dict) -> dict:
    raw = payload if isinstance(payload, dict) else {}
    experiments = _list(raw.get("experiments"))
    rows = []
    for item in experiments:
        n = normalize(item if isinstance(item, dict) else {"id": item})
        if n.get("ok"):
            r = n["record"]
            rows.append({"experimentId": r["experimentId"], "title": r["title"], "taskType": r["taskType"], "computeTarget": r["computeTarget"], "runCount": len(r["runs"]), "metricCount": len(r["metrics"]), "checkpointCount": len(r["checkpoints"]), "fingerprint": r["fingerprint"]})
    return {"ok": True, "version": VERSION, "rows": rows, "count": len(rows), "automaticWinner": None, "humanSelectionRequired": True, "boundary": BOUNDARY}


def experiment_compare(payload: dict) -> dict:
    raw = payload if isinstance(payload, dict) else {}
    left = normalize(_dict(raw.get("left")))
    right = normalize(_dict(raw.get("right")))
    if not left.get("ok") or not right.get("ok"):
        return {"ok": False, "version": VERSION, "error": "left and right experiments are required", "boundary": BOUNDARY}
    a, b = left["record"], right["record"]
    changed = [k for k in ("taskType", "datasets", "features", "transformations", "modelSpecification", "trainingConfiguration", "evaluationPlan", "computeTarget", "runtime") if _canon(a[k]) != _canon(b[k])]
    return {"ok": True, "version": VERSION, "leftExperimentId": a["experimentId"], "rightExperimentId": b["experimentId"], "changedFields": changed, "sameFingerprint": a["fingerprint"] == b["fingerprint"], "preferredExperiment": None, "boundary": BOUNDARY}


def provenance_graph(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    nodes = [{"id": r["experimentId"], "type": "experiment"}]
    edges = []
    for coll, typ in (("datasets", "dataset"), ("features", "feature"), ("transformations", "transformation"), ("runs", "training-run"), ("checkpoints", "checkpoint"), ("predictions", "prediction"), ("interpretations", "interpretation")):
        for i, item in enumerate(r[coll]):
            d = item if isinstance(item, dict) else {"id": item}
            ident = _txt(_get(d, "id", "ref", f"{typ}Ref"), 512) or f"{r['experimentId']}:{typ}:{i}"
            nodes.append({"id": ident, "type": typ})
            if typ in {"dataset", "feature", "transformation"}:
                edges.append({"from": ident, "to": r["experimentId"], "relationship": "declared-input"})
            else:
                edges.append({"from": r["experimentId"], "to": ident, "relationship": "declared-output"})
    return {"ok": True, "version": VERSION, "nodes": nodes, "edges": edges, "declaredRelationshipsOnly": True, "causalInference": False, "boundary": BOUNDARY}


def prediction_registry(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    rows = []
    for i, item in enumerate(out["record"]["predictions"]):
        p = item if isinstance(item, dict) else {"value": item}
        rows.append({"index": i, "predictionId": _txt(_get(p, "predictionId", "id"), 512) or f"prediction-{i}", "runId": _txt(_get(p, "runId", "run_id"), 512), "value": copy.deepcopy(p.get("value")), "probability": p.get("probability"), "uncertainty": copy.deepcopy(p.get("uncertainty")), "evidenceStatus": "prediction-not-evidence", "requiresIndependentValidation": True})
    return {"ok": True, "version": VERSION, "predictions": rows, "count": len(rows), "predictionIsEvidence": False, "boundary": BOUNDARY}


def interpretation_boundary(payload: dict | None = None) -> dict:
    return {"ok": True, "version": VERSION, "rules": ["prediction != evidence", "model score != scientific validity", "checkpoint != endorsed model", "embedding proximity != established relationship", "experiment comparison does not select a winner automatically"], "automaticScientificValidity": False, "automaticBestModelSelection": False, "boundary": BOUNDARY}


def reproducibility_packet(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    packet = {
        "schema": "sc-lab-ml-experiment-reproducibility-package/0.141.0",
        "experimentId": r["experimentId"],
        "sourceFingerprint": r["fingerprint"],
        "datasets": r["datasets"],
        "features": r["features"],
        "transformations": r["transformations"],
        "modelSpecification": r["modelSpecification"],
        "trainingConfiguration": r["trainingConfiguration"],
        "evaluationPlan": r["evaluationPlan"],
        "computeTarget": r["computeTarget"],
        "runtime": r["runtime"],
        "runs": r["runs"],
        "checkpoints": r["checkpoints"],
        "metrics": r["metrics"],
        "artifacts": r["artifacts"],
        "provenance": r["provenance"],
        "limitations": r["limitations"],
        "scientificValidityCertified": False,
        "reproductionCertified": False,
    }
    packet["fingerprint"] = _fp(packet)
    return {"ok": True, "version": VERSION, "packet": packet, "boundary": BOUNDARY}


def snapshot(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = copy.deepcopy(out["record"])
    snap = {"schema": SNAPSHOT_SCHEMA, "experimentId": r["experimentId"], "recordFingerprint": r["fingerprint"], "record": r}
    stable = copy.deepcopy(snap)
    if isinstance(stable.get("record"), dict): stable["record"].pop("createdAt", None)
    snap["fingerprint"] = _fp(stable)
    return {"ok": True, "version": VERSION, "snapshot": snap, "immutableByContract": True, "boundary": BOUNDARY}


def compare_snapshots(payload: dict) -> dict:
    raw = payload if isinstance(payload, dict) else {}
    left = _dict(raw.get("left")); right = _dict(raw.get("right"))
    lr = _dict(left.get("record")); rr = _dict(right.get("record"))
    fields = sorted(set(lr) | set(rr))
    changed = [k for k in fields if k not in {"createdAt", "fingerprint"} and _canon(lr.get(k)) != _canon(rr.get(k))]
    return {"ok": True, "version": VERSION, "leftFingerprint": left.get("fingerprint"), "rightFingerprint": right.get("fingerprint"), "changedFields": changed, "changed": bool(changed), "boundary": BOUNDARY}


def research_os_handoff(payload: dict) -> dict:
    out = normalize(payload)
    if not out.get("ok"):
        return out
    r = out["record"]
    ros_payload = {
        "projectId": r["projectId"], "studyId": r["studyId"], "title": r["title"], "phase": "compute" if r["runs"] else "design",
        "objective": r["objective"], "datasets": r["datasets"], "models": [r["modelSpecification"]] if r["modelSpecification"] else [],
        "executions": r["runs"], "analyses": r["metrics"], "findings": [], "limitations": r["limitations"], "provenance": r["provenance"],
    }
    ros = research_os.normalize(ros_payload)
    return {"ok": bool(ros.get("ok")), "version": VERSION, "sourceExperimentId": r["experimentId"], "researchOS": ros, "sourceVersion": "0.140.0", "automaticPhaseAdvance": False, "boundary": BOUNDARY}


def contract() -> dict:
    return {"ok": True, "version": VERSION, "schema": SCHEMA, "coreContract": CORE_CONTRACT, "workspaceHandoffSchema": WORKSPACE_HANDOFF_SCHEMA, "workspaceResultSchema": WORKSPACE_RESULT_SCHEMA, "computeTargets": list(COMPUTE_TARGETS), "taskTypes": list(TASK_TYPES), "routeCount": ROUTE_COUNT, "boundary": BOUNDARY}


def policy() -> dict:
    return {"ok": True, "version": VERSION, "coreDefines": True, "workspaceComputes": True, "labExperiments": True, "productsConsume": True, "labExecutesTraining": False, "predictionIsEvidence": False, "automaticBestModelSelection": False, "automaticScientificValidity": False, "boundary": BOUNDARY}


def acceptance_report() -> dict:
    return {
        "ok": True, "version": VERSION, "machineLearningExperimentWorkspace": True, "experimentLifecycle": True,
        "datasetTransformationLineage": True, "modelSpecificationBinding": True, "trainingPlan": True,
        "workspaceExecutionHandoff": True, "workspaceResultIngest": True, "runRegistry": True, "checkpointIndex": True,
        "metricSeries": True, "experimentComparison": True, "provenanceGraph": True, "predictionRegistry": True,
        "reproducibilityPacket": True, "deterministicSnapshots": True, "researchOSBridge": True,
        "backwardCompatibleV01400": True, "manifestScopeRepairRetainedV013901": True,
        "labExecutesTraining": False, "predictionIsEvidence": False, "automaticBestModelSelection": False,
        "automaticScientificValidity": False, "boundary": BOUNDARY,
    }


def health() -> dict:
    return {"ok": True, "version": VERSION, "service": "machine-learning-experiment-workspace", "routeCount": ROUTE_COUNT, "coreContract": CORE_CONTRACT, "workspaceExecutionRequired": True, "researchOSBridgeVersion": "0.140.0", "manifestIntegrityBaseline": "0.139.0.1", "boundary": BOUNDARY}


def release_gates() -> dict:
    return {"ok": True, "version": VERSION, "requiredRouteCount": ROUTE_COUNT, "requiresCoreNeuralObjectFoundation": True, "requiresWorkspaceNeuralExecution": True, "requiresResearchOSV01400": True, "requiresManifestScopeRepairV013901": True, "trainingExecutionInsideLab": False, "boundary": BOUNDARY}
