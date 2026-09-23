# Lab v0.135.1 — Scientific Visualization Experience Overhaul

Lab v0.135.1 turns Graph Studio from a primarily single-figure workspace into a multi-panel scientific analysis experience while preserving the existing governed rendering and research-object stack.

## Visual experience

- Primary scientific canvas remains authoritative.
- Analysis mode adds empirical response distribution, residual structure, sensitivity/influence linkage, dataset completeness, active renderer/layer status, model/method architecture, provenance pipeline, spatial/temporal capability view, higher-dimensional capability view, and evidence/assumption context.
- Under-the-hood mode exposes data → transform → binding → method → figure lineage plus renderer/capability state.
- Evidence mode foregrounds source, method, interpretation, and review boundaries.
- Figure mode hides supporting panels for presentation-focused work.
- Full-screen analysis is supported without changing scientific semantics.

## Scientific boundaries

The experience layer never fabricates missing posterior, sensitivity, diagnostic, spatial, or other scientific values. Panels requiring unavailable governed objects show explicit not-linked states. Empirical distribution previews are labeled empirical. Residual previews are created only when explicit observed and fitted/predicted numeric series are present. Presentation changes remain separate from the underlying scientific record.

## Architecture

Platform Core remains the semantic visual-object and cross-product reference authority. Lab remains the scientific-rendering authority. v0.135.1 reuses the existing visualization design system, linked-view, automatic-layout, Graph Studio, 3D/4D, spatial/raster, uncertainty, markup, provenance, WebGL2, and WebGPU layers.
