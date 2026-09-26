# Graph Studio Review State Machine — v0.135.14.0

The v0.135.14.0 layer consumes the review thread from v0.135.12.0 and the append-only disposition/revision lineage from v0.135.13.0. It adds a separate `graphStudioReviewAudits` record so verification and resolution governance can evolve without rewriting either prior source.

The principal workflow for revision-producing actions is:

`addressed + explicit action → action-required → verification-recorded → verified / verification-failed / verification-required → resolution-confirmed → resolved`

`ready-to-resolve` is used when an addressed resolution has no follow-up action. `deferred`, `withdrawn`, and `superseded` remain explicit workflow outcomes. `reopened` is an append-only transition that preserves the full earlier history.

Backend audit-trail reconstruction uses SHA-256 chaining over normalized events. Separate link-integrity validation checks `previousEventId` continuity. These mechanisms document mutation/tamper evidence within the audit record; they are not cryptographic signatures or scientific validation.
