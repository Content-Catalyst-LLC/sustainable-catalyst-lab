# Lab v0.135.18.0 — Multi-Reviewer Panels, Independent Sign-Off & Dissent

## Purpose
Extend the Graph Studio review lineage from a single review thread into a governed multi-reviewer panel without converting reviewer counts into scientific truth, majority voting, or automatic resolution.

## Architecture
- `graphStudioMultiReviewerPanels` persists panel objects in the project store.
- Each reviewer has an explicit reviewer identity, role, optional affiliation/expertise metadata, conflict disclosure, and user-attested independence flag.
- Independent assessment records are append-oriented and may supersede earlier assessments without deleting them.
- Sign-offs are reviewer-specific and sign only for the named reviewer; supported states are signed, withheld, and abstained.
- Dissent is first-class and preserved even when only one reviewer records it.
- Panel matrices display each reviewer independently and intentionally expose no majority winner, consensus score, reviewer ranking, or inferred scientific resolution.
- Administrative completion means each assigned reviewer has supplied an assessment and sign-off. It does not mean the science is resolved.
- Audit-event drafts can be handed to the v0.135.14 append-only review audit, but the v0.135.18 layer never appends or resolves automatically.
- Project Workspace can receive a portable context packet containing the panel, reviewer matrix, completion state, and governance boundary.

## Scientific boundary
Reviewer agreement is process evidence, not proof. Reviewer disagreement is retained rather than averaged away. The system does not infer truth, causation, evidentiary weight, scientific validity, consensus, or a preferred interpretation from review counts or sign-offs.
