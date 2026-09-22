# Sustainable Catalyst Lab 0.105.0 — Canonical Research Object Mapping

Lab v0.105.0 advances the Platform Core v3 integration line by mapping Lab's scientific research objects into Core v3 first-class object references.

## Added

- 20-type Lab-to-Core canonical object mapping catalog.
- Stable Lab-authoritative object references and optional version references.
- SHA-256 content identity without copying scientific payloads into Core.
- Core v3 `object-bindings` request generation, including the exact Core `{"data": ...}` envelope.
- Batch binding generation with duplicate-reference rejection.
- v0.38.1 typed cross-product handoff → Core v3 object-binding bridge.
- First-class scientific-figure object identity.
- WordPress health/catalog/schema surface for the mapping capability.
- Mirrored frontend/backend JSON mapping contracts.

## Preserved boundaries

- Platform Core remains reference-first.
- Research Lab remains authoritative for underlying scientific objects.
- No automatic Core submission.
- No automatic scientific execution.
- No object payload duplication into Core.
- No execution/visual/package specialized binding inference ahead of their planned builds.

## Compatibility

- Platform Core required release: 3.0.0
- Retained runtime adapter feature: Lab v0.104.0
- Retained typed handoff bridge: v0.38.1
- FastAPI path-route target: 1,015
- Canonical mapping count: 20
