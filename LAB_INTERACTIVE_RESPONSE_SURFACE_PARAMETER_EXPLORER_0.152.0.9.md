# Sustainable Catalyst Lab v0.152.0.9 — Interactive Response Surface & Parameter Explorer

## Purpose

v0.152.0.9 turns the recovered 4D front door into a bounded computational exploration surface. It keeps the v0.152 safe-shell architecture, does not restore the historical eager JavaScript fleet, and executes compute only after an explicit user action.

## Compute contract

The explorer uses the already-registered Python Compute Core method `simulation.parameter_sweep`. The backend scientific behavior is unchanged in this release.

Supported model families:

- `logistic_growth`
- `projectile_range`
- `photovoltaic_output`
- `michaelis_menten`

The user chooses three distinct model parameters for X, Y and W. X is evaluated by each registered parameter sweep. The browser coordinates bounded Y/W levels by issuing multiple registered sweeps and builds a compute-backed response grid from returned values. Z represents the model output, normalized output, or a numerical difference from a compatible user-selected baseline.

## Bounded execution

The front end enforces:

- X: up to 41 samples
- Y: up to 7 levels
- W: up to 5 slices
- up to 35 registered sweep requests
- up to 1,435 model evaluations
- at most 3 concurrent requests

No response-surface compute starts automatically. Browser demonstration surfaces remain available without backend execution.

## Interaction

The front door now supports:

- model-family selection;
- X/Y/W parameter assignment;
- editable ranges and bounded resolution;
- fixed controls for model parameters not assigned to axes;
- 4D W hyperslicing and XW/YW projection rotation;
- explicit compute-backed response-surface execution;
- pointer inspection using model parameter values and returned model output;
- run metadata including model, axes, requests, evaluations, elapsed time and output range;
- a user-selected baseline and difference visualization when grids are compatible;
- local browser saved configurations;
- PNG, JSON and CSV exports.

## Scientific boundary

A computed model response is not an observation or empirical evidence. A response-surface difference is a numerical comparison, not causal evidence. Browser interpolation between computed grid points is a visualization operation. Scientific validity, calibration, interpretation and publication decisions remain subject to the existing governed Lab workflows and human review.

## Recovery constraints retained

v0.152.0.9 retains:

- the v0.152 safe shell;
- late footer asset pruning;
- no eager optional mega-bundle;
- no eager historical module fleet;
- no v0.48 presentation runtime;
- no v0.26.6 production-budget monitor;
- no document-wide `MutationObserver` in the active 4D runtime;
- no interval polling loop;
- the v0.152.0.8 PHP output-safety gate.
