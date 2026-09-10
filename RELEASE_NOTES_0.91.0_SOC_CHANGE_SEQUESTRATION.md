# Sustainable Catalyst Lab v0.91.0 — Carbon & Nature Intelligence v0.8.0

## SOC Change & Sequestration Model

This release advances the Carbon & Nature scientific line from field-ready SOC stock calculation to governed change-through-time analysis. It compares baseline and follow-up SOC profiles only when their normalized fixed-depth intervals match exactly, then reports stock difference, elapsed time, annualized stock-change rate, relative change, direction, and optional parcel-scaled totals.

### Added
- Matched baseline/follow-up SOC profile comparison on the retained v0.6.0 fixed-depth fine-earth-corrected stock engine.
- Exact normalized depth-interval compatibility gate before any temporal difference is calculated.
- SOC stock change in Mg C/ha and annualized stock change in Mg C/ha/yr using an explicit 365.2425-day annualization basis.
- Relative SOC stock change where the baseline stock is nonzero.
- Optional area scaling to total Mg C change and annualized Mg C/yr.
- Multi-date SOC change series with ordered observation points, pairwise changes, and overall change.
- Explicit baseline, intervention, spatial-unit, source, and temporal identifiers.
- Deterministic input/result fingerprints.
- Carbon Project `model-run` handoff compatible with the v0.4+ project-object/provenance contract.
- New Lab browser workspace, Graph Studio handoff, Lab project persistence, WordPress routes, and FastAPI routes.

### Scientific interpretation boundary
A positive matched stock difference is reported as a **gross SOC accumulation signal**. It is not automatically labeled intervention-attributable sequestration. The release does not establish a counterfactual, additionality, leakage, permanence, net whole-farm GHG benefit, verification, methodology eligibility, or carbon-credit eligibility.

v0.8.0 also does not infer uncertainty, convert SOC change to CO2e, or implement equivalent-soil-mass correction. Those are intentionally retained as later governed capabilities.

### Reference fixture
For one 0–30 cm layer at 1.30 g/cm3 bulk density and zero coarse fragments:
- Baseline: 2.0% SOC = 78.0 Mg C/ha
- Follow-up: 2.2% SOC = 85.8 Mg C/ha
- Stock change: +7.8 Mg C/ha

### Version identity
- Lab: 0.91.0
- Carbon & Nature Intelligence: 0.8.0
- Compute Core: 1.0.0
- Previous Lab baseline: 0.90.0
- Next Carbon & Nature build: 0.9.0 — SOC Spatial Variability & Uncertainty
