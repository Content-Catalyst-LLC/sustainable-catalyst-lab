# Sustainable Catalyst Lab v0.38.0 Validation Report

## Release

**Sustainable Catalyst Research Interoperability Layer**

## Backend validation

- 302 current backend tests collected across 39 files.
- 289 pre-hardening integration tests passed across the complete v0.27.0–v0.37.2 stack.
- 13 focused v0.38.0 interoperability tests passed after final workspace-boundary, profile-product, and receipt-state hardening.
- 33 retained scientific-domain and instrumentation regression tests passed on the final source.
- 335 tests validated in total.

The monolithic pytest process can remain open after assertions because several retained FastAPI and worker suites keep application lifespans alive. Release validation therefore used fresh per-suite processes and clean database paths, which is the established Lab release-validation method.

## Live interoperability proof

The live proof completed:

1. Workspace-governed Lab and Decision Studio profile registration.
2. Contract and capability negotiation for `sc-research-dataset/1.0`.
3. Canonical handoff creation and sealing.
4. SHA-256 bundle export.
5. Idempotent envelope import.
6. HMAC-SHA256 acceptance receipt creation and verification.
7. Immutable event timeline inspection.

The proof contains no secrets, credentials, restricted dataset bytes, or executable payloads.

## Static and contract validation

- 138 Python files parsed.
- 109 PHP files passed syntax checks.
- 119 JavaScript files passed syntax checks.
- 404 JSON documents parsed.
- 294 JSON Schemas validated.
- 611 critical integrity hashes verified.
- 76 route aliases validated.
- 77 registered Lab modules confirmed in the release manifest.

## Security and governance assertions

- Cross-workspace profile identifier takeover is rejected.
- Source and target profiles must match the handoff products.
- Draft handoffs cannot receive final receipts.
- Imported envelope hashes are independently recomputed.
- Duplicate imports are idempotent.
- Arbitrary code, callbacks, secrets, credentials, embedded bytes, and restricted raw-data fields are rejected.
- Receipt signatures are verified using constant-time comparison when HMAC signing is configured.
- Withdrawals retain historical records; accepted handoffs require superseding records rather than destructive withdrawal.

## Installer proofs

- Current-baseline packaged-ZIP bridge: v0.37.2 → v0.38.0: 54 files changed, 2,094 insertions, 56 deletions
- Historical packaged-ZIP bridge: v0.31.1 → v0.38.0: 439 files changed, 41,515 insertions, 147 deletions

## Archive integrity

- Source payload files: 1,073
- Critical release hashes: 611
- Prohibited archived files: 0
- Archive CRC and single-root checks: passed for all four release archives
