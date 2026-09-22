# Sustainable Catalyst Lab v0.116.0 — Interactive Scientific Dashboards & Small Multiples

This release adds a publication-aware scientific dashboard composition layer over the existing visualization, linked-view, uncertainty, and statistical graphics stack.

## Added
- Responsive multi-panel scientific dashboards (up to 48 panels).
- Linked selection, brushing, filtering, cursor, state-axis, parameter, and time-window interactions.
- Dashboard controls with explicit targets.
- Scientific small multiples using the v0.114 design system.
- Explicit scale synchronization from declared domains.
- Deterministic state snapshots and explicit restore plans.
- Provenance trace and accessibility audit surfaces.
- Dashboard/figure-set/publication-sheet/state-bundle export planning.
- Core visual-binding plans that remain non-submitting.

## Boundaries
The dashboard layer does not infer joins, choose scale domains from hidden data, execute queries automatically, persist/restore state automatically, submit to Core automatically, perform statistical inference, certify scientific validity, or determine truth.
