# Interactive Scientific Dashboards & Small Multiples — v0.116.0

## Purpose
Provide a governed interactive composition layer for scientific figures, scenes, statistical graphics, and research context.

## Runtime model
`data/model → figure/scene → panel → dashboard → interaction state → publication/export plan`

## Interaction channels
selection, brush, filter, cursor, state-axis, parameter, time-window.

## Design rules
- Links are explicit; they are never inferred.
- Cross-dataset joins are outside the dashboard layer.
- Shared scales require declared domains; hidden data are not scanned to invent domains.
- State snapshots are deterministic and restore requires an explicit compatible plan.
- Provenance is preserved per panel and across the dashboard.
- Dashboard accessibility is auditable and not dependent on color alone.
- Core receives visual-reference plans only; Lab remains authoritative for scientific dashboards and rendering.

## Dependencies
- v0.79 linked views/faceting/composition
- v0.114 scientific visualization design system
- v0.115 advanced statistical & uncertainty graphics
- v0.109 Core visual bridge
