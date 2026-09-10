# Advanced 3D Scientific Scene Engine II — v0.88.0

Visualization Engine 2.14.0 adds a governed scene layer above the v0.87 WebGPU execution path.

The canonical scene contains explicit cameras, lights, materials, nodes, transforms, geometry counts/data, source identities and provenance. Parent/child relationships are validated, duplicate ids and cycles are rejected, and render plans record explicit renderer fallback policy.

The browser implementation includes native WebGPU point, line, line-strip and triangle pipelines with depth buffering and per-instance model matrices. A Three.js compatibility adapter is available only when a local `window.THREE` runtime is already present. No external CDN is loaded by Lab.

Scientific boundaries remain strict: no automatic triangulation, surface interpolation, geometry generation, normal generation, unit conversion, scientific interpretation, data-driven lighting, arbitrary shader source, silent renderer fallback, or observation creation from interaction.
