# Sustainable Catalyst Lab v0.114.0 — Scientific Visualization Design System & Publication-Grade Rendering

v0.114.0 converts the Lab's mature visualization runtime into a consistent publication-grade visual language. It layers on top of the existing v0.74 scientific visualization grammar, v0.83 provenance-aware figures, v0.84 renderer registry, v0.87 WebGPU renderer, v0.88 advanced scientific scenes, and v0.109 Core visual bridge.

## Added

- Six publication profiles: journal single/double column, report wide, responsive web, presentation, poster.
- Semantic series roles with redundant non-color encodings.
- Evidence-aware annotations and collision-policy metadata.
- First-class confidence, credible, prediction, ensemble, and sensitivity uncertainty styles.
- Responsive small-multiple composition with consistent panel labeling.
- Accessibility metadata, keyboard/focus expectations, reduced-motion behavior, and table fallbacks.
- Renderer planning that keeps ordinary publication figures vector-first while preserving WebGL/WebGPU for genuinely large or multidimensional scenes.
- SVG/PDF/PNG/TIFF/JSON/CSV export planning with print dimensions/DPI.
- Publication-readiness audits that separate layout/presentation readiness from scientific validity.
- WordPress CSS/JS presentation layer that applies the design system to the existing SVG renderer.
- Optional Core v3 scientific-figure binding plan through the retained v0.109 visual bridge.

## Boundaries

The design system does not infer scientific claims, uncertainty, source provenance, scientific validity, or truth. It does not automatically submit visual objects to Platform Core or write export files.
