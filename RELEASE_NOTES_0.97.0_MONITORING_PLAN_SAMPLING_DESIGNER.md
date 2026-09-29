# Sustainable Catalyst Lab v0.97.0 — Monitoring Plan & Sampling Designer

Carbon & Nature Intelligence advances from v0.13.0 to v0.14.0.

This release adds a governed monitoring-plan object and sampling-design workflow on top of the v0.95 MRV Method Registry and v0.96 MRV Protocol Builder. Users explicitly document campaigns, sampling frame, sample unit, strategy, strata, SOC depth intervals, field/laboratory QA/QC, method evidence, and source references.

The sampling calculator requires user-supplied variability and precision assumptions. It supports the standard planning expression `ceil((z*s/E)^2)` and optional finite-population correction. Stratified designs support equal, proportional, and Neyman allocation using only supplied stratum sizes and, for Neyman allocation, supplied stratum SDs.

Scientific boundaries are explicit: no sampling coordinates are invented, no hidden variability/precision defaults are supplied, representativeness is not inferred, sample-size output is not a statistical-power guarantee, and the release does not determine methodology eligibility, verification, certification, causal attribution, or carbon-credit eligibility.

The WordPress runtime remains slim and excludes Python backend source, virtual environments, caches, tests, SDKs, and repository-only documentation.
