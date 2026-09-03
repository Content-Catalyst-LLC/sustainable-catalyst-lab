# Sustainable Catalyst Lab v0.77.0 — 3D Scientific Scene Engine

## Purpose

v0.77.0 adds a native governed three-dimensional scene layer to Graph Studio. The release represents real x/y/z coordinates and explicit geometry under a renderer-aware scientific scene contract while preserving the existing 2D and 4D visualization paths.

## Capabilities

- `canvas3d` renderer with perspective and orthographic camera models.
- 3D point clouds, ordered polylines/trajectories, line segments, vector fields, and explicit triangle meshes.
- Orbit and zoom interaction with camera state captured in exported scene specifications.
- Explicit axis labels/units, scene bounds, clipping intent, lighting metadata, PNG and JSON export.
- Dataset-bound 3D scenes can reuse v0.75 governed transformations before rendering.
- Large 3D datasets reuse the v0.76 deterministic stride representation before scene construction; source-row authority remains upstream.
- Saved v0.77 figures carry scene, dataset, pipeline, mapping, adaptive-rendering, camera, renderer, and provenance state.

## Scientific boundaries

- Scattered observations are never converted into an inferred surface.
- Triangle topology must be supplied explicitly for mesh scenes.
- The current browser renderer uses painter depth sorting, not a WebGL depth buffer; no hidden-surface guarantee is claimed.
- Automatic triangulation, surface interpolation, forecasting, invented observations, arbitrary code, and remote geometry fetching are disabled.

## Compatibility

- Visualization Engine 2: 2.4.0
- `svg2d`: compatible with v0.74 advanced 2D grammar.
- v0.75 data binding/transformation lineage preserved.
- v0.76 large-data adaptive representation preserved.
- `canvas4d`: project-data 4D point projection remains available and separate from native 3D scenes.
