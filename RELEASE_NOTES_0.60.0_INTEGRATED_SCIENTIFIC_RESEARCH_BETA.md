# Sustainable Catalyst Lab v0.60.0 — Integrated Scientific Research Beta

v0.60.0 consolidates the scientific feature line from v0.41 through v0.59 into a coherent beta research journey without changing Lab's established navigation architecture. It adds a metadata-only integration/readiness layer that evaluates whether an active project has evidence across data, modeling, validation, workflows, reproducibility, and scientific audit, while also surfacing optional uncertainty, experiment, and figure evidence.

## Integrated beta contract

The release adds a governed capability matrix spanning Lab ↔ Workbench model exchange, reproducible model packages, advanced statistics, Bayesian inference, correlated uncertainty, data transformations, experimental design, Graph Studio, probabilistic analysis, Scientific Workflow Composer, compute hardening, and scientific audit.

The beta readiness endpoint accepts **metadata summaries only**. Raw datasets, scientific inputs, secrets, and credentials are rejected. The resulting beta packet contains project/capability/evidence hashes and readiness state rather than raw research content.

## Readiness states

- `blocked` — a required capability is unavailable or the current scientific audit is blocked.
- `needs-evidence` — Lab is operational but required project evidence is incomplete.
- `beta-review-ready` — the required integrated research evidence is present and the project is ready for accountable human beta review.

`beta-review-ready` is not scientific certification. Human review remains mandatory, and automatic publication, high-stakes decisions, registry promotion, and scientific certification remain disabled.

## Interface

The Integrated Scientific Research Beta appears contextually inside the existing Scientific Workflows workspace. It does not add another permanent navigation destination. The six-destination rail, Graph Studio front door, and three related application cards remain preserved.

## R1 lineage

v0.60.0 inherits the v0.59.0 R1 validation repair, including the governed `jsonschema` development dependency and isolated validation environment behavior.
