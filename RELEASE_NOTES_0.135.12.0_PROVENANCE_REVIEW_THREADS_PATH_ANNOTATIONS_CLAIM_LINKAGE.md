# Sustainable Catalyst Lab v0.135.12.0

## Provenance Review Threads, Path Annotations & Claim Linkage

This release extends Graph Studio competing-path analysis with a structured review layer.

### Added

- Provenance review threads bound to the current A/B comparison.
- Reviewer-authored path, edge, node, Object A, and Object B annotations.
- Annotation kinds for observation, question, limitation, explicit claim linkage, and evidence notes.
- Explicit claim/record references for `claim-link` annotations.
- Path-specific annotation retention when switching candidate paths.
- Incremental visual marking without full graph redraw.
- Explicit project persistence to `graphStudioReviewThreads`.
- Project Workspace review-context handoff.
- Backend normalization, summaries, explicit claim-link extraction, deterministic fingerprints, contracts, and review packets.

### Boundaries

The release does not infer claim links, truth, causation, evidentiary weight, scientific preference, or scientific validity from graph structure or annotation text.
