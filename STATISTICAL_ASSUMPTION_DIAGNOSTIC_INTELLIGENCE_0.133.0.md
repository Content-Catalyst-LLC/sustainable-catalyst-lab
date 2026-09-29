# Sustainable Catalyst Lab v0.133.0 — Statistical Assumption & Diagnostic Intelligence

This release introduces a cross-method assumption and diagnostic intelligence layer. It separates raw diagnostics, assumption states, and researcher adjudication so that diagnostics inform scientific judgment without silently making it.

## Core capabilities

- Five explicit assumption states: satisfied, violated, uncertain, untested, not-applicable.
- Cross-method assumption registry spanning classical, Bayesian, causal, time-series, spatial, simulation, sensitivity, and experimental-design workflows.
- Diagnostic registries and normalized diagnostic observations with source references.
- Residual, distribution, independence, variance, multicollinearity, influence, convergence, overlap, time-series, spatial, missingness, simulation, and experimental-design diagnostics.
- Assumption matrices, violation/uncertainty/untested reports, dependency graphs, method-impact reports, remediation options, robustness and sensitivity plans.
- Cross-method synthesis with no automatic winner or ranking.
- Researcher adjudication records, readiness/status reports, deterministic snapshots, provenance, project/session bindings, cross-product handoffs, and Platform Core plans.

## Scientific boundary

A diagnostic threshold is not automatic proof that an assumption is violated, and an assumption state does not by itself establish scientific validity. The Studio never automatically invalidates a method, selects a replacement method, certifies scientific validity, infers causality, generalizes beyond scope, or determines truth.
