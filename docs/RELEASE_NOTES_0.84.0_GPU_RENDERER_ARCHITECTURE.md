# Sustainable Catalyst Lab v0.84.0 — GPU Renderer Architecture

v0.84.0 establishes the governed renderer architecture required for the advanced visualization roadmap without making GPU availability a scientific dependency.

## Visualization Engine 2.11.0

The renderer registry now distinguishes production renderers from candidate GPU backends. SVG and existing Canvas renderers remain production-ready. WebGL2 and WebGPU enter the registry as browser-detectable, implementation-gated targets for v0.85 and v0.86.

## Governed capabilities

- browser renderer capability detection
- renderer capability registry
- explicit renderer negotiation
- recorded fallback decisions
- typed GPU buffer plans and bounded memory budgets
- approved shader descriptor contracts based on source fingerprints
- picking contracts that preserve source identity
- renderer diagnostics
- Graph Studio GPU capability console
- compatibility with v0.83 provenance-aware figures and the complete v0.75–v0.82 visualization lineage

## Scientific boundaries

v0.84 does not silently change scientific semantics based on device capabilities. GPU acceleration is optional. Renderer fallbacks are explicit and fingerprintable. Arbitrary shader source is not accepted. Server runtime does not assume that a browser has a GPU API merely because the backend is healthy.

The production WebGL2 renderer is reserved for v0.85.0. The production WebGPU renderer is reserved for v0.86.0.
