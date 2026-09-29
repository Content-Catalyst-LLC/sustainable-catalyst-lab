# Sustainable Catalyst Lab v0.88.0 R2 — Graph Studio Bootstrap & Static Asset Repair

This repair keeps the canonical public Lab release at **0.88.0** and layers two browser-side production fixes on top of the v0.88.0 R1 WebGPU pipeline-validation repair.

## Repairs

- Graph Studio 2D bindings no longer treat dormant `z` and `w` controls as required mapped columns for 2D figures.
- Missing-row governance now evaluates only columns scientifically required by the selected visualization kind plus declared series/interval/group mappings.
- The default confidence-band example can bootstrap from its valid `time`, `observed`, `lower`, and `upper` columns without all rows being removed by the v0.75 missingness gate.
- `assets/data/elements.json` is restored with all 118 elements so the Chemistry Laboratory / Periodic Table static-data request no longer returns HTTP 404.
- R1 WebGPU shader syntax, validation scopes, asynchronous render-pipeline creation, and GPU queue-completion guards are preserved unchanged.

## Scientific boundaries preserved

- Missing values in columns actually required by the selected visualization remain governed by `dropMissingMappedRows`.
- The repair does not impute data, infer mappings, generate geometry, create observations, or alter scientific values.
- The backend is unchanged; no Contabo Lab rebuild or restart is required.

## Production symptoms addressed

- `No rows remain after binding missingness checks.` during Graph Studio confidence-band bootstrap.
- HTTP 404 for `/wp-content/plugins/sustainable-catalyst-lab/assets/data/elements.json`.
