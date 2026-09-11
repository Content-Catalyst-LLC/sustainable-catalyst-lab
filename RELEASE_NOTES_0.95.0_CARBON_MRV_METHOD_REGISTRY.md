# Sustainable Catalyst Lab v0.95.0 — Carbon & Nature v0.12.0 Carbon MRV Method Registry

## Added

- Seven governed MRV method-family profiles with stable keys and deterministic fingerprints.
- Registry list/detail/filter APIs.
- Non-ranking descriptive method comparison.
- Documentation-readiness assessment against explicit named requirements.
- Library methodology crosswalks and source-role provenance.
- Draft Carbon Project `monitoring-record` packet handoff.
- Lab UI for method browsing, readiness, comparison, project save, and packet construction.
- Runtime-only WordPress package profile to reduce browser upload file count.

## Guardrails

Documentation readiness is not methodology eligibility. The registry is not an external MRV protocol and does not perform verification, certification, current-program compliance determinations, credit eligibility, or automatic method selection.

## WordPress runtime packaging

v0.95.0 introduces a runtime-only WordPress distribution. Repository tests, Python backend source, SDK material, examples, and release-history documentation are excluded from the plugin ZIP; the backend remains a separate deployment artifact. This reduces browser upload/unpack pressure while preserving PHP, templates, browser assets, governed contracts, static scientific data, and the canonical release manifest.

The exact final tiny-patch installer was rehearsed against an isolated clean v0.94.0 Git baseline through release validation, simulated main push, and simulated `lab-v0.95.0` tag push. No user repository or production service was modified by that rehearsal.
