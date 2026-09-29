# Lab v0.141.2 — Training Curves, Metrics & Checkpoint Visualization

This release turns Workspace-returned neural training telemetry into governed Lab visual research objects. It provides raw and derived training curves, metric catalogs and summaries, multi-run overlays, small multiples, train/validation gap views, checkpoint timelines, metric-to-checkpoint linkage, explicitly directed checkpoint-candidate markers, and descriptive convergence diagnostics.

## Boundary

Workspace remains execution authority. Raw telemetry is immutable. Smoothing is a derived visualization with declared parameters. A metric extremum may identify a checkpoint candidate only when the objective direction is explicitly supplied; it is never an endorsed model. Plateau heuristics do not certify convergence, and training metrics do not become evidence.
