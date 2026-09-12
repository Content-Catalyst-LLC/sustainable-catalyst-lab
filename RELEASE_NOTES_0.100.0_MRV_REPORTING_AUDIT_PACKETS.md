# Sustainable Catalyst Lab v0.100.0
## Carbon & Nature Intelligence v0.17.0 — MRV Reporting & Audit Packets

### Added

- Structured MRV report builder with three internal report types.
- Eight-section Sustainable Catalyst internal reporting scaffold.
- Explicit reporting-period validation.
- Declared metric registry that preserves values, units, source references, and uncertainty references without silent recalculation.
- Deviation and corrective-action register with open/resolved/internal-review states.
- Integration with the v0.16 Verification Evidence Ledger, including optional deterministic chain recomputation.
- Audit-preparation packet with component index, section fingerprints, supporting-artifact index, optional SHA-256 digests, unresolved-item summary, and deterministic packet fingerprint.
- Carbon Project `verification-record` handoff for MRV reporting/audit-preparation state.
- New Lab workspace panel, WordPress REST proxies, browser module, CSS, JSON contracts, Python engine, tests, and Contabo upgrader.

### Governance boundaries

- `ready-for-internal-review` is not external verification.
- `ready-for-internal-audit-preparation` is not auditor approval.
- A valid evidence-ledger hash chain is not source-authenticity proof.
- The report template is an internal Sustainable Catalyst scaffold, not an asserted external methodology/program template.
- Reported metrics are not recalculated by the reporting layer.
- No methodology compliance, certification, credit eligibility, or credit issuance is determined.

### Versioning

The active host line intentionally advances to **Lab v0.100.0**. It does not reuse `v1.0.0`, because this repository already contains a historical Lab 1.0.0 release identity and related v1000 production-platform artifacts.
