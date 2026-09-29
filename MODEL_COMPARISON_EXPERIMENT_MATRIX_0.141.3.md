# Lab v0.141.3 — Model Comparison & Experiment Matrix

This release adds governed side-by-side comparison of experiments, runs, configurations, observed metrics, checkpoints, provenance, and missingness. Comparison records carry explicit dataset/split, metric-definition, architecture, training-configuration, execution-environment, and provenance context.

## Epistemic boundary

A matrix is an inspection surface, not a leaderboard. Numeric differences are reported as differences only. Lab does not infer a winner, automatically rank or promote a model, normalize incompatible experiments into equivalence, or treat predictive performance as evidence.
