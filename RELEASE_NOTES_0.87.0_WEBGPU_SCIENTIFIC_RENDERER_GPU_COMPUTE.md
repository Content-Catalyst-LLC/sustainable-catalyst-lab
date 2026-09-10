# Sustainable Catalyst Lab v0.87.0 — WebGPU Scientific Renderer & GPU Compute

v0.87.0 promotes WebGPU from a detected candidate to a governed production renderer and browser-compute path while retaining v0.85 WebGL2 as the explicit production fallback. Visualization Engine 2 advances to 2.13.0; the v0.86 System Dynamics Engine remains 1.0.0.

## Capabilities

- Real `navigator.gpu` adapter/device acquisition and `GPUCanvasContext` configuration.
- Renderer-owned WGSL pipelines for scientific point/line/mesh/raster/picking surfaces.
- Governed WebGPU compute kernels for threshold filtering, histograms, min/max and sum reductions, and spatial binning.
- Typed storage-buffer and memory-budget contracts.
- Explicit WebGL2 rendering fallback and governed CPU compute fallback.
- Graph Studio WebGPU diagnostics, rendering preview, and compute-pipeline inspection.
- v0.86 systems-modeling and v0.85/v0.84/v0.83 visualization/provenance compatibility.

## Scientific boundaries

WebGPU availability is never required for scientific correctness. Fallback is explicit. Arbitrary WGSL is not accepted. GPU transforms cannot silently interpolate, impute, forecast, reinterpret scientific semantics, or create new observations. Large dispatches that exceed the governed workgroup limit must be explicitly chunked rather than silently truncated.
