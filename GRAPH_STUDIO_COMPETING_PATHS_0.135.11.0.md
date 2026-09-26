# Graph Studio v0.135.11.0 — Competing Paths & Evidence Context

This release extends the v0.135.10.0 two-object provenance path layer without replacing the native v0.135.8.5.x provenance controller.

## Runtime model

Graph Studio continues to treat the native provenance model as the authoritative visual graph. v0.135.11.0 reads the A/B anchors, direction mode, and hop bound from v0.135.10.0, enumerates multiple bounded simple paths, and applies only CSS/class-level path emphasis to the already-mounted graph.

The release does not rebuild the graph when the active candidate changes. Path selection changes the active path state, edge/node classes, the comparison inspector, and the Project Workspace handoff packet.

## Candidate paths

Candidate enumeration is deterministic and bounded. It supports directed lineage and structural traversal, at most 12 hops, and at most 10 returned paths. Paths are simple: a node cannot repeat within the same candidate path.

The runtime does not claim candidate paths are mutually exclusive scientific hypotheses. They are alternative declared graph routes between two governed objects and can be used as inputs to human research review.

## Evidence context

An edge may carry an explicitly declared `evidenceContext` / `evidenceState` value of `supporting`, `contradicting`, or `neutral`. If no supported value is stored, the edge is reported as `unclassified`.

No evidence category is inferred from the relationship label, graph geometry, node type, source, or path length. Counts are descriptive only and are not converted into scores, weights, rankings, truth probabilities, or preferred explanations.

## Project Workspace handoff

The handoff packet contains A/B object identity, candidate paths, the selected path index, ordered relationship steps, declared evidence-context counts, and a scientific-boundary statement. The handoff is presentation/research context and does not mutate scientific objects.
