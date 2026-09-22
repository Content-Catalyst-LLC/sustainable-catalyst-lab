# Lab v0.122.0 — Bayesian Analysis Workbench II

## Purpose
A governed research-facing Bayesian workflow layered on the existing v0.52 Bayesian inference runtime and the v0.114–v0.121 publication/analysis stack.

## Capabilities
- Explicit prior and posterior comparison.
- Split-R-hat, ESS, MCSE, acceptance-rate and trace diagnostics.
- Declared-threshold convergence audits without automatic certification.
- Posterior predictive checks and discrepancy summaries.
- Posterior probability statements from retained draws.
- Normal-normal hierarchical Bayesian random-effects model with declared priors, population/heterogeneity posteriors and group shrinkage summaries.
- Side-by-side Bayesian model comparison without automatic ranking or winner selection.
- Publication-aware visualization plans, reproducible snapshots, reproduction plans and exports.
- Reference-first Platform Core model-object plan.

## Boundaries
The Workbench never selects priors automatically, certifies convergence, assigns significance labels, selects a model, infers causality, authorizes population generalization, certifies scientific validity, or determines truth. Underlying datasets and model artifacts remain authoritative in Lab.
