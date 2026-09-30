# Lab v0.152.0.3 — Critical Bootstrap Dependency & Lab Navigation Recovery

## Failure repaired

v0.152.0.1 intentionally broke the historical all-or-nothing optional-module dependency chain, but the initial critical set omitted `workspace.js` and `feeds.js`. `sc-lab-app.js` renders Overview during bootstrap and synchronously calls `Lab.Workspace.traceCounts()` and `Lab.Workspace.projectTotal()`. When `workspace.js` had not executed yet, the main application could fail during initialization, leaving the Lab page in a loading state and primary navigation inert.

## Repair

- `workspace.js` and `feeds.js` are now explicit critical dependencies of the main Lab app.
- `sc-lab-app.js` has a minimal Workspace fallback so navigation can still initialize if secondary workspace metadata is unavailable.
- Overview feed loading degrades to a non-blocking status message instead of aborting startup.
- v0.152.0.2 full-panel DOM retention remains in force.
- v0.152 dependency-graph backend behavior is unchanged.

## Identity note

A stale `v0.48` label rendered outside the canonical plugin shell is a WordPress page-content/presentation identity issue, not the active plugin release identity. Canonical plugin/runtime identity remains `SC_LAB_RELEASE_VERSION`.
