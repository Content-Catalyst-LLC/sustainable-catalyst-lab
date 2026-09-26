# Sustainable Catalyst Lab v0.135.15.0

## Verification Artifact Manifests & Review Evidence Bundles

This release converts the free-form artifact reference introduced in v0.135.14.0 into a structured, versioned verification evidence layer while retaining the original review-audit record unchanged.

### Added

- Typed verification artifacts for datasets, methods, executions, figures, models, notebooks, documents, evidence sources, reproduction results, code, environments, and other declared artifact types.
- Multi-artifact evidence bundles stored as `graphStudioVerificationArtifactBundles`.
- Explicit binding between a v0.135.14.0 `verification-recorded` event and the v0.135.15.0 bundle that documents what was inspected.
- Optional artifact version/revision references and SHA-256 byte fingerprints.
- Optional source-object and execution references for lineage back to scientific objects and runs.
- Verification scope capturing exactly what the reviewer intended to check.
- Backend normalization, validation, event-binding checks, bundle summaries, fingerprints, integrity diagnostics, bundle comparisons, and verification packets.
- Graph Studio bundle composer supporting multiple artifacts before recording verification.
- Project persistence and Project Workspace verification context.
- Incremental UI integration with no Graph Studio full redraw for verification-artifact operations.

### Backward compatibility

v0.135.14.0 remains the authoritative review state machine and append-only audit history. v0.135.15.0 consumes that API and does not rewrite prior audit, resolution, or annotation records. The new bundle ID is written into `verificationRef` when the verification event is created, and the bundle records the resulting audit-event ID.

### Scientific boundaries

Verification manifests document the artifact set reviewed and, when supplied, byte identity through SHA-256. They do not determine whether a scientific claim is true, causal, important, sufficiently evidenced, or preferred over alternatives.
