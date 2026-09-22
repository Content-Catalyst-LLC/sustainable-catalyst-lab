# Platform Core v3 Scientific Investigation Integration — Lab v0.111.0

## Canonical Core target

`POST /v1/research/unified-runtime/investigation-bindings`

Core's investigation binding stores `session_id`, `investigation_ref`, `investigation_type`, `evidence_refs[]`, `claim_refs[]`, `hypothesis_refs[]`, visibility, and metadata. Lab v0.111.0 keeps richer scientific asset references in namespaced metadata and integration requirements.

## Authority boundary

Platform Core is a reference-first orchestrator. Sustainable Catalyst Lab remains authoritative for the underlying scientific investigation, models, datasets, experiments, analyses, executions, scenes, validation work, and reproducibility packages.

Core does not execute scientific work, infer findings, rank evidence, resolve contradictions, select hypotheses, infer causality, certify scientific validity, or determine truth.

## Integration plan

The v0.111 plan creates the canonical investigation-binding envelope and enumerates existing specialist bindings that should already exist or be created separately through the v0.105-v0.110 bridges. It never fabricates execution/visual/package data merely from a reference and never submits to Core automatically.
