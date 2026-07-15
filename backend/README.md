# Sustainable Catalyst Lab Python Compute Core v0.27.2

The v0.27.2 service is the governed numerical-compute, validation, and long-running job plane for Sustainable Catalyst Lab. It preserves the 23-method registry, fourteen known-answer benchmarks, isolated worker processes, HMAC authentication, and the v0.27.1 benchmark library while adding persistent checkpoints, resumable execution, partial-result inspection, queue priorities, result caching, and project-level compute limits.

## Governed numerical capabilities

- Root finding, quadrature, interpolation, and first-order ODE integration
- Eigen analysis and constrained optimization
- FFT signal spectra
- Seeded Monte Carlo and bootstrap uncertainty analysis
- Local sensitivity analysis and registered parameter sweeps
- Fourteen known-answer validation benchmarks
- Checkpointed parameter sweeps and bootstrap runs

All methods are allowlisted and schema-constrained. The public API does not execute arbitrary Python code. Every result includes reproducibility provenance.

## Local start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload
```

Open `/health`, `/docs`, `/v1/capabilities`, `/v1/queue/status`, `/v1/workers`, and `/v1/cache/status`.

## Persistent queue and checkpoints

Version 0.27.2 stores jobs, checkpoint history, partial results, and result-cache metadata in SQLite WAL mode. Configure the database with `SC_LAB_JOB_DB_PATH`. Place that file on host-provided persistent storage when jobs must survive host replacement or redeployment.

Supported states are `queued`, `running`, `paused`, `completed`, `failed`, `cancelled`, `timed_out`, and `retrying`. Interrupted checkpointable jobs are returned to the queue when the same database is reopened.

Checkpointable methods in this release:

- `simulation.parameter_sweep`
- `uncertainty.bootstrap_mean_interval`

## Long-job controls

```text
POST   /v1/jobs
GET    /v1/jobs
GET    /v1/jobs/{job_id}
DELETE /v1/jobs/{job_id}
POST   /v1/jobs/{job_id}/cancel
POST   /v1/jobs/{job_id}/pause
POST   /v1/jobs/{job_id}/resume
POST   /v1/jobs/{job_id}/retry
GET    /v1/jobs/{job_id}/checkpoints
GET    /v1/queue/status
GET    /v1/workers
GET    /v1/cache/status
DELETE /v1/cache
```

Job submissions accept `priority` from 0 to 100 and `cacheMode` values `use`, `refresh`, or `bypass`. The queue enforces `SC_LAB_MAX_ACTIVE_JOBS_PER_PROJECT`.

## Authentication

Production supports HMAC-SHA256 request signing with `SC_LAB_COMPUTE_SIGNING_SECRET`. Legacy API-key authentication remains available through `SC_LAB_COMPUTE_API_KEY`. When neither value is configured, the service uses open development mode and must not be exposed publicly.

## Extension preservation

Recovered domain routers from prior Lab releases are discovered at startup. Import failures are isolated and reported in `/health` rather than preventing the core service from starting.

## Benchmark API

Use `/v1/benchmarks`, `/v1/benchmarks/run`, `/v1/benchmarks/run-suite`, and `/v1/benchmarks/convergence` with the same HMAC or API-key authentication used by compute requests.
