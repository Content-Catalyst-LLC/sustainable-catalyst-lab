# Advanced 3D/4D Scientific Visualization — v0.117.0

## Architecture
Data/model output → explicit 3D/4D scene semantics → renderer-neutral plan → WebGL2/WebGPU/canvas runtime → dashboard or publication export.

## Core objects
Surface grids, triangle meshes, point clouds, vector fields, scalar fields, volumes, trajectories, streamlines, isosurfaces, slice planes, uncertainty envelopes, and glyph fields.

## Reproducibility rules
Mesh topology, coordinate frame, units, camera state, time axis, slice planes, isovalues, volume transfer functions, and uncertainty levels must be declared. Camera and time state are provenance-bearing.
