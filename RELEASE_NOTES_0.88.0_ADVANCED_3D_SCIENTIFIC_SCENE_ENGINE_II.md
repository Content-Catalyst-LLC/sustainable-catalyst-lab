# Sustainable Catalyst Lab v0.88.0 — Advanced 3D Scientific Scene Engine II

v0.88.0 advances Visualization Engine 2 to **2.14.0** on top of the production-certified v0.87 WebGPU line. It adds a governed advanced 3D scene layer rather than a second independent visualization engine.

## Added

- Nested scientific scene graphs with explicit parent/child validation and cycle rejection.
- Perspective and orthographic cameras with orbit/pan/zoom interaction state.
- Ambient, directional, and point lighting as presentation-only metadata.
- Explicit scientific materials, depth behavior, transparency, wireframe intent, and bounded scalar-color metadata.
- Native WebGPU point, line, line-strip, and triangle render pipelines with depth buffering.
- GPU instancing through explicit per-instance model matrices.
- Mesh, point-cloud, line, vector, group, and raster-plane scene nodes.
- A Three.js compatibility adapter that uses a locally available `window.THREE` runtime when present; Lab does not load a CDN automatically.
- Governed render plans, workspaces, provenance fingerprints, and v0.88 FastAPI/WordPress health/schema contracts.
- Graph Studio Advanced 3D diagnostics, native WebGPU scene demo, scene inspection, and explicit Three.js-adapter attempt.

## Scientific boundaries

v0.88 does not infer geometry, topology, normals, units, scientific meaning, surfaces, or data-driven lighting. Materials, lighting, camera motion, picking, and interaction do not create observations or mutate scientific values. Arbitrary shader source and silent renderer fallback remain disabled. Three.js and WebGPU availability are not required for scientific correctness.

## Compatibility

The release preserves the v0.87 WebGPU renderer/compute path, v0.85 WebGL2 fallback, v0.83 provenance, and v0.77 scientific-scene semantics. The independent System Dynamics Engine remains at 1.0.0.
