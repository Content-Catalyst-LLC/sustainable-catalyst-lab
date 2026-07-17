# Ensemble Simulation, Global Sensitivity, and Uncertainty — v0.34.1

Sustainable Catalyst Lab v0.34.1 adds governed ensemble execution and uncertainty analysis on top of the v0.34.0 scientific model registry.

## Scientific model ensembles

An ensemble study references one or more immutable registered-method model versions. Each member preserves its model hash, environment lock hash, semantic version, registered method, and normalized weight. The study definition itself is immutable and content-addressed.

Lab does not accept executable Python, shell commands, remote callbacks, or unregistered methods from an ensemble definition.

## Sampling designs

The engine supports:

- seeded Monte Carlo sampling;
- Latin hypercube sampling;
- scrambled Sobol sequences;
- Saltelli-style Sobol designs for first-order and total-order sensitivity indices.

Supported uncertain inputs include uniform, normal, lognormal, triangular, and discrete distributions. The v0.34.1 contract treats uncertain inputs as independent. Correlated and copula-based designs remain future work.

## Execution and reconciliation

Each sample and model-member pair becomes a governed distributed workload. The workload carries the immutable study hash, model ID, model version, project ID, seed, inputs, and execution policy. Existing dispatcher leases, signed worker contracts, retry policy, dead-letter operations, and worker provenance remain authoritative.

Study state is stored in SQLite WAL. Reconciliation imports terminal dispatcher results, resolves a declared numeric output path, preserves each member result, and computes the ensemble analysis only after complete cross-member sample groups are available.

## Uncertainty outputs

Completed analyses include:

- mean, variance, and standard deviation;
- minimum, maximum, and median;
- p01, p05, p25, p75, p95, and p99 quantiles;
- configurable confidence intervals;
- probabilities above and below declared thresholds;
- member-specific uncertainty summaries;
- weighted ensemble uncertainty summaries.

## Global sensitivity

Monte Carlo, Latin hypercube, and ordinary Sobol studies report Pearson correlation, Spearman rank correlation, and standardized regression coefficients for numeric variables. Saltelli-Sobol studies report first-order and total-order indices.

Sensitivity results are descriptive of the declared model ensemble, sampling design, uncertain-variable assumptions, and available completed evaluations. They are not causal claims.

## WordPress operations

The `ensemble-uncertainty` Lab panel provides study validation, immutable registration, start, reconciliation, inspection, timeline, cancellation, and governed operator-result recording. All compute mutations use administrator-only same-origin WordPress proxy routes.

Shortcodes:

- `[sc_lab_ensemble_simulation]`
- `[sc_lab_uncertainty_analysis]`
- `[sc_lab_global_sensitivity]`
