# Sustainable Catalyst Lab Python Compute Core v0.31.3

The v0.31.3 service is the governed scientific-compute plane for Sustainable Catalyst Lab. It preserves the 23-method registry, fourteen known-answer benchmarks, persistent SQLite WAL queue, checkpoints, retries, cache, and thirteen domain extensions while adding numerical precision profiles and solver governance.

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

## Secure worker agents and artifact transport v0.31.3

The backend bundle includes an installable pull-based worker runtime in `worker_agent/`. Workers enroll through `POST /v1/worker-agent/enroll`, receive a worker-scoped credential once, poll for compatible leases, verify each signed contract locally, execute only methods registered in `app.registry`, renew active leases, and submit execution receipts with result hashes and provenance.

Coordinator settings:

```bash
SC_LAB_DISPATCHER_DB_PATH=/app/data/sc-lab-dispatcher.sqlite3
SC_LAB_DISPATCHER_CONTRACT_SECRET=<long-random-contract-secret>
SC_LAB_WORKER_ENROLLMENT_TOKEN=<long-random-enrollment-token>
SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED=0
```

Worker settings are documented in `examples/worker-agent/sc-lab-worker-agent.env.example`.

```bash
cd backend
python3 -m worker_agent --validate-config
python3 -m worker_agent
```

`SC_LAB_DISPATCHER_PERSISTENT_DISK_MOUNTED=0` keeps the default Render blueprint free of a paid disk declaration. Queue data is then instance-local. Mount a persistent disk at `/app/data` and set the value to `1` only when durable cross-deploy storage is available.


## Distributed artifact transport v0.31.3

The compute core now stores governed input, result, checkpoint, log, report, dataset, and provenance artifacts in a content-addressed transport layer. Uploads use bounded sequential chunks, resumable offsets, per-chunk checksums, final SHA-256 verification, deduplication, quarantine, ranged reads, manifests, audit events, and retention cleanup.

Coordinator settings:

```bash
SC_LAB_ARTIFACT_ROOT=/app/data/artifacts
SC_LAB_ARTIFACT_DB_PATH=/app/data/sc-lab-artifacts.sqlite3
SC_LAB_ARTIFACT_MAX_BYTES=268435456
SC_LAB_ARTIFACT_CHUNK_BYTES=1048576
SC_LAB_ARTIFACT_UPLOAD_TTL_SECONDS=86400
SC_LAB_ARTIFACT_RETENTION_SECONDS=2592000
SC_LAB_ARTIFACT_PERSISTENT_DISK_MOUNTED=0
```

Workers upload large results automatically when the encoded result exceeds `SC_LAB_WORKER_RESULT_ARTIFACT_THRESHOLD_BYTES`. Artifact inputs listed in a dispatch workload are downloadable only while the worker owns the active lease.
