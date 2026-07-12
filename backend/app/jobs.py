from __future__ import annotations

import os
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from .tasks import perform

try:
    from redis import Redis
    from rq import Queue
    from rq.job import Job
except ImportError:  # Local development can use the in-memory fallback.
    Redis = None  # type: ignore[assignment]
    Queue = None  # type: ignore[assignment]
    Job = None  # type: ignore[assignment]


class JobManager:
    def __init__(self) -> None:
        self.redis_url = os.getenv("REDIS_URL", "").strip()
        self.queue_name = os.getenv("SC_LAB_QUEUE_NAME", "sc-lab-compute")
        self._executor = ThreadPoolExecutor(max_workers=max(1, min(4, int(os.getenv("SC_LAB_LOCAL_WORKERS", "2")))))
        self._records: dict[str, dict[str, Any]] = {}
        self._futures: dict[str, Future[Any]] = {}
        self._lock = threading.Lock()
        self._queue = None
        self._connection = None
        if self.redis_url and Redis is not None and Queue is not None:
            try:
                self._connection = Redis.from_url(self.redis_url)
                self._connection.ping()
                self._queue = Queue(self.queue_name, connection=self._connection, default_timeout=90)
            except Exception:
                self._queue = None
                self._connection = None

    @property
    def mode(self) -> str:
        return "redis-rq" if self._queue is not None else "in-memory"

    def submit(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self._queue is not None:
            job = self._queue.enqueue(
                "app.tasks.perform",
                operation,
                payload,
                job_timeout=max(30, int(payload.get("timeoutSeconds", 8)) + 25),
                result_ttl=3600,
                failure_ttl=3600,
            )
            return {"jobId": job.id, "status": "queued", "queueMode": self.mode, "submittedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

        job_id = uuid.uuid4().hex
        record = {
            "jobId": job_id,
            "operation": operation,
            "status": "queued",
            "queueMode": self.mode,
            "submittedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "result": None,
            "error": None,
        }
        with self._lock:
            self._records[job_id] = record
        future = self._executor.submit(self._perform_local, job_id, operation, payload)
        with self._lock:
            self._futures[job_id] = future
        return {key: record[key] for key in ("jobId", "status", "queueMode", "submittedAt")}

    def _perform_local(self, job_id: str, operation: str, payload: dict[str, Any]) -> None:
        with self._lock:
            if self._records[job_id]["status"] == "cancelled":
                return
            self._records[job_id]["status"] = "running"
            self._records[job_id]["startedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            result = perform(operation, payload)
        except Exception as exc:  # The API converts this stored error to a structured response.
            with self._lock:
                self._records[job_id]["status"] = "failed"
                self._records[job_id]["error"] = {"type": type(exc).__name__, "message": str(exc)}
                self._records[job_id]["finishedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            return
        with self._lock:
            self._records[job_id]["status"] = "finished"
            self._records[job_id]["result"] = result
            self._records[job_id]["finishedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def status(self, job_id: str) -> dict[str, Any] | None:
        if self._queue is not None and self._connection is not None and Job is not None:
            try:
                job = Job.fetch(job_id, connection=self._connection)
            except Exception:
                return None
            status = job.get_status(refresh=True)
            response: dict[str, Any] = {
                "jobId": job.id,
                "status": status,
                "queueMode": self.mode,
                "submittedAt": job.enqueued_at.isoformat() if job.enqueued_at else None,
                "startedAt": job.started_at.isoformat() if job.started_at else None,
                "finishedAt": job.ended_at.isoformat() if job.ended_at else None,
            }
            if job.is_finished:
                response["result"] = job.result
            if job.is_failed:
                response["error"] = {"message": job.exc_info[-4000:] if job.exc_info else "Worker failure"}
            return response
        with self._lock:
            record = self._records.get(job_id)
            return dict(record) if record else None

    def cancel(self, job_id: str) -> dict[str, Any] | None:
        if self._queue is not None and self._connection is not None and Job is not None:
            try:
                job = Job.fetch(job_id, connection=self._connection)
            except Exception:
                return None
            job.cancel()
            return {"jobId": job_id, "status": "cancelled", "queueMode": self.mode}
        with self._lock:
            record = self._records.get(job_id)
            if record is None:
                return None
            future = self._futures.get(job_id)
            cancelled = future.cancel() if future else False
            if record["status"] in {"queued", "running"}:
                record["status"] = "cancelled" if cancelled or record["status"] == "queued" else "cancellation_requested"
            return dict(record)


jobs = JobManager()
