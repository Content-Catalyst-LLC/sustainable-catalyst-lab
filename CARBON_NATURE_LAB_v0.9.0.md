# Carbon & Nature Intelligence v0.9.0 — SOC Spatial Variability & Uncertainty

## SOC Spatial Variability & Uncertainty

This release extends the fixed-depth SOC stock, field-sampling, and stock-change sequence with governed statistical uncertainty. It quantifies variability in supplied replicate SOC stock estimates without converting a confidence interval into a causal, verification, or crediting claim.

### Added
- Replicate SOC stock summaries with mean, sample standard deviation, standard error, coefficient of variation, and two-sided Student-t confidence intervals at 90%, 95%, or 99%.
- Stock observations may be supplied directly in Mg C/ha or calculated from v0.6.0 profile inputs, preserving calculation fingerprints.
- WGS84 coordinate coverage diagnostics: coordinate count, duplicate coordinates, centroid, bounding box, nearest-neighbor distance, and maximum pairwise distance. These are descriptive only and do not establish spatial representativeness.
- Area-weighted stratified SOC stock estimation with independent-strata variance, effective degrees of freedom, uncertainty interval, and parcel-scale total stock.
- Paired and independent baseline/follow-up stock-change uncertainty, including confidence thresholds and optional annualization when elapsed time is explicit.
- First-order propagation of user-supplied standard uncertainty for SOC concentration, bulk density, layer thickness, and coarse fragments.
- Carbon Project model-run handoff, Lab project persistence, Graph Studio handoff, WordPress proxy routes, FastAPI routes, and deterministic fingerprints.
- Restored the retained 118-element `assets/data/elements.json` static resource after detecting it was absent from the packaged v0.91.0 baseline; v0.92.0 release packaging now verifies this asset explicitly.

### Scientific boundary
Sample-replicate variability is not total uncertainty. v0.9.0 does not automatically remove outliers, infer spatial representativeness, fit a variogram, perform kriging, infer correlations, apply finite-population correction, implement equivalent-soil-mass correction, establish intervention causality/additionality/permanence, verify a project, or determine carbon-credit eligibility.

### Version identity
- Lab: 0.92.0
- Carbon & Nature Intelligence: 0.9.0
- Compute Core: 1.0.0
- Previous Lab baseline: 0.91.0
- Next Carbon & Nature build: 0.10.0 — SOC Management Scenario Studio
