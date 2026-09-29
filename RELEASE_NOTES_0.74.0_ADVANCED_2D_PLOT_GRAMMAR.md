# Sustainable Catalyst Lab v0.74.0 — Advanced 2D Scientific Plot Grammar

v0.74.0 expands Graph Studio's unified `svg2d` renderer into a governed Cartesian scientific plot grammar while preserving the v0.73 Visualization Engine 2 architecture and the existing `canvas4d` path.

## Added
- Plot grammar contract `sc-lab-advanced-2d-plot-grammar/0.74.0`.
- Advanced plot kinds: step, area, stacked area, bar, grouped/stacked bar, density/KDE, box, violin, error bar, confidence band, contour, hexbin, ECDF, Q-Q, residual, waterfall, and Pareto.
- Explicit axis metadata for linear, logarithmic, symmetric-log, probability, datetime, and categorical scales.
- Axis units, scientific/SI/plain/percent tick-format intent, inversion state, and category/domain metadata.
- Graph Studio controls for the new plot grammar and axis semantics.
- Backend normalization, figure/workspace contracts, FastAPI routes, WordPress health/schema routes, and compatibility tests.

## Compatibility
- Existing line/scatter/line-scatter/histogram/horizontal-bar/heatmap figures remain accepted.
- The v0.44 SVG renderer remains the low-level compatibility/export path.
- `surface-4d` remains a first-class `canvas4d` figure and is carried forward through the v0.73 adapter.
- Saved v0.73 and v0.47 figures remain discoverable in Graph Studio.

## Boundaries
- v0.74 is Cartesian 2D. Polar/radar plots are deferred until a coordinate-system contract can represent them correctly.
- Dual axes remain deferred to avoid ambiguous scale relationships.
- General dataset binding/transformation provenance remains a v0.75 concern.
- 4D project-data surface binding remains deferred to v0.75.
- Arbitrary code and remote image fetching remain disabled.
