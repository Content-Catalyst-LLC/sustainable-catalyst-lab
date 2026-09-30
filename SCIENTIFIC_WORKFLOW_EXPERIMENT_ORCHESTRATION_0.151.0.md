# Lab v0.151.0 — Scientific Workflow & Experiment Orchestration

## Purpose
v0.151.0 adds the governed orchestration layer above the Integrated Computational Research Laboratory. It represents research workflows as explicit directed stage/dependency graphs with approval gates, execution requests, checkpoints, failures, recovery plans, and provenance.

## Authority boundaries
- Platform Core: canonical workflow/governed-object contracts.
- Workspace: primary computational execution authority.
- Workbench: prototype/technical execution authority.
- Knowledge Library: source and document authority.
- Research Lab: experiment design, workflow state, orchestration, interpretation, review, and reproducibility.

Lab does not silently execute heavy compute, advance stages, approve gates, retry failed jobs, promote models, establish evidence, certify scientific validity, or accept publications.

## Main capabilities
Workflow/stage/dependency/gate/run objects; DAG and cycle audits; deterministic topological planning; readiness/blocker reports; execution planning and queues; cross-workspace handoffs; human approval queues; validation/reproducibility/publication gates; checkpoint lineage; runtime/environment/provenance audits; failure/retry/recovery/resume planning; change-impact analysis; snapshots/diffs; export and reproducibility packages.

## Epistemic boundaries
Workflow order is not scientific necessity. Dependency is not causality. Successful execution is not scientific validity. Gate passage is not publication acceptance. Retry does not repair invalid methodology. Reproducibility is not scientific validity.
