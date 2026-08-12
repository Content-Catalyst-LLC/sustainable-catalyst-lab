# Sustainable Catalyst Lab v0.43.0

## Model Diagnostics, Cross-Validation & Scientific Model Comparison

Lab v0.43.0 turns Model Studio's v0.42 equation-definition foundation into a governed statistical evidence workflow for the Lab's registered calibration families.

### Added

- Deterministic k-fold and repeated k-fold cross-validation with seeded splits.
- Fold-level RMSE, MAE, bias, R², and maximum absolute error with aggregate mean, standard deviation, minimum, and maximum summaries.
- Full-dataset refitting after cross-validation for final parameter estimates and diagnostics.
- Observed-versus-predicted parity plots, residual-versus-fitted plots, normal Q–Q diagnostics, standardized residuals, flagged large residuals, and fold-RMSE plots.
- AIC, AICc, and BIC information criteria for full fitted models.
- Scientific model comparison for 2–12 candidates using a common validation policy.
- Ranking by mean cross-validation RMSE, then AICc and BIC; ΔAICc and Akaike weights are included as supporting evidence.
- A horizontal comparison graph and evidence table in Model Studio.
- WordPress/FastAPI health, policy, diagnostics, cross-validation, and model-comparison routes.
- v0.43 contracts for models, scientific graphs, diagnostics, cross-validation, and model comparison.

### Scientific boundary

v0.43 deliberately separates **model definition** from **parameter fitting**. The v0.42 safe declarative equation grammar remains available for model definition and deterministic preview. Diagnostics, cross-validation, and comparison in v0.43 fit only the Lab's registered calibration forms. Arbitrary code and arbitrary-formula fitting remain disabled.

### Version and integrity contract

- WordPress release: `0.43.0`
- Model Studio feature release: `0.43.0`
- Internal platform compatibility: `1.0.0`
- Safe equation grammar foundation: `0.42.0`
- Shared scientific visualization foundation: `0.41.0`

The release and platform compatibility lines are validated independently by the runtime integrity layer.
