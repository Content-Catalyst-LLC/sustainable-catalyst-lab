# Sustainable Catalyst Lab v0.135.14.0

## Review State Machine, Action Verification & Resolution Audit

This release extends v0.135.13.0 review resolution with an explicit, append-only governance layer that separates a recorded response from a verified and confirmed resolution.

### Added

- Per-annotation review state machine derived from the current v0.135.13.0 disposition plus v0.135.14.0 audit events.
- Explicit states for open, action-required, verification-required, verification-failed, verified, ready-to-resolve, resolved, deferred, withdrawn, superseded, and reopened.
- Action verification events with outcome, verification method, and required evidence/artifact reference.
- Resolution confirmation gate: revision-producing actions cannot become resolved until verification passes.
- Explicit reopen events without mutating prior resolution or annotation history.
- Append-only resolution audit records persisted to `graphStudioReviewAudits`.
- Backend SHA-256 audit-chain reconstruction and previous-event-link integrity checks.
- Resolution-readiness extraction, state summaries, audit packets, fingerprints, contracts, and Project Workspace handoff.
- Incremental state badges that do not trigger a Graph Studio full redraw.

### State semantics

An `addressed` disposition with a non-`none` action begins in `action-required`. A passing explicit verification moves the item to `verified`; a separate `resolution-confirmed` event moves it to `resolved`. An addressed item with no follow-up action begins `ready-to-resolve` and still requires explicit resolution confirmation. Deferred, withdrawn, and superseded dispositions remain distinct terminal workflow states and can be reopened through an explicit audit event.

### Scientific boundaries

A verified action means the review action was checked against an explicitly referenced artifact/evidence item using a recorded method. It does not establish that the underlying scientific claim, causal interpretation, evidence weight, or preferred conclusion is true. v0.135.14.0 does not mutate v0.135.12.0 annotations or v0.135.13.0 resolution events.
