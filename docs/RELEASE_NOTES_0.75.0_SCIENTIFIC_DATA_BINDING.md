# Sustainable Catalyst Lab v0.75.0 — Scientific Data Binding & Transformation Pipeline

v0.75.0 connects real scientific datasets to the unified Visualization Engine 2 architecture introduced in v0.73 and expanded by the v0.74 Advanced 2D Plot Grammar.

## What this release adds

- A governed `scientific-dataset` object with row/column metadata, units, source provenance, and deterministic SHA-256 fingerprinting.
- A reproducible transformation pipeline with per-stage input/output hashes and explicit lineage.
- Compatibility with the established v0.55 transformation engine for derive/filter/rename/select/drop/scale/unit-convert/cast/impute plus v0.75 sort, aggregate, bin, and drop-missing stages.
- A visualization binding contract that maps dataset columns to x/y/z/w, intervals, groups, labels, values, sizes, weights, and contour levels.
- Dataset → pipeline → binding → figure provenance and fingerprints in saved Graph Studio v0.75 figures.
- Real project-data binding across the v0.74 2D plot grammar.
- Real project-data 4D point projection with x/y/z/w normalization for projection while preserving original domains and units.
- WordPress and FastAPI health/schema/execution endpoints for the v0.75 binding layer.

## Scientific boundaries

v0.75 never runs arbitrary code, SQL, filesystem operations, or network requests as part of the binding pipeline. Unit inference, imputation, and feature engineering are never automatic. Project-data 4D rendering projects supplied records only; it does not interpolate a response surface, infer uncertainty, forecast between records, or create synthetic observations.

Polar/radar and dual-axis scientific contracts remain deferred.
