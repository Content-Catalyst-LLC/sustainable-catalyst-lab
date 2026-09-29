# Release Notes — Lab v0.141.4

**Hyperparameter Study & Search Results**

This release adds a governed research layer for hyperparameter studies on top of the v0.141.3 Model Comparison & Experiment Matrix release.

### Added
- Explicit parameter-space definitions and validation
- Objective definitions with mandatory declared direction for candidate derivation
- Search strategy, budget, seed, dataset/split, architecture/configuration, environment, and provenance lineage
- Workspace search-execution handoff
- Normalized trial/result registry
- Trial status, failure, pruning, and budget audits
- Search-progress, parameter, objective, parallel-coordinate/scatter, status, and Pareto visual-spec surfaces
- Descriptive parameter/objective association summaries
- Single-objective review candidate sets and multi-objective non-dominated candidate sets
- Deterministic snapshots, exports, reproducibility packages, and Platform Core visual handoff

### Boundaries
No automatic ranking, winner selection, model promotion, checkpoint promotion, causal attribution, or evidence conversion is performed.
