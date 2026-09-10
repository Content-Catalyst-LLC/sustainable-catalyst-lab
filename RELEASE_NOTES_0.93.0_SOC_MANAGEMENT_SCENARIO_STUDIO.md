# Sustainable Catalyst Lab v0.93.0
## Carbon & Nature Intelligence v0.10.0 — SOC Management Scenario Studio

This release adds a governed scenario layer above the retained SOC stock, field sampling, temporal change, and uncertainty foundations.

### New scientific capability

- Project SOC stock trajectories from a supplied baseline stock or a v0.6.0 fixed-depth profile.
- Run constant annual stock-change scenarios in Mg C/ha/yr.
- Run compound relative-change scenarios in %/yr.
- Run explicit year-by-year stock-change schedules.
- Compare 2–50 scenarios without automatic ranking or recommendation.
- Run sensitivity sweeps over values explicitly supplied by the user.
- Attach measure, evidence, and assumption references without allowing those references to inject hidden rates.
- Define optional lower/upper assumption envelopes; these are labeled assumption envelopes, not confidence intervals.
- Scale per-hectare projections to an explicitly supplied parcel area.
- Save scenario results to Lab projects, hand trajectories to Graph Studio, and emit draft Carbon Project `model-run` packets.

### Scientific boundaries

Sustainable Catalyst does not supply a default SOC change or sequestration rate in this release. A scenario is a transparent calculation from declared assumptions, not a forecast. A projected increase does not establish causal intervention attribution, verified sequestration, additionality, leakage, permanence, MRV compliance, verification, carbon-credit eligibility, or whole-farm GHG benefit. Soil saturation/capacity is not inferred; scenarios that would create negative SOC stock are rejected rather than silently clipped below zero.

### Reference fixture

A baseline stock of 78 Mg C/ha with a user-supplied +2 Mg C/ha/yr assumption over 10 years produces:

- final stock: 98 Mg C/ha
- cumulative projected change: +20 Mg C/ha
- mean annual projected change: +2 Mg C/ha/yr

The result remains an assumption-driven scenario projection.
