# Sustainable Catalyst Lab v0.27.1

## Numerical Validation and Benchmark Library

This release adds a governed benchmark system for the Python Compute Core and a new Numerical Validation Library in the WordPress Lab interface.

### Validation capabilities

- Fourteen known-answer numerical benchmarks.
- Absolute and relative tolerance controls.
- Residual, monotonicity, deterministic-seed, and unit assertions.
- Analytic and browser-reference comparisons for supported cases.
- Root-finding and ODE convergence series.
- Full-suite execution and exportable validation reports.
- Backend provenance retained for every benchmark result.

### Backend API

- `GET /v1/benchmarks`
- `GET /v1/benchmarks/{benchmark_id}`
- `POST /v1/benchmarks/run`
- `POST /v1/benchmarks/run-suite`
- `POST /v1/benchmarks/convergence`

The library validates registered methods only. It does not enable arbitrary Python execution.
