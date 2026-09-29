# Sustainable Catalyst Lab v0.94.0 — Whole-Farm GHG Balance

**Carbon & Nature Intelligence v0.11.0**

Lab v0.94.0 adds a provenance-first whole-farm greenhouse-gas accounting layer on top of the retained SOC v0.6–v0.10 scientific chain.

## What this release adds

- Direct CO2e emissions/removals with explicit source references.
- Gas-mass accounting for CO2 and non-CO2 gases. CO2 uses the identity factor 1; non-CO2 gases require an explicit, sourced GWP factor.
- Activity × emission-factor accounting with a mandatory factor source reference.
- Gross emissions, gross removals, net balance, category aggregation, gas aggregation, area intensity, and optional explicit-period annualization.
- Optional SOC stock-change integration using the exact 44/12 C-to-CO2 molecular mass ratio. SOC is included in the net balance only when the user explicitly selects it.
- Deterministic input/result fingerprints and draft Carbon Project `model-run` packet handoff.
- A dedicated Lab browser workspace and Graph Studio handoff.

## Scientific boundary

Whole-farm balance is an accounting model, not verification. Sustainable Catalyst does not supply default non-CO2 GWP values or default activity emission factors in this release. The calculation does not infer inventory completeness, causal attribution, additionality, leakage, permanence, verification status, or carbon-credit eligibility. A positive SOC stock change is not automatically treated as attributed atmospheric sequestration.

## Reference fixture

The release gate uses deliberately illustrative test factors:

- 1,000 kg CO2 × 1 = 1,000 kg CO2e
- 10 kg CH4 × user-supplied GWP 10 = 100 kg CO2e
- 1 kg N2O × user-supplied GWP 100 = 100 kg CO2e
- Gross emissions = 1,200 kg CO2e
- SOC gain = 0.1 Mg C/ha × 1 ha × 44/12 = 366.6667 kg CO2e removal
- Net balance = 833.3333 kg CO2e net emissions

The GWP values 10 and 100 are test fixtures, not current authoritative factors and must not be reused as policy/scientific defaults.

## Deployment

No database migration and no new credential are required. The backend upgrade preserves `.env.production` and the existing `sc-lab-data` Docker volume.
