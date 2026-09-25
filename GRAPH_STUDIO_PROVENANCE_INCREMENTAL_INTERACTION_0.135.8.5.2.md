# Graph Studio v0.135.8.5.2 — Provenance Interaction Responsiveness, Relationship Filtering & Incremental Rendering

This patch hardens the native provenance runtime introduced in v0.135.8.5 and made authoritative in v0.135.8.5.1.

## Changes

- Relationship filtering listens to both `input` and `change` and no longer destroys/recreates the selector.
- Node and edge selection update classes and the inspector without a full graph render.
- Upstream, downstream, focus, and relation filters update visibility incrementally.
- Layered, radial, and swimlane layout changes update node/edge geometry in-place.
- Zoom and fit update only the camera transform.
- Local presentation-state cache is written immediately; Lab project persistence is debounced by 220 ms.
- Runtime diagnostics expose `fullRenderCount`, `incrementalUpdateCount`, `lastInteractionMs`, `cacheWrites`, and `projectPersistenceWrites`.
- Scientific records are not mutated by presentation interaction.

## Browser acceptance

Chromium executes the exact release JavaScript in a DOM fixture. The release gate verifies node selection, radial geometry, relationship filtering, selector identity stability, upstream traversal, incremental-update counts, stable full-render count, and debounced project-state persistence.
