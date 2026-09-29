# Sustainable Catalyst Lab v0.51.0

## Advanced Statistical Modeling & Generalized Regression

v0.51.0 deepens Model Studio with governed multivariable statistical modeling while preserving the v0.48.3 contextual-navigation architecture, Graph Studio front door, three related-application cards, v0.49 Lab ↔ Workbench model exchange, and v0.50 reproducible model packages.

### Statistical modeling

- Gaussian multiple linear regression with ordinary least squares (OLS).
- Positive-weight weighted least squares (WLS).
- Huber robust regression for reduced sensitivity to large residuals.
- Ridge, lasso, and elastic-net regularized Gaussian regression with an unpenalized intercept.
- Binomial generalized linear models with a logit link, using unpenalized GLM or ridge estimation.
- Poisson generalized linear models with a log link, using unpenalized GLM or ridge estimation.
- Gaussian cubic-spline regression using a governed truncated-power basis with up to 12 interior knots.
- Optional standardization of non-intercept design columns.

### Validation and evidence

- Deterministic k-fold and repeated k-fold cross-validation with explicit seed control.
- Family-appropriate validation metrics and fold evidence.
- Candidate model comparison using the same validation design.
- Coefficient records, fit metrics, convergence evidence, and classical uncertainty only where statistically appropriate.
- Regularized and Huber estimates are explicitly not given classical p-values in this release.
- Shared v0.44 scientific graph contracts for observed/predicted, residual, coefficient, spline, and comparison figures.
- Direct Graph Studio handoff without introducing another renderer.

### Reproducibility integration

- Statistical results, validation evidence, and model comparisons can be saved into the active Lab project as analysis packets.
- v0.50 reproducible model packages now include project analysis packets, allowing v0.51 statistical evidence to travel with a frozen research package.
- Existing v0.49 computational-model handoff and v0.50 model package contracts are preserved.

### Safety and methodological boundaries

- Dataset columns must be named explicitly; arbitrary formula or arbitrary code execution is not supported.
- No arbitrary Python, JavaScript, R, SQL, shell, or remote callback execution is introduced.
- No automatic feature selection, causal claim, publication, or high-stakes decision is authorized.
- Cubic splines are limited to Gaussian regression in v0.51.0.
- Binomial and Poisson families use linear predictors in this release.
- Correlated uncertainty, Bayesian inference, mixed-effects/hierarchical models, survival models, time-series models, and causal-inference workflows remain outside v0.51.0 scope.

### Interface

The established Lab presentation remains intact. Advanced statistics appears as a contextual full-width Model Studio section rather than another permanent left-rail destination. The six primary Lab destinations, Graph Studio front door, and Prototyping Workbench / Decision Studio / Site Intelligence card row are preserved.

### Version contract

- WordPress/release/feature version: `0.51.0`
- Advanced statistical modeling: `0.51.0`
- Reproducible model packages: `0.50.0`
- Lab ↔ Workbench model handoff: `0.49.0`
- Contextual navigation: `0.48.3`
- Probabilistic analysis: `0.48.0`
- Graph Studio: `0.47.0`
- Response surfaces: `0.46.0`
- Dynamic systems: `0.45.0`
- Scientific visualization engine: `0.44.0`
- Diagnostics / cross-validation: `0.43.0`
- Safe equation engine: `0.42.0`
- Internal platform compatibility: `1.0.0`
