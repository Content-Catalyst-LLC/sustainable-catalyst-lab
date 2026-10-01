# Sustainable Catalyst Lab v0.163.0.1 — Institutional Governance Configuration Namespace & Backend Startup Repair

This patch repairs the production startup failure introduced by v0.163.0. The v0.163 federation manager referenced settings such as `institutional_governance_max_bodies`, but the established `SC_LAB_INSTITUTIONAL_GOVERNANCE_*` namespace already belongs to the older institutional-governance subsystem and does not define those fields.

## Repair

- Introduces a dedicated `institutional_review_federation_*` Settings namespace.
- Introduces dedicated `SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_*` environment variables.
- Keeps the existing `institutional_governance_*` / `SC_LAB_INSTITUTIONAL_GOVERNANCE_*` subsystem unchanged.
- Rebinds the v0.163.0 federation manager to the new namespace.
- Adds a release-time startup-binding test that resolves every Settings attribute used by the manager constructor.
- Adds a v0.163.0.1 health capability while preserving the v0.163.0 feature version.
- Updates the Contabo deployer to use the new DB path and to restore the pre-deploy backend automatically when post-start health verification fails.

`releaseVersion = 0.163.0.1`  
`featureVersion = 0.163.0`

The scientific/governance semantics of v0.163.0 are unchanged.
