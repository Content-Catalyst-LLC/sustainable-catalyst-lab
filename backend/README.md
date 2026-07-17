# Sustainable Catalyst Lab Python Compute Core v0.34.0

The v0.34.0 service is the governed scientific-compute plane for Sustainable Catalyst Lab. It preserves registered methods, benchmark validation, persistent jobs, distributed dispatch, secure workers, artifact transport, dead-letter operations, checkpoint-aware workflows, workflow automation, adaptive campaigns, and closed-loop research while adding immutable scientific model registration and reproducible environment governance.

## v0.34.0 scientific model registry

- Register immutable semantic model versions backed by SHA-256 identity hashes.
- Capture runtime, system, architecture, container, dependency, source-revision, and build environments.
- Deduplicate scientifically identical environments using stable lock hashes.
- Promote versions through candidate, production, and archive channels.
- Deprecate versions with required reasons and retained event history.
- Generate and verify portable reproduction manifests.
- Compare environments for dependency, runtime, system, and container drift.
- Persist records in SQLite WAL storage with explicit deployment-durability reporting.

## v0.33.2 closed-loop campaigns

The service now coordinates simulation, instrument, and hybrid campaign cycles through typed command and measurement envelopes. It enforces safety ranges, maximum setpoint deltas, emergency-stop signals, operator approval, canonical hashing, optional HMAC measurement signatures, and durable loop timelines. The coordinator does not execute arbitrary device instructions or outbound callbacks.

## v0.33.1 Bayesian optimization and active learning

Campaigns can fit Gaussian-process surrogates, preview deterministic candidate proposals, choose expected-improvement, probability-improvement, confidence-bound, or maximum-variance acquisitions, and adjust scientific value by estimated resource cost. Existing v0.33.0 deterministic random, grid, and explore/exploit strategies remain available.

## v0.33.0 adaptive experiment campaigns

Experiment campaigns are durable, workflow-backed sequences of scientific trials. A campaign declares a typed parameter space, binds each parameter to a workflow input path, selects a proposal policy, declares an objective result path and goal, and applies explicit trial, failure, concurrency, patience, target, and improvement controls.

Supported proposal policies are:

- `random` for seeded exploratory sampling
- `grid` for deterministic enumeration of bounded parameter domains
- `adaptive-explore-exploit` for seeded exploration followed by best-neighborhood exploitation

Each proposed parameter set receives a canonical fingerprint so duplicate designs are not launched. Every trial creates an immutable workflow run carrying campaign, trial, sequence, proposal, and parameter provenance. Completed workflow results are reconciled into objective observations, best-known designs, stopping decisions, and a durable campaign timeline. Operators may pause, resume, cancel, advance, reconcile, or add a manual observation without bypassing provenance.

The campaign store uses SQLite WAL at `SC_LAB_EXPERIMENT_CAMPAIGN_DB_PATH`. Set `SC_LAB_EXPERIMENT_CAMPAIGN_PERSISTENT_DISK_MOUNTED=1` only when that path is actually backed by durable storage.

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

- `GET /v1/experiment-campaigns/health`
- `GET /v1/experiment-campaigns/policies`
- `POST /v1/experiment-campaigns/validate`
- `POST /v1/experiment-campaigns`
- `GET /v1/experiment-campaigns`
- `GET /v1/experiment-campaigns/{campaignId}`
- `POST /v1/experiment-campaigns/{campaignId}/start`
- `POST /v1/experiment-campaigns/{campaignId}/pause`
- `POST /v1/experiment-campaigns/{campaignId}/resume`
- `POST /v1/experiment-campaigns/{campaignId}/advance`
- `POST /v1/experiment-campaigns/{campaignId}/reconcile`
- `POST /v1/experiment-campaigns/{campaignId}/cancel`
- `POST /v1/experiment-campaigns/{campaignId}/observations`
- `GET /v1/experiment-campaigns/{campaignId}/trials`
- `GET /v1/experiment-campaigns/{campaignId}/timeline`
- `POST /v1/experiment-campaigns/tick`

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


## Dispatcher operations and dead-letter recovery v0.31.4

The persistent dispatcher now classifies failures, applies bounded exponential retry delays, and moves non-retryable or attempt-exhausted work into a durable dead-letter state. Administrator routes provide queue inspection, combined event timelines, single and bulk replay, cancellation, metrics, recovery, and SQLite diagnostics.

```bash
SC_LAB_DISPATCHER_RETRY_BASE_DELAY_SECONDS=15
SC_LAB_DISPATCHER_RETRY_MAX_DELAY_SECONDS=900
```

Backend operations routes require the compute API key. WordPress recovery and operator routes require an authenticated administrator with `manage_options`. Dead-letter replay preserves the earlier failure and operator history instead of deleting it.

## Scientific workflow orchestration v0.32.0

The compute core stores validated workflow definitions and immutable run snapshots in SQLite WAL storage. A workflow is a directed acyclic graph of registered methods. Independent nodes enter the persistent dispatcher together, while dependent nodes are scheduled only after every upstream dependency completes successfully.

Workflow nodes can bind selected upstream result paths into downstream request paths. Artifact identifiers found in completed dependency results are also propagated as lease-governed artifact inputs. The orchestrator does not evaluate arbitrary code or call arbitrary callback URLs.

Coordinator settings:

```bash
SC_LAB_WORKFLOW_DB_PATH=/app/data/sc-lab-workflows.sqlite3
SC_LAB_WORKFLOW_MAX_NODES=100
SC_LAB_WORKFLOW_MAX_RUNS=5000
SC_LAB_WORKFLOW_HISTORY_LIMIT=20000
SC_LAB_WORKFLOW_PERSISTENT_DISK_MOUNTED=0
```

Core routes include workflow validation and saving, definition listing, run creation, run reconciliation, cancellation, timelines, policies, and health. WordPress workflow creation and operator actions require `manage_options`.



## Workflow checkpoints and partial recovery v0.32.1

Workflow nodes may declare bounded, non-executable conditions over `run.inputs`, `run.context`, or earlier `nodes.<id>` state and results. Conditions use an allowlisted expression tree (`all`, `any`, `not`) and registered comparison operators; arbitrary code is never evaluated.

The workflow registry stores checkpoint history separately from final results. Checkpoints may be captured from dispatcher results or recorded by an authenticated operator. Recovery creates a new run with immutable lineage: successful nodes are reused, failed or selected nodes are restarted, downstream dependents are included by default, and eligible checkpoints are passed to the resumed workload.

Additional routes provide recovery planning, recovery-run creation, single-node branch restart, and checkpoint listing/recording. WordPress mutations remain restricted to administrators with `manage_options`.

## Scheduled and event-driven research runs v0.32.2

The workflow automation service stores interval, UTC cron, one-time, and event trigger definitions in a separate SQLite WAL database. It preserves next-fire timestamps across restarts, records every started or skipped firing, links automation to workflow-run provenance, and reconciles firing status with the workflow orchestrator.

```bash
SC_LAB_WORKFLOW_SCHEDULE_DB_PATH=/app/data/sc-lab-workflow-schedules.sqlite3
SC_LAB_WORKFLOW_SCHEDULER_POLL_SECONDS=30
SC_LAB_WORKFLOW_SCHEDULER_MAX_CATCH_UP_RUNS=10
SC_LAB_WORKFLOW_SCHEDULER_HISTORY_LIMIT=20000
SC_LAB_WORKFLOW_EVENT_SECRET=<optional-separate-hmac-secret>
SC_LAB_WORKFLOW_EVENT_SIGNATURE_TOLERANCE_SECONDS=300
SC_LAB_WORKFLOW_SCHEDULE_PERSISTENT_DISK_MOUNTED=0
```

Cron expressions contain five fields and are evaluated in UTC. Event ingestion always requires normal compute authentication. When `SC_LAB_WORKFLOW_EVENT_SECRET` is configured, events must additionally include `X-SC-Lab-Event-Timestamp` and `X-SC-Lab-Event-Signature`, where the signature is HMAC-SHA256 over `<timestamp>.<canonical-json-payload>`. Arbitrary callbacks and executable trigger expressions are not accepted.

