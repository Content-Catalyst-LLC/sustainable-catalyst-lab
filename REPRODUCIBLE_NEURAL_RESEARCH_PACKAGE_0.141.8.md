# Sustainable Catalyst Lab v0.141.8 — Reproducible Neural Research Package

## Purpose

v0.141.8 consolidates the Lab neural research line into a governed, fingerprinted research package that can be inspected, exported, handed to Workspace for a rerun attempt, handed to Platform Core as a canonical governed object, and connected back to the Scientific Research Operating System.

The package is a manifest plus verifiable references. It does not flatten the underlying scientific objects into an opaque archive and does not claim that packaging alone reproduces a result.

## Neural research lineage consolidated

- v0.141.0 — Machine Learning Experiment Workspace
- v0.141.1 — Neural Architecture & Training Configuration
- v0.141.2 — Training Curves, Metrics & Checkpoint Visualization
- v0.141.3 — Model Comparison & Experiment Matrix
- v0.141.4 — Hyperparameter Study & Search Results
- v0.141.5 — Ablation Study Framework
- v0.141.6 — Neural Explainability Workspace
- v0.141.7 — Embedding Explorer

## Package contents

The package supports research context, dataset/split lineage, code references, model architecture, training configuration, execution environment, seed/determinism declarations, execution lineage, telemetry, checkpoints, model comparisons, hyperparameter studies, ablations, explanation artifacts, embedding artifacts, provenance, limitations, review records, reproduction instructions, and publication handoffs.

Every component can carry a source release/schema, reference, SHA-256, dependencies, run/model/checkpoint/dataset references, provenance reference, environment reference, and a verification state.

## Verification states

`unverified`, `declared`, `hash-verified`, `runtime-verified`, `independently-reproduced`, and `independently-replicated` are deliberately distinct states. A declared hash is not treated as proof that an artifact was independently verified, and a successful rerun is not silently relabeled an independent replication.

## Reproduction workflow

Workspace remains the execution authority. Lab builds the package and reproduction instructions, Workspace performs the requested rerun, and returned artifacts can be compared against the package. Any override to a rerun request requires new lineage rather than mutating the original package.

Platform Core remains the canonical governed-object authority. Research OS receives an explicit reproduction-phase handoff without automatic phase advancement.

## Epistemic boundary

Package completeness is descriptive. It is not scientific validity, methodological quality, correctness, successful reproduction, independent replication, causal proof, model superiority, evidentiary status, or publication acceptance.

The package retains all prior neural guardrails: prediction is not evidence; embedding proximity is not a real-world relationship; explanation output is not causal proof; ablation delta is not causal effect; metric superiority is not scientific superiority.
