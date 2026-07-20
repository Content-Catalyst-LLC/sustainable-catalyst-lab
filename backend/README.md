# Sustainable Catalyst Lab Python Compute Core

**Current release: v0.39.0 — Institutional Administration, Identity, and Governance**

The v0.39.0 service adds the institutional identity and governance control plane while retaining the complete v0.38.2 public integration and scientific-compute stack. It records authority and governance decisions but does not issue credentials, store service-account secrets, or perform SSO token exchange.

## Institutional governance configuration

```text
SC_LAB_INSTITUTIONAL_GOVERNANCE_DB_PATH=/app/data/sc-lab-institutional-governance.sqlite3
SC_LAB_INSTITUTIONAL_GOVERNANCE_MAX_INSTITUTIONS=5000
SC_LAB_INSTITUTIONAL_GOVERNANCE_MAX_PRINCIPALS=250000
SC_LAB_INSTITUTIONAL_GOVERNANCE_HISTORY_LIMIT=250000
SC_LAB_INSTITUTIONAL_GOVERNANCE_PERSISTENT_DISK_MOUNTED=1
```

Key authenticated endpoints begin at `/v1/institutional-governance`, `/v1/institutions`, and `/v1/team-workspaces/{workspaceId}/institutional-governance`.

## Prior release: v0.38.2

# Sustainable Catalyst Python Compute Core

**Current release: v0.38.2 — Public API, Webhooks, Embeds, and Research SDK**


The v0.38.2 service exposes the governed interoperability stack through a stable `/v1` catalog, scoped integration authentication, SSRF-resistant signed webhooks, expiring reference-only embeds, and Python, TypeScript, and browser SDK packages. Outbound webhook delivery is disabled by default and must be explicitly enabled.

## Public research integration configuration

```text
SC_LAB_PUBLIC_INTEGRATION_DB_PATH=/app/data/sc-lab-public-research-integrations.sqlite3
SC_LAB_PUBLIC_API_KEY=<strong-random-key>
SC_LAB_PUBLIC_API_SCOPES=research:read,research:write,webhooks:read,webhooks:write,webhooks:emit,embeds:write
SC_LAB_WEBHOOK_SIGNING_SECRET=<strong-random-secret>
SC_LAB_WEBHOOK_DELIVERY_ENABLED=0
SC_LAB_PUBLIC_INTEGRATION_PERSISTENT_DISK_MOUNTED=1
```

The v0.38.1 service adds executable typed product adapters and deterministic route planning over the v0.38.0 governed interoperability engine. The v0.38.0 service preserves the full governed scientific-compute, collaboration, federation, publication, and verification stack while adding typed cross-product research exchange. Interoperability is envelope-driven and hash-verified; the coordinator does not execute submitted code or call arbitrary remote endpoints.

## Research interoperability configuration

```text
SC_LAB_INTEROPERABILITY_DB_PATH=/app/data/sc-lab-research-interoperability.sqlite3
SC_LAB_INTEROPERABILITY_RECEIPT_SECRET=
SC_LAB_INTEROPERABILITY_MAX_PROFILES=5000
SC_LAB_INTEROPERABILITY_MAX_HANDOFFS=250000
SC_LAB_INTEROPERABILITY_PERSISTENT_DISK_MOUNTED=0
```

Key authenticated endpoints begin at `/v1/research-interoperability` and `/v1/team-workspaces/{workspaceId}/research-handoffs`.

The v0.37.1 service preserves the complete governed scientific-compute, federation, collaboration, reproducibility, and publication stack while adding structured research-document assembly. It creates safe document outputs and output-only notebooks; it does not execute manuscript content or notebook code.

## Manuscript assembly configuration

```text
SC_LAB_MANUSCRIPT_ASSEMBLY_DB_PATH=/app/data/sc-lab-manuscript-assembly.sqlite3
SC_LAB_MANUSCRIPT_ASSEMBLY_MAX_ASSEMBLIES=5000
SC_LAB_MANUSCRIPT_ASSEMBLY_MAX_SECTIONS=20000
SC_LAB_MANUSCRIPT_ASSEMBLY_MAX_SECTIONS_PER_ASSEMBLY=500
SC_LAB_MANUSCRIPT_ASSEMBLY_PERSISTENT_DISK_MOUNTED=0
```

# Sustainable Catalyst Lab Python Compute Core

**Current release: v0.37.0 — Reproducibility Packages and Research Publication Studio**

The v0.37.0 service is the governed scientific-compute plane for Sustainable Catalyst Lab. It preserves registered methods, benchmark validation, persistent jobs, distributed dispatch, secure workers, artifact transport, dead-letter operations, checkpoint-aware workflows, workflow automation, adaptive campaigns, and closed-loop research while extending the scientific model registry with immutable registered-model ensembles, dispatcher-backed uncertainty studies, and global sensitivity analysis.



## Reproducibility Packages and Research Publication Studio — v0.37.0

The compute service now stores workspace-governed reproducibility packages, seals canonical manifests, verifies package integrity, renders Markdown/HTML/JSON/CITATION.cff outputs, and publishes only after a signed v0.35.1 scientific approval is verified. Package records contain references and hashes rather than executable code or restricted data bytes.

Key settings:

```text
SC_LAB_PUBLICATION_STUDIO_DB_PATH=/app/data/sc-lab-publication-studio.sqlite3
SC_LAB_PUBLICATION_STUDIO_MAX_PACKAGES=5000
SC_LAB_PUBLICATION_STUDIO_MAX_PUBLICATIONS=5000
SC_LAB_PUBLICATION_STUDIO_MAX_RESOURCES=1000
SC_LAB_PUBLICATION_STUDIO_PERSISTENT_DISK_MOUNTED=0
```

Key endpoints:

- `GET /v1/publication-studio/health`
- `GET /v1/publication-studio/policies`
- `GET|POST /v1/team-workspaces/{workspaceId}/reproducibility-packages`
- `GET|PATCH /v1/team-workspaces/{workspaceId}/reproducibility-packages/{packageId}`
- `POST /v1/team-workspaces/{workspaceId}/reproducibility-packages/{packageId}/seal`
- `POST /v1/team-workspaces/{workspaceId}/reproducibility-packages/{packageId}/verify`
- `GET|POST /v1/team-workspaces/{workspaceId}/research-publications`
- `POST /v1/team-workspaces/{workspaceId}/research-publications/{publicationId}/render`
- `POST /v1/team-workspaces/{workspaceId}/research-publications/{publicationId}/ready`
- `POST /v1/team-workspaces/{workspaceId}/research-publications/{publicationId}/publish`

## Offline Field Research and Edge Synchronization — v0.36.2

- Sealed offline work packages with protocols, forms, registered methods, hashes, and references.
- One-time edge-device credentials and workspace-governed enrollment.
- Signed resumable synchronization, cursor-based delta exchange, duplicate suppression, and conflict-safe reconciliation.
- Restricted institutional data bytes remain outside field packages and browser controls.

## Institutional Node Federation and Local-Data Execution — v0.36.1

The coordinator now registers workspace-governed institutional compute nodes and metadata-only local data assets. Research teams can issue HMAC-signed execution envelopes for registered Lab methods while confidential and restricted data stays inside the institutional boundary. Nodes claim work with a node credential and return a signed attestation containing result, data-access, and environment hashes plus a policy-approved summary. The coordinator does not execute submitted code or call arbitrary node endpoints.

Key settings:

```text
SC_LAB_INSTITUTIONAL_NODE_DB_PATH=/app/data/sc-lab-institutional-nodes.sqlite3
SC_LAB_INSTITUTIONAL_NODE_COORDINATOR_SECRET=<generated secret>
SC_LAB_INSTITUTIONAL_NODE_PERSISTENT_DISK_MOUNTED=0
SC_LAB_EDGE_SYNC_DB_PATH=/app/data/sc-lab-edge-sync.sqlite3
SC_LAB_EDGE_SYNC_PERSISTENT_DISK_MOUNTED=0
```


## v0.34.1 ensemble simulation and uncertainty

The compute core now stores immutable ensemble studies that reference registered-method model versions, generates governed sampling designs, dispatches sample/member evaluations, reconciles numeric results, and computes weighted uncertainty and global-sensitivity summaries. Study records use SQLite WAL and preserve model, environment, dispatcher, sample, result, and analysis hashes.

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


## v0.34.2 surrogate and reduced-order service

The compute core exposes authenticated `/v1/surrogate-rom/*` routes for immutable surrogate training, POD/SVD reduced-order analysis, prediction or state reconstruction, Scientific Model Registry publication, and audit timelines. Configure `SC_LAB_SURROGATE_ROM_DB_PATH` for the SQLite WAL store. Set `SC_LAB_SURROGATE_ROM_PERSISTENT_DISK_MOUNTED=1` only when that path is actually backed by a durable disk.

## Shared Research Projects and Team Workspaces — v0.35.0

The `/v1/team-workspaces` service stores private shared workspaces, memberships, invitation digests, resource links, access decisions, and event history in SQLite WAL. Every request is authenticated through the normal compute gateway and carries a stable actor identity in `X-SC-Lab-Actor`. Direct clients should set that header to their institutionally governed subject identifier.

The v0.35.0 service does not execute code or grant access to linked resources by itself. v0.35.1 adds a separate review service over the same governed workspace database.

```bash
SC_LAB_TEAM_WORKSPACE_DB_PATH=/app/data/sc-lab-team-workspaces.sqlite3
SC_LAB_TEAM_WORKSPACE_PERSISTENT_DISK_MOUNTED=0
```



## Review, Comments, Approvals, and Scientific Sign-Off — v0.35.1

The `/v1/workspace-reviews` and workspace-scoped review routes store append-only comments, reviewer assignments, approval requests, immutable decisions, and immutable scientific sign-off records in the shared workspace SQLite WAL database. State-changing review operations use `expectedRevision` and return HTTP 409 on stale updates.


## Version History, Branching, Merge, and Conflict Resolution — v0.35.2

The `/v1/workspace-versions` service shares the governed team-workspace SQLite WAL database and migrates it in place to schema version 3. It stores immutable snapshots, named branches, merge requests, conflict resolutions, and hashed version events.

Snapshots contain canonical JSON trees and SHA-256 identities. Branch heads use optimistic checks. Three-way merges retain base, source, and target values for every conflict. Restoring an earlier snapshot creates a new descendant snapshot; history is never rewritten. Protected branch finalization requires an attached v0.35.1 approval request in `signed` state with an immutable scientific sign-off.


## Scientific Artifact Repository and Data Federation — v0.36.0

The authenticated `/v1/artifact-repository/*` and workspace-scoped artifact routes store governed collection metadata, immutable artifact version records, registered federation nodes, manifest synchronization runs, tombstones, conflicts, and hashed timelines in a dedicated SQLite WAL database. Artifact bytes remain in the existing content-addressed transport store; repository records can bind to a verified `transportArtifactId` or describe a remote artifact through its SHA-256 identity.

Federation is manifest-driven. Lab does not automatically call arbitrary submitted endpoints. External nodes send or export canonical `sc-lab-federation-manifest/0.36.0` documents through authenticated routes.

```bash
SC_LAB_ARTIFACT_REPOSITORY_DB_PATH=/app/data/sc-lab-artifact-repository.sqlite3
SC_LAB_ARTIFACT_REPOSITORY_PERSISTENT_DISK_MOUNTED=0
```


## v0.37.2 Public Reproduction and Verification Portal

Publishes safe immutable reproduction records, nonce-bound verification challenges, and signed receipts without exposing private workspace data, executable code, credentials, callbacks, or restricted dataset bytes.


## v0.39.2 Multi-Instance Operations, Backup, Migration, and Disaster Recovery

The authenticated `/v1/multi-instance-operations/*` service provides stable instance manifests, consistent SQLite snapshots, signed backup archives, staged restore verification, idempotent migration journals, signed cross-instance transfer bundles, and RPO/RTO recovery drills. Restore operations are deliberately non-destructive: the service extracts and verifies into a new staging directory and never replaces active production files through the API.

```bash
SC_LAB_MULTI_INSTANCE_OPERATIONS_DB_PATH=/app/data/sc-lab-multi-instance-operations.sqlite3
SC_LAB_BACKUP_ROOT=/app/data/sc-lab-backups
SC_LAB_INSTANCE_ID=sc-lab-production
SC_LAB_INSTANCE_NAME="Sustainable Catalyst Lab"
SC_LAB_INSTANCE_ENVIRONMENT=production
SC_LAB_INSTANCE_REGION=us-central
SC_LAB_INSTANCE_PUBLIC_URL=https://lab.example.org
SC_LAB_BACKUP_SIGNING_SECRET=<strong-random-secret>
SC_LAB_MULTI_INSTANCE_PERSISTENT_DISK_MOUNTED=1
SC_LAB_RECOVERY_RPO_HOURS=24
SC_LAB_RECOVERY_RTO_MINUTES=240
```

The backup signing secret belongs only in the hosting provider's secret manager. WordPress and browser clients must never receive it. Remote object storage and automated failover are intentionally not enabled by this release.
