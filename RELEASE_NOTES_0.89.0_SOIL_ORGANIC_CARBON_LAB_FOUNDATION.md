# Sustainable Catalyst Lab v0.89.0 — Carbon & Nature: Soil Organic Carbon Lab Foundation

**Carbon & Nature Intelligence domain release:** v0.6.0  
**Lab application release:** v0.89.0  
**Python Compute Core service line:** 1.0.0

v0.89.0 is the first Carbon & Nature scientific-modeling release outside the Library. It consumes the governed domain, evidence, methodology, project-object, provenance, and Research Librarian foundation established in Carbon & Nature v0.1.0–v0.5.0 and adds an explicit Soil Organic Carbon calculation workspace to Lab.

## Added

- Fixed-depth soil organic carbon stock calculations by soil layer.
- SOC concentration normalization across g/kg, mg/g, percent, and fraction inputs.
- Bulk-density normalization across g/cm³, Mg/m³, t/m³, and kg/m³.
- cm/mm/m depth normalization with explicit top/bottom intervals.
- Supplied coarse-fragment correction and fine-earth fraction reporting.
- Non-overlapping layer aggregation into profile SOC stock in Mg C/ha.
- Optional parcel-area scaling from Mg C/ha to total Mg C.
- Deterministic input/result fingerprints and explicit calculation basis.
- Carbon Project `model-run` handoff packets using the existing `sc-carbon-project-packet/1.0` contract.
- Browser-local Lab project persistence under `carbonCycleRecords`.
- A Carbon & Nature navigation group, `[sc_lab_soil_organic_carbon]` focused shortcode, and SOC command-search entry.
- A profile visualization plus Graph Studio handoff.
- FastAPI + WordPress proxy endpoints for health, schema, policy, layer calculation, profile calculation, and project packet construction.

## Scientific formula

For each supplied layer:

`SOC stock (Mg C/ha) = SOC (g/kg) × bulk density (g/cm³) × layer thickness (cm) × 0.1 × (1 − coarse fragments % / 100)`

The profile stock is the sum of non-overlapping layer stocks. The implementation reports gaps rather than filling them.

## Scientific boundaries

v0.6.0 does **not** infer stock change, annual sequestration, CO₂e, uncertainty, additionality, leakage, permanence, methodology eligibility, project verification, certification, or carbon-credit eligibility. It does not implement equivalent-soil-mass correction. Supplied measurements are treated as inputs, not as verified observations.

## Versioning

Carbon & Nature retains its own domain release line. Lab does not regress from v0.88.0 to v0.6.0; the host Lab application therefore advances to **v0.89.0**, while the embedded Carbon & Nature scientific capability is **v0.6.0**.

## Next domain releases

The next SOC sequence remains: v0.7.0 Sampling & Field Measurement Studio → v0.8.0 SOC Change & Sequestration Model → v0.9.0 SOC Spatial Variability & Uncertainty → v0.10.0 SOC Management Scenario Studio → v0.11.0 Whole-Farm GHG Balance.
