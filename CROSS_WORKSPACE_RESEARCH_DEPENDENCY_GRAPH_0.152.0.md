# Lab v0.152.0 — Cross-Workspace Research Dependency Graph

## Purpose
Create a persistent governed graph of research-object dependencies across the integrated computational laboratory. The graph links sources, datasets, analyses, models, simulations, graph objects, validation records, findings, figures, reviews, reproductions, and publications while preserving object identity, workspace ownership, provenance, and edge semantics.

## Architecture
- Platform Core: canonical governed-object and provenance authority.
- Workspace: primary computational execution authority.
- Workbench: prototype execution authority.
- Knowledge Library: source/document authority.
- Research Lab: dependency analysis, impact review, staleness candidates, visualization, and reproducibility.
- v0.151.0 orchestration consumes dependency information but does not gain automatic scientific advancement.

## Scientific boundary
Dependency is not causality. Graph reachability is not evidentiary support. Staleness and impact are review candidates, not automatic invalidations. Degree, path length, bridge position, and cross-workspace connectivity are structural properties, not scientific importance. Publication impact is not an automatic retraction decision.

## Capability surface
- 120 backend API routes.
- 32 governed node types, 21 edge types, 13 dependency classes, 14 workspace identities.
- Direct and transitive dependency traversal.
- Computational cycle auditing and strongly connected components.
- Cross-workspace matrices and boundary summaries.
- Change impact, blast-radius, staleness-candidate, revalidation, recomputation, review, and publication-impact plans.
- Snapshots/diffs, Graph Studio visualization, workflow-orchestration handoff, reproducibility packages, and authority-preserving product handoffs.
