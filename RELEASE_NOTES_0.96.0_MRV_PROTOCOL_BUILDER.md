# Sustainable Catalyst Lab v0.96.0 — Carbon & Nature v0.13.0 MRV Protocol Builder

## Added

- Method-derived MRV protocol templates tied to the v0.12.0 foundation-method registry.
- Nine governed protocol sections covering scope, measurement/sampling, calculation, uncertainty, QA/QC, data/provenance, schedule, reporting, and change control.
- Explicit project, boundary, monitoring-period, monitoring-frequency, role/responsibility, evidence, methodology, and source-reference fields.
- Structural validation and method-documentation gap analysis.
- Deterministic protocol and validation fingerprints.
- `ready-for-internal-review` status with explicit non-equivalence to external methodology compliance.
- Draft Carbon Project `monitoring-record` protocol handoff with provenance.
- Lab browser workspace for template loading, protocol construction, validation, project persistence, and packet creation.

## Guardrails

Protocol completeness is not external methodology compliance. The builder does not perform automatic method selection, current-program rule assertions, verification, certification, carbon-credit eligibility, causal attribution, or hidden sampling/measurement/factor inference.

## WordPress runtime packaging

The v0.95 runtime-only WordPress packaging boundary is retained. Python backend source, repository tests, SDKs, examples, and historical documentation remain outside the WordPress plugin ZIP. No `.venv` tree is packaged.
