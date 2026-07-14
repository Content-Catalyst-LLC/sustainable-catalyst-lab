from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
import os
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
ALL_STATES = RUNNABLE_STATES | TERMINAL_STATES | {"running"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def request_digest(operation: str, payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json({"operation": operation, "payload": payload}).encode("utf-8")).hexdigest()


def _process_job(payload: dict[str, Any], auth: dict[str, str], result_queue: Any) -> None:
    """Execute one registered compute request in an isolated child process."""
    try:
        from .compute import ComputeExecutionError, run_compute
        from .schemas import ComputeRequest

        request = ComputeRequest.model_validate(payload)
        result = run_compute(request, auth)
        result_queue.put({"ok": True, "result": result.model_dump(mode="json", by_alias=True)})
    except Exception as exc:  # child boundary: serialize every failure
        status_code = int(getattr(exc, "status_code", 500))
        retryable = bool(getattr(exc, "retryable", status_code >= 500))
        code = str(getattr(exc, "code", "worker_process_error"))
        result_queue.put(
            {
                "ok": False,
                "error": {
                    "code": code,
                    "message": str(exc),
                    "statusCode": status_code,
                    "retryable": retryable,
                },
            }
        )


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
                    error_json TEXT
                );
                CREATE INDEX IF NOT EXISTS jobs_status_next_idx ON jobs(status, next_run_at, created_at);
                CREATE INDEX IF NOT EXISTS jobs_request_hash_idx ON jobs(request_sha256, status);
                CREATE INDEX IF NOT EXISTS jobs_idempotency_idx ON jobs(idempotency_key, created_at);
                CREATE INDEX IF NOT EXISTS jobs_project_idx ON jobs(project_id, created_at);
                """
            )

    def _recover_interrupted_jobs(self) -> None:
        now = utc_now()
        error = canonical_json(
            {
                "code": "worker_restart_recovery",
                "message": "The compute service restarted before the worker reported completion. The job was returned to the queue.",
                "retryable": True,
            }
        )
        with self._db_lock, self._connect() as db:
            db.execute(
                """
                UPDATE jobs
                   SET status='queued', progress=0, progress_message='Recovered after service restart',
                       worker_id=NULL, worker_pid=NULL, cancel_requested=0, started_at=NULL,
                       updated_at=?, next_run_at=0, error_json=?
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
    ) -> tuple[dict[str, Any], bool]:
        self.start()
        digest = request_digest(operation, payload)
        clean_key = (idempotency_key or "").strip()[:128] or None
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
        auth_record = {"mode": str(auth.get("mode") or "unknown"), "client_id": client_id}

        with self._db_lock, self._connect() as db:
            queued = int(db.execute("SELECT COUNT(*) FROM jobs WHERE status IN ('queued','retrying','running')").fetchone()[0])
            if queued >= settings.max_queued_jobs:
                raise QueueCapacityError("The compute queue is at capacity. Try again after existing jobs finish.")
            db.execute(
                """
                INSERT INTO jobs (
                    id, operation, method, request_json, auth_json, request_sha256, idempotency_key,
                    status, progress, progress_message, attempts, max_attempts, timeout_seconds,
                    project_id, client_id, created_at, updated_at, next_run_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', 0, 'Waiting for an available worker', 0, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    job_id,
                    operation,
                    method,
                    canonical_json(payload),
                    canonical_json(auth_record),
                    digest,
                    clean_key,
                    attempts,
                    timeout,
                    project_id,
                    client_id,
                    now,
                    now,
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
                       AND (status IN ('queued','retrying','running') OR (status='completed' AND strftime('%s', created_at) >= ?))
                     ORDER BY created_at DESC LIMIT 1
                    """,
                    (idempotency_key, int(cutoff)),
                ).fetchone()
                if row:
                    return row
            return db.execute(
                """
                SELECT * FROM jobs
                 WHERE request_sha256=? AND status IN ('queued','retrying','running')
                 ORDER BY created_at DESC LIMIT 1
                """,
                (digest,),
            ).fetchone()

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._db_lock, self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
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

    def retry(self, job_id: str) -> dict[str, Any] | None:
        now = utc_now()
        with self._db_lock, self._connect() as db:
            row = db.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                return None
            if row["status"] not in {"failed", "timed_out", "cancelled"}:
                raise InvalidJobStateError("Only failed, timed-out, or cancelled jobs can be retried manually.")
            db.execute(
                """
                UPDATE jobs SET status='queued', progress=0, progress_message='Queued for manual retry',
                       attempts=0, manual_retries=manual_retries+1, cancel_requested=0,
                       started_at=NULL, finished_at=NULL, worker_id=NULL, worker_pid=NULL,
                       next_run_at=0, updated_at=?, result_json=NULL, error_json=NULL
                 WHERE id=?
                """,
                (now, job_id),
            )
        self.start()
        return self.get(job_id)

    def queue_status(self) -> dict[str, Any]:
        with self._db_lock, self._connect() as db:
            rows = db.execute("SELECT status, COUNT(*) AS count FROM jobs GROUP BY status").fetchall()
            oldest = db.execute("SELECT created_at FROM jobs WHERE status IN ('queued','retrying') ORDER BY created_at LIMIT 1").fetchone()
        counts = {state: 0 for state in ALL_STATES}
        for row in rows:
            counts[str(row["status"])] = int(row["count"])
        with self._active_lock:
            active = len(self._active)
        return {
            "schema": "sc-lab-job-queue-status/1.0",
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
            "schema": "sc-lab-worker-health/1.0",
            "version": settings.version,
            "model": "isolated-process-workers",
            "configuredWorkers": settings.job_workers,
            "active": workers,
            "healthy": all(worker["alive"] for worker in workers),
        }

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
                 ORDER BY created_at ASC LIMIT 1
                """,
                (now_epoch,),
            ).fetchone()
            if not row:
                db.execute("COMMIT")
                return None
            worker_id = f"worker-{uuid.uuid4().hex[:12]}"
            db.execute(
                """
                UPDATE jobs SET status='running', attempts=attempts+1, progress=5,
                       progress_message='Starting isolated compute worker', worker_id=?,
                       started_at=?, updated_at=?, last_heartbeat_at=?, error_json=NULL
                 WHERE id=? AND status IN ('queued','retrying')
                """,
                (worker_id, now_text, now_text, now_text, row["id"]),
            )
            db.execute("COMMIT")
            return db.execute("SELECT * FROM jobs WHERE id=?", (row["id"],)).fetchone()

    def _start_worker(self, row: sqlite3.Row) -> None:
        result_queue = self._ctx.Queue(maxsize=2)
        payload = json.loads(row["request_json"])
        auth = json.loads(row["auth_json"])
        process = self._ctx.Process(target=_process_job, args=(payload, auth, result_queue), daemon=True)
        process.start()
        handle = WorkerHandle(
            job_id=str(row["id"]),
            worker_id=str(row["worker_id"]),
            process=process,
            result_queue=result_queue,
            started_monotonic=time.monotonic(),
            timeout_seconds=int(row["timeout_seconds"]),
        )
        with self._active_lock:
            self._active[handle.job_id] = handle
        with self._db_lock, self._connect() as db:
            db.execute(
                "UPDATE jobs SET worker_pid=?, progress=10, progress_message='Compute worker running', updated_at=? WHERE id=?",
                (process.pid, utc_now(), handle.job_id),
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
                    handle.job_id,
                    "timed_out",
                    f"The compute worker exceeded the {handle.timeout_seconds}-second execution limit.",
                    error={"code": "job_timeout", "message": "The isolated worker exceeded its execution limit.", "retryable": True},
                )
                continue
            try:
                message = handle.result_queue.get_nowait()
            except queue.Empty:
                message = None
            if message is not None:
                self._remove_active(handle.job_id)
                handle.process.join(timeout=0.5)
                if handle.process.is_alive():
                    self._terminate(handle)
                if message.get("ok"):
                    self._complete(handle.job_id, message.get("result") or {})
                else:
                    self._handle_failure(handle.job_id, message.get("error") or {})
                continue
            if not handle.process.is_alive():
                self._remove_active(handle.job_id)
                handle.process.join(timeout=0.2)
                self._handle_failure(
                    handle.job_id,
                    {
                        "code": "worker_exited_without_result",
                        "message": f"The isolated worker exited with code {handle.process.exitcode} before returning a result.",
                        "retryable": True,
                    },
                )
                continue
            with self._db_lock, self._connect() as db:
                db.execute(
                    "UPDATE jobs SET last_heartbeat_at=?, updated_at=?, progress=MAX(progress, 25), progress_message='Compute worker active' WHERE id=?",
                    (utc_now(), utc_now(), handle.job_id),
                )

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
                    UPDATE jobs SET status='retrying', progress=0,
                           progress_message=?, next_run_at=?, updated_at=?, worker_id=NULL,
                           worker_pid=NULL, error_json=? WHERE id=?
                    """,
                    (
                        f"Retry {attempts + 1} of {max_attempts} scheduled in {delay} seconds",
                        time.time() + delay,
                        now,
                        canonical_json(error),
                        job_id,
                    ),
                )
            return
        self._finish_state(job_id, "failed", str(error.get("message") or "Compute worker failed."), error=error)

    def _complete(self, job_id: str, result: dict[str, Any]) -> None:
        now = utc_now()
        with self._db_lock, self._connect() as db:
            db.execute(
                """
                UPDATE jobs SET status='completed', progress=100, progress_message='Completed',
                       result_json=?, error_json=NULL, finished_at=?, updated_at=?,
                       worker_id=NULL, worker_pid=NULL, last_heartbeat_at=? WHERE id=?
                """,
                (canonical_json(result), now, now, now, job_id),
            )

    def _finish_state(self, job_id: str, status: str, message: str, error: dict[str, Any] | None = None) -> None:
        now = utc_now()
        with self._db_lock, self._connect() as db:
            db.execute(
                """
                UPDATE jobs SET status=?, progress_message=?, error_json=?, finished_at=?,
                       updated_at=?, worker_id=NULL, worker_pid=NULL, last_heartbeat_at=? WHERE id=?
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

    def _trim_records(self) -> None:
        cutoff = time.time() - settings.job_retention_seconds
        with self._db_lock, self._connect() as db:
            db.execute(
                "DELETE FROM jobs WHERE status IN ('completed','failed','cancelled','timed_out') AND strftime('%s', finished_at) < ?",
                (int(cutoff),),
            )
            count = int(db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0])
            overflow = count - settings.max_job_records
            if overflow > 0:
                ids = db.execute(
                    "SELECT id FROM jobs WHERE status IN ('completed','failed','cancelled','timed_out') ORDER BY finished_at ASC LIMIT ?",
                    (overflow,),
                ).fetchall()
                db.executemany("DELETE FROM jobs WHERE id=?", [(row["id"],) for row in ids])

    @staticmethod
    def _public(row: sqlite3.Row) -> dict[str, Any]:
        result = json.loads(row["result_json"]) if row["result_json"] else None
        error = json.loads(row["error_json"]) if row["error_json"] else None
        return {
            "schema": "sc-lab-compute-job/1.0",
            "jobId": row["id"],
            "parentJobId": row["parent_job_id"],
            "operation": row["operation"],
            "method": row["method"],
            "status": row["status"],
            "progress": float(row["progress"]),
            "progressMessage": row["progress_message"],
            "attempts": int(row["attempts"]),
            "maxAttempts": int(row["max_attempts"]),
            "manualRetries": int(row["manual_retries"]),
            "timeoutSeconds": int(row["timeout_seconds"]),
            "projectId": row["project_id"],
            "clientId": row["client_id"],
            "workerId": row["worker_id"],
            "workerPid": row["worker_pid"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "startedAt": row["started_at"],
            "finishedAt": row["finished_at"],
            "lastHeartbeatAt": row["last_heartbeat_at"],
            "result": result,
            "error": error,
        }


class QueueCapacityError(RuntimeError):
    pass


class InvalidJobStateError(RuntimeError):
    pass

