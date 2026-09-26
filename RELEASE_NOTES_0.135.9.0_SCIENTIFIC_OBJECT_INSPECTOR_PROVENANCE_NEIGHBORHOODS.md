# Sustainable Catalyst Lab v0.135.9.0

## Scientific Object Inspector, Provenance Neighborhoods & Cross-Workspace Navigation

This release moves Graph Studio beyond the v0.135.8.x recovery line. The native provenance runtime remains authoritative and incremental, while a new object-exploration layer turns selected provenance nodes into governed project-object views.

- 1-hop and 2-hop neighborhoods use only declared project relationships.
- Related objects can be selected directly from the scientific-object inspector.
- Project record metadata is shown when the selected provenance object maps to the active Lab project.
- A selected project record can be handed off to Project Workspace through a presentation-only session focus reference.
- Scope changes do not trigger a full provenance render.
- The release does not infer causal, evidentiary, semantic, or truth relationships.
