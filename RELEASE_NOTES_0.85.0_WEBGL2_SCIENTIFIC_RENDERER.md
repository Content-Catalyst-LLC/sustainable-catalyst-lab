# Sustainable Catalyst Lab v0.85.0 — WebGL2 Scientific Renderer

v0.85.0 turns the v0.84 GPU renderer architecture into the first production GPU renderer in Graph Studio.

## Visualization Engine 2.12.0

WebGL2 is now a production renderer while WebGPU remains capability-detected and implementation-gated for v0.86. Existing SVG and Canvas renderers remain valid fallbacks; GPU availability never changes the scientific contract.

## Production WebGL2 capabilities

- real WebGL2 browser context and renderer lifecycle
- depth-buffered 3D scientific scenes
- GPU point clouds and line segments
- indexed and non-indexed triangle meshes
- instanced geometry with explicit instance offsets
- raster textures on declared spatial quads
- alpha blending and face culling
- bounded GPU memory/draw contracts
- RGBA8 framebuffer object picking with source-object identity preservation
- renderer-owned approved GLSL programs only
- explicit fallback to an existing Canvas renderer when WebGL2 is unavailable
- compatibility with v0.84 GPU negotiation and v0.83 figure provenance

## Scientific boundaries

The renderer does not generate surfaces, interpolate spatial or temporal observations, alter figure semantics, or accept arbitrary user shader source. Picking is an interaction result, not a scientific observation. WebGPU remains non-production until v0.86.0.
