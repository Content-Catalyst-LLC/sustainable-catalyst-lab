# Lab v0.139.0.1 — WordPress Release Manifest Scope & Integrity Repair

## Defect repaired
Lab v0.139.0 generated `wordpressCriticalFiles` from the repository surface while the WordPress package intentionally excluded repository-only directories such as `scripts/`, `tests/`, `sdk/`, `examples/`, `docs/`, and `backend/`. The installed plugin therefore could never satisfy its own manifest verification contract.

## Repair
- Rebuild `wordpressCriticalFiles` from the exact WordPress package inclusion policy.
- Keep backend integrity hashes independently scoped to the backend package.
- Add packaging validation that extracts the WordPress ZIP and verifies every manifest-listed WordPress-critical file exists and matches SHA-256.
- Preserve v0.139.0 scholarly/original-research semantics unchanged.
- Add a backend diagnostic health/policy surface for this repair line.

## Upgrade gate
Do not proceed to v0.140.0 until `/wp-json/sc-lab/v1/runtime/health` reports `state: verified`, `partialInstallRisk: false`, and `routeIntegrityVerified: true`.
