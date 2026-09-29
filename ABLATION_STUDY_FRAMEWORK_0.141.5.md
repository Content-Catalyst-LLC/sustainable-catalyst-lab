# Sustainable Catalyst Lab v0.141.5 — Ablation Study Framework

## Purpose
Add a governed research layer for controlled neural-model ablation studies without moving training execution into Lab.

## Architecture
**Platform Core defines canonical objects → Workspace executes variants/training → Lab plans, audits, compares, visualizes, and packages ablation studies.**

## Primary objects
- Ablation Study Plan
- Ablation Factor
- Baseline Variant
- Ablation Variant
- Controlled Contrast Audit
- Paired Metric Delta Matrix
- Component Effect Summary
- Replicate Summary
- Confounding Audit
- Ablation Visualization Specification
- Deterministic Ablation Snapshot
- Reproducibility Package

## Scientific boundaries
An ablation delta is not automatically a causal effect. A metric change is not scientific superiority. Multi-factor changes do not establish interactions without an explicit design/estimand. Lab does not automatically rank variants, select a winner, promote a model, or treat predictions/results as evidence.

## Release lineage
v0.141.4 Hyperparameter Study & Search Results → **v0.141.5 Ablation Study Framework** → v0.141.6 Neural Explainability Workspace.
