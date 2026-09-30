# Lab v0.152.0.1 — Navigation Bootstrap & Graph Studio Access Recovery

## Purpose
Repair a front-end availability regression where the Lab main application script could be starved behind a very large cumulative JavaScript dependency chain. When a late optional module request failed, was throttled, or was unavailable, the primary Lab navigation could remain uninitialized and all module buttons—including Graph Studio—appeared inert.

## Changes
- Loads the minimal interactive shell (`core`, `projects`, `project-workspace-v0280`) before the optional module fleet.
- Enqueues `sc-lab-app.js` before optional research modules so primary navigation is not blocked by one late optional asset.
- Removes the cumulative 247-module dependency chain; optional modules depend only on the production bootstrap.
- Adds `sc-lab-navigation-recovery-v015201.js`, a fail-safe module navigator that activates only when the full Lab app has not reached ready state or has failed.
- Preserves v0.152.0 Cross-Workspace Research Dependency Graph backend contracts and all scientific boundaries unchanged.

## Graph Studio
Graph Studio itself is not replaced or downgraded. The repair restores reachability to the existing canonical Graph Studio stack and preserves its renderer/provenance/review modules.

## Backend
No backend behavior changes are required. The v0.152.0 backend remains compatible; a backend package is retained in the release bundle for release-line completeness.
