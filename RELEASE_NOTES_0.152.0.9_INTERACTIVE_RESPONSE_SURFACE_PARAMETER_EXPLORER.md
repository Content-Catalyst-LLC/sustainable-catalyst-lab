# Release notes — Lab v0.152.0.9

**Release:** Interactive Response Surface & Parameter Explorer  
**Feature line:** v0.152.0  
**Backend scientific behavior:** unchanged

v0.152.0.9 extends the bounded v0.152.0.7 4D front door after the v0.152.0.8 PHP output-safety repair. It exposes a user-configurable response-surface workflow backed by the registered Python Compute Core `simulation.parameter_sweep` method.

### Added

- Four registered model families in the front-door explorer.
- Distinct X, Y and W model-parameter selectors.
- Editable axis ranges and bounded X/Y/W resolution.
- Fixed-parameter controls for unused model inputs.
- Compute-backed X/Y/W grid assembly using bounded registered sweeps.
- Z mapping for model output, normalized output and compatible-baseline difference.
- Run metadata and execution-budget preview.
- Baseline capture and comparison mode.
- Up to 20 browser-local saved configurations.
- CSV response-grid export in addition to PNG and JSON.
- v0.152.0.9 frontend health endpoint.

### Preserved

- Safe-shell navigation and full-panel retention.
- Explicit compute only; no automatic backend execution.
- Legacy eager runtime isolation.
- v0.152.0.8 PHP output-safety certification gate.
- Cross-workspace dependency graph backend v0.152.0 with 120 routes.

### Scientific interpretation

The response surface visualizes registered model output. It does not convert simulations into observations, evidence, calibration, causal inference or scientific validity. Baseline differences are numerical differences between compatible computed grids.
