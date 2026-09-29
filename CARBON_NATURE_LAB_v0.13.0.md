# Carbon & Nature Intelligence v0.13.0 — MRV Protocol Builder

Hosted by Sustainable Catalyst Lab v0.96.0.

This release turns the v0.12.0 Carbon MRV Method Registry into a governed protocol-construction workflow. A user explicitly selects a foundation method, then documents the project scope, monitoring frame, responsible roles, method inputs/evidence, nine governed protocol sections, source references, and methodology references. Lab returns a versioned protocol record, deterministic fingerprint, structural gap analysis, foundation-method documentation gap analysis, and optional Carbon Project `monitoring-record` handoff.

## Governed protocol sections

1. Objective & scope
2. Measurement & sampling plan
3. Calculation plan
4. Uncertainty plan
5. QA/QC plan
6. Data & provenance plan
7. Monitoring schedule
8. Reporting plan
9. Change-control plan

The template endpoint exposes method-specific required inputs, required evidence, uncertainty expectations, and quality controls from the v0.12.0 registry. It does not silently mark those requirements as satisfied.

## Readiness semantics

`ready-for-internal-review` means the Sustainable Catalyst protocol scaffold is structurally populated, explicit source/methodology references are present, and the selected foundation method's named documentation requirements are represented. It does **not** mean an external methodology is satisfied or approved.

## Boundaries

The Protocol Builder does not select an MRV method automatically, reproduce an external standard, assert current program rules, approve a monitoring plan for a verifier, infer missing measurement/sampling settings, infer emission factors or GWP values, determine causal attribution, perform verification/certification, or determine carbon-credit eligibility. External rules must be checked against their authoritative current sources.
