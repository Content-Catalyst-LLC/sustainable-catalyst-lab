# Sustainable Catalyst Lab 0.104.0 — Platform Core v3 Runtime Adapter & Capability Registration

Lab v0.104.0 begins the formal integration of Sustainable Catalyst Lab with Platform Core v3.0.0.

## Added

- Platform Core v3 runtime adapter with canonical Lab identity as `product:sustainable-catalyst-lab`.
- Explicit compatibility with `sc.research.unified-runtime-contract.v1` and `sc.research.unified-research-scientific-investigation-runtime.v1`.
- Core contract product-registration payload generation.
- Core v3 per-session product-binding payload generation.
- Unified research session/runtime-context normalization.
- Cross-product handoff validation for Core-to-Lab handoffs.
- Platform Core v3 readiness and architectural-boundary compatibility checks.
- WordPress health, manifest, and schema surfaces for release/runtime introspection.
- Mirrored JSON contracts in the WordPress and Python backend trees.

## Architectural boundary

Platform Core remains the reference-first orchestration, research-object, provenance, validation, package, and session layer. Research Lab remains the scientific-execution authority. v0.104.0 does not automatically call or mutate Core, does not automatically execute scientific work when a handoff is received, and does not infer scientific truth or certify scientific validity.

## Compatibility

- Required Platform Core release: v3.0.0.
- Existing Lab v0.38.0/v0.38.1 research interoperability and typed cross-product handoff contracts remain available.
- Canonical Lab-to-Core research object mapping is intentionally deferred to Lab v0.105.0.
