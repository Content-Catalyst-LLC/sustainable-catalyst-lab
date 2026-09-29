# Lab v0.145.0 — Simulation & Computational Experiment Workspace

## Purpose
Unifies governed computational experiments across deterministic/stochastic simulation, Monte Carlo, agent-based/discrete-event/system-dynamics, ODE/PDE/state-space, spatial/spatiotemporal, engineering numerical methods, ensembles, parameter sweeps, uncertainty, sensitivity, verification, validation and reproducibility.

## Architecture
Platform Core defines canonical objects. Workspace and Workbench execute numerical workloads. Research Lab governs experiment design, returned results, diagnostics, comparison, visualization, verification/validation state, interpretation and reproducibility.

## Scientific boundaries
- Simulation output is modeled output, not observational evidence.
- Verification is not validation.
- Numerical convergence is not scientific validity.
- Calibration is not independent validation.
- Sensitivity/importance does not establish causality.
- A scenario is not automatically a forecast or prediction.
- Reproducibility does not certify scientific validity.

## Integration
Preserves v0.144.0 Statistical & Econometric Research Workspace, v0.143.0 Computational Linguistics Research Workspace, v0.142.0 Integrated Neural Research Workspace, the v0.141.x neural series, and the v0.140.0 Scientific Research Operating System.
