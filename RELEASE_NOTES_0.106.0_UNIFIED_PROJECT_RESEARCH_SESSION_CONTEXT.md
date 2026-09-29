# Sustainable Catalyst Lab v0.106.0

## Unified Project & Research Session Context

This release extends the v0.104 Core runtime adapter and v0.105 canonical research-object mapper with a shared project/session context layer. Lab can now construct Core v3 session, product-context, object, and handoff envelopes carrying stable project, workflow, project-state, researcher/agent/contributor, and provenance context.

### Boundaries

- Core owns the session registry and cross-product reference graph.
- Lab owns scientific workspace state and scientific execution.
- No automatic Core submission or mutation.
- No automatic scientific execution.
- Execution lineage is deferred to v0.107.0.
- Corrected WordPress Core-integration health checks so they validate WordPress-shipped contracts/includes rather than backend-only Python files.
- Core compatibility uses minimum release 3.0.0 rather than an exact version pin.
