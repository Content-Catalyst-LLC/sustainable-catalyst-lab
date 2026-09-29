# Release Notes — Lab v0.135.16.0
## Revision Impact Graph & Scientific Dependency Analysis

### Added
- governed scientific dependency graph normalization and validation;
- revision-seed impact analysis;
- direct versus transitive downstream impact;
- upstream dependency traversal;
- bounded impact paths through declared relationships;
- cycle detection and dangling-reference diagnostics;
- revision-impact snapshots and snapshot comparison;
- Graph Studio impact overlay without renderer ownership or full redraw;
- explicit persistence to `graphStudioRevisionImpactAnalyses`;
- Project Workspace revision-impact context handoff;
- WordPress REST health/acceptance surface;
- 16 FastAPI endpoints for normalization, validation, traversal, snapshots, analysis, handoff, contract, and acceptance.

### Retained
- v0.135.15.0 typed verification artifact manifests and review evidence bundles;
- v0.135.14.0 review state machine and append-only audit lineage;
- v0.135.13.0 explicit revision actions;
- native Graph Studio incremental interaction and provenance renderer authority.

### Interpretation guardrails
No automatic scientific invalidation, causal inference, truth ranking, evidence-weight inference, or scientific preference is introduced. `Potentially affected` means reachable through declared dependencies within the configured depth bound.

### Validation
Release validation exercises the v0.135.16.0 backend plus the prior Graph Studio review/provenance regression stack. A browser fixture is included; automated headless-browser certification is not claimed unless separately recorded.
