# Sustainable Catalyst Lab Python Compute Core v0.27.0

The v0.27.0 service is the governed numerical-compute plane for Sustainable Catalyst Lab. It preserves the persistent SQLite job queue and isolated worker processes from v0.26.1 while adding twelve registered scientific numerical methods.

## Numerical capabilities

- Root finding and adaptive quadrature
- Interpolation and first-order ODE integration
- Eigen analysis and constrained optimization
- FFT signal spectra
- Seeded Monte Carlo and bootstrap uncertainty analysis
- Local sensitivity analysis and registered parameter sweeps

All methods are allowlisted and schema-constrained. The public API does not execute arbitrary Python code. Every result includes reproducibility provenance.

This FastAPI service is the governed scientific compute plane for Sustainable Catalyst Lab. It accepts registered methods only and does not expose arbitrary `eval` or `exec` endpoints.

## Local start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload
```

Open `/health`, `/docs`, `/v1/capabilities`, `/v1/queue/status`, and `/v1/workers`.

## Persistent queue

Version 0.27.0 stores job records in SQLite WAL mode and executes each calculation in an isolated child process. Configure the database with `SC_LAB_JOB_DB_PATH`. Place that file on host-provided persistent storage when jobs must survive host replacement or redeployment.

Supported states are `queued`, `running`, `completed`, `failed`, `cancelled`, `timed_out`, and `retrying`. Running jobs left behind by an interrupted API process are returned to the queue when the same database is reopened.

## Authentication

Production supports HMAC-SHA256 request signing with `SC_LAB_COMPUTE_SIGNING_SECRET`. Legacy API-key authentication remains available through `SC_LAB_COMPUTE_API_KEY`. When neither value is configured, the service uses open development mode and must not be exposed publicly.

## Queue endpoints

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

## Extension preservation

Recovered domain routers from prior Lab releases are discovered at startup. Import failures are isolated and reported in `/health` rather than preventing the core service from starting.
