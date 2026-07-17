# Surrogate Models and Reduced-Order Analysis — v0.34.2

Sustainable Catalyst Lab v0.34.2 adds governed model approximation and state-space reduction above the v0.34.0 model registry and v0.34.1 ensemble/uncertainty layer.

## Surrogate training

A surrogate study is an immutable, content-addressed training record. It preserves the normalized dataset, feature order, algorithm configuration, validation split, training metrics, model parameters, provenance, definition hash, and final model hash.

Supported algorithms are:

- polynomial ridge regression with deterministic polynomial feature expansion;
- radial-basis interpolation with ridge stabilization;
- Gaussian-process regression using RBF, Matérn 3/2, or Matérn 5/2 kernels.

Gaussian-process predictions include predictive standard deviation. Polynomial and radial-basis models return deterministic predictions.

## Reduced-order analysis

Proper orthogonal decomposition uses centered singular-value decomposition to identify a compact basis for high-dimensional state snapshots. The study records the retained rank, available rank, singular values, component energy, cumulative retained energy, mean state, basis hash, training coefficients, and reconstruction metrics.

The `hybrid-rom` mode combines POD with one surrogate per retained coefficient. It maps declared physical or simulation parameters into reduced coordinates and then reconstructs the full state.

## Validation and error reporting

Surrogate studies support seeded holdout validation with RMSE, normalized RMSE, MAE, maximum absolute error, and R². Reduced-order studies report equivalent reconstruction metrics. Validation thresholds are declared in the study and preserved with the result.

A failed validation result remains inspectable but is not silently treated as validated.

## Scientific Model Registry integration

A validated study can be published as an immutable `surrogate` model version in the Scientific Model Registry. The registry record preserves the study ID, definition hash, model hash, validation metrics, reduced rank, training environment, artifacts, source revision, and dataset provenance.

Registry promotion, production aliases, deprecation, reproduction manifests, and environment verification remain governed by v0.34.0.

## Security and governance

Surrogate and ROM definitions contain numeric data and declarative training settings only. They cannot execute arbitrary Python, shell commands, executable expressions, or remote callbacks.

The WordPress operations panel uses administrator-only same-origin proxy routes. The backend uses the existing compute authentication controls and SQLite WAL persistence.

## WordPress operations

The `surrogate-reduced-order` panel provides validation, immutable training, inspection, prediction or reconstruction, registry publication, saved-study discovery, and timeline review.

Shortcodes:

- `[sc_lab_surrogate_models]`
- `[sc_lab_reduced_order_analysis]`
- `[sc_lab_rom_studio]`

- Surrogate and ROM training routes use a dedicated 16 MB governed request limit; other Lab routes retain their existing request limits.
