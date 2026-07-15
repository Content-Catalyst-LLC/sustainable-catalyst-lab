from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import queue
import sqlite3
import threading
import time
import uuid
from typing import Any

from .config import settings

TERMINAL_STATES = {"completed", "failed", "cancelled", "timed_out"}
RUNNABLE_STATES = {"queued", "retrying"}
ALL_STATES = RUNNABLE_STATES | TERMINAL_STATES | {"running", "paused"}
CACHE_MODES = {"use", "refresh", "bypass"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def request_digest(operation: str, payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json({"operation": operation, "payload": payload}).encode("utf-8")).hexdigest()


def _process_job(
    payload: dict[str, Any],
    auth: dict[str, str],
    checkpoint: dict[str, Any] | None,
    result_queue: Any,
) -> None:
    """Execute one registered compute request in an isolated child process."""
    try:
        from .compute import run_compute
        from .long_jobs import is_checkpointable, run_checkpointed
        from .schemas import ComputeRequest

        request = ComputeRequest.model_validate(payload)

        def emit(progress: float, message: str, state: dict[str, Any], partial: dict[str, Any] | None = None) -> None:
            result_queue.put(
                {
                    "type": "checkpoint",
                    "progress": max(0.0, min(99.0, float(progress))),
                    "message": str(message)[:512],
                    "checkpoint": state,
                    "partial": partial,
                },
                timeout=10,
            )

        if is_checkpointable(request.method):
            result = run_checkpointed(request, auth, checkpoint, emit)
        else:
            result = run_compute(request, auth)
        result_queue.put(
            {"type": "result", "ok": True, "result": result.model_dump(mode="json", by_alias=True)},
            timeout=10,
        )
    except Exception as exc:  # child boundary: serialize every failure
        status_code = int(getattr(exc, "status_code", 500))
        retryable = bool(getattr(exc, "retryable", status_code >= 500))
        code = str(getattr(exc, "code", "worker_process_error"))
        try:
            result_queue.put(
                {
                    "type": "result",
                    "ok": False,
                    "error": {
                        "code": code,
                        "message": str(exc),
                        "statusCode": status_code,
                        "retryable": retryable,
                    },
                },
                timeout=5,
            )
        except Exception:
            pass


@dataclass
class WorkerHandle:
    job_id: str
    worker_id: str
    process: Any
    result_queue: Any
    started_monotonic: float
    timeout_seconds: int


class PersistentJobQueue:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path or settings.job_db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_lock = threading.RLock()
        self._active_lock = threading.RLock()
        self._active: dict[str, WorkerHandle] = {}
        self._scheduler: threading.Thread | None = None
        self._stop = threading.Event()
        self._started_at: str | None = None
        self._last_scheduler_tick: str | None = None
        self._ctx = mp.get_context("spawn")
        self._initialize_database()
        self._recover_interrupted_jobs()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.db_path), timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA busy_timeout=10000")
        return connection

    @staticmethod
    def _columns(db: sqlite3.Connection, table: str) -> set[str]:
        return {str(row[1]) for row in db.execute(f"PRAGMA table_info({table})").fetchall()}

    def _initialize_database(self) -> None:
        with self._db_lock, self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    parent_job_id TEXT,
                    operation TEXT NOT NULL,
                    method TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    auth_json TEXT NOT NULL,
                    request_sha256 TEXT NOT NULL,
                    idempotency_key TEXT,
                    status TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0,
                    progress_message TEXT NOT NULL DEFAULT '',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 1,
                    manual_retries INTEGER NOT NULL DEFAULT 0,
                    timeout_seconds INTEGER NOT NULL,
                    project_id TEXT,
                    client_id TEXT NOT NULL DEFAULT 'unknown',
                    worker_id TEXT,
                    worker_pid INTEGER,
                    cancel_requested INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    next_run_at REAL NOT NULL DEFAULT 0,
                    last_heartbeat_at TEXT,
                    result_json TEXT,
                    error_json TEXT,
                    priority INTEGER NOT NULL DEFAULT 50,
                    cache_mode TEXT NOT NULL DEFAULT 'use',
                    cache_key TEXT,
                    cache_hit INTEGER NOT NULL DEFAULT 0,
                    estimated_seconds REAL,
                    checkpoint_json TEXT,
                    checkpoint_sequence INTEGER NOT NULL DEFAULT 0,
                    checkpoint_updated_at TEXT,
                    partial_result_json TEXT,
                    resumed_count INTEGER NOT NULL DEFAULT 0,
                    result_bytes INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS job_checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    progress REAL NOT NULL,
                    message TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,
                    partial_result_json TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(job_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS result_cache (
                    cache_key TEXT PRIMARY KEY,
                    method TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    result_bytes INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    hit_count INTEGER NOT NULL DEFAULT 0,
                    last_hit_at TEXT
                );
                CREATE INDEX IF NOT EXISTS jobs_status_next_idx ON jobs(status, next_run_at, priority, created_at);
                CREATE INDEX IF NOT EXISTS jobs_request_hash_idx ON jobs(request_sha256, status);
                CREATE INDEX IF NOT EXISTS jobs_idempotency_idx ON jobs(idempotency_key, created_at);
                CREATE INDEX IF NOT EXISTS jobs_project_idx ON jobs(project_id, created_at);
                CREATE INDEX IF NOT EXISTS job_checkpoints_job_idx ON job_checkpoints(job_id, sequence DESC);
                CREATE INDEX IF NOT EXISTS result_cache_expiry_idx ON result_cache(expires_at);
                """
            )
            # Migrate v0.26.1/v0.27.1 databases without discarding queued or completed work.
            columns = self._columns(db, "jobs")
            additions = {
                "priority": "INTEGER NOT NULL DEFAULT 50",
                "cache_mode": "TEXT NOT NULL DEFAULT 'use'",
                "cache_key": "TEXT",
                "cache_hit": "INTEGER NOT NULL DEFAULT 0",
                "estimated_seconds": "REAL",
                "checkpoint_json": "TEXT",
                "checkpoint_sequence": "INTEGER NOT NULL DEFAULT 0",
                "checkpoint_updated_at": "TEXT",
                "partial_result_json": "TEXT",
                "resumed_count": "INTEGER NOT NULL DEFAULT 0",
                "result_bytes": "INTEGER NOT NULL DEFAULT 0",
            }
            for column, definition in additions.items():
                if column not in columns:
                    db.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")

    def _recover_interrupted_jobs(self) -> None:
        now = utc_now()
        error = canonical_json(
            {
                "code": "worker_restart_recovery",
                "message": "The compute service restarted before completion. The job was returned to the queue and will resume from its latest checkpoint when supported.",
                "retryable": True,
            }
        )
        with self._db_lock, self._connect() as db:
            db.execute(
                """
                UPDATE jobs
                   SET status='queued', progress=CASE WHEN checkpoint_sequence > 0 THEN progress ELSE 0 END,
                       progress_message=CASE WHEN checkpoint_sequence > 0 THEN 'Recovered after restart; checkpoint available' ELSE 'Recovered after service restart' END,
                       worker_id=NULL, worker_pid=NULL, cancel_requested=0, started_at=NULL,
                       updated_at=?, next_run_at=0, error_json=?, resumed_count=resumed_count+1
                 WHERE status='running'
                """,
                (now, error),
            )

    def start(self) -> None:
        with self._active_lock:
            if self._scheduler and self._scheduler.is_alive():
                return
            self._stop.clear()
            self._started_at = self._started_at or utc_now()
            self._scheduler = threading.Thread(target=self._scheduler_loop, name="sc-lab-job-scheduler", daemon=True)
            self._scheduler.start()

    def stop(self) -> None:
        self._stop.set()
        with self._active_lock:
            handles = list(self._active.values())
            self._active.clear()
        for handle in handles:
            self._terminate(handle)
        scheduler = self._scheduler
        if scheduler and scheduler.is_alive() and scheduler is not threading.current_thread():
            scheduler.join(timeout=2)

    def submit(
        self,
        *,
        operation: str,
        payload: dict[str, Any],
        auth: dict[str, str],
        timeout_seconds: int | None = None,
        max_attempts: int | None = None,
        idempotency_key: str | None = None,
        priority: int | None = None,
        cache_mode: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        self.start()
        digest = request_digest(operation, payload)
        clean_key = (idempotency_key or "").strip()[:128] or None
        mode = str(cache_mode or "use").lower()
        if mode not in CACHE_MODES:
            raise ValueError("cacheMode must be use, refresh, or bypass.")
        existing = self._find_duplicate(digest, clean_key)
        if existing:
            record = self._public(existing)
            record["deduplicated"] = True
            return record, True

        now = utc_now()
        job_id = str(uuid.uuid4())
        method = str(payload.get("method") or payload.get("methodId") or "")[:128]
        timeout = max(1, min(settings.max_job_timeout_seconds, int(timeout_seconds or settings.default_job_timeout_seconds)))
        attempts = max(1, min(settings.max_job_attempts, int(max_attempts or settings.default_job_attempts)))
        project_id = str(payload.get("project_id") or payload.get("projectId") or "")[:128] or None
        client_id = str(auth.get("client_id") or auth.get("client") or "unknown")[:128]
        auth_record = {"mode": str(auth.get("mode") or "unknown"), "client_id": client_id, "client": client_id}
        safe_priority = max(0, min(100, int(settings.default_job_priority if priority is None else priority)))

        cached = self._cache_lookup(digest) if mode == "use" else None
        with self._db_lock, self._connect() as db:
            active_total = int(db.execute("SELECT COUNT(*) FROM jobs WHERE status IN ('queued','retrying','running')").fetchone()[0])
            if active_total >= settings.max_queued_jobs:
                raise QueueCapacityError("The compute queue is at capacity. Try again after existing jobs finish.")
            if project_id:
                active_project = int(
                    db.execute(
                        "SELECT COUNT(*) FROM jobs WHERE project_id=? AND status IN ('queued','retrying','running')",
                        (project_id,),
                    ).fetchone()[0]
                )
                if active_project >= settings.max_active_jobs_per_project:
                    raise ProjectLimitError(
                        f"Project {project_id} already has {active_project} active jobs; the configured limit is {settings.max_active_jobs_per_project}."
                    )
            if cached:
                result_text = str(cached["result_json"])
                db.execute(
                    """
                    INSERT INTO jobs (
                        id, operation, method, request_json, auth_json, request_sha256, idempotency_key,
                        status, progress, progress_message, attempts, max_attempts, timeout_seconds,
                        project_id, client_id, created_at, updated_at, started_at, finished_at, next_run_at,
                        result_json, priority, cache_mode, cache_key, cache_hit, result_bytes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'completed', 100, 'Completed from result cache', 0, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        job_id, operation, method, canonical_json(payload), canonical_json(auth_record), digest, clean_key,
                        attempts, timeout, project_id, client_id, now, now, now, now, result_text,
                        safe_priority, mode, digest, int(cached["result_bytes"]),
                    ),
                )
            else:
                db.execute(
                    """
                    INSERT INTO jobs (
                        id, operation, method, request_json, auth_json, request_sha256, idempotency_key,
                        status, progress, progress_message, attempts, max_attempts, timeout_seconds,
                        project_id, client_id, created_at, updated_at, next_run_at,
                        priority, cache_mode, cache_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', 0, 'Waiting for an available worker', 0, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
                    """,
                    (
                        job_id, operation, method, canonical_json(payload), canonical_json(auth_record), digest, clean_key,
                        attempts, timeout, project_id, client_id, now, now, safe_priority, mode, digest,
                    ),
                )
        self._trim_records()
        return self.get(job_id) or {}, False

    def _find_duplicate(self, digest: str, idempotency_key: str | None) -> sqlite3.Row | None:
        cutoff = time.time() - settings.job_dedupe_window_seconds
        with self._db_lock, self._connect() as db:
            if idempotency_key:
                row = db.execute(
                    """
                    SELECT * FROM jobs
                     WHERE idempotency_key=?
                       AND (status IN ('queued','retrying','running','paused') OR (status='completed' AND strftime('%s', created_at) >= ?))
                     ORDER BY created_at DESC LIMIT 1
                    """,
                    (idempotency_key, int(cutoff)),
                ).fetchone()
                if row:
                    return row
            return db.execute(
                """
                SELECT * FROM jobs
                 WHERE request_sha256=? AND status IN ('queued','retrying','running','paused')
                 ORDER BY created_at DESC LIMIT 1
                """,
                (digest,),
            ).fetchone()

    def _cache_lookup(self, key: str) -> sqlite3.Row | None:
        now = time.time()
        with self._db_lock, self._connect() as db:
            db.execute("DELETE FROM result_cache WHERE expires_at < ?", (now,))
            row = db.execute("SELECT * FROM result_cache WHERE cache_key=? AND expires_at>=?", (key, now)).fetchone()
            if row:
                db.execute(
                    "UPDATE result_cache SET hit_count=hit_count+1,last_hit_at=? WHERE cache_key=?",
                    (utc_now(), key),
                )
            return row

    def get(self, job_id: str) -> dict[str, Any] | None:
        row = self._row(job_id)
        return self._public(row) if row else None

    def list(self, *, status: str | None = None, project_id: str | None = None, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        clauses: list[str] = []
        params: list[Any] = []
        if status:
            if status not in ALL_STATES:
                raise ValueError("Unknown job status filter.")
            clauses.append("status=?")
            params.append(status)
        if project_id:
            clauses.append("project_id=?")
            params.append(project_id[:128])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        safe_limit = max(1, min(200, int(limit)))
        safe_offset = max(0, int(offset))
        with self._db_lock, self._connect() as db:
            total = int(db.execute(f"SELECT COUNT(*) FROM jobs {where}", params).fetchone()[0])
            rows = db.execute(
                f"SELECT * FROM jobs {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                [*params, safe_limit, safe_offset],
            ).fetchall()
        return {"jobs": [self._public(row) for row in rows], "total": total, "limit": safe_limit, "offset": safe_offset}

    def cancel(self, job_id: str) -> dict[str, Any] | None:
        with self._active_lock:
            handle = self._active.pop(job_id, None)
        if handle:
            self._terminate(handle)
        now = utc_now()
        with self._db_lock, self._connect() as db:
            row = db.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                return None
            if row["status"] not in TERMINAL_STATES:
                db.execute(
                    """
                    UPDATE jobs SET status='cancelled', progress_message='Cancelled by request',
                           cancel_requested=1, finished_at=?, updated_at=?, worker_id=NULL, worker_pid=NULL
                     WHERE id=?
                    """,
                    (now, now, job_id),
                )
        return self.get(job_id)

    def pause(self, job_id: str) -> dict[str, Any] | None:
        with self._active_lock:
            handle = self._active.pop(job_id, None)
        if handle:
            self._terminate(handle)
        now = utc_now()
        with self._db_lock, self._connect() as db:
            row = db.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                return None
            if row["status"] in TERMINAL_STATES:
                raise InvalidJobStateError("Completed, failed, cancelled, or timed-out jobs cannot be paused.")
            db.execute(
                """
                UPDATE jobs SET status='paused', progress_message=CASE WHEN checkpoint_sequence>0 THEN 'Paused with checkpoint available' ELSE 'Paused before a checkpoint was created' END,
                       cancel_requested=0, updated_at=?, worker_id=NULL, worker_pid=NULL
                 WHERE id=?
                """,
                (now, job_id),
            )
        return self.get(job_id)

    def resume(self, job_id: str) -> dict[str, Any] | None:
        now = utc_now()
        with self._db_lock, self._connect() as db:
            row = db.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                return None
            if row["status"] not in {"paused", "failed", "timed_out", "cancelled"}:
                raise InvalidJobStateError("Only paused, failed, timed-out, or cancelled jobs can be resumed.")
            db.execute(
                """
                UPDATE jobs SET status='queued', progress_message=CASE WHEN checkpoint_sequence>0 THEN 'Queued to resume from checkpoint' ELSE 'Queued to restart' END,
                       attempts=0, cancel_requested=0, started_at=NULL, finished_at=NULL,
                       worker_id=NULL, worker_pid=NULL, next_run_at=0, updated_at=?,
                       result_json=NULL, error_json=NULL, cache_hit=0, resumed_count=resumed_count+1
                 WHERE id=?
                """,
                (now, job_id),
            )
        self.start()
        return self.get(job_id)

    def retry(self, job_id: str) -> dict[str, Any] | None:
        record = self.resume(job_id)
        if record:
            with self._db_lock, self._connect() as db:
                db.execute("UPDATE jobs SET manual_retries=manual_retries+1 WHERE id=?", (job_id,))
            return self.get(job_id)
        return None

    def checkpoints(self, job_id: str, limit: int = 20) -> dict[str, Any] | None:
        row = self._row(job_id)
        if not row:
            return None
        safe_limit = max(1, min(200, int(limit)))
        with self._db_lock, self._connect() as db:
            rows = db.execute(
                "SELECT sequence,progress,message,partial_result_json,created_at FROM job_checkpoints WHERE job_id=? ORDER BY sequence DESC LIMIT ?",
                (job_id, safe_limit),
            ).fetchall()
        latest_checkpoint = json.loads(row["checkpoint_json"]) if row["checkpoint_json"] else None
        latest_partial = json.loads(row["partial_result_json"]) if row["partial_result_json"] else None
        return {
            "schema": "sc-lab-job-checkpoints/1.0",
            "jobId": job_id,
            "checkpointable": bool(row["checkpoint_sequence"] or row["method"] in {"simulation.parameter_sweep", "uncertainty.bootstrap_mean_interval"}),
            "latestSequence": int(row["checkpoint_sequence"]),
            "latestCheckpointAt": row["checkpoint_updated_at"],
            "latestCheckpoint": latest_checkpoint,
            "partialResult": latest_partial,
            "history": [
                {
                    "sequence": int(item["sequence"]),
                    "progress": float(item["progress"]),
                    "message": item["message"],
                    "partialResult": json.loads(item["partial_result_json"]) if item["partial_result_json"] else None,
                    "createdAt": item["created_at"],
                }
                for item in rows
            ],
        }

    def queue_status(self) -> dict[str, Any]:
        with self._db_lock, self._connect() as db:
            rows = db.execute("SELECT status, COUNT(*) AS count FROM jobs GROUP BY status").fetchall()
            oldest = db.execute("SELECT created_at FROM jobs WHERE status IN ('queued','retrying') ORDER BY priority DESC,created_at LIMIT 1").fetchone()
            cache = db.execute("SELECT COUNT(*) AS count,COALESCE(SUM(result_bytes),0) AS bytes,COALESCE(SUM(hit_count),0) AS hits FROM result_cache WHERE expires_at>=?", (time.time(),)).fetchone()
        counts = {state: 0 for state in ALL_STATES}
        for row in rows:
            counts[str(row["status"])] = int(row["count"])
        with self._active_lock:
            active = len(self._active)
        return {
            "schema": "sc-lab-job-queue-status/1.1",
            "version": settings.version,
            "persistent": True,
            "storage": "sqlite-wal",
            "databaseFile": self.db_path.name,
            "counts": counts,
            "activeWorkers": active,
            "workerCapacity": settings.job_workers,
            "availableWorkers": max(0, settings.job_workers - active),
            "oldestQueuedAt": oldest["created_at"] if oldest else None,
            "schedulerStartedAt": self._started_at,
            "lastSchedulerTick": self._last_scheduler_tick,
            "priorityScheduling": True,
            "checkpointRecovery": True,
            "maxActiveJobsPerProject": settings.max_active_jobs_per_project,
            "cache": {"records": int(cache["count"]), "bytes": int(cache["bytes"]), "hits": int(cache["hits"]), "ttlSeconds": settings.result_cache_ttl_seconds},
        }

    def workers_status(self) -> dict[str, Any]:
        with self._active_lock:
            workers = [
                {
                    "workerId": handle.worker_id,
                    "jobId": handle.job_id,
                    "pid": handle.process.pid,
                    "alive": bool(handle.process.is_alive()),
                    "timeoutSeconds": handle.timeout_seconds,
                    "runtimeSeconds": round(time.monotonic() - handle.started_monotonic, 3),
                }
                for handle in self._active.values()
            ]
        return {
            "schema": "sc-lab-worker-health/1.1",
            "version": settings.version,
            "model": "isolated-process-workers",
            "configuredWorkers": settings.job_workers,
            "active": workers,
            "healthy": all(worker["alive"] for worker in workers),
            "checkpointAware": True,
        }

    def cache_status(self) -> dict[str, Any]:
        now = time.time()
        with self._db_lock, self._connect() as db:
            db.execute("DELETE FROM result_cache WHERE expires_at < ?", (now,))
            summary = db.execute("SELECT COUNT(*) AS count,COALESCE(SUM(result_bytes),0) AS bytes,COALESCE(SUM(hit_count),0) AS hits FROM result_cache").fetchone()
            rows = db.execute("SELECT cache_key,method,result_bytes,created_at,expires_at,hit_count,last_hit_at FROM result_cache ORDER BY created_at DESC LIMIT 50").fetchall()
        return {
            "schema": "sc-lab-result-cache-status/1.0",
            "version": settings.version,
            "records": int(summary["count"]),
            "bytes": int(summary["bytes"]),
            "hits": int(summary["hits"]),
            "ttlSeconds": settings.result_cache_ttl_seconds,
            "entries": [
                {
                    "cacheKey": row["cache_key"], "method": row["method"], "resultBytes": int(row["result_bytes"]),
                    "createdAt": row["created_at"], "expiresAtEpoch": float(row["expires_at"]),
                    "hitCount": int(row["hit_count"]), "lastHitAt": row["last_hit_at"],
                }
                for row in rows
            ],
        }

    def purge_cache(self) -> dict[str, Any]:
        with self._db_lock, self._connect() as db:
            count = int(db.execute("SELECT COUNT(*) FROM result_cache").fetchone()[0])
            db.execute("DELETE FROM result_cache")
        return {"ok": True, "purged": count}

    def _scheduler_loop(self) -> None:
        while not self._stop.is_set():
            self._last_scheduler_tick = utc_now()
            try:
                self._reap_workers()
                self._dispatch_workers()
                self._trim_records()
            except Exception:
                # A scheduler exception must not stop future queue processing.
                pass
            self._stop.wait(settings.job_scheduler_interval_seconds)

    def _dispatch_workers(self) -> None:
        while not self._stop.is_set():
            with self._active_lock:
                if len(self._active) >= settings.job_workers:
                    return
            row = self._claim_next()
            if not row:
                return
            self._start_worker(row)

    def _claim_next(self) -> sqlite3.Row | None:
        now_epoch = time.time()
        now_text = utc_now()
        with self._db_lock, self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                """
                SELECT * FROM jobs
                 WHERE status IN ('queued','retrying') AND next_run_at <= ?
                 ORDER BY priority DESC, next_run_at ASC, created_at ASC LIMIT 1
                """,
                (now_epoch,),
            ).fetchone()
            if not row:
                db.execute("COMMIT")
                return None
            worker_id = f"worker-{uuid.uuid4().hex[:12]}"
            message = "Resuming isolated compute worker from checkpoint" if int(row["checkpoint_sequence"]) > 0 else "Starting isolated compute worker"
            db.execute(
                """
                UPDATE jobs SET status='running', attempts=attempts+1,
                       progress=CASE WHEN checkpoint_sequence>0 THEN progress ELSE 5 END,
                       progress_message=?, worker_id=?, started_at=?, updated_at=?, last_heartbeat_at=?, error_json=NULL
                 WHERE id=? AND status IN ('queued','retrying')
                """,
                (message, worker_id, now_text, now_text, now_text, row["id"]),
            )
            db.execute("COMMIT")
            return db.execute("SELECT * FROM jobs WHERE id=?", (row["id"],)).fetchone()

    def _start_worker(self, row: sqlite3.Row) -> None:
        result_queue = self._ctx.Queue(maxsize=128)
        payload = json.loads(row["request_json"])
        auth = json.loads(row["auth_json"])
        checkpoint = json.loads(row["checkpoint_json"]) if row["checkpoint_json"] else None
        process = self._ctx.Process(target=_process_job, args=(payload, auth, checkpoint, result_queue), daemon=True)
        process.start()
        handle = WorkerHandle(
            job_id=str(row["id"]), worker_id=str(row["worker_id"]), process=process,
            result_queue=result_queue, started_monotonic=time.monotonic(), timeout_seconds=int(row["timeout_seconds"]),
        )
        with self._active_lock:
            self._active[handle.job_id] = handle
        with self._db_lock, self._connect() as db:
            db.execute(
                "UPDATE jobs SET worker_pid=?, progress=MAX(progress,10), progress_message=?, updated_at=? WHERE id=?",
                (process.pid, "Compute worker running with checkpoint support", utc_now(), handle.job_id),
            )

    def _reap_workers(self) -> None:
        with self._active_lock:
            handles = list(self._active.values())
        for handle in handles:
            record = self._row(handle.job_id)
            if not record:
                self._remove_active(handle.job_id)
                self._terminate(handle)
                continue
            if int(record["cancel_requested"]):
                self._remove_active(handle.job_id)
                self._terminate(handle)
                self._finish_state(handle.job_id, "cancelled", "Cancelled by request")
                continue
            elapsed = time.monotonic() - handle.started_monotonic
            if elapsed > handle.timeout_seconds:
                self._remove_active(handle.job_id)
                self._terminate(handle)
                self._finish_state(
                    handle.job_id, "timed_out", f"The compute worker exceeded the {handle.timeout_seconds}-second execution limit.",
                    error={"code": "job_timeout", "message": "The isolated worker exceeded its execution limit.", "retryable": True},
                )
                continue

            final_message: dict[str, Any] | None = None
            while True:
                try:
                    message = handle.result_queue.get_nowait()
                except queue.Empty:
                    break
                if message.get("type") == "checkpoint":
                    self._save_checkpoint(
                        handle.job_id,
                        float(message.get("progress") or 0),
                        str(message.get("message") or "Checkpoint created"),
                        message.get("checkpoint") if isinstance(message.get("checkpoint"), dict) else {},
                        message.get("partial") if isinstance(message.get("partial"), dict) else None,
                    )
                elif message.get("type") == "result" or "ok" in message:
                    final_message = message

            if final_message is not None:
                self._remove_active(handle.job_id)
                handle.process.join(timeout=0.5)
                if handle.process.is_alive():
                    self._terminate(handle)
                if final_message.get("ok"):
                    self._complete(handle.job_id, final_message.get("result") or {})
                else:
                    self._handle_failure(handle.job_id, final_message.get("error") or {})
                continue
            if not handle.process.is_alive():
                self._remove_active(handle.job_id)
                handle.process.join(timeout=0.2)
                self._handle_failure(
                    handle.job_id,
                    {"code": "worker_exited_without_result", "message": f"The isolated worker exited with code {handle.process.exitcode} before returning a result.", "retryable": True},
                )
                continue
            with self._db_lock, self._connect() as db:
                db.execute(
                    "UPDATE jobs SET last_heartbeat_at=?,updated_at=?,progress=MAX(progress,25),progress_message=CASE WHEN checkpoint_sequence>0 THEN progress_message ELSE 'Compute worker active' END WHERE id=?",
                    (utc_now(), utc_now(), handle.job_id),
                )

    def _save_checkpoint(self, job_id: str, progress: float, message: str, checkpoint: dict[str, Any], partial: dict[str, Any] | None) -> None:
        checkpoint_text = canonical_json(checkpoint)
        if len(checkpoint_text.encode("utf-8")) > settings.max_checkpoint_bytes:
            return
        partial_text = canonical_json(partial) if partial is not None else None
        now = utc_now()
        with self._db_lock, self._connect() as db:
            row = db.execute("SELECT checkpoint_sequence,started_at FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                return
            sequence = int(row["checkpoint_sequence"]) + 1
            estimated = None
            if row["started_at"] and progress > 0:
                try:
                    started = datetime.fromisoformat(str(row["started_at"])).timestamp()
                    elapsed = max(0.001, time.time() - started)
                    estimated = max(0.0, elapsed * (100.0 - progress) / progress)
                except Exception:
                    estimated = None
            db.execute(
                """
                UPDATE jobs SET progress=?,progress_message=?,checkpoint_json=?,checkpoint_sequence=?,
                       checkpoint_updated_at=?,partial_result_json=COALESCE(?,partial_result_json),estimated_seconds=?,updated_at=?,last_heartbeat_at=?
                 WHERE id=?
                """,
                (progress, message[:512], checkpoint_text, sequence, now, partial_text, estimated, now, now, job_id),
            )
            db.execute(
                "INSERT OR REPLACE INTO job_checkpoints(job_id,sequence,progress,message,checkpoint_json,partial_result_json,created_at) VALUES(?,?,?,?,?,?,?)",
                (job_id, sequence, progress, message[:512], checkpoint_text, partial_text, now),
            )
            old_rows = db.execute(
                "SELECT id FROM job_checkpoints WHERE job_id=? ORDER BY sequence DESC LIMIT -1 OFFSET ?",
                (job_id, settings.checkpoint_retention_per_job),
            ).fetchall()
            if old_rows:
                db.executemany("DELETE FROM job_checkpoints WHERE id=?", [(item["id"],) for item in old_rows])

    def _handle_failure(self, job_id: str, error: dict[str, Any]) -> None:
        row = self._row(job_id)
        if not row:
            return
        retryable = bool(error.get("retryable"))
        attempts = int(row["attempts"])
        max_attempts = int(row["max_attempts"])
        now = utc_now()
        if retryable and attempts < max_attempts:
            delay = min(settings.max_retry_delay_seconds, settings.retry_base_delay_seconds * (2 ** max(0, attempts - 1)))
            with self._db_lock, self._connect() as db:
                db.execute(
                    """
                    UPDATE jobs SET status='retrying',progress=CASE WHEN checkpoint_sequence>0 THEN progress ELSE 0 END,
                           progress_message=?,next_run_at=?,updated_at=?,worker_id=NULL,worker_pid=NULL,error_json=? WHERE id=?
                    """,
                    (
                        f"Retry {attempts + 1} of {max_attempts} scheduled in {delay} seconds; checkpoint preserved" if int(row["checkpoint_sequence"]) else f"Retry {attempts + 1} of {max_attempts} scheduled in {delay} seconds",
                        time.time() + delay, now, canonical_json(error), job_id,
                    ),
                )
            return
        self._finish_state(job_id, "failed", str(error.get("message") or "Compute worker failed."), error=error)

    def _complete(self, job_id: str, result: dict[str, Any]) -> None:
        now = utc_now()
        result_text = canonical_json(result)
        result_bytes = len(result_text.encode("utf-8"))
        with self._db_lock, self._connect() as db:
            row = db.execute("SELECT method,cache_mode,cache_key FROM jobs WHERE id=?", (job_id,)).fetchone()
            db.execute(
                """
                UPDATE jobs SET status='completed',progress=100,progress_message='Completed',result_json=?,
                       result_bytes=?,error_json=NULL,finished_at=?,updated_at=?,worker_id=NULL,worker_pid=NULL,
                       last_heartbeat_at=?,estimated_seconds=0 WHERE id=?
                """,
                (result_text, result_bytes, now, now, now, job_id),
            )
            if row and row["cache_mode"] != "bypass" and row["cache_key"]:
                db.execute(
                    """
                    INSERT INTO result_cache(cache_key,method,result_json,result_bytes,created_at,expires_at,hit_count,last_hit_at)
                    VALUES(?,?,?,?,?,?,0,NULL)
                    ON CONFLICT(cache_key) DO UPDATE SET method=excluded.method,result_json=excluded.result_json,
                        result_bytes=excluded.result_bytes,created_at=excluded.created_at,expires_at=excluded.expires_at
                    """,
                    (row["cache_key"], row["method"], result_text, result_bytes, now, time.time() + settings.result_cache_ttl_seconds),
                )
        self._trim_cache()

    def _finish_state(self, job_id: str, status: str, message: str, error: dict[str, Any] | None = None) -> None:
        now = utc_now()
        with self._db_lock, self._connect() as db:
            db.execute(
                """
                UPDATE jobs SET status=?,progress_message=?,error_json=?,finished_at=?,updated_at=?,
                       worker_id=NULL,worker_pid=NULL,last_heartbeat_at=?,estimated_seconds=NULL WHERE id=?
                """,
                (status, message[:512], canonical_json(error) if error else None, now, now, now, job_id),
            )

    def _row(self, job_id: str) -> sqlite3.Row | None:
        with self._db_lock, self._connect() as db:
            return db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()

    def _remove_active(self, job_id: str) -> WorkerHandle | None:
        with self._active_lock:
            return self._active.pop(job_id, None)

    @staticmethod
    def _terminate(handle: WorkerHandle) -> None:
        try:
            if handle.process.is_alive():
                handle.process.terminate()
                handle.process.join(timeout=1)
            if handle.process.is_alive() and hasattr(handle.process, "kill"):
                handle.process.kill()
                handle.process.join(timeout=1)
        finally:
            try:
                handle.result_queue.close()
            except Exception:
                pass

    def _trim_cache(self) -> None:
        with self._db_lock, self._connect() as db:
            db.execute("DELETE FROM result_cache WHERE expires_at < ?", (time.time(),))
            count = int(db.execute("SELECT COUNT(*) FROM result_cache").fetchone()[0])
            overflow = count - settings.max_cache_records
            if overflow > 0:
                keys = db.execute("SELECT cache_key FROM result_cache ORDER BY COALESCE(last_hit_at,created_at) ASC LIMIT ?", (overflow,)).fetchall()
                db.executemany("DELETE FROM result_cache WHERE cache_key=?", [(row["cache_key"],) for row in keys])

    def _trim_records(self) -> None:
        cutoff = time.time() - settings.job_retention_seconds
        with self._db_lock, self._connect() as db:
            old = db.execute(
                "SELECT id FROM jobs WHERE status IN ('completed','failed','cancelled','timed_out') AND strftime('%s',finished_at) < ?",
                (int(cutoff),),
            ).fetchall()
            if old:
                db.executemany("DELETE FROM job_checkpoints WHERE job_id=?", [(row["id"],) for row in old])
                db.executemany("DELETE FROM jobs WHERE id=?", [(row["id"],) for row in old])
            count = int(db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0])
            overflow = count - settings.max_job_records
            if overflow > 0:
                ids = db.execute(
                    "SELECT id FROM jobs WHERE status IN ('completed','failed','cancelled','timed_out') ORDER BY finished_at ASC LIMIT ?",
                    (overflow,),
                ).fetchall()
                db.executemany("DELETE FROM job_checkpoints WHERE job_id=?", [(row["id"],) for row in ids])
                db.executemany("DELETE FROM jobs WHERE id=?", [(row["id"],) for row in ids])
        self._trim_cache()

    @staticmethod
    def _public(row: sqlite3.Row) -> dict[str, Any]:
        result = json.loads(row["result_json"]) if row["result_json"] else None
        error = json.loads(row["error_json"]) if row["error_json"] else None
        partial = json.loads(row["partial_result_json"]) if row["partial_result_json"] else None
        checkpoint_available = int(row["checkpoint_sequence"]) > 0
        return {
            "schema": "sc-lab-compute-job/1.1",
            "jobId": row["id"], "parentJobId": row["parent_job_id"], "operation": row["operation"],
            "method": row["method"], "status": row["status"], "progress": float(row["progress"]),
            "progressMessage": row["progress_message"], "attempts": int(row["attempts"]),
            "maxAttempts": int(row["max_attempts"]), "manualRetries": int(row["manual_retries"]),
            "timeoutSeconds": int(row["timeout_seconds"]), "projectId": row["project_id"],
            "clientId": row["client_id"], "workerId": row["worker_id"], "workerPid": row["worker_pid"],
            "priority": int(row["priority"]), "cacheMode": row["cache_mode"], "cacheHit": bool(row["cache_hit"]),
            "checkpointAvailable": checkpoint_available, "checkpointSequence": int(row["checkpoint_sequence"]),
            "checkpointUpdatedAt": row["checkpoint_updated_at"], "partialResult": partial,
            "estimatedRemainingSeconds": None if row["estimated_seconds"] is None else round(float(row["estimated_seconds"]), 3),
            "resumedCount": int(row["resumed_count"]), "resultBytes": int(row["result_bytes"]),
            "createdAt": row["created_at"], "updatedAt": row["updated_at"], "startedAt": row["started_at"],
            "finishedAt": row["finished_at"], "lastHeartbeatAt": row["last_heartbeat_at"],
            "result": result, "error": error,
        }


class QueueCapacityError(RuntimeError):
    pass


class ProjectLimitError(RuntimeError):
    pass


class InvalidJobStateError(RuntimeError):
    pass
