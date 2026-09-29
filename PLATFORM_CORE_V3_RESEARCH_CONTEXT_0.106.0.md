# Lab v0.106.0 — Unified Project & Research Session Context

Platform Core owns the unified research-session registry and reference graph. Research Lab owns the underlying scientific workspace state and computation.

## Contract surfaces

- Context normalization: stable `context_ref` across project/session/workflow/project-state identity.
- Session registration envelope: `/v1/research/unified-runtime/sessions`.
- Product context binding: `/v1/research/unified-runtime/product-bindings`.
- Contextual object binding: reuses the v0.105 canonical object mapper.
- Contextual handoff binding: `/v1/research/unified-runtime/handoff-bindings`.
- Continuity validation: detects declared project/session/context mismatches; it does not infer identity.

All Core submissions remain explicit and disabled by default. Execution lineage is v0.107.0 scope. Minimum compatible Core release: 3.0.0.
