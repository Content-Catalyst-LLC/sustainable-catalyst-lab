# Sustainable Catalyst Lab v0.48.0
## Integrated Uncertainty, Sensitivity & Probabilistic Visualization

Lab v0.48.0 makes uncertainty a first-class Model Studio workflow and connects probabilistic evidence directly to Graph Studio. It layers a governed probabilistic-analysis runtime over the safe declarative equation system introduced in v0.42, while preserving the existing v0.34.1 dispatcher-backed registered-model ensemble system for larger distributed studies.

### Major capabilities

- Dedicated **Uncertainty & sensitivity** workspace in the MODEL navigation group.
- Direct Model Studio → probabilistic-analysis handoff.
- Explicit uncertain-input definitions; Lab does not silently invent distributions or standard deviations.
- Uniform, Normal, Lognormal, and Triangular input distributions.
- Monte Carlo, Latin-hypercube, Sobol-sequence, and Saltelli–Sobol sampling.
- Seeded deterministic study generation for reproducibility.
- Mean, variance, standard deviation, median, skewness, excess kurtosis, quantiles, and central uncertainty intervals.
- User-defined output thresholds with exceedance and non-exceedance probabilities.
- Pearson, Spearman, and standardized-regression sensitivity for general sampling designs.
- Saltelli–Sobol first-order and total-order global sensitivity indices.
- Probabilistic output histograms and empirical cumulative distribution functions.
- Ranked sensitivity figures.
- Optional prediction curves with propagated central uncertainty ribbons.
- Direct probabilistic-figure handoff to Graph Studio for publication refinement and export.
- Project persistence for complete probabilistic analysis records and their governed graph specifications.

### Scientific governance

The v0.48 integrated workflow executes only safe declarative Model Studio equations. Arbitrary Python, JavaScript, shell commands, imports, filesystem operations, network access, and user-defined executable functions remain disabled.

Input uncertainties are currently treated as statistically independent. Correlated or copula-based input models are not silently approximated. The integrated v0.48 workflow also does not claim Bayesian posterior inference, stochastic differential equations, probabilistic ODE calibration, or posterior predictive sampling. Those require explicit future scientific contracts.

The existing **Registered-model ensembles** module remains available for immutable registered-model members, dispatcher-backed evaluation, weighted ensembles, and distributed uncertainty studies.

### Visualization architecture

v0.48 does not create another chart renderer. Distribution, CDF, sensitivity, and uncertainty-ribbon specifications continue to use the governed `sc-lab-scientific-graph/0.46.0` contract and the shared **Scientific Visualization Engine v0.44.0**. Graph Studio v0.47.0 remains the dedicated publication and figure-management surface.

### Version contract

- WordPress release: **0.48.0**
- Integrated probabilistic analysis: **0.48.0**
- Graph Studio: **0.47.0**
- Response surfaces: **0.46.0**
- Dynamic systems: **0.45.0**
- Scientific Visualization Engine: **0.44.0**
- Diagnostics / cross-validation: **0.43.0**
- Safe equation engine: **0.42.0**
- Registered-model ensemble compatibility: **0.34.1**
- Internal platform compatibility: **1.0.0**

### Release certification

The focused scientific/modeling gate contains **128 tests** and includes v0.48 probabilistic analysis plus the v0.47 Graph Studio, v0.46 response-surface, v0.45 dynamic-system, v0.43 diagnostics, v0.42 equation, calibration, visualization, design-study, model-registry, ensemble, and surrogate/ROM regression suites.

The release manifest governs 1,021 WordPress/source files and 401 backend files with SHA-256 hashes. WordPress runtime integrity validates the 0.48.0 release line independently from the retained 1.0.0 platform-compatibility line.
