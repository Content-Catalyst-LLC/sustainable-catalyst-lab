# Sustainable Catalyst Lab v0.66.0 — Competing Hypotheses & Scientific Argumentation

## Release intent

v0.66.0 extends the v0.62–v0.65 evidence chain into an explicit scientific argumentation layer. Researchers can represent multiple rival explanations, state predictions, connect governed evidence to each hypothesis, record discriminating tests, preserve falsifying challenges, and make explicit human review decisions without Lab automatically proving, ranking, or falsifying hypotheses.

## Added

- Project-scoped scientific argumentation cases linked to v0.62 scientific claims and v0.65 evidence-boundary assessments.
- Multiple competing hypotheses with explicit statements, mechanisms, scope notes, linked claims, and predictions.
- Prediction records with expected outcomes and optional discriminating-test references.
- Governed hypothesis-evidence relations: support, contradiction, neutral/context, uncertainty, falsifying candidate, and discriminating evidence for/against.
- Discriminating-test records that compare expected outcomes across at least two alternatives.
- Human hypothesis review: retain, provisionally prefer, reject, block, or reopen.
- Human argument-map review: accept the map, accept with unresolved alternatives, block, or reopen.
- Explicit gates for missing alternatives, missing predictions, missing discriminating tests, unresolved evidence, falsification challenges, unresolved alternatives, provisional preference, and bounded argument review.
- Deterministic case, hypothesis, prediction, evidence-link, discriminating-test, evaluation, review, and packet hashes.
- Project collections `scientificArgumentationCasesV0660`, `scientificHypothesesV0660`, `scientificArgumentEvidenceLinksV0660`, and `scientificDiscriminatingTestsV0660`; final evidence also enters `analysisPackets` as `scientific-argumentation-v0660`.

## Scientific boundaries

- No automatic hypothesis proof, hidden winner selection, automatic falsification, numeric truth score, causal certification, or publication authorization.
- A falsifying candidate is preserved as a challenge requiring human review; it does not automatically reject a hypothesis.
- A provisional preference remains explicitly provisional and does not become a scientific proof statement.
- Multiple viable alternatives may remain unresolved; the researcher can accept an argument map only with an explicit unresolved-alternatives boundary when appropriate.
- Raw scientific data, credentials, full-text literature, network fetching during evaluation, and arbitrary code are excluded.

## Interface

The feature is contextual inside Scientific Workflows immediately after the v0.65 evidence-grading panel. The six primary rail destinations, Graph Studio front door, and three related application cards remain unchanged. No MutationObserver is introduced.
