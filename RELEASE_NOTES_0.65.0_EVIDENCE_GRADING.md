# Sustainable Catalyst Lab v0.65.0 — Scientific Evidence Grading, Contradiction Analysis & Consensus Boundaries

## Release intent

v0.65.0 extends the v0.62–v0.64 evidence chain into a transparent, human-governed layer for describing evidence strength, preserving scientific disagreement, and stating where a defensible consensus boundary ends. Evidence grades are rule states, not numeric truth or authority scores.

## Added

- Project-scoped evidence-boundary assessments linked to v0.62 scientific claims and v0.64 synthesis protocols.
- Transparent evidence grades: `insufficient`, `limited`, `moderate`, `substantial`, and `contested`.
- Per-claim contradiction analysis covering direct contradictory literature, non-replication, replication disagreement, heterogeneity, and source caution.
- Consensus-candidate states that distinguish emerging agreement, qualified agreement, contested evidence, and bounded-consensus candidates.
- Explicit human consensus-boundary review with accept, qualified accept, block, and reopen decisions.
- Human-written population/system, context, outcome, boundary-statement, and qualification fields.
- Deterministic assessment, grade, contradiction, boundary, evaluation, review, and packet hashes.
- Project collection `scientificEvidenceGradingAssessmentsV0650`; final evidence also enters `analysisPackets` as `scientific-evidence-consensus-v0650`.

## Evidence grading rules

- Substantial evidence requires a reviewed v0.64 synthesis, multiple reviewed supports, at least one directionally consistent replication, no material contradiction, and no high heterogeneity.
- Moderate evidence can be supported by a reviewed synthesis or multiple reviewed supports but does not automatically justify an unqualified consensus boundary.
- Limited evidence records useful but incomplete support.
- Contested evidence preserves direct contradictions, replication disagreement, or high heterogeneity.
- Claim review, source caution, excluded/retracted sources, unresolved references, and qualified reviews remain visible rather than being collapsed into a score.

## Scientific boundaries

- No numeric truth score, authority score, or automatic scientific consensus certification.
- Citation counts and journal prestige are not used to grade evidence.
- No automatic study-quality scoring, causal certification, publication, or high-stakes decision authorization.
- No network fetching, raw scientific data, full-text paper content, credentials, or arbitrary code in the evidence-grading packet.
- A final consensus boundary is a scoped human-reviewed statement about the current evidence record, not a declaration that a claim is universally true.

## Interface

The feature is contextual inside Scientific Workflows immediately after the v0.64 evidence-synthesis panel. The six primary rail destinations, Graph Studio front door, and three related application cards remain unchanged. No MutationObserver is introduced.
