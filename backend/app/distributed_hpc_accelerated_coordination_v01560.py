from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.156.0"
TARGET_SCHEMA = "sc-lab-compute-target/0.156.0"
PLAN_SCHEMA = "sc-lab-distributed-execution-plan/0.156.0"
WAVE_SCHEMA = "sc-lab-execution-wave/0.156.0"
RECEIPT_SCHEMA = "sc-lab-execution-receipt/0.156.0"
MANIFEST_SCHEMA = "sc-lab-distributed-execution-manifest/0.156.0"
SCHEDULER_BUNDLE_SCHEMA = "sc-lab-scheduler-submission-bundle/0.156.0"
SUPPORTED_SCHEDULERS = {"workspace", "slurm", "pbs", "lsf", "kubernetes", "manual"}
SUPPORTED_ACCELERATORS = {"cpu", "cuda", "rocm", "metal", "tpu", "other"}
BOUNDARY = (
    "Distributed/HPC coordination records capabilities, resource intent, placement rationale, execution waves, "
    "scheduler-neutral submission bundles, and result receipts. It does not submit jobs, store cluster credentials, "
    "execute arbitrary code, autonomously fail over workloads, or establish scientific validity. Workspace/runtime "
    "fabric and external schedulers remain execution authorities; human review remains required."
)
SECRET_KEYS = {"password", "passwd", "token", "secret", "api_key", "apikey", "private_key", "credential", "credentials"}


class DistributedCoordinationError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _clean_id(value: Any, label: str) -> str:
    text = str(value or "").strip()
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
    if not text or len(text) > 180 or any(ch not in allowed for ch in text):
        raise DistributedCoordinationError(f"Invalid {label}.")
    return text


def _text(value: Any, label: str, maximum: int = 4000, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise DistributedCoordinationError(f"{label} is required.")
    if len(text) > maximum:
        raise DistributedCoordinationError(f"{label} exceeds {maximum} characters.")
    return text


def _json(value: Any, label: str, maximum_bytes: int = 2_000_000) -> Any:
    try:
        raw = _canonical(value)
    except Exception as exc:
        raise DistributedCoordinationError(f"{label} must be JSON serializable.") from exc
    if len(raw) > maximum_bytes:
        raise DistributedCoordinationError(f"{label} exceeds the payload limit.", 413)
    return json.loads(raw.decode("utf-8"))


def _finite(value: Any, label: str, minimum: float = 0.0, maximum: float | None = None) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise DistributedCoordinationError(f"{label} must be numeric.") from exc
    if not math.isfinite(out) or out < minimum or (maximum is not None and out > maximum):
        raise DistributedCoordinationError(f"{label} is outside the allowed range.")
    return out


def _int(value: Any, label: str, minimum: int, maximum: int, default: int) -> int:
    try:
        out = int(default if value is None else value)
    except (TypeError, ValueError) as exc:
        raise DistributedCoordinationError(f"{label} must be an integer.") from exc
    if out < minimum or out > maximum:
        raise DistributedCoordinationError(f"{label} must be between {minimum} and {maximum}.")
    return out


def _assert_no_secrets(value: Any, path: str = "target") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in SECRET_KEYS or any(word in normalized for word in ("password", "secret", "private_key", "credential", "token", "api_key", "apikey")):
                if item not in (None, "", [], {}):
                    raise DistributedCoordinationError(f"Credentials/secrets are not accepted in {path}; store them in the execution authority instead.")
            _assert_no_secrets(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_no_secrets(item, f"{path}[{index}]")


def normalize_target(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DistributedCoordinationError("Target payload must be an object.")
    _assert_no_secrets(payload)
    scheduler = str(payload.get("scheduler") or "workspace").strip().lower()
    if scheduler not in SUPPORTED_SCHEDULERS:
        raise DistributedCoordinationError(f"Unsupported scheduler: {scheduler}.")
    name = _text(payload.get("name"), "target name", 300, True)
    capabilities = payload.get("capabilities") or {}
    if not isinstance(capabilities, dict):
        raise DistributedCoordinationError("capabilities must be an object.")
    accelerators = capabilities.get("acceleratorKinds") or capabilities.get("accelerators") or ["cpu"]
    if not isinstance(accelerators, list) or not accelerators:
        raise DistributedCoordinationError("acceleratorKinds must be a non-empty array.")
    accelerator_kinds = []
    for item in accelerators[:20]:
        kind = str(item or "").strip().lower()
        if kind not in SUPPORTED_ACCELERATORS:
            raise DistributedCoordinationError(f"Unsupported accelerator kind: {kind}.")
        if kind not in accelerator_kinds:
            accelerator_kinds.append(kind)
    normalized = {
        "schema": TARGET_SCHEMA,
        "version": VERSION,
        "name": name,
        "scheduler": scheduler,
        "region": _text(payload.get("region"), "region", 200, False),
        "queue": _text(payload.get("queue") or payload.get("partition"), "queue/partition", 200, False),
        "workspaceTargetRef": _text(payload.get("workspaceTargetRef"), "workspaceTargetRef", 300, False),
        "capabilities": {
            "cpuCores": _int(capabilities.get("cpuCores"), "cpuCores", 1, 100000, 1),
            "memoryGB": _finite(capabilities.get("memoryGB", 1), "memoryGB", 0.1, 10_000_000),
            "gpuCount": _int(capabilities.get("gpuCount"), "gpuCount", 0, 10000, 0),
            "acceleratorKinds": accelerator_kinds,
            "gpuMemoryGB": _finite(capabilities.get("gpuMemoryGB", 0), "gpuMemoryGB", 0, 1_000_000),
            "mpi": bool(capabilities.get("mpi", False)),
            "maxWalltimeMinutes": _int(capabilities.get("maxWalltimeMinutes"), "maxWalltimeMinutes", 1, 60 * 24 * 30, 1440),
            "maxArraySize": _int(capabilities.get("maxArraySize"), "maxArraySize", 1, 1_000_000, 1000),
            "maxParallelJobs": _int(capabilities.get("maxParallelJobs"), "maxParallelJobs", 1, 100000, 10),
        },
        "labels": [str(v)[:120] for v in (payload.get("labels") or []) if str(v).strip()][:50],
        "enabled": bool(payload.get("enabled", True)),
        "storesCredentials": False,
    }
    normalized["targetHash"] = _sha(normalized)
    return normalized


def normalize_resource_request(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = payload or {}
    if not isinstance(raw, dict):
        raise DistributedCoordinationError("resources must be an object.")
    accelerator = str(raw.get("acceleratorKind") or "cpu").strip().lower()
    if accelerator not in SUPPORTED_ACCELERATORS:
        raise DistributedCoordinationError(f"Unsupported accelerator kind: {accelerator}.")
    return {
        "cpuCores": _int(raw.get("cpuCores"), "resource cpuCores", 1, 100000, 1),
        "memoryGB": _finite(raw.get("memoryGB", 1), "resource memoryGB", 0.1, 10_000_000),
        "gpuCount": _int(raw.get("gpuCount"), "resource gpuCount", 0, 10000, 0),
        "acceleratorKind": accelerator,
        "gpuMemoryGB": _finite(raw.get("gpuMemoryGB", 0), "resource gpuMemoryGB", 0, 1_000_000),
        "walltimeMinutes": _int(raw.get("walltimeMinutes"), "resource walltimeMinutes", 1, 60 * 24 * 30, 60),
        "mpiRanks": _int(raw.get("mpiRanks"), "resource mpiRanks", 1, 100000, 1),
        "threadsPerRank": _int(raw.get("threadsPerRank"), "resource threadsPerRank", 1, 100000, 1),
        "scratchGB": _finite(raw.get("scratchGB", 0), "resource scratchGB", 0, 10_000_000),
        "exclusiveNode": bool(raw.get("exclusiveNode", False)),
    }


def target_eligibility(target: dict[str, Any], resources: dict[str, Any]) -> tuple[bool, list[str]]:
    c = target["capabilities"]
    reasons: list[str] = []
    if not target.get("enabled", True): reasons.append("target-disabled")
    if resources["cpuCores"] > c["cpuCores"]: reasons.append("insufficient-cpu")
    if resources["memoryGB"] > c["memoryGB"]: reasons.append("insufficient-memory")
    if resources["gpuCount"] > c["gpuCount"]: reasons.append("insufficient-gpu-count")
    if resources["gpuMemoryGB"] > c["gpuMemoryGB"]: reasons.append("insufficient-gpu-memory")
    if resources["acceleratorKind"] not in c["acceleratorKinds"]: reasons.append("accelerator-unavailable")
    if resources["walltimeMinutes"] > c["maxWalltimeMinutes"]: reasons.append("walltime-exceeds-target")
    if resources["mpiRanks"] > 1 and not c.get("mpi"): reasons.append("mpi-unavailable")
    return (not reasons, reasons)


def _scheduler_contract(target: dict[str, Any], resources: dict[str, Any], wave: int, task_count: int, max_parallel: int) -> dict[str, Any]:
    scheduler = target["scheduler"]
    c = target["capabilities"]
    body = {
        "schema": SCHEDULER_BUNDLE_SCHEMA,
        "scheduler": scheduler,
        "targetId": target["id"],
        "queue": target.get("queue") or "",
        "wave": wave,
        "taskCount": task_count,
        "maxParallel": min(max_parallel, c["maxParallelJobs"], task_count),
        "resources": resources,
        "submissionRequested": False,
        "executionAuthority": "Workspace/runtime fabric or external scheduler",
    }
    if scheduler == "slurm":
        body["directives"] = {"array": f"0-{task_count - 1}%{body['maxParallel']}", "cpusPerTask": resources["cpuCores"], "memoryGB": resources["memoryGB"], "gpus": resources["gpuCount"], "timeMinutes": resources["walltimeMinutes"], "partition": target.get("queue") or ""}
    elif scheduler == "pbs":
        body["directives"] = {"arrayRange": f"0-{task_count - 1}", "select": 1, "ncpus": resources["cpuCores"], "memoryGB": resources["memoryGB"], "ngpus": resources["gpuCount"], "walltimeMinutes": resources["walltimeMinutes"], "queue": target.get("queue") or ""}
    elif scheduler == "lsf":
        body["directives"] = {"jobArray": f"[1-{task_count}]%{body['maxParallel']}", "ncpus": resources["cpuCores"], "memoryGB": resources["memoryGB"], "gpuCount": resources["gpuCount"], "walltimeMinutes": resources["walltimeMinutes"], "queue": target.get("queue") or ""}
    elif scheduler == "kubernetes":
        body["directives"] = {"kind": "Job", "parallelism": body["maxParallel"], "completions": task_count, "cpu": resources["cpuCores"], "memoryGB": resources["memoryGB"], "gpuCount": resources["gpuCount"], "acceleratorKind": resources["acceleratorKind"]}
    elif scheduler == "workspace":
        body["directives"] = {"mode": "workspace-execution-broker", "parallelism": body["maxParallel"], "workspaceTargetRef": target.get("workspaceTargetRef") or target["id"]}
    else:
        body["directives"] = {"mode": "manual-external", "parallelism": body["maxParallel"]}
    body["contractHash"] = _sha(body)
    return body


class DistributedHPCCoordinationManager:
    def __init__(self, db_path: str, campaigns: Any | None = None, persistent_disk_mounted: bool = False, max_targets: int = 500, max_plans: int = 5000, max_tasks_per_plan: int = 100000, history_limit: int = 100000) -> None:
        self.db_path = str(db_path)
        self.campaigns = campaigns
        self.persistent_disk_mounted = bool(persistent_disk_mounted)
        self.max_targets = max(1, int(max_targets)); self.max_plans = max(1, int(max_plans)); self.max_tasks_per_plan = max(1, int(max_tasks_per_plan)); self.history_limit = max(100, int(history_limit))
        self._lock = threading.RLock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        class _ClosingConnection(sqlite3.Connection):
            def __exit__(self, exc_type, exc, tb):
                try:
                    return super().__exit__(exc_type, exc, tb)
                finally:
                    self.close()
        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False, factory=_ClosingConnection)
        db.row_factory = sqlite3.Row; db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS dhc_targets(
              id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL, scheduler TEXT NOT NULL, status TEXT NOT NULL,
              definition_json TEXT NOT NULL, target_hash TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, actor TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS dhc_target_project_idx ON dhc_targets(project_id, updated_at DESC);
            CREATE TABLE IF NOT EXISTS dhc_plans(
              id TEXT PRIMARY KEY, project_id TEXT NOT NULL, campaign_id TEXT NOT NULL DEFAULT '', target_id TEXT NOT NULL,
              title TEXT NOT NULL, status TEXT NOT NULL, definition_json TEXT NOT NULL, plan_hash TEXT NOT NULL,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL, actor TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS dhc_plan_project_idx ON dhc_plans(project_id, updated_at DESC);
            CREATE TABLE IF NOT EXISTS dhc_receipts(
              id TEXT PRIMARY KEY, plan_id TEXT NOT NULL, campaign_id TEXT NOT NULL DEFAULT '', trial_id TEXT NOT NULL,
              wave INTEGER NOT NULL, status TEXT NOT NULL, execution_ref TEXT NOT NULL DEFAULT '', result_ref TEXT NOT NULL DEFAULT '',
              worker_ref TEXT NOT NULL DEFAULT '', target_ref TEXT NOT NULL DEFAULT '', details_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL, actor TEXT NOT NULL, receipt_hash TEXT NOT NULL,
              FOREIGN KEY(plan_id) REFERENCES dhc_plans(id)
            );
            CREATE INDEX IF NOT EXISTS dhc_receipt_plan_idx ON dhc_receipts(plan_id, created_at DESC);
            CREATE TABLE IF NOT EXISTS dhc_events(
              seq INTEGER PRIMARY KEY AUTOINCREMENT, object_id TEXT NOT NULL, project_id TEXT NOT NULL, event_type TEXT NOT NULL,
              occurred_at TEXT NOT NULL, actor TEXT NOT NULL, payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
            );
            """)

    def _event(self, db: sqlite3.Connection, object_id: str, project_id: str, event_type: str, actor: str, payload: Any) -> None:
        row = db.execute("SELECT event_hash FROM dhc_events ORDER BY seq DESC LIMIT 1").fetchone(); previous = str(row["event_hash"]) if row else ""; occurred = _now()
        envelope = {"objectId": object_id, "projectId": project_id, "eventType": event_type, "occurredAt": occurred, "actor": actor, "payload": payload, "previousHash": previous}
        event_hash = _sha(envelope)
        db.execute("INSERT INTO dhc_events(object_id,project_id,event_type,occurred_at,actor,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)", (object_id, project_id, event_type, occurred, actor, json.dumps(payload, sort_keys=True), previous, event_hash))
        db.execute("DELETE FROM dhc_events WHERE seq NOT IN (SELECT seq FROM dhc_events ORDER BY seq DESC LIMIT ?)", (self.history_limit,))

    def policies(self) -> dict[str, Any]:
        return {"ok": True, "version": VERSION, "supportedSchedulers": sorted(SUPPORTED_SCHEDULERS), "supportedAccelerators": sorted(SUPPORTED_ACCELERATORS), "maxTargets": self.max_targets, "maxPlans": self.max_plans, "maxTasksPerPlan": self.max_tasks_per_plan, "automaticDispatch": False, "automaticFailover": False, "credentialsStored": False, "arbitraryCodeExecution": False, "executionAuthority": "Workspace/runtime fabric or external scheduler", "humanScientificReviewRequired": True, "boundary": BOUNDARY}

    def health(self) -> dict[str, Any]:
        with self._connect() as db:
            targets = int(db.execute("SELECT COUNT(*) AS n FROM dhc_targets WHERE status='active'").fetchone()["n"]); plans = int(db.execute("SELECT COUNT(*) AS n FROM dhc_plans WHERE archived=0").fetchone()["n"]); receipts = int(db.execute("SELECT COUNT(*) AS n FROM dhc_receipts").fetchone()["n"])
        return {"ok": True, "status": "ready", "version": VERSION, "storage": "persistent-disk" if self.persistent_disk_mounted else "instance-local-volume", "targetSchema": TARGET_SCHEMA, "planSchema": PLAN_SCHEMA, "waveSchema": WAVE_SCHEMA, "receiptSchema": RECEIPT_SCHEMA, "manifestSchema": MANIFEST_SCHEMA, "supportedSchedulers": sorted(SUPPORTED_SCHEDULERS), "acceleratorAwarePlacement": True, "hpcJobArrayPlanning": True, "executionWavePlanning": True, "resourceIntent": True, "automaticDispatch": False, "automaticFailover": False, "credentialsStored": False, "counts": {"targets": targets, "plans": plans, "receipts": receipts}, "boundary": BOUNDARY}

    @staticmethod
    def _target(row: sqlite3.Row) -> dict[str, Any]:
        body = json.loads(row["definition_json"]); body.update({"id": row["id"], "projectId": row["project_id"], "status": row["status"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"], "targetHash": row["target_hash"]}); return body

    def create_target(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "projectId"); actor = _text(actor, "actor", 300, True); definition = normalize_target(payload); now = _now(); target_id = "target:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) AS n FROM dhc_targets WHERE project_id=? AND status='active'", (project_id,)).fetchone()["n"])
            if count >= self.max_targets: raise DistributedCoordinationError("Project compute-target limit reached.", 409)
            db.execute("INSERT INTO dhc_targets(id,project_id,name,scheduler,status,definition_json,target_hash,created_at,updated_at,actor) VALUES(?,?,?,?,?,?,?,?,?,?)", (target_id, project_id, definition["name"], definition["scheduler"], "active", json.dumps(definition, sort_keys=True), definition["targetHash"], now, now, actor))
            self._event(db, target_id, project_id, "compute-target-created", actor, {"scheduler": definition["scheduler"], "targetHash": definition["targetHash"]}); db.commit()
        return {"ok": True, "target": self.get_target(target_id)}

    def get_target(self, target_id: str) -> dict[str, Any]:
        target_id = _clean_id(target_id, "targetId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM dhc_targets WHERE id=?", (target_id,)).fetchone()
        if not row: raise DistributedCoordinationError("Compute target not found.", 404)
        return self._target(row)

    def list_targets(self, project_id: str, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
        project_id = _clean_id(project_id, "projectId"); where = "project_id=?" if include_archived else "project_id=? AND status='active'"
        with self._connect() as db: rows = db.execute(f"SELECT * FROM dhc_targets WHERE {where} ORDER BY updated_at DESC LIMIT ?", (project_id, max(1, min(1000, int(limit))))).fetchall()
        return {"ok": True, "count": len(rows), "targets": [self._target(r) for r in rows]}

    def archive_target(self, target_id: str, actor: str) -> dict[str, Any]:
        target = self.get_target(target_id); actor = _text(actor, "actor", 300, True)
        with self._lock, self._connect() as db:
            db.execute("UPDATE dhc_targets SET status='archived',updated_at=? WHERE id=?", (_now(), target_id)); self._event(db, target_id, target["projectId"], "compute-target-archived", actor, {}); db.commit()
        return {"ok": True, "target": self.get_target(target_id)}

    def _campaign_handoffs(self, campaign_id: str, limit: int, status: str) -> list[dict[str, Any]]:
        if self.campaigns is None: raise DistributedCoordinationError("Batch campaign manager is unavailable.", 503)
        batch = self.campaigns.execution_batch(campaign_id, min(limit, self.max_tasks_per_plan), status)
        return list(batch.get("handoffs") or [])

    def create_plan(self, project_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        project_id = _clean_id(project_id, "projectId"); actor = _text(actor, "actor", 300, True)
        if not isinstance(payload, dict): raise DistributedCoordinationError("Plan payload must be an object.")
        campaign_id = _text(payload.get("campaignId"), "campaignId", 180, False)
        target_id = _clean_id(payload.get("targetId"), "targetId"); target = self.get_target(target_id)
        if target["projectId"] != project_id: raise DistributedCoordinationError("Compute target belongs to a different project.", 409)
        resources = normalize_resource_request(payload.get("resources"))
        eligible, reasons = target_eligibility(target, resources)
        if not eligible: raise DistributedCoordinationError("Target does not satisfy resource intent: " + ", ".join(reasons), 409)
        handoffs = payload.get("handoffs")
        if handoffs is None:
            if not campaign_id: raise DistributedCoordinationError("campaignId or handoffs is required.")
            handoffs = self._campaign_handoffs(campaign_id, _int(payload.get("limit"), "limit", 1, self.max_tasks_per_plan, self.max_tasks_per_plan), str(payload.get("trialStatus") or "planned"))
        handoffs = _json(handoffs, "handoffs", 8_000_000)
        if not isinstance(handoffs, list) or not handoffs: raise DistributedCoordinationError("Plan requires at least one execution handoff.")
        if len(handoffs) > self.max_tasks_per_plan: raise DistributedCoordinationError("Plan exceeds configured task limit.", 413)
        max_parallel = _int(payload.get("maxParallel"), "maxParallel", 1, 100000, target["capabilities"]["maxParallelJobs"])
        wave_size = min(max_parallel, target["capabilities"]["maxParallelJobs"], target["capabilities"]["maxArraySize"])
        tasks: list[dict[str, Any]] = []
        for i, handoff in enumerate(handoffs):
            if not isinstance(handoff, dict): raise DistributedCoordinationError(f"handoff {i + 1} must be an object.")
            trial_id = _clean_id(handoff.get("trialId") or f"task:{i+1}", f"handoff {i + 1} trialId")
            task = {"ordinal": i + 1, "trialId": trial_id, "campaignId": str(handoff.get("campaignId") or campaign_id), "attempt": int(handoff.get("attempt") or 1), "handoffHash": str(handoff.get("handoffHash") or _sha(handoff)), "handoff": handoff, "wave": (i // wave_size) + 1}
            task["taskHash"] = _sha(task); tasks.append(task)
        waves = []
        for wave_no in range(1, max(t["wave"] for t in tasks) + 1):
            members = [t for t in tasks if t["wave"] == wave_no]
            wave = {"schema": WAVE_SCHEMA, "wave": wave_no, "targetId": target_id, "taskCount": len(members), "taskIds": [t["trialId"] for t in members], "schedulerBundle": _scheduler_contract(target, resources, wave_no, len(members), max_parallel), "submissionRequested": False}
            wave["waveHash"] = _sha(wave); waves.append(wave)
        title = _text(payload.get("title") or (f"Distributed plan for {campaign_id}" if campaign_id else "Distributed execution plan"), "title", 500, True)
        definition = {"schema": PLAN_SCHEMA, "version": VERSION, "title": title, "campaignId": campaign_id, "targetId": target_id, "targetHash": target["targetHash"], "resources": resources, "placementPolicy": str(payload.get("placementPolicy") or "declared-target"), "tasks": tasks, "waves": waves, "automaticDispatch": False, "automaticFailover": False, "credentialsStored": False, "executionAuthority": "Workspace/runtime fabric or external scheduler", "humanScientificReviewRequired": True}
        definition["planHash"] = _sha(definition); plan_id = "plan:" + uuid.uuid4().hex; now = _now()
        with self._lock, self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) AS n FROM dhc_plans WHERE project_id=? AND archived=0", (project_id,)).fetchone()["n"])
            if count >= self.max_plans: raise DistributedCoordinationError("Project execution-plan limit reached.", 409)
            db.execute("INSERT INTO dhc_plans(id,project_id,campaign_id,target_id,title,status,definition_json,plan_hash,created_at,updated_at,actor,archived) VALUES(?,?,?,?,?,?,?,?,?,?,?,0)", (plan_id, project_id, campaign_id, target_id, title, "planned", json.dumps(definition, sort_keys=True), definition["planHash"], now, now, actor))
            self._event(db, plan_id, project_id, "execution-plan-created", actor, {"campaignId": campaign_id, "targetId": target_id, "taskCount": len(tasks), "waveCount": len(waves), "planHash": definition["planHash"]}); db.commit()
        return self.get_plan(plan_id)

    @staticmethod
    def _plan(row: sqlite3.Row) -> dict[str, Any]:
        definition = json.loads(row["definition_json"]); return {"schema": PLAN_SCHEMA, "id": row["id"], "projectId": row["project_id"], "campaignId": row["campaign_id"], "targetId": row["target_id"], "title": row["title"], "status": row["status"], "definition": definition, "planHash": row["plan_hash"], "createdAt": row["created_at"], "updatedAt": row["updated_at"], "actor": row["actor"], "archived": bool(row["archived"])}

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        plan_id = _clean_id(plan_id, "planId")
        with self._connect() as db:
            row = db.execute("SELECT * FROM dhc_plans WHERE id=?", (plan_id,)).fetchone(); receipts = db.execute("SELECT * FROM dhc_receipts WHERE plan_id=? ORDER BY created_at", (plan_id,)).fetchall() if row else []
        if not row: raise DistributedCoordinationError("Execution plan not found.", 404)
        return {"ok": True, "plan": self._plan(row), "receipts": [self._receipt(r) for r in receipts]}

    def list_plans(self, project_id: str, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
        project_id = _clean_id(project_id, "projectId"); where = "project_id=?" if include_archived else "project_id=? AND archived=0"
        with self._connect() as db: rows = db.execute(f"SELECT * FROM dhc_plans WHERE {where} ORDER BY updated_at DESC LIMIT ?", (project_id, max(1, min(1000, int(limit))))).fetchall()
        return {"ok": True, "count": len(rows), "plans": [self._plan(r) for r in rows]}

    @staticmethod
    def _receipt(row: sqlite3.Row) -> dict[str, Any]:
        return {"schema": RECEIPT_SCHEMA, "id": row["id"], "planId": row["plan_id"], "campaignId": row["campaign_id"], "trialId": row["trial_id"], "wave": int(row["wave"]), "status": row["status"], "executionRef": row["execution_ref"], "resultRef": row["result_ref"], "workerRef": row["worker_ref"], "targetRef": row["target_ref"], "details": json.loads(row["details_json"] or "{}"), "createdAt": row["created_at"], "actor": row["actor"], "receiptHash": row["receipt_hash"]}

    def waves(self, plan_id: str) -> dict[str, Any]:
        p = self.get_plan(plan_id)["plan"]; return {"ok": True, "planId": plan_id, "count": len(p["definition"]["waves"]), "waves": p["definition"]["waves"], "automaticDispatch": False}

    def scheduler_bundle(self, plan_id: str) -> dict[str, Any]:
        p = self.get_plan(plan_id)["plan"]; return {"ok": True, "planId": plan_id, "targetId": p["targetId"], "submissionRequested": False, "bundles": [w["schedulerBundle"] for w in p["definition"]["waves"]]}

    def record_receipt(self, plan_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        plan = self.get_plan(plan_id)["plan"]; actor = _text(actor, "actor", 300, True); trial_id = _clean_id(payload.get("trialId"), "trialId"); status = str(payload.get("status") or "").strip().lower()
        if status not in {"queued", "running", "succeeded", "failed", "cancelled"}: raise DistributedCoordinationError("Unsupported receipt status.")
        tasks = plan["definition"]["tasks"]; task = next((t for t in tasks if t["trialId"] == trial_id), None)
        if not task: raise DistributedCoordinationError("Trial is not part of this execution plan.", 404)
        details = _json(payload.get("details") or {}, "receipt details", 1_000_000); execution_ref = _text(payload.get("executionRef"), "executionRef", 500, False); result_ref = _text(payload.get("resultRef"), "resultRef", 500, False); worker_ref = _text(payload.get("workerRef"), "workerRef", 500, False); target_ref = _text(payload.get("targetRef") or plan["targetId"], "targetRef", 500, False)
        body = {"schema": RECEIPT_SCHEMA, "planId": plan_id, "campaignId": plan["campaignId"], "trialId": trial_id, "wave": int(task["wave"]), "status": status, "executionRef": execution_ref, "resultRef": result_ref, "workerRef": worker_ref, "targetRef": target_ref, "details": details, "createdAt": _now(), "actor": actor}; body["receiptHash"] = _sha(body); rid = "receipt:" + uuid.uuid4().hex
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO dhc_receipts(id,plan_id,campaign_id,trial_id,wave,status,execution_ref,result_ref,worker_ref,target_ref,details_json,created_at,actor,receipt_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (rid, plan_id, plan["campaignId"], trial_id, task["wave"], status, execution_ref, result_ref, worker_ref, target_ref, json.dumps(details, sort_keys=True), body["createdAt"], actor, body["receiptHash"]))
            self._event(db, plan_id, plan["projectId"], "execution-receipt-recorded", actor, {"trialId": trial_id, "status": status, "executionRef": execution_ref, "resultRef": result_ref, "receiptHash": body["receiptHash"]}); db.execute("UPDATE dhc_plans SET status=?,updated_at=? WHERE id=?", ("active" if status in {"queued", "running"} else plan["status"], _now(), plan_id)); db.commit()
        campaign_synced = False
        if bool(payload.get("syncCampaignTrial")) and plan["campaignId"] and self.campaigns is not None:
            metrics = details.get("metrics") if isinstance(details, dict) and isinstance(details.get("metrics"), dict) else {}
            self.campaigns.record_trial_state(plan["campaignId"], trial_id, {"status": status, "executionRef": execution_ref, "resultRef": result_ref, "metrics": metrics, "error": details.get("error", "") if isinstance(details, dict) else ""}, actor); campaign_synced = True
        return {"ok": True, "receipt": self.get_receipt(rid), "campaignTrialSynchronized": campaign_synced}

    def get_receipt(self, receipt_id: str) -> dict[str, Any]:
        receipt_id = _clean_id(receipt_id, "receiptId")
        with self._connect() as db: row = db.execute("SELECT * FROM dhc_receipts WHERE id=?", (receipt_id,)).fetchone()
        if not row: raise DistributedCoordinationError("Execution receipt not found.", 404)
        return self._receipt(row)

    def reconcile(self, plan_id: str) -> dict[str, Any]:
        p = self.get_plan(plan_id)["plan"]; tasks = p["definition"]["tasks"]
        with self._connect() as db: rows = db.execute("SELECT trial_id,status,created_at FROM dhc_receipts WHERE plan_id=? ORDER BY created_at", (plan_id,)).fetchall()
        latest: dict[str, str] = {}
        for r in rows: latest[r["trial_id"]] = r["status"]
        counts = {k: 0 for k in ["unreported", "queued", "running", "succeeded", "failed", "cancelled"]}
        for task in tasks: counts[latest.get(task["trialId"], "unreported")] += 1
        terminal = counts["succeeded"] + counts["failed"] + counts["cancelled"]
        status = "completed" if terminal == len(tasks) and counts["failed"] == 0 else ("completed-with-failures" if terminal == len(tasks) else ("active" if rows else "planned"))
        with self._lock, self._connect() as db: db.execute("UPDATE dhc_plans SET status=?,updated_at=? WHERE id=?", (status, _now(), plan_id)); db.commit()
        return {"ok": True, "planId": plan_id, "status": status, "taskCount": len(tasks), "counts": counts, "automaticRetry": False, "automaticFailover": False}

    def replan_failed(self, plan_id: str) -> dict[str, Any]:
        p = self.get_plan(plan_id)["plan"]; resources = p["definition"]["resources"]
        with self._connect() as db:
            receipts = db.execute("SELECT trial_id,status,created_at FROM dhc_receipts WHERE plan_id=? ORDER BY created_at", (plan_id,)).fetchall(); targets = db.execute("SELECT * FROM dhc_targets WHERE project_id=? AND status='active' ORDER BY updated_at DESC", (p["projectId"],)).fetchall()
        latest: dict[str, str] = {}
        for r in receipts: latest[r["trial_id"]] = r["status"]
        failed = [t for t in p["definition"]["tasks"] if latest.get(t["trialId"]) == "failed"]
        candidate_targets = []
        for row in targets:
            target = self._target(row); ok, reasons = target_eligibility(target, resources)
            candidate_targets.append({"targetId": target["id"], "eligible": ok, "reasons": reasons, "scheduler": target["scheduler"], "targetHash": target["targetHash"]})
        return {"ok": True, "planId": plan_id, "failedTaskCount": len(failed), "failedTrialIds": [t["trialId"] for t in failed], "candidateTargets": candidate_targets, "automaticFailover": False, "replanRequiresExplicitAction": True}

    def manifest(self, plan_id: str) -> dict[str, Any]:
        data = self.get_plan(plan_id); p = data["plan"]
        body = {"schema": MANIFEST_SCHEMA, "version": VERSION, "planId": plan_id, "projectId": p["projectId"], "campaignId": p["campaignId"], "targetId": p["targetId"], "planHash": p["planHash"], "resourceIntent": p["definition"]["resources"], "waves": [{"wave": w["wave"], "waveHash": w["waveHash"], "schedulerContractHash": w["schedulerBundle"]["contractHash"], "taskCount": w["taskCount"]} for w in p["definition"]["waves"]], "receipts": [{"id": r["id"], "trialId": r["trialId"], "status": r["status"], "receiptHash": r["receiptHash"]} for r in data["receipts"]], "automaticDispatch": False, "automaticFailover": False, "credentialsStored": False, "humanScientificReviewRequired": True}
        body["manifestDigest"] = _sha(body); return {"ok": True, "manifest": body}

    def verify_manifest(self, payload: dict[str, Any]) -> dict[str, Any]:
        manifest = _json(payload.get("manifest") or payload, "manifest", 4_000_000)
        if not isinstance(manifest, dict): raise DistributedCoordinationError("manifest must be an object.")
        supplied = str(manifest.get("manifestDigest") or ""); unsigned = dict(manifest); unsigned.pop("manifestDigest", None); computed = _sha(unsigned)
        return {"ok": bool(supplied) and supplied == computed, "suppliedDigest": supplied, "computedDigest": computed, "schema": manifest.get("schema")}

    def timeline(self, plan_id: str, limit: int = 500) -> dict[str, Any]:
        p = self.get_plan(plan_id)["plan"]
        with self._connect() as db: rows = db.execute("SELECT * FROM dhc_events WHERE object_id=? ORDER BY seq DESC LIMIT ?", (plan_id, max(1, min(5000, int(limit))))).fetchall()
        events = [{"seq": int(r["seq"]), "eventType": r["event_type"], "occurredAt": r["occurred_at"], "actor": r["actor"], "payload": json.loads(r["payload_json"] or "{}"), "previousHash": r["previous_hash"], "eventHash": r["event_hash"]} for r in rows]
        return {"ok": True, "planId": plan_id, "projectId": p["projectId"], "count": len(events), "events": events}

    def archive_plan(self, plan_id: str, actor: str) -> dict[str, Any]:
        p = self.get_plan(plan_id)["plan"]; actor = _text(actor, "actor", 300, True)
        with self._lock, self._connect() as db: db.execute("UPDATE dhc_plans SET archived=1,status='archived',updated_at=? WHERE id=?", (_now(), plan_id)); self._event(db, plan_id, p["projectId"], "execution-plan-archived", actor, {}); db.commit()
        return self.get_plan(plan_id)
