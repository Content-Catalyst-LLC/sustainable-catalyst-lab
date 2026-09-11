# Carbon & Nature Intelligence v0.15.0 — MRV Uncertainty & Detection Engine

Host product: Sustainable Catalyst Lab v0.98.0

## Purpose

v0.15.0 turns monitoring-plan assumptions and observed variability into a governed MRV uncertainty and detectability assessment. It distinguishes uncertainty accounting, statistical signal detection, and sample-size planning from verification, methodology compliance, and credit issuance.

## Capabilities

- explicit uncertainty budgets using absolute or relative standard-uncertainty components;
- optional explicit covariance terms rather than an automatic independence assumption;
- combined standard uncertainty and optional expanded uncertainty using a user-supplied coverage factor;
- paired and independent observed-change detection using user-supplied critical values;
- detection-oriented sample-size planning for paired and equal-size independent designs using explicit alpha-side and power-side critical values;
- monitoring-plan and protocol references;
- deterministic assessment, validation, and project-packet fingerprints;
- Carbon Project `model-run` handoff.

## Equations

For standard uncertainties `u_i` and explicit covariance terms `cov(i,j)`:

`u_c = sqrt(sum(u_i^2) + 2 * sum(cov(i,j)))`

Expanded uncertainty is only reported when a coverage factor `k` is supplied:

`U = k * u_c`

Paired observed-change detection uses:

`SE_change = s_change / sqrt(n_pairs)`

Independent observed-change detection uses:

`SE_change = sqrt(s_baseline^2 / n_baseline + s_followup^2 / n_followup)`

and the supplied detection threshold is:

`threshold = critical_value * SE_change`

For detection-oriented paired sample-size planning with user-supplied `z_alpha` and `z_power`:

`n = ceil(((z_alpha + z_power) * s_change / MDD)^2)`

For equal-size independent groups:

`n_per_period = ceil((z_alpha + z_power)^2 * (s_baseline^2 + s_followup^2) / MDD^2)`

## Guardrails

No confidence level, coverage factor, power target, correlation structure, uncertainty component, or deduction factor is inferred. Statistical detection is not verification. A planning sample size does not guarantee achieved power. The engine does not determine external methodology compliance, verification/certification, additionality, causal attribution, or carbon-credit eligibility.
