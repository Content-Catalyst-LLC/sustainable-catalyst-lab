# Sustainable Catalyst Lab v0.135.11.0
## Provenance Hypothesis Comparison, Competing Paths & Evidence Context

### Added
- Bounded enumeration of multiple simple provenance paths between the v0.135.10.0 Graph Studio A/B anchors.
- Deterministic candidate ordering with configurable maximum candidate count.
- Incremental active-path switching without full native graph reconstruction.
- Side-by-side candidate-path summaries in the Graph Studio inspector.
- Explicit declared evidence-context summaries for supporting, contradicting, neutral, and unclassified edges.
- Project Workspace comparison handoff containing all candidate paths and the selected path.
- WordPress and FastAPI health/acceptance contracts for the new layer.

### Scientific boundaries
- The release does not rank candidate paths.
- It does not infer causation, scientific validity, evidentiary strength, or a preferred explanation.
- Supporting/contradicting labels are displayed only when explicitly declared in edge metadata.
- The underlying governed scientific graph is not mutated by candidate selection.

### Compatibility
- Retains v0.135.8.5.x native provenance authority.
- Retains v0.135.9.0 object explorer/neighborhood navigation.
- Retains v0.135.10.0 A/B bounded path analysis as the anchor/context source.
