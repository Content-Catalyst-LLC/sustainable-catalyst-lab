# Lab v0.115.0 — Advanced Statistical & Uncertainty Graphics

## Purpose

v0.115.0 extends the v0.114 publication-grade visualization design system with advanced statistical and uncertainty figure contracts. It is a visualization and descriptive-statistics layer; it does not infer scientific validity, statistical significance, causality, model quality, or truth.

## Figure families

- empirical histogram, ECDF and box summaries
- violin, raincloud and ridge distributions with explicitly declared Gaussian KDE bandwidth
- confidence, credible, prediction, bootstrap and custom interval ribbons
- nested quantile fan charts
- posterior interval/caterpillar views
- coefficient forest plots
- calibration/reliability diagrams with descriptive expected calibration error
- residual-versus-fitted diagnostics with declared normal-reference Q–Q data
- Q–Q plots with explicitly selected reference distribution
- Sobol, Morris, tornado and ranked-effect sensitivity views
- variance/uncertainty decomposition
- interval coverage graphics
- responsive statistical small multiples

## Scientific boundaries

The bridge never automatically chooses a KDE bandwidth, selects a probability distribution, assigns interval semantics, declares statistical significance, infers causality, certifies a model, certifies science, or determines truth. Those decisions stay explicit and auditable.

## Compatibility

- Scientific Visualization Design System: v0.114.0
- Uncertainty / Ensemble / Distribution layer: v0.82.0
- Scientific Visualization Grammar: v0.74.0
- Platform Core visual bridge remains v0.109.0
