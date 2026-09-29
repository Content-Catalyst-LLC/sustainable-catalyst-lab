# Carbon & Nature Intelligence v0.7.0 in Sustainable Catalyst Lab v0.90.0

## SOC Sampling & Field Measurement Studio

This release extends the v0.89.0 fixed-depth Soil Organic Carbon foundation with governed field-sampling records and field-to-model handoffs.

### Added
- Structured SOC field-sample records with stable IDs, parcel/profile/stratum context, depth intervals, WGS84 coordinates, collector/time metadata, and deterministic fingerprints.
- Core-volume bulk-density calculation using explicit oven-dry mass and core volume, with mass basis retained.
- Sampling-plan registry for simple random, systematic grid, stratified random, transect, paired, composite, purposive, and other declared designs.
- Deterministic planned sample IDs without pretending to spatially randomize or generate coordinates.
- Chain-of-custody metadata events for collection, transfer, receipt, subsampling, analysis, storage, and disposal.
- Batch normalization and QA/readiness diagnostics.
- Explicit handoff from profile-ready field samples to the v0.6.0 fixed-depth SOC stock engine.
- Carbon Project packet construction using `sample` and `observation` objects.
- New Lab browser workspace and WordPress/FastAPI routes.
- Restores the 118-element periodic-table static asset from the certified v0.88.0 R2 baseline so the retained Graph Studio/static-asset compatibility contract remains executable.
- Narrows release packaging exclusions to mutable runtime `data/` roots so static application assets under `assets/data/` remain in repository and WordPress distributions.

### Scientific boundaries
The release does not determine sample-size adequacy, perform statistical power analysis, generate spatial sample locations, average replicates, infer SOC stock change, estimate sequestration rates, infer uncertainty, determine methodology eligibility, or determine credit eligibility. Chain-of-custody metadata is recorded but not digitally signed.

### Version identity
- Lab: 0.90.0
- Carbon & Nature Intelligence: 0.7.0
- Compute Core: 1.0.0
- Previous Lab baseline: 0.89.0
- Next Carbon & Nature build: 0.8.0 — SOC Change & Sequestration Model
