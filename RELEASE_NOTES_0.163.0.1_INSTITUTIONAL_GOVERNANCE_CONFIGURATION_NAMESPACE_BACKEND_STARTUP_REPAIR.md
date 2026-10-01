# Release Notes — Lab v0.163.0.1

## Fixed

- Corrected the v0.163.0 backend crash loop caused by a configuration namespace collision.
- Added the missing dedicated federation settings under `institutional_review_federation_*`.
- Rebound the v0.163 manager constructor to the dedicated namespace.
- Preserved the existing `institutional_governance_*` settings and database contract.
- Added a startup-binding regression test so undefined Settings references in the v0.163 constructor fail local validation.
- Added rollback-on-health-failure behavior to the Contabo deployment script.

## Compatibility

The v0.163.0 governance API, object schemas, database semantics, WordPress proxy routes, and human-governance boundaries are retained. This is a startup/configuration repair, not a new scientific feature release.
