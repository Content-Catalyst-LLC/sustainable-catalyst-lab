# Lab v0.160.0 — Computational Research Operating System II

Lab v0.160.0 consolidates the modern research lifecycle into one governed operating layer. It does not replace Platform Core, Workspace, Workbench, the Knowledge Library, or the specialized Lab workspaces. Instead, it coordinates their references and human-controlled lifecycle state.

## Canonical lifecycle

`Question → Protocol → Notebook → Workflow → Campaign → Compute → Results → Synthesis → Replication → Review → Publication Package`

## New capabilities

- Unified Research Project Graph with reference-first links to protocols, notebooks, workflows, datasets, models, campaigns, execution plans, results, cross-study workspaces, replication networks, review dossiers, claims, evidence and reproducibility packages.
- Human-controlled Lifecycle State Machine with explicit prerequisites and one-stage-at-a-time forward progression.
- Research Command Center with project stage, object coverage, stale/withdrawn dependency blockers, next-stage readiness and package status.
- Cross-Module Object Resolution for governed upstream campaign, cross-study, replication-network and review-dossier references.
- Research Package Composer that freezes a reproducible, digest-verifiable reference package only after the project reaches `publication-package` and a human explicitly authorizes composition.
- Dependency Integrity Validation using expected/observed digests and explicit stale/superseded/withdrawn states.
- Explicit downstream handoffs that never execute or publish automatically.
- One v0.160.0 backend health contract preserving v0.154–v0.159 capabilities.

## Architectural boundaries

Platform Core remains canonical object/contract/provenance authority. Workspace remains execution authority. Lab v0.160.0 coordinates lifecycle state and research evidence. It does not execute scientific workloads, infer scientific validity or causality, judge replication success, publish automatically, store execution credentials, or advance lifecycle stages without explicit human authorization.
