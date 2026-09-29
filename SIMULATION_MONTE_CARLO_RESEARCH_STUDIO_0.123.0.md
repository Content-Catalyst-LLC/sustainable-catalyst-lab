# Sustainable Catalyst Lab v0.123.0 — Simulation & Monte Carlo Research Studio

## Purpose
v0.123.0 provides a governed, reproducible simulation layer for uncertainty propagation, Monte Carlo experiments, parameter sweeps, scenario ensembles, and simulation diagnostics. It builds on the Lab v0.48 probabilistic-analysis engine and the safe declarative Model Studio rather than introducing arbitrary-code execution.

## Sampling designs
- Monte Carlo
- Latin hypercube
- Sobol quasi-random sampling
- Saltelli-Sobol sampling for uncertainty propagation and sensitivity-compatible designs

## Research workflows
- normalized simulation study contracts
- explicit sampling and compute-budget plans
- seeded simulation execution
- checkpoint-based convergence diagnostics
- cross-seed replication diagnostics
- deterministic multi-axis parameter sweeps
- scenario ensembles with declared overrides and assumptions
- threshold-probability reports
- publication-grade visualization plans
- deterministic research snapshots and reproduction plans
- reference-first Platform Core object and execution-lineage plans

## Scientific boundaries
Simulation outputs are explicitly marked `modeled-not-observed`. The Studio does not automatically certify convergence, rank or select scenarios, optimize parameter sweeps, promote simulated output into empirical evidence, infer causality, certify scientific validity, submit to Platform Core, or determine truth.

## Integration
v0.123.0 reuses Lab v0.48 probabilistic analysis, the v0.114 publication design system, v0.115 statistical uncertainty graphics, v0.116 dashboards, v0.119 figure intelligence, and the v0.105/v0.107 Platform Core mapping/lineage layers.
