# Graph Studio Provenance Review Resolution — v0.135.13.0

## Purpose

v0.135.13.0 extends provenance review threads with explicit resolution workflow. Review annotations remain intact; a separate append-only resolution record captures how each annotation was dispositioned, what response was recorded, and whether an explicit revision or follow-up action was requested.

## Resolution model

Supported dispositions are `addressed`, `deferred`, `withdrawn`, and `superseded`. Supported actions are `none`, `revise-method`, `revise-data`, `revise-figure`, `add-evidence`, `clarify-claim`, `rerun-analysis`, and `follow-up`.

Revision-producing actions (`revise-method`, `revise-data`, `revise-figure`, and `rerun-analysis`) require an explicit revision or artifact reference. The runtime does not invent a revision reference from annotation text or graph structure.

## Decision lineage

Resolution events are append-only. Recording a later disposition for the same annotation does not delete the earlier event; the most recent event determines the current workflow badge while the full sequence remains available as decision lineage.

The original v0.135.12.0 annotation is not mutated. This keeps reviewer observation history separate from response and revision history.

## Rendering ownership

The v0.135.8.5.x native provenance controller remains the sole graph renderer. v0.135.13.0 updates review-card status markers only and does not rebuild the provenance graph.

## Project persistence

`Save resolution record` writes the record to the active Lab project collection `graphStudioReviewResolutions`. Saving is explicit; adding or viewing a resolution does not silently modify other scientific objects.

## Cross-workspace handoff

`Open resolution context` carries the review thread snapshot, resolution record, current summary, pending annotation IDs, and decision lineage into Project Workspace.

## Scientific boundary

A workflow disposition does not establish truth or falsity. `addressed` means that an explicit response/action was recorded for the review item; it does not certify the underlying scientific claim, model, path, figure, evidence, or conclusion.
