# Lab v0.141.1 — Neural Architecture & Training Configuration

Extends the v0.141.0 Machine Learning Experiment Workspace with governed, framework-neutral neural architecture specifications and explicit training configuration objects. Lab owns experimental design and comparison; Platform Core remains canonical object/provenance authority and Workspace remains execution authority.

## New objects and plans
- architecture families, layers, connections, input/output signatures, declared parameter counts and architecture fingerprints
- optimizer, loss, scheduler, seed, precision, checkpoint, early-stopping, resource and compute-target declarations
- experiment-to-architecture/training bindings
- Workspace execution handoffs and Platform Core object/provenance handoffs
- deterministic declared-configuration fingerprints, snapshots, comparison records and reproducibility packages

## Interpretation boundaries
Architecture specification is not executed behavior. Training configuration is not a successful run. A declared seed does not guarantee determinism. A checkpoint is not an endorsed model. A prediction is not evidence.
