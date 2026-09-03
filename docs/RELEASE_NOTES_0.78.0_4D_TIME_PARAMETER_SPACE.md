# Sustainable Catalyst Lab v0.78.0 — 4D, Time & Parameter-Space Visualization

v0.78.0 advances Visualization Engine 2 to 2.5.0 and extends Graph Studio with a governed Canvas4D state-space layer for observed four-dimensional records, discrete time-state playback, parameter sweeps, hyperslicing, and XW/YW/ZW projection controls.

## Scientific contract

The v0.78 state-space engine treats x/y/z/w records as authoritative observations. Time playback moves between supplied observed states only. Parameter sweeps select supplied parameter states only. Hyperslices filter supplied W coordinates. The renderer does not invent intermediate frames, interpolate unobserved parameter values, infer trajectories, construct response surfaces, forecast future states, or execute arbitrary code.

## Modes

- `4d-points` — observed x/y/z/w point projection.
- `time-sequence` — discrete playback and scrubbing across observed time states.
- `parameter-sweep` — observed parameter-state exploration without interpolation.

## Projection and interaction

- XW, YW, and ZW rotations.
- optional W hyperslice center/tolerance.
- source coordinate preservation with normalization used only for projection.
- discrete time playback with bounded frame rate and optional looping.
- PNG and JSON export from the browser renderer.

## Data and provenance

v0.78 preserves v0.75 transformation lineage for bounded browser/backend datasets and v0.76 deterministic adaptive rendering for large datasets. Large datasets are never transformed after adaptive sampling; they must be pre-transformed or aggregated upstream and submitted with an identity pipeline. Saved v0.78 figures carry state-space fingerprints, source dataset fingerprints, pipeline fingerprints, binding definitions, state-axis definitions, projection settings, and explicit no-interpolation boundaries.

## Compatibility

- v0.77 native `canvas3d` scientific scenes remain intact.
- v0.76 adaptive large-data rendering remains intact.
- v0.75 scientific data binding and transformation pipelines remain intact.
- v0.74 advanced 2D plot grammar and v0.73 Visualization Engine 2 compatibility remain intact.
- legacy v0.75 project-data 4D projection remains available as a compatibility path.

## Explicit boundaries

`syntheticFrames=false`, `temporalInterpolation=false`, `parameterInterpolation=false`, `automaticTrajectories=false`, `surfaceInterpolation=false`, `forecasting=false`, `arbitraryCode=false`.
