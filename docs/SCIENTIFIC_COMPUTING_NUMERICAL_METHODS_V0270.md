# Scientific Computing and Numerical Methods — v0.27.0

Sustainable Catalyst Lab v0.27.0 adds a governed numerical-computing layer to the Python Compute Core and a dedicated Numerical Methods Studio in WordPress.

## Architecture

- WordPress remains the authenticated control plane and project workspace.
- JavaScript provides the interactive method selector, JSON editors, progress states, accessible plots, save, and export controls.
- FastAPI executes only registered numerical methods with validated inputs, bounded resources, and reproducibility provenance.
- Heavier methods use the persistent v0.26.1 job queue; lightweight methods can return synchronously.
- Public arbitrary Python execution remains disabled.

## Registered methods

1. Bracketed polynomial root finding
2. Adaptive polynomial quadrature
3. Linear, PCHIP, and cubic interpolation
4. First-order ODE integration for governed model families
5. Dense matrix eigen analysis
6. Bounded scalar optimization
7. Continuous linear programming
8. FFT amplitude and power spectra
9. Seeded Monte Carlo uncertainty propagation
10. Bootstrap mean confidence intervals
11. Local finite-difference sensitivity analysis
12. Registered parameter sweeps

## Reproducibility

Each backend result records the method and service versions, Python and package versions, execution duration, random seed where applicable, input and result SHA-256 hashes, authentication mode, worker type, and execution timestamp.

## Safety and resource boundaries

The service rejects unknown methods and extra request fields. Input arrays, matrices, sample sizes, interpolation queries, ODE output points, optimization iterations, and sweep lengths are bounded. Long-running jobs can be cancelled or timed out by the persistent worker system.

## WordPress endpoints

- `/wp-json/sc-lab/v1/numerical/v0270/catalog`
- `/wp-json/sc-lab/v1/numerical/v0270/health`
- Existing Compute Core and queue proxy endpoints remain authoritative for execution.

## Focused shortcode

`[sc_lab_numerical_methods]`
