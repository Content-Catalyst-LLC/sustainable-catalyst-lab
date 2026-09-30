# Lab v0.152.0.12 — 4D Scene Persistence, Provenance & Research Object Handoff

## Purpose
Promote the v0.152 4D front door from transient visualization state into a persistent, inspectable research workspace object without re-enabling the legacy eager runtime fleet.

## Capabilities
- Save up to 12 bounded 4D scenes in browser local storage.
- Restore scene camera/hyperslice/layer state, response-surface grids, uncertainty/sensitivity/ensemble results, selections, history, and pins without automatically rerunning compute.
- Capture descriptive provenance and a SHA-256 scene-state digest when Web Crypto is available.
- Export persisted scenes as JSON.
- Prepare a reference-first canonical `workspace-snapshot` research object using `sc-lab-canonical-research-object/0.105.0`.
- Explicitly hand the research object to Graph Studio, Notebook, or Experiments through `sessionStorage` plus a `sc-lab:research-object-handoff` event.

## Scientific boundaries
Persistence and handoff preserve computational and visualization state. They do not convert a modeled output into observed evidence, establish causality or significance, certify calibration, or establish scientific validity. Platform Core submission remains explicit and is not automatic in this release.

## Runtime architecture
The v0.152.0.12 asset gate permits only the canonical safe bootstrap, the consolidated linked-scientific-views runtime, the scene-persistence runtime, and consolidated Lab CSS. Heavy historical modules remain non-eager.
