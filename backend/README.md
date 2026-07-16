# Sustainable Catalyst Lab Python Compute Core v0.28.2

The v0.27.3 service is the governed scientific-compute plane for Sustainable Catalyst Lab. It preserves the 23-method registry, fourteen known-answer benchmarks, persistent SQLite WAL queue, checkpoints, retries, cache, and thirteen domain extensions while adding numerical precision profiles and solver governance.

## Solver governance

Every compute request may include a `governance` object with:

- `precisionProfile`: `fast`, `balanced`, `strict`, or `diagnostic`
- `solverPolicy`: `automatic`, `recommended`, or `manual`
- `requestedSolver`: a registered solver for the selected method
- absolute and relative tolerances
- unit policy: `off`, `warn`, or `strict`
- condition-number threshold and ill-conditioned-system policy
- uncertainty standard
- optional reference-method comparison

The response records effective tolerances, solver recommendation and selection, IEEE-754 binary64 characteristics, unit validation, convergence and conditioning diagnostics, warnings, and any reference comparison in both the result and provenance.

## Endpoints

- `GET /health`
- `GET /v1/capabilities`
- `GET /v1/methods`
- `POST /v1/compute/run`
- `GET /v1/governance/health`
- `GET /v1/governance/policies`
- `POST /v1/governance/recommend`
- `POST /v1/governance/compare`
- persistent jobs, checkpoints, cache, workers, and benchmark endpoints from v0.27.2

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

The public service never evaluates arbitrary Python. Only registered methods and registered solver families are accepted.


## Scientific visualization v0.27.4

The backend exposes `/v1/visualization/health`, `/v1/visualization/profiles`, `/v1/visualization/spec`, and `/v1/visualization/csv`. These endpoints return bounded, registered visualization specifications; they do not evaluate arbitrary plotting code.
