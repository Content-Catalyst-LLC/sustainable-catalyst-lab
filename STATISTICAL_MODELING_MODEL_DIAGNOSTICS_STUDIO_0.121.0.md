# Sustainable Catalyst Lab v0.121.0 — Statistical Modeling & Model Diagnostics Studio

Lab v0.121.0 adds a governed statistical-modeling layer over the v0.120 EDA Studio and the existing v0.51 numerical model engine. It supports Gaussian regression (OLS/WLS/Huber/ridge/lasso/elastic-net), binomial-logit GLMs, Poisson-log GLMs, coefficient/effect reporting, residual and influence diagnostics, multicollinearity, heteroskedasticity, calibration/classification, deviance/dispersion, prediction evaluation, cross-validation, side-by-side model comparison, publication-aware visualization plans, reproducible snapshots, exports, and Platform Core object plans.

## Scientific boundaries

The Studio does not perform automatic feature selection, automatic model selection, automatic significance labeling, causal inference, scientific-validity certification, or Core submission. Diagnostic tests and p-values are reported as evidence for researcher judgment rather than converted into automatic pass/fail decisions. Source rows remain immutable.

## Integration

- v0.120 EDA provides exploratory profiles and transformation previews.
- v0.121 provides declared model fitting and diagnostics.
- v0.115/v0.114 provide statistical/publication graphics.
- v0.107 preserves execution lineage; v0.105 maps the fitted model into Core by reference.

## Runtime bounds

Interactive fitted-model requests are limited to 5,000 rows and 40 declared feature columns in v0.121.0; larger studies should use the governed batch/runtime pathway rather than silently downsampling.
