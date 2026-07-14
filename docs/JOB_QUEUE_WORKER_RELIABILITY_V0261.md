# Sustainable Catalyst Lab v0.26.1 — Job Queue and Worker Reliability

Version 0.26.1 replaces the v0.26.0 in-memory thread pool with a persistent, inspectable compute queue built from Python's standard-library SQLite and multiprocessing facilities.

## Reliability model

- Job records are stored in SQLite using WAL mode.
- Each running calculation executes in an isolated child process.
- Cancellation and timeout handling terminate the child process without stopping FastAPI.
- Jobs left in `running` state after an API restart are returned to `queued` state when the same database is reopened.
- Retryable infrastructure failures use bounded exponential backoff.
- Idempotency keys and active-request hashes prevent duplicate queue submissions.
- Queue, worker, progress, attempts, error, and provenance records are available through versioned endpoints.

## Job states

`queued`, `running`, `completed`, `failed`, `cancelled`, `timed_out`, and `retrying`.

## API

```text
POST   /v1/jobs
GET    /v1/jobs
GET    /v1/jobs/{job_id}
DELETE /v1/jobs/{job_id}
POST   /v1/jobs/{job_id}/cancel
POST   /v1/jobs/{job_id}/retry
GET    /v1/queue/status
GET    /v1/workers
```

The WordPress control plane exposes corresponding same-origin routes under `/wp-json/sc-lab/v1/compute/` and keeps backend credentials server-side.

## Storage boundary

The default database is `./data/sc-lab-compute-jobs.sqlite3`. For recovery across host replacement or redeployment, configure `SC_LAB_JOB_DB_PATH` on storage that persists for the lifetime required by the project. Without persistent host storage, the queue remains restart-safe only while the database file survives.

## Execution boundary

The queue accepts registered methods only. It does not expose arbitrary Python execution. The diagnostic method `system.controlled_delay` is bounded to ten seconds and exists to validate cancellation, timeout, and worker-health behavior.
