# Sustainable Catalyst Lab v0.141.0
## Machine Learning Experiment Workspace

v0.141.0 begins the Lab neural experimentation line. It integrates the repaired v0.139.0.1 release-integrity baseline and the intended v0.140.0 Scientific Research Operating System milestone, then adds a governed machine-learning experiment workspace.

### Added
- first-class ML experiment records and lifecycle
- dataset, feature, and transformation provenance views
- Platform Core neural/model object contract binding
- Workspace neural-execution request/result contracts
- declared CPU, MPS, CUDA, and remote-GPU compute targets
- run, checkpoint, metric, prediction, and artifact registries
- experiment comparison matrix with no automatic winner
- prediction/evidence separation
- deterministic experiment snapshots and reproducibility packages
- Research OS bridge for study-level continuity

### Architecture
`Platform Core defines → Workspace computes → Lab experiments → products consume.`

### Safety / epistemic contract
`prediction ≠ evidence` and `model score ≠ scientific validity`. Lab does not execute training in this release and does not silently adjudicate model quality or scientific truth.
