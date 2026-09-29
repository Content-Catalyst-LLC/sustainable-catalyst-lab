# Lab v0.141.0 — Machine Learning Experiment Workspace

## Purpose
Lab v0.141.0 makes machine-learning experiments first-class governed scientific studies inside Sustainable Catalyst Lab.

## Ownership boundary
- **Platform Core defines** governed neural/model/dataset/transformation/checkpoint/prediction objects.
- **Workspace computes** training and inference workloads across CPU, Apple MPS, CUDA, and remote GPU targets.
- **Lab experiments**: research objectives, experiment designs, comparisons, interpretation, provenance, and reproducibility.
- **Downstream products consume** governed results without converting model output into evidence by default.

## Capabilities
- ML experiment object and lifecycle
- dataset/feature/transformation lineage
- Core model-specification binding
- training-plan construction without local training execution
- Workspace execution handoff and returned-result ingestion
- run registry, checkpoint index, and metric series
- experiment matrix and pairwise comparison without automatic winner selection
- provenance graph
- prediction registry with explicit `prediction != evidence` status
- deterministic snapshots and comparison
- reproducibility package
- v0.140.0 Scientific Research OS handoff
- retained v0.139.0.1 release-manifest integrity baseline

## Scientific boundaries
The release does not train models inside Lab, automatically select a best model, certify scientific validity, infer causal truth, rank evidence, or promote predictions to evidence. Learned graph or embedding relationships remain model outputs unless independently established through governed evidence processes.
