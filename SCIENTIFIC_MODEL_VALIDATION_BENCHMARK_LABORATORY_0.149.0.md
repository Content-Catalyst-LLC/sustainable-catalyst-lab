# Lab v0.149.0 — Scientific Model Validation & Benchmark Laboratory

## Purpose
Create a governed laboratory for benchmark design, model validation, reference standards, metric suites, calibration, generalization, robustness, domain shift, subgroup analysis, failure analysis, external validation, and reproducibility across Sustainable Catalyst model families.

## Architecture
- Platform Core defines canonical validation, benchmark, metric, and provenance objects.
- Workspace executes benchmark and validation computation.
- Workbench prototypes model and validation workflows.
- Lab defines protocols, audits leakage and reference standards, compares returned results, analyzes failures, records external validation, visualizes findings, and packages reproducible validation research.

## Governing boundaries
- Benchmark performance is not scientific validity.
- Held-out performance is not proof of real-world adequacy.
- External validation is scoped to its population/site/time and is not universal validity.
- Reference standards are provenance-bearing and fallible.
- Outperforming a baseline is not automatic scientific superiority.
- Calibration, robustness, and reproducibility do not by themselves establish deployment readiness.
- Human scientific review remains required.

## API
78 backend routes under `/v1/scientific-model-validation-benchmark-laboratory/v01490/`.
