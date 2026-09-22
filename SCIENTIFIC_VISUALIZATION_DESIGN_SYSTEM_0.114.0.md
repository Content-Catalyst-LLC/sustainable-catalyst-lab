# Scientific Visualization Design System 0.114.0

## Design objective

Every Sustainable Catalyst figure should communicate scientific structure before decoration. The system therefore treats typography, hierarchy, scale, uncertainty, annotation, provenance, accessibility, and export fidelity as parts of the scientific interface rather than cosmetic post-processing.

## Publication profiles

- `journal-single` — compact 89 mm figure, 600 DPI raster fallback.
- `journal-double` — 183 mm figure, 600 DPI raster fallback.
- `report-wide` — report/brief layout.
- `web-responsive` — 1440×810 reference canvas with responsive collapse.
- `slide-wide` — presentation-scale typography.
- `poster` — large-format composition.

## Visual semantics

Semantic roles include observed, model, forecast, comparison, reference, threshold, anomaly, positive, negative, and muted. Roles combine color, line treatment, and marker treatment so scientific meaning is not encoded by color alone.

## Uncertainty

Confidence, credible, prediction, ensemble, and sensitivity bands use distinct boundary and fill treatments. The bridge only styles uncertainty explicitly supplied by upstream scientific methods; it never manufactures an interval.

## Rendering

Publication-oriented 2D figures prefer SVG and PDF. Large interactive datasets may use WebGL2. 3D/4D scenes may use WebGPU with raster export where vector representation is not meaningful. Renderer choice is advisory and execution remains in the established Lab renderer stack.
