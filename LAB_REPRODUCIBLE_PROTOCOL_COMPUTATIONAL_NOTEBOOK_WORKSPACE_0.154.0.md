# Lab v0.154.0 — Reproducible Protocol & Computational Notebook Workspace

## Purpose

Turn the stable 4D Computational Research Workspace into a reproducible scientific workflow by binding computational scenes and results to explicit protocols and versioned notebooks.

## Architecture

- **Platform Core** remains the canonical object/contract authority.
- **Lab** stores project-linked protocol and notebook records plus immutable revisions.
- **Python Compute Core** remains the execution authority for registered scientific methods.
- **v0.153.0 4D workspace assets** remain the persistent computational-scene layer.
- **v0.154.0 protocols** declare purpose, ordered steps, method references, input/workspace references, parameters, and acceptance criteria.
- **v0.154.0 notebooks** preserve typed cells, workspace references, compute-result references, linked protocol identity, notes, and immutable revision history.
- **Reproduction manifests** bind the latest notebook revision, linked protocol revision, workspace references, compute references, and registered method names into a SHA-256-verifiable manifest.

## Notebook cell types

- `markdown`
- `parameter`
- `compute-call`
- `result-ref`
- `figure-ref`
- `protocol-ref`
- `workspace-ref`

`compute-call` is a registered-method specification. It is not an arbitrary code cell. Execution occurs only when the user explicitly requests it through the governed Compute Core endpoint.

## Storage

Default backend database:

`/app/data/sc-lab-protocol-notebook-v01540.sqlite3`

The deploy script binds this path to the existing persistent `/app/data` volume.

## Scientific boundary

Protocol, notebook, workspace, result-reference, and manifest persistence improves reproducibility and traceability. It does not establish evidence, causality, statistical significance, calibration, forecast skill, or scientific validity. Human scientific review remains required.
