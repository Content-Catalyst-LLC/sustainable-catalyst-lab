# Sustainable Catalyst Lab v0.12.0

Sustainable Catalyst Lab is a modular scientific, engineering, computational, visualization, and reporting environment delivered through WordPress with an optional Render compute backend. Version 0.9.4 adds structured PDF reports and a formal Decision Studio handoff while retaining the scientific laboratories, universal visualization, 3D/4D scenes, workspace backup/reset, portable method contracts, and curated multi-language execution introduced in earlier releases.

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

WordPress sanitizes report payloads and proxies them to the optional Render backend without exposing the compute API key to browser JavaScript.

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
