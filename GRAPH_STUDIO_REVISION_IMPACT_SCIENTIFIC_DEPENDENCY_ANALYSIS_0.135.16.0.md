# Sustainable Catalyst Lab v0.135.16.0
## Revision Impact Graph & Scientific Dependency Analysis

v0.135.16.0 extends the Graph Studio provenance-review sequence with explicit revision impact analysis over the loaded declared research graph.

### Core capability

A researcher can select a revision seed and inspect:

- direct downstream objects reachable in one declared dependency hop;
- transitive downstream objects reachable within a bounded traversal;
- upstream dependencies of the revised object;
- shortest declared dependency paths to each reached object;
- edge sets participating in the impact traversal;
- cycle and dangling-reference diagnostics;
- reproducible impact snapshots and before/after snapshot comparisons;
- persistent revision-impact analysis records and Project Workspace handoff.

### Scientific boundary

`potentially affected` is a structural workflow term. It means an object is reachable through declared relationships in the loaded graph. It does **not** mean the object is invalid, false, unsupported, causally changed, or scientifically inferior. The release performs no automatic invalidation, truth ranking, evidence weighting, or causal inference.

### Review lineage

The analysis record can carry a v0.135.13 revision action and revision reference while remaining backward compatible with the v0.135.15 verification-artifact layer. This permits the sequence:

review annotation → revision action → revised scientific object → dependency impact analysis → verification bundle → review audit.

### Project collection

`graphStudioRevisionImpactAnalyses`

### Runtime contract

- max nodes: 5,000
- max edges: 20,000
- max traversal depth: 12
- directions: downstream, upstream, both
- deterministic adjacency ordering
- bounded traversal in cyclic graphs
- no full Graph Studio redraw for impact highlighting
