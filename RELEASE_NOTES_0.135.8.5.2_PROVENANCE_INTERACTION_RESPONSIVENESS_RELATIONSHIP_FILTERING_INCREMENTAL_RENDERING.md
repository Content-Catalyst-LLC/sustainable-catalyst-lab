# Sustainable Catalyst Lab v0.135.8.5.2

## Provenance Interaction Responsiveness, Relationship Filtering & Incremental Rendering

v0.135.8.5.2 is a Graph Studio hardening release. It preserves the Renderer 3.1/native-provenance architecture while removing full graph reconstruction from ordinary interaction.

### Fixed

- Relationship selector now remains mounted while a relationship filter is applied.
- `All relations` can be changed to a concrete relationship and restored.
- Layout buttons update geometry without rebuilding Graph Studio controls.
- Node/edge selection updates selection state and the inspector incrementally.
- Traversal and relationship filtering update visibility incrementally.
- Project-state writes are debounced to reduce interaction latency and store churn.

### Diagnostics

The native provenance status now reports full-render count, incremental-update count, last-interaction timing, cache writes, project persistence writes, visible nodes/edges, and the active relationship filter.

### Acceptance

The Chromium fixture must keep the relationship `<select>` node identity stable, reduce `sourced-from` to one visible edge on the sample graph, keep `fullRenderCount` unchanged during ordinary interaction, and increase `incrementalUpdateCount`.
