# Lab v0.144.0 — Statistical & Econometric Research Workspace

## Purpose

v0.144.0 integrates the Lab's statistical, econometric, diagnostic, uncertainty, panel-data, time-series, causal-research and reproducibility surfaces around a governed **estimand → specification → estimate** workflow.

## Object model

The release adds explicit dataset/variable, estimand, model specification, estimate/result and diagnostic objects. Every object carries references to its dataset, run, software/runtime and provenance where available. Estimands remain separate from fitted model coefficients so changes in specification do not silently redefine the research target.

## Research surfaces

The workspace supports descriptive/regression/GLM, panel data, IV/2SLS/LIML, GMM, difference-in-differences, event study, regression discontinuity, synthetic-control declarations, ARIMA/SARIMA, VAR/VECM, cointegration/state-space, survival/duration/hazard, Bayesian and hierarchical result objects. It provides specification and identification audits, diagnostic summaries, robust/clustered inference summaries, specification/robustness matrices, model and estimand comparison, sensitivity and uncertainty reporting.

## Execution boundary

Workspace remains execution authority for statistical and econometric runtimes and numerical estimation. Lab governs study design, returned result objects, comparison, diagnostics, interpretation, review, visualization and reproducibility. Platform Core remains canonical object/provenance authority.

## Epistemic boundaries

- coefficient ≠ estimand
- statistical significance ≠ substantive importance
- association ≠ causation
- model fit ≠ scientific validity
- diagnostic passage ≠ proof that assumptions hold
- robust standard errors ≠ repaired identification
- forecast ≠ evidence
- model comparison ≠ automatic winner selection
- reproducibility ≠ scientific validity
