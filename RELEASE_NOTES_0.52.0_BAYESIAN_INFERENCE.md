# Sustainable Catalyst Lab v0.52.0

## Bayesian Inference, Posterior Diagnostics & Posterior Predictive Modeling

v0.52.0 extends the governed Model Studio statistical stack with Bayesian regression while preserving the v0.48.3 contextual-navigation architecture, Graph Studio front door, three related-application cards, v0.49 Lab ↔ Workbench model handoff, v0.50 reproducible model packages, and v0.51 advanced statistical modeling.

### Bayesian model families

- Gaussian regression, including the existing linear and Gaussian cubic-spline design bases.
- Binomial-logit regression.
- Poisson-log regression.
- Named dataset columns only; arbitrary formulas and executable code are not accepted.

### Priors

- Independent normal intercept and coefficient priors.
- Optional term-specific normal priors keyed to the resolved design-term label.
- Inverse-gamma residual-variance prior for Gaussian models.
- Priors are explicit and user-declared. Lab does not automatically choose priors or claim that a default prior is scientifically appropriate for a particular domain.

### Posterior sampling

- Gaussian models: multi-chain Gibbs sampler for coefficients and residual variance.
- Binomial-logit and Poisson-log: adaptive random-walk Metropolis initialized from a governed Laplace approximation.
- Explicit chain count, retained draws, warmup, deterministic seed, proposal scale, and target-acceptance controls.
- Bounded release limits on chains, draws, warmup, retained posterior samples, and posterior-predictive draws.

### Posterior diagnostics

- Split-Rhat screening.
- Initial-positive-sequence autocorrelation effective sample size.
- Monte Carlo standard error for posterior means.
- Per-chain acceptance-rate evidence for Metropolis models.
- Shared-engine trace plots.
- Diagnostic warnings for Rhat, ESS, and broad acceptance-rate review thresholds.
- Diagnostics are screening evidence and never an automatic convergence certificate.

### Posterior predictive modeling

- Posterior latent-mean/probability/rate intervals.
- Posterior-predictive intervals.
- Observed-versus-posterior-predictive graph.
- Posterior-predictive checks for relevant summary statistics, including mean, spread, and Poisson zero rate.
- Bayesian tail-probability screening flags for extreme predictive-check values.

### Integration

- New FastAPI Bayesian health, policy, normalization, fitting, and posterior-predictive routes.
- New WordPress compute-core Bayesian proxy routes.
- Contextual Bayesian workspace inside Model Studio; no new permanent left-rail destination.
- Scientific figures use the shared v0.44 visualization engine and can be opened in Graph Studio.
- Bayesian evidence saves into project `analysisPackets`, which the v0.50 reproducible-model-package collector already includes.

### Scientific boundaries

- Posterior statements are conditional on the declared model, data, priors, and sampler.
- No automatic prior selection.
- No automatic convergence certification.
- No causal claims from posterior association alone.
- No Bayes factors in v0.52.0.
- No hierarchical/multilevel models in v0.52.0.
- No arbitrary Python, R, JavaScript, shell, callback, or executable payload fields.
- No automatic publication or scientific certification.

### Version contract

- WordPress/release/feature version: `0.52.0`
- Bayesian inference: `0.52.0`
- Advanced statistical modeling: `0.51.0`
- Reproducible model packages: `0.50.0`
- Shared Lab ↔ Workbench model contract: `0.49.0`
- Contextual navigation: `0.48.3`
- Scientific visualization engine: `0.44.0`
- Platform compatibility: `1.0.0`
