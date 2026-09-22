# Platform Core v3 Production Runtime — Lab v0.113.0

Lab v0.113.0 turns the v0.104–v0.112 Core interoperability stack into an explicit production control plane for Core↔Lab research-session round trips.

## Purpose

The bridge prepares deterministic, auditable operations for Platform Core while preserving the established authority boundary:

- Platform Core remains the reference-first session/orchestration authority.
- Sustainable Catalyst Lab remains authoritative for scientific execution, scientific objects, visuals, investigations, and package contents.
- v0.113.0 never automatically submits a Core request, retries a failed request, performs recovery, executes science, certifies science/product quality, or determines truth.

## Production primitives

The runtime adds:

1. deterministic operation normalization and request hashes;
2. deterministic default idempotency keys and correlation references;
3. explicit HTTP submission plans without credentials;
4. idempotency checks with `new`, `replay-safe`, and `conflict` states;
5. explicit receipts whose success/failure outcome is declared rather than inferred from HTTP status;
6. advisory retry plans with bounded exponential-delay suggestions;
7. recovery plans for failed, uncertain, duplicate, and conflicting receipts;
8. production checkpoints for context/operation/receipt continuity;
9. cross-operation project/session continuity checks;
10. component diagnostics for all v0.104–v0.112 integration layers;
11. production readiness checks against Core >=3.0.0 plus declared v0.112 conformance;
12. explicit seven-stage round-trip plans and declared round-trip assessments.

## Governed operation families

The production runtime can wrap fourteen existing Core-facing operation families: session registration, product-context binding, object binding, execution binding, finding, claim, evidence link, validation challenge, replication, visual binding, package binding, investigation binding, cross-product handoff, and integration-certification planning.

## Idempotency rule

The default idempotency key is derived from the normalized request hash. Reusing the same key with the same request hash is reported as `replay-safe`; reusing the same key with a different request hash is a `conflict`. The bridge does not resolve conflicts or replay requests automatically.

## Receipt rule

A Core response code does not establish the production outcome. Receipts require one declared outcome: `succeeded`, `failed`, `uncertain`, `duplicate`, `conflict`, or `cancelled`. This prevents the control plane from treating an HTTP 2xx response as proof that scientific state, persistence, or downstream integration is correct.

## Readiness boundary

Production readiness requires:

- Core health reports a semantic version >=3.0.0;
- all nine retained integration components report their expected release versions and healthy status;
- the caller supplies a v0.112 certification assessment with `declared_conformance=true`.

This is operational readiness only. It is not scientific-validity certification or product-quality certification.
