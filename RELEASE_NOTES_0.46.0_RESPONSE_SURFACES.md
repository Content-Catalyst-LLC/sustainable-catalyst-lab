# Sustainable Catalyst Lab v0.46.0

## Response Surfaces, Optimization & Design-Space Exploration

Lab v0.46.0 extends Model Studio with governed response-surface methodology for bounded experimental design spaces.

### Scientific capabilities

- Full second-order response-surface models in coded factor space.
- Linear, quadratic, and all two-factor interaction terms.
- Two to eight continuous factors with explicit experimental bounds.
- Coefficient estimates, standard errors, t statistics, p values, and approximate 95% confidence intervals.
- R², adjusted R², RMSE, MAE, bias, SSE, AIC, AICc, and BIC.
- Design-matrix rank, singular values, and condition-number diagnostics.
- Pure-error / lack-of-fit F testing when replicated design points provide the required degrees of freedom.
- Observed-versus-predicted, residual, and coded-coefficient graphics.
- Bounded two-factor response heatmaps while other factors are held at declared values.
- Optional response minimum / maximum feasibility constraints with feasible design-space fraction.
- Prediction standard-error propagation from the fitted coefficient covariance matrix.
- Deterministic bounded optimization for maximize, minimize, and target-response goals.
- Optimization uses SciPy differential evolution with a fixed seed and polishing inside declared factor bounds.
- Boundary-optimum warnings and approximate prediction intervals at the optimum.

### Model Studio integration

The Model Studio workflow now exposes response-surface definition, fitting, exploration, optimization, evidence storage, and governed handoff alongside the existing equation builder, diagnostics, interactive scientific graphs, and dynamic-system tools.

The shared Scientific Visualization Engine v0.44 remains the renderer for response-surface fit graphics and design-space heatmaps.

### Safety and scientific boundaries

v0.46.0 does not execute arbitrary Python, JavaScript, shell, or user-defined code.

Optimization is deliberately restricted to the declared continuous factor bounds. Lab will not extrapolate a quadratic response surface beyond the experimental design region. Mixed-integer optimization, higher-order surfaces, Gaussian-process optimization, and multi-response desirability optimization are not enabled in this release.

### Compatibility line

- WordPress / feature release: **0.46.0**
- Platform compatibility marker: **1.0.0**
- Dynamic Systems: **0.45.0**
- Scientific Visualization Engine: **0.44.0**
- Model Diagnostics / Cross-Validation: **0.43.0**
- Safe Equation Grammar: **0.42.0**

### Release validation

The v0.46.0 focused scientific/modeling gate contains **111 Python tests** plus browser, PHP, FastAPI route, syntax, WordPress runtime-integrity, and manifest-hash checks.
