# Lab v0.125.0 — Causal Research Studio II

Causal Research Studio II turns the governed causal-design layer introduced in v0.67.0 into an executable research workflow. It adds DAG normalization and declared adjustment plans, propensity-score estimation, nearest-neighbor matching, inverse-probability weighting, balance and overlap diagnostics, difference-in-differences, interrupted time series, local-linear regression discontinuity, synthetic control, robustness/placebo planning, counterfactual reporting, visualization plans, snapshots, reproduction/export plans, and Platform Core reference plans.

## Scientific boundaries

All causal estimates remain conditional on explicit identification assumptions and diagnostics. DAG edges and adjustment sets are researcher-declared. The Studio does not prove causal direction, certify backdoor sufficiency, certify parallel trends, continuity, stable pretrends, overlap, absence of unmeasured confounding, or scientific validity. Counterfactuals and synthetic controls are modeled constructs rather than observed alternate histories. Human causal review remains required through the retained v0.67 governance contract.

## Runtime limits

- 20,000 study rows
- 64 covariates
- 128 DAG nodes / 512 DAG edges
- 128 synthetic-control donors
- 64 placebo-plan entries
- 28 v0.125 API surfaces
