# Sustainable Catalyst Lab v0.50.0 — Reproducible Model Packages, Registry & Research Bundles

## Release purpose

v0.50.0 turns the v0.49 shared computational model into a durable, portable and independently verifiable research object. A model package freezes the model definition together with its data context, methods, results, figures, runtime environment, assumptions, limitations and provenance.

## Added

- `sc-lab-reproducible-model-package/0.50.0`
- `sc-lab-model-research-bundle/0.50.0`
- `sc-lab-model-package-registry-projection/0.50.0`
- Model Studio reproducibility workspace
- Dataset reference or bounded snapshot capture
- Method/result/figure attachment
- Backend environment capture and dependency lock hash
- Per-component SHA-256 hashes
- Immutable package hash
- Package verification endpoint and UI
- Portable JSON package export
- Portable ZIP research bundle export with `SHA256SUMS`
- Scientific Model Registry projection and immutable version registration
- Project persistence in `reproducibilityBundles`

## Portable ZIP contents

- `manifest.json`
- `model.json`
- `dataset.json`
- `methods.json`
- `results.json`
- `figures.json`
- `environment.json`
- `provenance.json`
- `registry-projection.json`
- `package.json`
- `README.txt`
- `SHA256SUMS`

## Scientific boundaries

- Arbitrary executable code remains disabled.
- Embedded scripts, callbacks, shell commands and executable payload fields are rejected.
- Dataset snapshots are capped at 5,000 rows in this direct package workflow.
- Package payloads are capped at 8 MiB.
- Registry registration creates immutable semantic versions and does not auto-promote them.
- Publication remains operator-controlled.
- Workbench exchange remains governed by the v0.49 shared computational model contract.

## Preserved interface and capabilities

- v0.48.3 contextual six-destination navigation remains unchanged.
- The three related-application cards remain unchanged.
- Graph Studio front door remains unchanged.
- v0.49 Lab ↔ Workbench exchange remains available.
- v0.42–v0.48 scientific modeling, diagnostics, dynamic systems, response surfaces and probabilistic analysis remain intact.

## Validation

The release gate runs 146 focused scientific/modeling Python tests plus v0.50 browser/PHP/runtime-integrity checks, syntax validation, FastAPI route assertions and complete release-manifest hash verification.
