# Sustainable Catalyst Lab v0.152.0.10 — 4D Uncertainty, Sensitivity & Ensemble Explorer

## Purpose
Extend the v0.152 safe-shell 4D front door with explicit, compute-backed uncertainty propagation, local sensitivity diagnostics, and bounded seed-replication ensembles while retaining the v0.152.0.9 response-surface explorer.

## Compute contracts
- `uncertainty.monte_carlo_propagation` for registered algebraic Monte Carlo propagation.
- `sensitivity.local_finite_difference` for local finite-difference derivatives and elasticities.
- Bounded seed-replication ensembles composed from explicit Monte Carlo runs.
- `simulation.parameter_sweep` remains the response-surface method from v0.152.0.9.

## Safety and scientific boundaries
No compute starts on page load. Monte Carlo intervals and sensitivities are modeled diagnostics, not observations, causal effects, significance tests, calibrated forecast skill, or scientific-validity certification. Formal Sobol/Morris workflows remain in the specialist Sensitivity & Global Uncertainty Analysis Studio.

## Limits
- Monte Carlo samples: 500–50,000 per explicit run.
- Ensemble members: 3–7.
- Response-surface limits from v0.152.0.9 remain unchanged.
- Legacy mega-bundle and historical eager module fleet remain disabled.
