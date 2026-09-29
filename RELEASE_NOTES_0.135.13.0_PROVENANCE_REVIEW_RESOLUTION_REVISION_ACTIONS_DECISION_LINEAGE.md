# Sustainable Catalyst Lab v0.135.13.0

## Provenance Review Resolution, Revision Actions & Decision Lineage

This release extends Graph Studio provenance review threads with an explicit resolution and revision-action layer.

### Added

- Append-only resolution records linked to v0.135.12.0 review annotations.
- Dispositions: addressed, deferred, withdrawn, and superseded.
- Explicit revision actions for method, data, figure, evidence, claim clarification, rerun, and follow-up workflows.
- Required revision/artifact references for revision-producing actions.
- Current disposition badges without mutation of the original annotation record.
- Pending-review counts and decision-lineage reconstruction.
- Explicit project persistence to `graphStudioReviewResolutions`.
- Project Workspace resolution-context handoff.
- Backend normalization, summaries, pending-item extraction, revision-action extraction, decision lineage, fingerprints, contracts, and resolution packets.

### Boundaries

A review disposition is a workflow record, not a scientific verdict. The release does not infer truth, falsity, causation, evidentiary weight, or preferred explanations from a disposition, response, revision reference, or graph structure.
