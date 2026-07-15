# Numerical Validation and Benchmark Library

The v0.27.1 benchmark library checks numerical methods against known reference solutions and acceptance rules.

## Benchmark families

- Polynomial root finding
- Adaptive quadrature
- Linear interpolation
- First-order ODE integration
- Symmetric eigen analysis
- Bounded scalar optimization
- Linear programming
- FFT frequency and amplitude recovery
- Seeded Monte Carlo propagation
- Bootstrap stability
- Finite-difference sensitivity
- Deterministic parameter sweeps
- Dense linear-system residuals
- Sampled integration

## Acceptance rules

Each case can assert exact equality, absolute and relative closeness, maximum residuals, sequence agreement, monotonic behavior, deterministic sample counts, and named derivative agreement. Results include the Python Compute Core provenance record.

## Convergence diagnostics

The root and ODE fixtures include tolerance sweeps. The runner records the actual value, analytic reference, absolute error, runtime, and error-ratio trend at each level.
