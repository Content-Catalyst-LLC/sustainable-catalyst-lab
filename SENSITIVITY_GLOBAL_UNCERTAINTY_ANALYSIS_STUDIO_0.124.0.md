# Lab v0.124.0 — Sensitivity & Global Uncertainty Analysis Studio

Provides governed global-sensitivity workflows on top of the existing probabilistic and simulation runtimes.

## Capabilities
- Saltelli–Sobol first- and total-order indices.
- Morris elementary-effects screening (mu, mu-star, sigma).
- Correlation/SRC screening.
- Variance-decomposition summaries with explicit finite-sample caveats.
- Pairwise standardized quadratic interaction screening.
- Second-order polynomial response surfaces over declared parameter sweeps.
- Sensitivity convergence across sample counts and replication across seeds.
- Publication visualization plans, reproducible snapshots, exports, and Core reference plans.

## Scientific boundaries
Sensitivity results depend on the declared model, parameter distributions/ranges, independence assumptions, sample size, and seed. The Studio does not automatically rank parameters, infer significance or causality, select models/optima, certify scientific validity, or promote simulated output to observed evidence.
