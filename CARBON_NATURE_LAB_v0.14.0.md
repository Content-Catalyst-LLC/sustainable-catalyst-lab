# Carbon & Nature Intelligence v0.14.0 — Monitoring Plan & Sampling Designer

Host product: Sustainable Catalyst Lab v0.97.0

## Purpose

v0.14.0 converts an explicitly selected MRV foundation method and protocol into a governed monitoring and sampling plan. It is a planning and documentation layer, not a verifier, methodology authority, or crediting engine.

## Capabilities

- monitoring campaign schedules with explicit IDs, purposes, planned dates, and repeat relationships;
- explicit spatial-boundary, sampling-frame, and sample-unit references;
- documented sampling strategies: simple random, systematic, stratified random, repeated location, and judgmental/purposive;
- precision-based planning sample-size estimates using user-supplied expected SD, z value, and target half-width;
- optional finite-population correction when a population size is supplied;
- equal, proportional, and Neyman allocation across user-defined strata;
- SOC depth-interval validation with non-overlap checks;
- field and laboratory QA/QC planning records;
- method input/evidence readiness inherited from the v0.12 MRV Method Registry;
- deterministic plan and validation fingerprints;
- Carbon Project `monitoring-record` handoff linked to the upstream MRV protocol when supplied.

## Planning equations

For an absolute target half-width `E`, expected standard deviation `s`, and user-supplied normal critical value `z`:

`n0 = ceil((z * s / E)^2)`

When a finite population size `N` is explicitly supplied:

`n = ceil(n0 / (1 + (n0 - 1) / N))`

These are planning estimates only. Sustainable Catalyst does not infer the expected SD, precision target, z value, population size, independence, sampling-frame quality, or design effect.

For stratified allocation, the supported descriptive planning weights are:

- equal: `w_h = 1`
- proportional: `w_h = N_h`
- Neyman: `w_h = N_h * s_h`

Integer allocations use largest-remainder rounding and preserve at least one planned sample per stratum when total sample size is at least the number of strata.

## Guardrails

A generated monitoring plan is not proof of spatial or statistical representativeness. A planning sample size is not a power guarantee for a particular hypothesis test. The designer does not generate coordinates, remove outliers, select a methodology automatically, establish current-program compliance, determine verification or certification, infer causal attribution, or determine carbon-credit eligibility.
