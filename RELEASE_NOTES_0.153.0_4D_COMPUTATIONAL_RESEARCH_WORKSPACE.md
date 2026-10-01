# Release notes — Lab v0.153.0

**Release:** 4D Computational Research Workspace

This release advances the stable v0.152.0.13 4D front door into a server-backed project workspace.

### Added
- Server-backed project-linked 4D workspace assets.
- Immutable workspace revisions.
- Explicit fork lineage.
- Descriptive latest-revision comparison.
- Compute-run/result reference preservation.
- Workspace asset load without automatic recomputation.
- Asset archive without revision deletion.
- New WordPress REST bridge and authenticated Python backend routes.
- New workspace asset, revision, and lineage schemas.

### Retained
- v0.152.0.13 front-door layout and explicit canvas palette.
- Response-surface, uncertainty, sensitivity, ensemble, linked-view, and scene-provenance functionality.
- Browser-local saved-scene migration key from v0.152.0.12.
- PHP output-safety release gate.
- 120-route v0.152 cross-workspace dependency graph.

### Scientific behavior
The workspace backend changes persistence and lineage behavior. Registered scientific compute methods are unchanged and still execute only on explicit user action.
