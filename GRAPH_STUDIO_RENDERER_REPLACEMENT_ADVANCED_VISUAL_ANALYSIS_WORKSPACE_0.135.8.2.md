# Lab v0.135.8.2 — Graph Studio Renderer Replacement & Advanced Visual Analysis Workspace

v0.135.8.2 replaces legacy Graph Studio primary-canvas ownership with a dedicated renderer host. The canonical workspace keeps eight research views while the Figure workspace gains six genuinely distinct renderer modes: Plot, Distribution, Diagnostics, Uncertainty, Provenance, and 3D/Spatial.

## Runtime ownership
- Primary renderer owner: `graph-studio-renderer-v013582`
- Renderer engine: `3.0.0`
- Historical Graph Studio v0.79–v0.88 JavaScript generations are retained in the repository but skipped by the live module loader.
- v0.135.8.1 remains navigation/lifecycle infrastructure; it no longer owns the scientific rendering surface.

## Visual-analysis behavior
The renderer reads already-bound Graph Studio scientific objects and renders independent analytical views. Plot selection, camera state, provenance layout, distribution bins, diagnostics and renderer choice remain presentation state. Missing uncertainty, joins, model structure, CRS, causal relationships, evidence meaning, and claim state are never fabricated.

## Acceptance boundary
A valid runtime has one primary viewport, zero visible legacy primary canvases, zero stacked research surfaces, and no executed historical Graph Studio generation on the canonical route.
