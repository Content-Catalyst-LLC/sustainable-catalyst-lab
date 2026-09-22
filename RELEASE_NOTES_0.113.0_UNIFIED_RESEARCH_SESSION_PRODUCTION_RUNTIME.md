# Sustainable Catalyst Lab v0.113.0 — Unified Research Session Production Runtime

## Summary

v0.113.0 production-hardens the Platform Core integration sequence completed in v0.112.0. It adds deterministic operation envelopes, idempotency, explicit submission plans, receipts, retry/recovery planning, checkpoints, continuity, diagnostics, readiness, and round-trip assessment across the existing Core↔Lab research-session stack.

## Added

- Fourteen governed Core-facing operation families.
- Deterministic request hashes, operation refs, correlation refs, and default idempotency keys.
- Explicit submission plans carrying `Idempotency-Key` and `X-SC-Correlation-Ref` headers without embedded authorization material.
- Idempotency states: `new`, `replay-safe`, and `conflict`.
- Declared production receipts with response hashes and Core references.
- Advisory retry plans for declared transport/429/5xx failures.
- Explicit recovery plans with no automatic retry, conflict resolution, or resubmission.
- Project/session production checkpoints and continuity checks.
- Diagnostics across v0.104–v0.112 integration components.
- Production readiness check against Core >=3.0.0 and declared v0.112 contract conformance.
- Seven-stage round-trip planning and declared round-trip assessment.

## Boundaries retained

- Core remains the session/reference authority.
- Lab remains the scientific execution authority.
- HTTP response codes do not automatically establish success.
- No automatic Core submission, retry, recovery, mutation, scientific execution, scientific certification, product-quality certification, or truth determination.

## Compatibility

Minimum Platform Core release: 3.0.0. Newer compatible Core 3.x releases are accepted by semantic minimum-version checks.
