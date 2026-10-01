# Build Lab v0.155.0

Release: **Batch Experiment, Sweep & Ensemble Orchestration**

This build adds a governed research-campaign layer above the existing Lab workflow/campaign/ensemble primitives. It creates bounded reproducible trial matrices and explicit Workspace execution handoffs for parameter sweeps, hyperparameter searches, Monte Carlo campaigns, factorial designs, repeated trials, and ensembles.

## Core capabilities

- deterministic trial specifications and SHA-256 trial hashes
- deterministic random-seed lineage
- parameter sweep and factorial grid generation
- bounded random hyperparameter/Monte Carlo generation
- repeated-trial and ensemble campaign expansion
- persistent SQLite/WAL campaign and trial state
- explicit Workspace/runtime execution handoffs; no automatic dispatch
- per-trial execution/result references and metrics
- partial-failure campaign state
- explicit failed-trial retry with attempt lineage
- descriptive metric aggregation
- hash-chained campaign/trial events
- digest-verifiable campaign reproduction manifests
- WordPress campaign workspace and authenticated HMAC proxy routes

## Scientific boundary

The release does not execute arbitrary code, autonomously dispatch compute, infer causal relationships, establish statistical significance, or establish scientific/model validity. Lab coordinates campaign specifications and provenance; Workspace/runtime infrastructure remains the execution authority, and human scientific review remains required.

## Retained baselines

- v0.154.0 Reproducible Protocol & Computational Notebook Workspace
- v0.153.0 4D Computational Research Workspace
- v0.152.0.13 front-door layout/render recovery
