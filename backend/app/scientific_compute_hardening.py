from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

VERSION = "0.58.0"
JOB_SCHEMA = "sc-lab-scientific-compute-job/0.58.0"
ASSESSMENT_SCHEMA = "sc-lab-workload-assessment/0.58.0"
CACHE_SCHEMA = "sc-lab-scientific-result-cache/0.58.0"


class ScientificComputeHardeningError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _safe_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _strip_ephemeral(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(k): _strip_ephemeral(v)
            for k, v in value.items()
            if str(k) not in {"requestId", "requestedAt", "clientTimestamp", "uiState", "nonce", "_runtime"}
        }
    if isinstance(value, list):
        return [_strip_ephemeral(v) for v in value]
    return value


def _dataset_shape(payload: dict[str, Any]) -> tuple[int, int]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        dataset = payload.get("dataset")
        if isinstance(dataset, dict):
            rows = dataset.get("rows")
    if not isinstance(rows, list):
        inputs = payload.get("inputs")
        if isinstance(inputs, dict):
            dataset = inputs.get("dataset")
            if isinstance(dataset, dict):
                rows = dataset.get("rows")
    row_count = len(rows) if isinstance(rows, list) else _safe_int(payload.get("rowCount"), 0, 0, 10_000_000)
    columns: set[str] = set()
    if isinstance(rows, list):
        for row in rows[:100]:
            if isinstance(row, dict):
                columns.update(str(k) for k in row.keys())
    column_count = len(columns) if columns else _safe_int(payload.get("columnCount"), 0, 0, 100_000)
    return row_count, column_count


def assess_workload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificComputeHardeningError("Workload assessment requires an object payload.")
    rows, columns = _dataset_shape(payload)
    workflow = payload.get("workflow") if isinstance(payload.get("workflow"), dict) else {}
    stages = len(workflow.get("stages") or []) if isinstance(workflow.get("stages"), list) else _safe_int(payload.get("stageCount"), 0, 0, 10_000)
    parameter_count = _safe_int(payload.get("parameterCount"), 0, 0, 1_000_000)
    draws = _safe_int(payload.get("draws") or payload.get("samples"), 0, 0, 10_000_000)
    estimated_cells = rows * max(columns, 1)
    score = 0
    score += min(45, estimated_cells // 100_000)
    score += min(20, stages * 2)
    score += min(20, parameter_count // 25)
    score += min(25, draws // 5_000)
    serialized_bytes = len(_canonical(_strip_ephemeral(payload)))
    score += min(20, serialized_bytes // 1_000_000)

    hard_limits = {
        "maxRows": 1_000_000,
        "maxColumns": 5_000,
        "maxCells": 50_000_000,
        "maxWorkflowStages": 24,
        "maxPayloadBytes": 64 * 1024 * 1024,
    }
    violations: list[str] = []
    if rows > hard_limits["maxRows"]:
        violations.append("row limit exceeded")
    if columns > hard_limits["maxColumns"]:
        violations.append("column limit exceeded")
    if estimated_cells > hard_limits["maxCells"]:
        violations.append("dataset cell limit exceeded")
    if stages > hard_limits["maxWorkflowStages"]:
        violations.append("workflow stage limit exceeded")
    if serialized_bytes > hard_limits["maxPayloadBytes"]:
        violations.append("payload size limit exceeded")

    if violations:
        disposition = "reject"
    elif score >= 35 or estimated_cells >= 1_000_000 or draws >= 20_000 or stages >= 10:
        disposition = "async-recommended"
    else:
        disposition = "interactive"

    chunk_rows = 5000 if rows >= 50_000 else (2000 if rows >= 10_000 else max(rows, 250))
    warnings: list[str] = []
    if estimated_cells >= 2_000_000:
        warnings.append("Large dataset: use bounded windows for browser previews.")
    if draws >= 20_000:
        warnings.append("Large probabilistic workload: asynchronous execution is recommended.")
    if stages >= 10:
        warnings.append("Long workflow: asynchronous execution is recommended to keep the UI responsive.")
    return {
        "ok": not violations,
        "schema": ASSESSMENT_SCHEMA,
        "version": VERSION,
        "disposition": disposition,
        "score": int(score),
        "shape": {"rows": rows, "columns": columns, "estimatedCells": estimated_cells},
        "workflowStages": stages,
        "parameterCount": parameter_count,
        "drawsOrSamples": draws,
        "serializedBytes": serialized_bytes,
        "recommendedPreviewRows": chunk_rows,
        "hardLimits": hard_limits,
        "violations": violations,
        "warnings": warnings,
    }


def dataset_window(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        dataset = payload.get("dataset")
        rows = dataset.get("rows") if isinstance(dataset, dict) else None
    if not isinstance(rows, list):
        raise ScientificComputeHardeningError("Dataset window requires rows.")
    offset = _safe_int(payload.get("offset"), 0, 0, max(len(rows), 0))
    limit = _safe_int(payload.get("limit"), 500, 1, 5000)
    requested_columns = payload.get("columns")
    columns = [str(v) for v in requested_columns[:250]] if isinstance(requested_columns, list) else []
    selected = rows[offset : offset + limit]
    if columns:
        selected = [{key: row.get(key) for key in columns if isinstance(row, dict) and key in row} for row in selected]
    source_hash = _hash(rows)
    return {
        "ok": True,
        "version": VERSION,
        "sourceHash": source_hash,
        "windowHash": _hash(selected),
        "offset": offset,
        "limit": limit,
        "returnedRows": len(selected),
        "totalRows": len(rows),
        "hasMore": offset + len(selected) < len(rows),
        "rows": selected,
    }


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "boundedAsyncExecution": True,
        "persistentResultCache": True,
        "deterministicCacheKeys": True,
        "datasetWindowing": True,
        "cooperativeCancellation": True,
        "forceTerminateRunningScientificCode": False,
        "arbitraryCodeExecution": False,
        "automaticScaling": False,
        "automaticRemoteCompute": False,
        "maximumPreviewRows": 5000,
        "maximumWorkflowStages": 24,
    }


class ScientificComputeManager:
    def __init__(
        self,
        db_path: str,
        adapters: dict[str, Callable[[dict[str, Any]], Any]],
        *,
        max_workers: int = 2,
        max_queued: int = 12,
        cache_ttl_seconds: int = 86400,
        max_cache_records: int = 128,
        max_result_bytes: int = 16 * 1024 * 1024,
    ) -> None:
        self.db_path = str(db_path)
        self.adapters = dict(adapters)
        self.max_workers = max(1, min(int(max_workers), 8))
        self.max_queued = max(1, min(int(max_queued), 100))
        self.cache_ttl_seconds = max(60, min(int(cache_ttl_seconds), 30 * 86400))
        self.max_cache_records = max(1, min(int(max_cache_records), 5000))
        self.max_result_bytes = max(65536, min(int(max_result_bytes), 64 * 1024 * 1024))
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="sc-lab-v0580")
        self._futures: dict[str, Future[Any]] = {}
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS compute_jobs(
                  id TEXT PRIMARY KEY, operation TEXT NOT NULL, status TEXT NOT NULL,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  request_hash TEXT NOT NULL, request_json TEXT NOT NULL,
                  result_hash TEXT, result_json TEXT, error TEXT, cache_hit INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS result_cache(
                  cache_key TEXT PRIMARY KEY, operation TEXT NOT NULL,
                  created_at_epoch REAL NOT NULL, expires_at_epoch REAL NOT NULL,
                  result_hash TEXT NOT NULL, result_json TEXT NOT NULL, size_bytes INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_compute_jobs_status ON compute_jobs(status);
                CREATE INDEX IF NOT EXISTS idx_result_cache_expiry ON result_cache(expires_at_epoch);
                """
            )

    def health(self) -> dict[str, Any]:
        with self._connect() as db:
            jobs = db.execute("SELECT status,COUNT(*) c FROM compute_jobs GROUP BY status").fetchall()
            cache = db.execute("SELECT COUNT(*) c,COALESCE(SUM(size_bytes),0) b FROM result_cache WHERE expires_at_epoch>=?", (time.time(),)).fetchone()
        return {
            "ok": True,
            "status": "compute-hardened",
            "version": VERSION,
            "workers": self.max_workers,
            "queueLimit": self.max_queued,
            "registeredOperations": sorted(self.adapters),
            "jobs": {row["status"]: row["c"] for row in jobs},
            "cache": {"records": cache["c"], "bytes": cache["b"]},
            "cooperativeCancellation": True,
            "forceTermination": False,
        }

    def _operation(self, operation: Any) -> str:
        op = str(operation or "").strip()
        if op not in self.adapters:
            raise ScientificComputeHardeningError("Operation is not registered for hardened scientific compute.")
        return op

    def cache_key(self, operation: str, payload: dict[str, Any]) -> str:
        return _hash({"version": VERSION, "operation": operation, "payload": _strip_ephemeral(payload)})

    def _prune_cache(self, db: sqlite3.Connection) -> None:
        now = time.time()
        db.execute("DELETE FROM result_cache WHERE expires_at_epoch<?", (now,))
        rows = db.execute("SELECT cache_key FROM result_cache ORDER BY created_at_epoch DESC").fetchall()
        for row in rows[self.max_cache_records :]:
            db.execute("DELETE FROM result_cache WHERE cache_key=?", (row["cache_key"],))

    def _cache_get(self, operation: str, payload: dict[str, Any]) -> tuple[str, Any, str] | None:
        key = self.cache_key(operation, payload)
        with self._connect() as db:
            self._prune_cache(db)
            row = db.execute("SELECT result_json,result_hash FROM result_cache WHERE cache_key=? AND expires_at_epoch>=?", (key, time.time())).fetchone()
        if not row:
            return None
        return key, json.loads(row["result_json"]), row["result_hash"]

    def _cache_put(self, operation: str, payload: dict[str, Any], result: Any) -> tuple[str, str, bool]:
        body = _canonical(result)
        key = self.cache_key(operation, payload)
        result_hash = hashlib.sha256(body).hexdigest()
        if len(body) > self.max_result_bytes:
            return key, result_hash, False
        now = time.time()
        with self._connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO result_cache(cache_key,operation,created_at_epoch,expires_at_epoch,result_hash,result_json,size_bytes) VALUES(?,?,?,?,?,?,?)",
                (key, operation, now, now + self.cache_ttl_seconds, result_hash, body.decode("utf-8"), len(body)),
            )
            self._prune_cache(db)
        return key, result_hash, True

    def execute(self, operation: Any, payload: dict[str, Any], *, use_cache: bool = True) -> dict[str, Any]:
        op = self._operation(operation)
        assessment = assess_workload(payload)
        if assessment["disposition"] == "reject":
            raise ScientificComputeHardeningError("Workload exceeds v0.58 bounded-compute limits: " + ", ".join(assessment["violations"]))
        if use_cache:
            cached = self._cache_get(op, payload)
            if cached:
                key, result, result_hash = cached
                return {"ok": True, "version": VERSION, "operation": op, "cacheHit": True, "cacheKey": key, "resultHash": result_hash, "assessment": assessment, "result": result}
        started = time.perf_counter()
        result = self.adapters[op](payload)
        key, result_hash, stored = self._cache_put(op, payload, result) if use_cache else (self.cache_key(op, payload), _hash(result), False)
        return {"ok": True, "version": VERSION, "operation": op, "cacheHit": False, "cacheStored": stored, "cacheKey": key, "resultHash": result_hash, "durationMs": round((time.perf_counter()-started)*1000,3), "assessment": assessment, "result": result}

    def _active_count(self) -> int:
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM compute_jobs WHERE status IN ('queued','running','cancellation-requested')").fetchone()[0])

    def submit(self, operation: Any, payload: dict[str, Any]) -> dict[str, Any]:
        op = self._operation(operation)
        assessment = assess_workload(payload)
        if assessment["disposition"] == "reject":
            raise ScientificComputeHardeningError("Workload exceeds v0.58 bounded-compute limits: " + ", ".join(assessment["violations"]))
        cached = self._cache_get(op, payload)
        job_id = f"scientific-job-{uuid.uuid4().hex[:16]}"
        now = _now()
        request_hash = _hash(_strip_ephemeral(payload))
        if cached:
            key, result, result_hash = cached
            with self._connect() as db:
                db.execute("INSERT INTO compute_jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)", (job_id,op,"completed",now,now,request_hash,_canonical(payload).decode(),result_hash,_canonical(result).decode(),None,1))
            return {"ok": True, "version": VERSION, "job": self.status(job_id), "assessment": assessment, "cacheKey": key}
        if self._active_count() >= self.max_queued + self.max_workers:
            raise ScientificComputeHardeningError("Scientific compute queue is at its bounded capacity.")
        with self._connect() as db:
            db.execute("INSERT INTO compute_jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)", (job_id,op,"queued",now,now,request_hash,_canonical(payload).decode(),None,None,None,0))
        future = self._executor.submit(self._run_job, job_id, op, payload)
        with self._lock:
            self._futures[job_id] = future
        return {"ok": True, "version": VERSION, "job": self.status(job_id), "assessment": assessment}

    def _run_job(self, job_id: str, operation: str, payload: dict[str, Any]) -> None:
        with self._connect() as db:
            row = db.execute("SELECT status FROM compute_jobs WHERE id=?", (job_id,)).fetchone()
            if not row or row["status"] == "cancelled":
                return
            db.execute("UPDATE compute_jobs SET status='running',updated_at=? WHERE id=?", (_now(), job_id))
        try:
            result = self.adapters[operation](payload)
            body = _canonical(result)
            result_hash = hashlib.sha256(body).hexdigest()
            with self._connect() as db:
                status = db.execute("SELECT status FROM compute_jobs WHERE id=?", (job_id,)).fetchone()["status"]
                if status == "cancellation-requested":
                    db.execute("UPDATE compute_jobs SET status='cancelled-after-completion',updated_at=?,result_hash=NULL,result_json=NULL WHERE id=?", (_now(), job_id))
                    return
            self._cache_put(operation, payload, result)
            with self._connect() as db:
                db.execute("UPDATE compute_jobs SET status='completed',updated_at=?,result_hash=?,result_json=?,error=NULL WHERE id=?", (_now(), result_hash, body.decode("utf-8"), job_id))
        except Exception as exc:
            with self._connect() as db:
                db.execute("UPDATE compute_jobs SET status='failed',updated_at=?,error=? WHERE id=?", (_now(), str(exc)[:4000], job_id))
        finally:
            with self._lock:
                self._futures.pop(job_id, None)

    def status(self, job_id: str) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM compute_jobs WHERE id=?", (str(job_id),)).fetchone()
        if not row:
            raise ScientificComputeHardeningError("Scientific compute job was not found.")
        return {
            "schema": JOB_SCHEMA,
            "version": VERSION,
            "id": row["id"],
            "operation": row["operation"],
            "status": row["status"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "requestHash": row["request_hash"],
            "resultHash": row["result_hash"],
            "cacheHit": bool(row["cache_hit"]),
            "error": row["error"],
        }

    def list_jobs(self, limit: int = 30) -> dict[str, Any]:
        limit = _safe_int(limit, 30, 1, 200)
        with self._connect() as db:
            rows = db.execute("SELECT id FROM compute_jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return {"ok": True, "version": VERSION, "jobs": [self.status(row["id"]) for row in rows]}

    def result(self, job_id: str) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT status,result_json,result_hash,error FROM compute_jobs WHERE id=?", (str(job_id),)).fetchone()
        if not row:
            raise ScientificComputeHardeningError("Scientific compute job was not found.")
        if row["status"] != "completed":
            return {"ok": False, "version": VERSION, "status": row["status"], "error": row["error"], "result": None}
        return {"ok": True, "version": VERSION, "status": "completed", "resultHash": row["result_hash"], "result": json.loads(row["result_json"])}

    def cancel(self, job_id: str) -> dict[str, Any]:
        job_id = str(job_id)
        current = self.status(job_id)
        if current["status"] in {"completed", "failed", "cancelled", "cancelled-after-completion"}:
            return {"ok": True, "version": VERSION, "job": current, "changed": False}
        with self._lock:
            future = self._futures.get(job_id)
        if current["status"] == "queued" and future is not None and future.cancel():
            target = "cancelled"
        else:
            target = "cancellation-requested"
        with self._connect() as db:
            db.execute("UPDATE compute_jobs SET status=?,updated_at=? WHERE id=?", (target, _now(), job_id))
        return {"ok": True, "version": VERSION, "job": self.status(job_id), "changed": True, "forceTermination": False}

    def cache_stats(self) -> dict[str, Any]:
        with self._connect() as db:
            self._prune_cache(db)
            row = db.execute("SELECT COUNT(*) c,COALESCE(SUM(size_bytes),0) b FROM result_cache").fetchone()
        return {"ok": True, "schema": CACHE_SCHEMA, "version": VERSION, "records": row["c"], "bytes": row["b"], "ttlSeconds": self.cache_ttl_seconds, "maxRecords": self.max_cache_records}

    def clear_cache(self) -> dict[str, Any]:
        with self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) FROM result_cache").fetchone()[0])
            db.execute("DELETE FROM result_cache")
        return {"ok": True, "version": VERSION, "cleared": count}

    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait, cancel_futures=True)
