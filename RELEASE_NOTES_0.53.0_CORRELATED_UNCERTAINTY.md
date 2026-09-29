# Sustainable Catalyst Lab v0.53.0
## Correlated Uncertainty & Probabilistic Dependency Models

v0.53.0 extends the v0.48 probabilistic-analysis line so uncertain inputs no longer have to be treated as independent when evidence supports dependence. The release preserves the v0.48.3 contextual navigation, Graph Studio front door, three related-application cards, v0.49 Lab ↔ Workbench model exchange, v0.50 reproducible model packages, v0.51 advanced statistical modeling, and v0.52 Bayesian inference.

### Added
- Explicit dependency models: independent inputs or Gaussian copula.
- Correlation-matrix and covariance-matrix inputs aligned to the declared uncertain-input order.
- Strict symmetry, diagonal, correlation-bound, covariance-variance, and positive-semidefinite validation.
- Covariance-to-correlation normalization for copula construction.
- Monte Carlo, Latin hypercube, and Sobol-sequence propagation with dependent inputs.
- Marginal-distribution preservation for normal, uniform, lognormal, and triangular uncertain inputs.
- Empirical Pearson and Spearman dependency diagnostics after sampling.
- Dependency heatmap rendered through the shared v0.44 scientific visualization engine and transferable to Graph Studio.
- Review-only empirical dependency estimation from complete observations using Pearson, Spearman, or Gaussian-rank correlation.
- Dependency evidence persisted in project analysis packets and therefore captured by v0.50 reproducible research packages.

### Scientific boundaries
- Standard Saltelli–Sobol variance decomposition is blocked when dependent inputs are active because its standard interpretation assumes independent inputs.
- Correlation/covariance structures are never inferred silently.
- Estimated dependency structures require operator review before use.
- Statistical association is not presented as causal dependence.
- No arbitrary Python, JavaScript, shell command, callback, or executable formula is accepted through the dependency contract.
- v0.53 does not yet provide vine copulas, t-copulas, dynamic correlation models, Bayesian dependency networks, or causal graphical models.

### Compatibility
- WordPress/release/feature version: `0.53.0`
- Platform compatibility: `1.0.0`
- Probabilistic foundation: `0.48.0`
- Graph Studio: `0.47.0`
- Shared visualization engine: `0.44.0`
- Bayesian inference: `0.52.0`
- Advanced statistical modeling: `0.51.0`
- Reproducible model packages: `0.50.0`
- Lab ↔ Workbench shared model contract: `0.49.0`

### Validation target
The v0.53 release gate runs the new dependency tests together with the inherited v0.41–v0.52 scientific/modeling chain and WordPress/browser/runtime integrity checks.
