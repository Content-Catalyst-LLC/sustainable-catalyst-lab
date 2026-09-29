# Lab v0.57.0 — Scientific Workflow Composer

## Release purpose

v0.57.0 connects the scientific capabilities built across the current Lab line into saved, rerunnable, in-project research pipelines. It does not replace the older v0.32.1 operational workflow orchestrator: v0.57 composes scientific stages and reproducibility evidence, while v0.32.1 remains the lower-level layer for queues, checkpoints, schedules, recovery, and distributed operational execution.

## Scientific workflow contracts

The release introduces:

- `sc-lab-scientific-workflow-composer/0.57.0`
- `sc-lab-scientific-workflow-run/0.57.0`
- `sc-lab-scientific-workflow-stage-result/0.57.0`

A workflow is a bounded directed acyclic graph of registered Lab stages. Stage inputs are explicit, bindings may reference the run input or outputs from earlier stages, and every stage records request/output hashes, timing, status, proposal-only state, and result evidence.

## Registered scientific stages

The v0.57 catalog connects existing Lab capabilities without introducing arbitrary code execution. Registered adapters include:

- dataset profiling;
- scientific data transformation and bounded joins;
- model normalization;
- advanced statistical fitting, cross-validation, and comparison;
- model diagnostics and cross-validation;
- Bayesian fitting and posterior predictive analysis;
- independent and correlated uncertainty propagation;
- dynamic-system simulation, bifurcation evidence, and phase analysis;
- response-surface fitting and bounded optimization;
- advanced experimental design and sequential proposals;
- graph and figure normalization;
- reproducible model-package construction;
- Model Registry projection; and
- research-bundle/report assembly.

## Rerun and reproducibility evidence

Workflows use deterministic content hashes for normalized workflow definitions, stage requests, semantic stage outputs, and the final run record. Runtime-only timestamp/hash fields are excluded from semantic reproducibility comparisons so a rerun with the same scientific inputs and outputs can reproduce the same `runHash`.

Run comparison reports whether the workflow definition changed, whether the final run hash changed, and which stage outputs changed. A changed dataset or scientific parameter therefore propagates into the run evidence instead of being hidden behind a generic rerun status.

## Project persistence

The browser composer stores normalized workflows and run records in the active project using dedicated v0.57 collections. A compact workflow-run evidence record is also written to project `analysisPackets`, allowing the existing v0.50 reproducible-model-package layer to capture workflow provenance.

The composer can load the active project dataset into the run input and provides templates for common data-to-model, validation, uncertainty, and experimental-design pipelines.

## Interface integration

Scientific Workflow Composer is embedded contextually inside the existing **Scientific Workflows / Workflow Orchestration** workspace. It does not add a new permanent left-rail destination. The v0.48.3 six-destination navigation, Graph Studio front door, and Prototyping Workbench / Decision Studio / Site Intelligence three-card row remain unchanged.

The interface supports:

- template loading;
- workflow and run-input editing;
- workflow normalization/validation;
- execution through registered stage adapters;
- deterministic rerun and run comparison;
- active-project dataset injection;
- workflow and run persistence; and
- stage timeline/reproducibility inspection.

## Relationship to v0.32.1 operational orchestration

v0.57 and v0.32.1 intentionally remain separate layers:

- **v0.57 Scientific Workflow Composer** — describes and executes bounded scientific research pipelines inside the current Lab project.
- **v0.32.1 Workflow Orchestration** — retains operational queues, checkpoints, schedules, recovery, and distributed execution concerns.

v0.57 does not silently promote itself into an autonomous background scheduler.

## Scientific and safety boundaries

- No arbitrary Python, JavaScript, SQL, shell, `eval`, or executable code fields.
- No arbitrary callback, webhook, or external command execution.
- No automatic experiment execution.
- No automatic Model Registry promotion.
- No automatic publication.
- No automatic scientific-workflow scheduling.
- No bypass of the existing scientific validation or normalization layers used by each registered stage adapter.
- Workflows are capped at 24 stages and request trees are bounded.

## Interface continuity

- Six-destination v0.48.3 rail preserved.
- Graph Studio front door preserved.
- Prototyping Workbench / Decision Studio / Site Intelligence three-card row preserved.
- No new `MutationObserver` or document-wide responsiveness loop.
- Platform compatibility remains `1.0.0`.
