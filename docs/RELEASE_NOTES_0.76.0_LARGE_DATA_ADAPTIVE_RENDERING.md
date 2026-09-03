# Sustainable Catalyst Lab v0.76.0 — Large-Data Visualization & Adaptive Rendering

v0.76.0 adds a governed adaptive-rendering layer above the v0.75 scientific data-binding pipeline and the v0.74 plot grammar. Large source datasets can now be reduced to deterministic render representations without changing the authoritative source dataset.

## Capabilities

- Backend source datasets up to 250,000 flat rows.
- Browser inline adaptive sources up to 50,000 rows.
- Render budgets from 100 to 5,000 points.
- Plot-aware strategies: LTTB, grid-preserving selection, quantile-preserving selection, deterministic stride, and full rendering within budget.
- Progressive preview, interactive, and detail representations.
- Source-row count, rendered-row count, omitted-row count, strategy, point budget, and render-plan identity are retained with figures.
- v0.75 data binding, v0.74 advanced 2D plots, and canvas4d project-data projection remain compatible.

## Scientific boundary

Adaptive rendering changes only the displayed representation. It does not mutate the authoritative source dataset, invent observations, interpolate surfaces, forecast, or add uncertainty. Scientific transformations are never applied after sampling; large transformed sources must be transformed or aggregated upstream before the adaptive rendering stage.

Streaming, server-side tiles, and WebGL rendering remain deferred to later visualization releases.
