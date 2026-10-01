# Sustainable Catalyst Lab v0.153.0 — 4D Computational Research Workspace

v0.153.0 promotes the recovered v0.152.0.13 4D front door from browser-local exploration into a project-linked computational research workspace.

## Runtime architecture

- v0.152.0.13 layout and visible 4D rendering baseline is retained.
- Browser scenes remain compatible with the `sc-lab-v015212-scenes` migration key.
- A new authenticated WordPress bridge proxies project-workspace operations to the Python Compute Core.
- The backend stores project-linked 4D assets in SQLite WAL under the Lab `/app/data` persistent volume.
- Workspace assets use immutable revisions rather than in-place scientific-state mutation.
- Explicit forks preserve parent-asset lineage.
- Descriptive comparison reports tracked scene-state differences without drawing scientific conclusions.
- Compute-result/run references are preserved with the scene and provenance when available.
- Restoring a workspace asset never reruns computation automatically.

## Contracts

- `sc-lab-4d-computational-workspace-asset/0.153.0`
- `sc-lab-4d-computational-workspace-revision/0.153.0`
- `sc-lab-4d-computational-workspace-lineage/0.153.0`
- `sc-lab-4d-computational-workspace-comparison/0.153.0`

## User workflow

1. Explore or compute a 4D scene.
2. Save/select the browser scene in Scene / Provenance.
3. Promote it to the active project workspace.
4. Preserve later scene states as immutable revisions.
5. Load any workspace asset without recomputing.
6. Fork an asset to start an explicit alternative line of work.
7. Compare latest revisions descriptively.
8. Inspect parent/fork lineage and revision history.
9. Archive an asset without deleting its research record.

## Scientific boundary

Workspace persistence and comparison preserve computational state, selections, compute references, provenance, and lineage. They do not establish evidence, causality, statistical significance, calibration, forecast skill, or scientific validity. Scientific compute remains user-initiated.
