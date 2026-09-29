# Lab v0.135.9.0 — Scientific Object Inspector, Provenance Neighborhoods & Cross-Workspace Navigation

## Architecture

The v0.135.8.5.x native provenance controller remains the sole interaction owner. v0.135.9.0 layers object exploration on top of its stable state events rather than taking over rendering.

### New capabilities

1. **Governed object inspector** — selected nodes resolve to active-project records when possible and expose stable identifiers, record type, collection, status, method/source references, and declared incoming/outgoing relations.
2. **Bounded provenance neighborhoods** — 1-hop and 2-hop scopes are computed from the current declared graph. Nodes outside the selected scope are presentation-dimmed without changing the scientific graph.
3. **Related-object navigation** — incoming and outgoing declared neighbors are selectable from the inspector.
4. **Project Workspace handoff** — Graph Studio can store a session-scoped focus reference and navigate to Project Workspace, which applies the record title as an initial local filter and displays the focused object identity.
5. **Incremental behavior** — scope changes use DOM class updates only. The base provenance full-render counter must not increase.

### Scientific boundary

Neighborhood membership means only that a declared project relationship connects the records within the requested hop depth. It is not evidence strength, causal structure, semantic similarity, or a truth claim.
