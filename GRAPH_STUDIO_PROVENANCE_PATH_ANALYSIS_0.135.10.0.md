# Graph Studio Provenance Path Analysis — v0.135.10.0

This release adds a non-mutating analytical overlay above the v0.135.8.5.3 native provenance controller and v0.135.9.0 object explorer.

## Runtime ownership
The native provenance controller remains the sole graph renderer and interaction owner. v0.135.10.0 subscribes to native provenance state and modifies only presentation classes plus its own comparison controls. It does not call `renderTo()` or rebuild the SVG for path changes.

## Path semantics
- **Directed lineage** follows declared `from -> to` edge orientation.
- **Structural path** may traverse a declared edge in either direction and records whether each step is forward or reverse.
- Search is deterministic breadth-first traversal with a configurable 1–12 hop bound.
- A missing bounded path is not treated as evidence that no relationship exists outside the loaded graph.

## Scientific boundary
A path is a sequence of declared graph relationships. It is not a causal claim, evidence-quality judgment, semantic-similarity score, ranking, or scientific-validity determination.

## Cross-workspace context
The handoff stores the two selected objects, mode, hop bound, and ordered declared steps in session storage for Project Workspace. No project scientific record is mutated.
