# Sustainable Catalyst Lab

**Current release: v0.38.2 — Public API, Webhooks, Embeds, and Research SDK**


## v0.38.2 highlights

- Stable, versioned `/v1` public research API catalog and OpenAPI discovery.
- Scoped integration authentication for protected research, webhook, and embed operations.
- HTTPS-only webhook subscriptions with SSRF safeguards, one-time secrets, HMAC-SHA256 signatures, delivery queues, and guarded dispatch.
- Signed, expiring research embed manifests limited to public references and policy-approved metadata.
- Dependency-light Python and TypeScript SDKs plus a browser research-embed loader.
- WordPress Public Research Integration Studio for API, webhook, delivery, SDK, and embed operations.
- Outbound webhook delivery remains disabled by default.

## v0.38.1 highlights

- Executable typed adapters for 13 Sustainable Catalyst products.
- Deterministic product-pair route planning with contract inference and target bindings.
- Dry-run validation, SHA-256 route and plan identities, and governed handoff creation.
- Optional profile-aware create-and-seal operations.
- New WordPress Product Handoff Studio and authenticated FastAPI routes.
- No arbitrary callbacks, executable code, credentials, or embedded restricted dataset bytes.

## v0.38.0 highlights

- Workspace-governed interoperability profiles for Sustainable Catalyst products and institutional systems.
- Canonical typed research handoff envelopes with resource hashes, provenance, safety declarations, and stable identities.
- Contract-version and capability negotiation between source and target profiles.
- Hash-verified, idempotent imports with immutable delivery and acceptance receipts.
- Optional HMAC-SHA256 receipt signing and retained interoperability timelines.
- No arbitrary code, embedded restricted data, browser-held credentials, or unrestricted remote callbacks.
- New Sustainable Catalyst Research Interoperability Layer workspace, bringing Lab to 77 registered panels.

## v0.37.1 highlights

- Reusable, revisioned section library with immutable snapshots inside assemblies.
- Manuscript, technical report, methods supplement, research dossier, and output-only notebook document types.
- Structured methods narratives generated from sealed v0.37.0 reproducibility packages.
- Cross-format Markdown, escaped HTML, JATS-lite XML, Jupyter notebook, BibTeX, methods, and JSON exports.
- Validation, immutable sealing, render hashes, and parent-revision lineage.
- New `Manuscript, Report, Notebook & Methods Assembly` Lab workspace.

## v0.37.0 highlights

- Workspace-governed reproducibility packages with immutable sealed manifests and SHA-256 identities.
- Logical research bundles containing methods, environment locks, citations, provenance, resources, and verification receipts.
- Publication-ready Markdown, escaped HTML, JSON, and `CITATION.cff` outputs.
- Reviewer readiness gates and publication restricted to an existing signed scientific workspace approval.
- No arbitrary code, shell commands, secrets, raw restricted data bytes, or unrestricted callbacks.
- New Reproducibility Packages and Research Publication Studio panel, bringing Lab to 74 registered panels.

## v0.36.2 highlights

- Sealed offline work packages for disconnected field research.
- One-time edge-device credentials and workspace-governed enrollment.
- Signed, resumable synchronization sessions with cursor-based deltas.
- Duplicate suppression, conflict records, explicit reconciliation, and hashed field provenance.
- Institutional data remains local; field packages contain references, forms, protocols, and hashes rather than restricted data bytes.

## v0.36.1 highlights

- Workspace-governed institutional node registration with one-time node credentials and explicit status controls.
- Local data asset records that centralize only schema, classification, hashes, and export policy—not restricted data bytes.
- Signed execution envelopes restricted to registered Lab methods and node allowlists.
- Node-authenticated request claiming with concurrency limits.
- HMAC-attested completion receipts containing result, data-access, and environment hashes.
- Automatic rejection of raw artifact export for confidential or restricted datasets.
- Durable execution, cancellation, receipt, and node timelines.
- New Institutional Node Federation and Local-Data Execution panel, bringing Lab to 72 registered panels.


## v0.36.0 highlights

- Workspace-governed scientific artifact collections with private, workspace, and public visibility metadata.
- Immutable artifact version records identified by SHA-256, semantic version, canonical URI, provenance, and stable record hashes.
- Optional binding to the existing content-addressed artifact transport for byte-level size and digest verification.
- Registered institutional federation nodes with explicit trust and conflict policies.
- Canonical export and authenticated import of `sc-lab-federation-manifest/0.36.0` documents.
- Idempotent delta synchronization, tombstones, retained sync runs, and hashed repository timelines.
- Durable conflict records with keep-local, accept-remote, retain-both, and dismiss resolutions.
- No automatic callbacks to submitted endpoints and no arbitrary code execution.
- New Scientific Artifact Repository and Data Federation panel, bringing Lab to 71 registered panels.


## v0.35.2 highlights

- Immutable workspace snapshots with canonical JSON trees and SHA-256 identities.
- Named research branches with optimistic branch-head and revision checks.
- Three-way merge with durable path-level base, source, and target conflict records.
- Reviewer conflict resolution and editor-controlled merge finalization.
- Protected branch merges gated by signed v0.35.1 scientific approvals.
- Non-destructive restore that creates a new snapshot instead of rewriting history.
- In-place workspace database migration to schema version 3.
- New Version History, Branching, Merge, and Conflict Resolution panel, bringing Lab to 70 registered panels.

## v0.35.1 highlights

- Resource-scoped, append-only review threads and nested comments with withdrawal records.
- Reviewer assignments with due dates, explicit states, and optimistic-concurrency revisions.
- Approval gates for required decisions, open threads, completed assignments, and signatory roles.
- Immutable approve, reject, request-changes, and abstain decisions with rationale and evidence.
- Immutable scientific sign-off records binding workspace, resource, approval, decisions, signatory, and statement.
- In-place workspace database migration to schema version 2.
- New Review, Approvals & Sign-Off panel, bringing Lab to 69 registered panels.

## v0.35.0 highlights

- Private shared research workspaces with stable workspace identities and primary-project links.
- Owner, administrator, editor, contributor, reviewer, and viewer roles with backend-enforced permissions.
- Single-use invitation tokens retained only as SHA-256 digests, with bounded expiry and optional target actors.
- Governed links to projects, datasets, workflows, runs, campaigns, models, artifacts, notebooks, sources, evidence, and reports.
- Per-resource minimum roles and durable hashed access decisions.
- Ownership transfer that preserves the previous owner as an administrator.
- Archive-without-deletion semantics and a complete hashed collaboration event timeline.
- New Shared Research Projects and Team Workspaces panel, bringing Lab to 68 registered panels.
- The v0.35.1 review and sign-off layer now builds on these workspace records without changing their original contracts.


## v0.34.2 highlights

- Immutable surrogate and reduced-order training studies with canonical definition and model hashes.
- Polynomial-ridge, radial-basis, and Gaussian-process surrogate algorithms.
- Seeded holdout validation with RMSE, normalized RMSE, MAE, maximum error, and R².
- Proper orthogonal decomposition using centered SVD, retained-energy targets, and basis hashes.
- Hybrid ROM training that maps declared parameters to reduced coefficients and reconstructed states.
- Predictive uncertainty for Gaussian-process models and durable prediction hashes.
- Publication of validated surrogate versions into the Scientific Model Registry.
- New Surrogate Models and Reduced-Order Analysis workspace, bringing Lab to 67 registered panels.


## v0.34.1 highlights

- Immutable weighted ensembles of registered scientific model versions.
- Monte Carlo, Latin hypercube, Sobol, and Saltelli-Sobol sampling.
- Uniform, normal, lognormal, triangular, and discrete uncertainty inputs.
- Dispatcher-backed sample/member evaluations with existing worker security and retry controls.
- Output distributions, confidence intervals, threshold probabilities, and member comparisons.
- Pearson, Spearman, standardized-regression, and Sobol global sensitivity measures.
- Durable ensemble studies, evaluations, analysis hashes, and event timelines.
- New Ensemble Simulation, Global Sensitivity, and Uncertainty Lab workspace.

## v0.34.0 highlights

- Durable scientific model, model-version, environment, alias, and event registries.
- Immutable semantic versions with canonical SHA-256 model hashes.
- Runtime, operating-system, architecture, container, dependency, source-revision, and build capture.
- Stable environment lock hashes and dependency-drift comparison.
- Draft, candidate, production, deprecated, and archived governance channels.
- Portable reproduction manifests with model, environment, artifact, source, and manifest verification.
- Administrator-only Scientific Model Registry workspace, bringing Lab to 65 registered panels.


## v0.33.2 highlights

- Closed-loop simulation, instrument, and hybrid campaigns above the adaptive campaign engine.
- Reviewable command envelopes with operator approval instead of direct device execution.
- Signed measurement ingestion, canonical hashes, deduplication, and objective reconciliation.
- Signal and parameter limits, maximum step deltas, emergency-stop signals, and bounded failure handling.
- Durable cycles, commands, measurements, safety decisions, and complete campaign/workflow provenance.
- A dedicated Closed-Loop Campaigns workspace, bringing Lab to 64 registered panels.

## v0.33.1 highlights

- Gaussian-process surrogates with RBF, Matérn 3/2, and Matérn 5/2 kernels.
- Expected improvement, probability of improvement, confidence-bound, and maximum-variance acquisition.
- Mixed continuous, integer, and categorical parameter encoding.
- Predictive mean, uncertainty, model condition diagnostics, and reproducible model hashes.
- Resource-aware candidate scoring, per-trial limits, total-cost budgets, and observed-cost provenance.
- Non-mutating proposal previews and inspectable surrogate records.
- In-place migration of existing v0.33.0 campaign stores to schema version 2.

## v0.33.0 highlights

- Durable adaptive experiment campaigns backed by the existing scientific workflow engine
- Typed continuous, integer, and categorical parameter spaces with explicit workflow input bindings
- Deterministic random, grid, and adaptive explore/exploit proposal policies
- Duplicate-design prevention through canonical parameter fingerprints
- Objective extraction from declared workflow result paths with minimize/maximize goals
- Trial, failure, concurrency, patience, target, and minimum-improvement stopping controls
- Campaign pause, resume, cancellation, manual observations, and operator-driven advancement
- Immutable workflow-run provenance for campaign, trial, proposal, parameter, and objective lineage
- Separate SQLite WAL campaign, trial, and event store with background reconciliation
- New Adaptive Experiment Campaigns operations panel
- Direct cumulative installer bridge from v0.31.0 through v0.32.2

## v0.32.2 highlights

- Durable interval, UTC cron, one-time, and event-triggered workflow schedules
- Persistent next-fire timestamps and startup missed-run recovery
- `skip`, `catch-up-one`, and bounded `catch-up-all` misfire policies
- `allow`, `forbid`, and `replace` workflow concurrency controls
- Authenticated event ingestion with optional HMAC event signatures
- Idempotent external-event receipts and duplicate-event protection
- Declarative event filters without executable expressions or callbacks
- Schedule firings linked directly to workflow run IDs and automation context
- Background scheduler lifecycle plus administrator-operated manual ticks
- Separate SQLite WAL schedule, firing, and event-receipt store
- New Scheduled & Event-Driven Runs operations panel
- Direct cumulative installer bridge from v0.31.0 through v0.32.1

## v0.32.1 highlights

- Declarative workflow conditions over run inputs, run context, and prior node state/results
- Safe `all`, `any`, and `not` composition with a bounded allowlist of comparison operators
- Explicit skipped-node outcomes and condition-evaluation timeline records
- Persistent node checkpoint history with deduplication and latest-checkpoint pointers
- Automatic capture of worker/dispatcher checkpoints and checkpoint artifact identifiers
- Resume context propagated into recovered dispatcher workloads
- Recovery planning for failed, cancelled, skipped, completed, or operator-selected branches
- Lineage-preserving recovery runs that reuse successful nodes and restart only selected branches plus downstream dependents
- Recovery generations, source-run/source-node links, operator reasons, and auditable recovery events
- Administrator workflow recovery, node restart, checkpoint inspection, and manual-checkpoint controls
- In-place workflow database migration from schema version 1 to schema version 2
- Direct cumulative installer bridge from v0.31.0 through v0.32.0

## v0.32.0 highlights

- Typed scientific workflow definitions with stable SHA-256 definition fingerprints
- Directed acyclic graph validation with duplicate, unknown-dependency, self-dependency, binding, and cycle checks
- Dependency-aware node scheduling through the persistent distributed dispatcher
- Parallel scheduling of independent root and newly ready nodes
- Immutable workflow-definition snapshots attached to every run
- Node-level queue IDs, states, results, errors, timestamps, and execution timeline events
- Safe result bindings from completed upstream nodes into downstream registered-method requests
- Automatic propagation of upstream artifact IDs into downstream artifact inputs
- Dispatcher-managed node retry and dead-letter behavior
- Workflow cancellation that also cancels active dispatcher queue items
- Persistent SQLite WAL workflow registry and run store
- Administrator-only WordPress Scientific Workflows panel and compute proxies
- Direct cumulative installer bridge from v0.31.0 through v0.31.4

## v0.31.4 highlights

- Normalized failure classification for transient, validation, security, capacity, artifact, lease, and worker failures
- Bounded exponential retry backoff with configurable base and maximum delays
- Durable `retrying`, `dead-lettered`, and operator-cancelled queue lifecycles
- Attempt-exhaustion handling without dropping the original workload or event history
- Single and bulk dead-letter replay with optional attempt reset
- Per-item queue, contract, lease, and operator-action timelines
- Queue depth, oldest-ready age, lease-expiry, throughput, failure-distribution, and operator-action metrics
- SQLite integrity, foreign-key, WAL, size, schema, and storage-path diagnostics
- Administrator-only WordPress Dispatcher Operations panel and recovery proxies
- Direct cumulative installer bridge from v0.31.0 through v0.31.3

## v0.31.3 highlights

- Content-addressed storage for inputs, results, checkpoints, logs, reports, datasets, and provenance artifacts
- Sequential resumable chunk uploads with per-chunk and final SHA-256 verification
- Deduplication, quarantine for failed integrity checks, ranged downloads, manifests, and audit events
- Worker-scoped uploads and lease-bound input-artifact downloads
- JSON, text, and base64 binary input materialization into registered compute requests
- Automatic externalization of large worker results from completion receipts
- Queue, contract, project, worker, method, and receipt provenance on retained artifacts
- Upload expiration and artifact-retention cleanup controls
- WordPress Artifact Transport operations panel and same-origin backend proxies
- Direct installer bridge from v0.31.0, v0.31.1, or v0.31.2

## v0.31.2 highlights

- Installable Python worker agent for local, Raspberry Pi, Render, and institutional nodes
- One-time coordinator enrollment with worker-scoped credentials
- Coordinator-side credential digests, rotation, revocation, and quarantine
- Pull-based compatible-lease claiming without inbound worker callbacks
- Local HMAC contract verification with exact worker, method, and expiration binding
- Registered-method-only execution; arbitrary code, commands, callbacks, and executable payloads are rejected
- Automatic lease renewal during long computations
- Idempotent completion receipts with result hashes and compute provenance
- WordPress Secure Worker Agents operations panel and health routes
- Corrected dispatcher database deployment path and explicit instance-local versus persistent-disk health reporting

# Sustainable Catalyst Lab v0.27.1 — Numerical Validation and Benchmark Library

Fourteen governed known-answer benchmarks verify the numerical methods registry with tolerance, residual, deterministic-seed, unit, and convergence checks. The Numerical Validation Library supports selected and full-suite runs, browser references, provenance inspection, and JSON export.

# Sustainable Catalyst Lab v0.27.0 — Scientific Computing and Numerical Methods

Twelve governed numerical methods and the Numerical Methods Studio added root finding, quadrature, interpolation, ODEs, eigen analysis, optimization, FFT, Monte Carlo, bootstrap, sensitivity analysis, and parameter sweeps.

# Sustainable Catalyst Lab v0.26.3.2 — Installation, Version, and Asset Integrity Patch

This release verifies the active WordPress plugin identity, unifies public release reporting, applies SHA-256 content versions to Lab assets without rewriting legacy loader methods, detects duplicate plugin copies and partial installations, validates canonical panel routes, and publishes a machine-readable build manifest and runtime health endpoint.

# Sustainable Catalyst Lab v0.26.3.1 — Panel Alias and Compatibility Routing Repair

Canonical panel routing for legacy identifiers, false-positive compatibility-warning suppression, content-hash cache busting, and duplicate-plugin diagnostics.

# Sustainable Catalyst Lab v0.26.3 — Cross-Laboratory Calculator Activation and Runtime Repair

This release repairs a shared browser-runtime failure that prevented later laboratory controllers from mounting when the single-panel lifecycle removed inactive markup. It adds guarded initialization, active-panel controller mounting, file-hash cache busting, runtime diagnostics, and resilient project storage while preserving the v0.26.1 Python Compute Core and persistent queue.

# Sustainable Catalyst Lab v0.26.1 — Job Queue and Worker Reliability

This release adds a SQLite-backed persistent queue, isolated Python worker processes, hard cancellation and timeouts, retry policies, duplicate-job prevention, restart recovery, worker health, queue monitoring, and same-origin WordPress job controls while preserving the v0.26.0 Python Compute Core and v0.25.5 lifecycle isolation.

# Sustainable Catalyst Lab v0.26.0 — Python Compute Core Foundation

Version 0.26.0 promoted FastAPI/Python into the governed compute plane with registered methods, HMAC signing, capability discovery, and reproducible provenance.

# Sustainable Catalyst Lab v0.25.3 — Calibration, Validation, and Chain of Custody

This release adds eight validation profiles, eight acceptance states, eight provenance event types, eight deviation types, 16 deterministic readiness methods and benchmarks, component-hashed validation manifests, parent-linked SHA-256 custody events, tamper verification, weighted release dispositions, and validation dossiers while preserving the complete v0.25.0-v0.25.2 stack.

# Sustainable Catalyst Lab v0.25.2 — Live Sensor and Instrument Visualization

This release adds eight live visualization modes, 16 deterministic streaming and dashboard-analysis methods with 16 benchmarks, eight channel templates, eight connection states, eight event types, bounded multi-channel buffers, warning/action and gap events, pause/replay controls, CSV and JSON replay, synchronized SVG dashboards, exports, and research handoffs while preserving v0.25.0 and v0.25.1.

# Sustainable Catalyst Lab v0.25.1 — Instrumentation Production Reliability

This release adds unconditional instrumentation asset activation, canonical panel/root recovery, duplicate suppression, stale-state cleanup, retry and mutation recovery, browser diagnostics, WordPress/FastAPI production health, and mobile/long-table hardening while preserving the complete v0.25.0 48/48/8/9/8/8 contract.

# Sustainable Catalyst Lab v0.25.0 — Laboratory Data and Instrumentation Platform

This release adds 48 deterministic instrumentation calculations, structured instrument/sensor/sample/run/calibration/maintenance/measurement/custody records, normalized ingestion, SHA-256 manifests, custody verification, eight connection profiles, WordPress/FastAPI routes, and local-first Arduino/Raspberry Pi preparation.

# Sustainable Catalyst Lab v0.24.3 — Genomic Validation and Sequence Provenance

This release completes the v0.24 genomics chain: 48 deterministic sequence methods and benchmarks, production reliability, comparative visualization, eight validation profiles, component-hashed dataset manifests, reference and pipeline context, sequence and variant provenance, tamper-aware ledgers, and reproducibility dossiers with explicit non-clinical boundaries.

# Sustainable Catalyst Lab v0.23.2 — Biosignal Visualization, Annotation, and Comparative Analysis

This release adds eight synchronized visualization modes, 16 deterministic comparative-analysis methods, 16 benchmarks, six annotation types, multi-channel CSV import, raw/filtered overlays, lag and alignment analysis, run comparison, SVG/CSV/JSON exports, project/notebook/provenance handoffs, and mobile chart fallback while preserving v0.23.0 and v0.23.1.

# Sustainable Catalyst Lab v0.23.1 — Biosignal Production Activation and Interface Reliability

This release activates the v0.23.0 biosignal assets unconditionally on the public interface and adds canonical panel and mount repair, duplicate-root suppression, stale-marker cleanup, controlled startup retries, navigation and browser-restoration recovery, dynamic DOM observation, browser diagnostics, WordPress/FastAPI production-health routes, and mobile overflow reliability while preserving all 48 methods, 48 benchmarks, eight categories, and non-clinical boundaries.

# Sustainable Catalyst Lab v0.23.0 — Biomedical Engineering and Biosignals

This release adds 48 deterministic biomedical and biosignal methods, 48 reference benchmarks, ECG, PPG, respiration, EMG, EEG, acquisition, filtering, waveform analysis, signal-quality review, CSV batch execution, project/notebook handoffs, and v0.22.3 provenance integration with explicit non-clinical boundaries.

# Sustainable Catalyst Lab v0.22.3 — Bioprocess Validation and Batch Provenance

This release adds eight validation profiles, batch acceptance checks, cross-batch comparability, CPP/CQA conformance, excursion disposition, hold-time stability, release-readiness decisions, SHA-256 provenance records, linked-ledger verification, tamper detection, and dossier exports.

# Sustainable Catalyst Lab v0.22.2 — Bioprocess Monitoring, Control, and Visualization

This release adds time-series monitoring, excursion detection, rolling statistics, PID-style control simulations, multi-run comparison, native SVG charts, CSV workflows, exports, and provenance handoffs while preserving the v0.22.0 48-method engine and v0.22.1 production layer.

# Sustainable Catalyst Lab v0.22.1 — Bioprocess Production Activation and Interface Reliability

This release adds canonical mount repair, duplicate suppression, stale-render cleanup, controlled retries, browser and REST health diagnostics, and mobile reliability while preserving the v0.22.0 48-method bioprocess engine.

# Sustainable Catalyst Lab v0.22.0 — Biotechnology and Bioprocess Engineering

This release adds 48 bioprocess methods, 48 reference benchmarks, batch/fed-batch/continuous simulations, CSV batch monitoring, oxygen-transfer and scale-up tools, WordPress/FastAPI routes, and v0.21.3 provenance handoffs.

# Sustainable Catalyst Lab v0.21.3 — Molecular Analysis Validation and Provenance

This release adds eight analytical validation protocols, explicit acceptance criteria, validation dossiers, SHA-256 payload fingerprints, parent-hash provenance chains, independent ledger verification, evidence metadata, and tamper-detection tests while preserving the v0.21.0 method catalog and v0.21.2 visualization/batch layer.

# Sustainable Catalyst Lab v0.21.2 — Biochemistry Visualization and Batch Analysis

This release adds native SVG biochemical plots, standard-curve regression, kinetics and binding visualizations, CSV batch execution across all 48 methods, replicate statistics, CV review flags, row-level error isolation, exports, and WordPress/FastAPI batch routes.

# Sustainable Catalyst Lab v0.21.1 — Biochemistry Production Activation and Interface Reliability

This maintenance release hardens Biochemistry asset activation, late-mount initialization, panel routing, empty-render recovery, diagnostics, health checks, mobile presentation, and version-aware release validation while preserving the validated 48-method v0.21.0 analysis catalog.

# Sustainable Catalyst Lab v0.21.0 — Biochemistry and Molecular Analysis

The current release adds 48 formula-visible biochemical and molecular-analysis methods, deterministic JavaScript/PHP/Python benchmarks, browser calculators, WordPress REST routes, FastAPI routes, project/notebook handoffs, and responsible-use boundaries.

# Sustainable Catalyst Lab v0.20.0

Sustainable Catalyst Lab is a modular scientific, engineering, computational, visualization, and reporting environment delivered through WordPress with a governed Python Compute Core backend. Version 0.9.4 adds structured PDF reports and a formal Decision Studio handoff while retaining the scientific laboratories, universal visualization, 3D/4D scenes, workspace backup/reset, portable method contracts, and curated multi-language execution introduced in earlier releases.

## Stable WordPress plugin identity

Use the WordPress installer archive named:

```text
sustainable-catalyst-lab.zip
```

It always contains:

```text
sustainable-catalyst-lab/
└── sustainable-catalyst-lab.php
```

WordPress identifies a plugin by this folder and bootstrap path. Uploading the repository ZIP or release bundle can create a second plugin instance. The administrator duplicate detector remains available under **Settings → Sustainable Catalyst Lab → Plugin installation identity**.

## PDF Report Studio

The Report Studio can assemble one to twelve analyses into a structured report. Supported report types are:

```text
Technical report
Decision brief
Evidence packet
Executive summary
```

A report can retain:

- project context and report metadata
- equations and method identifiers
- labeled inputs and outputs with units
- vector line, bar, and scatter figures
- assumptions and warnings
- validation records
- sources and evidence references
- code, compiler, runtime, and execution metadata
- input, output, report, and PDF fingerprints
- dimensional-scene references and figure records

Two coordinated PDF paths use the same report contract:

1. **Local browser PDF** for immediate offline, selectable-text reports.
2. **Render ReportLab PDF** for vector figures and larger multi-page reports.

## Decision Studio handoff

Version 0.9.4 advances the handoff contract to:

```text
sc-decision-studio-analysis-packet/2.0
```

A handoff can include the complete report contract, analyses, charts, tables, 3D/4D scene specifications, evidence, assumptions, uncertainties, warnings, validation, runtime metadata, and audit fingerprints. Decision Studio receives structured content rather than only a screenshot, so figures and report sections remain traceable to the originating Lab calculation.

Protected routes include:

```text
POST /wp-json/sc-lab/v1/compute/reports/validate
POST /wp-json/sc-lab/v1/compute/reports/pdf
POST /wp-json/sc-lab/v1/compute/handoffs/decision-studio/validate
```

WordPress sanitizes report payloads and proxies them to the Python Compute Core backend without exposing the compute API key to browser JavaScript.

## Render compute and report API

The FastAPI backend provides:

```text
GET    /health
GET    /version
GET    /v1/methods
GET    /v1/languages
POST   /v1/validate
POST   /v1/execute
POST   /v1/compare
POST   /v1/jobs
GET    /v1/jobs/{job_id}
DELETE /v1/jobs/{job_id}
POST   /v1/reports/validate
POST   /v1/reports/pdf
POST   /v1/handoffs/decision-studio/validate
```

Native curated-worker targets remain Python, JavaScript, TypeScript, C, C++, Fortran, Rust, and Go. R, Julia, SQL, and Haskell remain source-generation targets until dedicated workers are added.

## Universal Code Studio

Code Studio provides equivalent source views for:

```text
Python
R
Julia
JavaScript
TypeScript
SQL
C
C++
Fortran
Rust
Go
Haskell
```

Curated method contracts can be inspected, downloaded, locally evaluated where supported, executed through Render workers, and compared for numerical parity.

## Universal visualization and dimensional scenes

Existing shared visualization capabilities include:

- SVG, high-resolution PNG, PDF, CSV, and JSON exports
- complete analysis-package ZIPs
- project visualization records
- interactive 3D scenes
- projected 4D cube, tesseract, 4-simplex, and 16-cell scenes
- six independent 4D rotation planes
- scene JSON and Decision Studio scene handoff

## Workspace data management

The Lab retains:

- full workspace JSON and ZIP backup
- per-project export
- notebook Markdown and observation CSV
- restore as copies, merge, or replace
- selective note and observation clearing
- analysis-history clearing
- active-project reset or deletion
- factory reset with typed confirmation and minimal deletion receipt

## Project schema additions

Version 0.9.4 adds or formalizes:

```text
reports
reportFigures
reportExports
decisionStudioHandoffs
```

The original browser-storage keys remain unchanged:

```text
scLabProjectsV010
scLabActiveProjectV010
```

Projects from v0.1.x through v0.9.3 are normalized non-destructively to schema version `0.9.4`.

## Shortcodes

```text
[sc_lab_app]
[sc_lab_reports]
[sc_lab_report_studio]
[sc_lab_visualization]
[sc_lab_workspace_data]
[sc_lab_code_switcher]
```

All focused scientific-laboratory shortcodes remain available.

## Contracts

```text
contracts/project.schema.json
contracts/analysis.schema.json
contracts/scene.schema.json
contracts/report.schema.json
contracts/report-result.schema.json
contracts/decision-studio-packet.schema.json
contracts/method.schema.json
contracts/method-catalog.json
contracts/execution.schema.json
contracts/language-comparison.schema.json
contracts/execution-job.schema.json
```

## Validation

Run:

```bash
chmod +x scripts/test_release.sh tests/test-generated-code.sh
./scripts/test_release.sh
```

The release suite covers PHP and JavaScript syntax, WordPress template rendering, all inherited scientific engines and benchmarks, portable method contracts, generated code, curated compute execution, report contracts, browser PDFs, ReportLab PDFs, report endpoints, Decision Studio packet validation, project migration, visualization, 3D/4D scenes, backup, reset, and restore.

## Boundaries

- Reports preserve supplied calculations and metadata; they do not independently certify a scientific or engineering conclusion.
- Medical, safety-critical, structural, electrical, environmental, and other regulated analyses still require appropriate professional review.
- The compute API executes only curated, versioned methods. It does not accept arbitrary source code or shell commands.
- Interactive browser and backend PDF generation share a report contract but can differ slightly in pagination and typography.

## v0.9.5 — Report Composer, visualization accessibility, and restore validation

Lab v0.9.5 adds ordered report compositions with drafts and revision history, structural accessibility enhancements and audit records for scientific visualizations, and validation-first JSON/ZIP workspace restores with dry runs, conflict detection, safety backups, fingerprints, migration checks, and restore receipts. Existing v0.9.4 PDF and Decision Studio contracts remain compatible.

## v0.10.0 — Electrical, Electronics, and Embedded Systems

Lab v0.10.0 adds a dedicated electrical and embedded laboratory with 45 curated browser methods, protected backend methods, circuit and interface records, device profiles, firmware artifacts, hardware-validation records, and a focused `[sc_lab_electrical]` shortcode. The release retains all v0.9.5 report, accessibility, restore, visualization, compute, and Decision Studio capabilities.

## v0.11.0 — Mechanical and Thermal Engineering

Lab v0.11.0 adds 48 shared browser/Python methods for statics, strength, failure, machine design, dynamics, vibration, fluids, thermodynamics, and heat transfer. Results remain compatible with project storage, notebooks, visualization, reports, restore validation, and Decision Studio handoffs.

## v0.12.0 — Civil Engineering and Infrastructure Systems

Adds 48 methods spanning structures, geotechnical engineering, hydrology, transportation, water and wastewater systems, infrastructure risk, reliability, resilience, lifecycle cost, and embodied carbon.

## v0.13.0 — Architecture and Building Performance

Adds 48 auditable methods across building geometry and program, envelope and thermal performance, solar and daylight systems, ventilation and indoor environmental quality, building energy and HVAC, water, operational and embodied carbon, acoustics, and passive survivability.

## v0.14.0 — Urban Planning and Spatial Systems

Adds 48 auditable methods across land use and development, accessibility and mobility, spatial networks, GIS analysis, public services and infrastructure planning, equity, resilience, and urban scenario comparison.

## v0.15.0 — Sustainable Cities and Urban Resilience

Adds 48 auditable methods across urban metabolism, decarbonization, climate adaptation, infrastructure continuity, equity, social resilience, and integrated city scenarios. Also repairs the Civil and Infrastructure interface so all formulas and executable expressions render reliably.

## v0.16.0 — Circular Economy and Industrial Ecology

Adds 48 auditable methods across material-flow accounting, circular products and business models, waste prevention and recovery, industrial symbiosis, lifecycle footprints, resource productivity, supply risk, and circular transition scenarios.

## v0.17.0 — Comparative Economics and Development Systems

Adds 48 auditable methods across material-flow accounting, circular products and business models, waste prevention and recovery, industrial symbiosis, lifecycle footprints, resource productivity, supply risk, and circular transition scenarios.

## v0.18.0 — Aerospace Engineering and Flight Systems

Adds 48 auditable methods across atmosphere and aerodynamics, flight mechanics, aircraft performance, stability and control, propulsion integration, structures and loads, aeroelastic screening, navigation, mission analysis, and flight-system reliability.

## v0.19.0 — Rocket Propulsion and Spaceflight

Adds 48 auditable methods across rocket-propulsion fundamentals, nozzle and engine performance, launch-vehicle mass and staging, ascent dynamics, orbital mechanics, spacecraft mission systems, and reliability.

## v0.20.0 — Microbiology Laboratory

Adds 48 auditable methods across microbial growth, continuous culture, enumeration and microscopy, environmental microbiology, antimicrobial screening, microbial ecology, and laboratory quality control.


## Python Compute Core Foundation

v0.26.0 includes a deployable `backend/` FastAPI service, a registered scientific method catalog, HMAC request signing, provenance manifests, and WordPress gateway routes under `/wp-json/sc-lab/v1/compute/core/*`.


## v0.26.3.4 Scientific Feed Rendering and Observe Data Reliability

Marine Biology and Space Observations now auto-load, expose connector health, fall back from the WordPress proxy to browser-direct official APIs, and always render an explicit loading, empty, or error state.

## Numerical validation

Use **Analyze → Numerical Validation Library** or `[sc_lab_numerical_validation]` to run the v0.27.1 known-answer benchmark suite against the configured Python Compute Core.


## v0.27.3 solver governance

Use **Analyze → Precision & Solver Governance** or `[sc_lab_solver_governance]` to select precision profiles, inspect solver recommendations, validate units, review condition and convergence diagnostics, and run reference-method comparisons through the Python Compute Core.

## v0.27.4.1 integrity scope repair

The WordPress runtime verifies only files shipped in the WordPress plugin package. Backend files are tracked separately and no longer create false partial-install warnings.


## v0.28.0 project architecture

Use `[sc_lab_project_workspace]` or open **Project → Project architecture** to inspect the shared project schema, indexed records, relationships, checkpoints, import/export bundles, and migration state. Project content remains browser-local in this release.


## v0.28.1 dataset registry

Use `[sc_lab_dataset_registry]` or open **Project → Dataset registry** to register CSV, JSON, GeoJSON, NetCDF metadata, and existing Lab datasets with structured variables, units, validation, source/license metadata, profiles, and lineage.


## v0.28.2 reproducible computational runs

Use **Project → Reproducible runs** or `[sc_lab_reproducible_runs]` to freeze completed requests and results, verify checksums, rerun and compare within tolerances, and export portable reproducibility bundles.


## v0.29.1 Research Quality and Method Review

The Lab now stores benchmark coverage, validation evidence, calibration state, reviewer decisions, approval status, and deprecation history as project-scoped method-review records.

## v0.29.2 — External Scholarly and Data Discovery

The Project workspace now includes governed discovery across Crossref, OpenAlex, and DataCite, plus WorldCat, Google Scholar, DOI, and OpenURL handoffs. Results can be deduplicated and imported into project research sources for evidence, provenance, reproducibility, and method review.


### v0.30.0 — Reproducible Experiment Framework

Adds a project-scoped reproducible experiment framework with protocol validation, run histories, replication comparison, reports, and portable bundles.

## v0.30.1 — Parameter Studies and Design of Experiments

- Factorial, fractional-factorial, Latin-hypercube, central-composite, Box-Behnken, and one-factor-at-a-time designs.
- Response-surface fitting, sensitivity ranking, optimal-design recommendations, and registered-method batch plans.

### v0.30.2 — Scientific Model Calibration and Validation

Project-scoped calibration and validation for registered scientific model forms, including holdout metrics, uncertainty, residuals, comparison, and provenance.


## v0.31.0 — Distributed Compute Dispatcher

Adds worker capability discovery, governed workload routing, signed leases, heartbeat/load tracking, project-aware dispatch records, and browser/Render/local/Raspberry Pi/institutional worker profiles.


## v0.37.2 Public Reproduction and Verification Portal

Publishes safe immutable reproduction records, nonce-bound verification challenges, and signed receipts without exposing private workspace data, executable code, credentials, callbacks, or restricted dataset bytes.


## v0.38.2 research integrations

Discover the API at `/v1/public-research-api`. Configure `SC_LAB_PUBLIC_API_KEY` and `SC_LAB_WEBHOOK_SIGNING_SECRET` before enabling institutional integrations. SDK source is included under `sdk/python` and `sdk/typescript`.
