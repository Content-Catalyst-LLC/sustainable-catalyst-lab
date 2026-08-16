# Sustainable Catalyst Lab v0.68.0 — Hierarchical, Multilevel & Cross-Study Modeling

## Release intent
v0.68.0 adds governed aggregate hierarchical modeling above the v0.67 causal-inference line. It supports explicit partial pooling and structured variation across groups, sites, cohorts, institutions, regions, and studies while keeping heterogeneity, shrinkage, moderator range, scope, and human review visible.

## Added
- Hierarchical normal / empirical-Bayes partial pooling from aggregate unit estimates and reported standard errors.
- Random-intercept cluster pooling using aggregate within-cluster estimates followed by between-cluster partial pooling.
- Random-slope / one-moderator random-effects meta-regression with residual heterogeneity reporting.
- Cross-study random-effects pooling and cross-study meta-regression with required source provenance.
- DerSimonian–Laird between-unit variance (`tauSquared`), Cochran Q, I², pooled confidence intervals, and explicit unit shrinkage diagnostics.
- Random-slope/meta-regression intercept, slope, uncertainty intervals, observed moderator range, residuals, and residual heterogeneity.
- Explicit population and generalization boundaries before a model can reach a bounded interpretation state.
- Human multilevel-model review: Accept within stated scope, Accept with qualification, Block interpretation, Reopen.
- Project collections `scientificHierarchicalModelsV0680` and `scientificHierarchicalUnitEstimatesV0680`.
- Tamper-evident `hierarchical-modeling-v0680` evidence packets in `analysisPackets`.

## Interpretation gates
- `needs-units`
- `needs-study-provenance`
- `weak-group-structure`
- `needs-moderator-variation`
- `model-fit-blocked`
- `needs-generalization-boundary`
- `heterogeneity-caution`
- `needs-review`
- `blocked`
- `multilevel-estimate-bounded`
- `multilevel-estimate-bounded-with-qualification`

## Scientific boundaries
A bounded multilevel estimate summarizes modeled variation among the recorded aggregate units under stated assumptions. It does not establish universal population transportability, ecological inference, automatic model correctness, or causal proof. High heterogeneity requires qualified human review. Raw participant-level records, automatic generalization, hidden model selection, network fetching during evaluation, and arbitrary code execution remain disabled.

## Interface
The capability is contextual inside the existing Scientific Workflows workspace. The six-destination rail, Graph Studio front door, and Prototyping Workbench / Decision Studio / Site Intelligence card row remain unchanged.
