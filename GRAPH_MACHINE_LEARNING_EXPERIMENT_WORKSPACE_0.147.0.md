# Lab v0.147.0 — Graph Machine Learning Experiment Workspace

v0.147.0 builds on the classical graph/network-science foundation introduced in v0.146.0 and adds a governed graph-machine-learning research surface.

## Scope
- Node, edge, and graph classification/regression research objects.
- Link-prediction candidate objects that never establish relationships automatically.
- Node/edge/graph anomaly detection result objects.
- Graph/node/edge embedding and representation-learning objects.
- GNN model and run objects with graph-specific split, label, feature, and execution provenance.
- Graph-specific leakage audits: split overlap, feature leakage, temporal leakage, negative-sampling contamination, and transductive/inductive scope.
- Evaluation, calibration, ranking, robustness, sensitivity, uncertainty, OOD, fairness, and explainability audits.
- Workspace/Workbench execution handoffs, Platform Core canonical-object handoff, Research OS handoff, deterministic snapshots, export, reproducibility, and publication handoffs.

## Architectural rule
Platform Core defines canonical graph-ML research contracts. Workspace trains and runs graph-ML models. Workbench prototypes algorithms. Lab structures experiments, interprets returned outputs, compares results, audits validity boundaries, visualizes, reviews, and packages reproducible research.

## Epistemic rule
A predicted link is a candidate relationship, not an evidence edge. Prediction, anomaly score, embedding proximity, explanation, or benchmark score does not automatically become scientific evidence or scientific validity.
