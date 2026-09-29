# Sustainable Catalyst Lab v0.62.0 — Scientific Claims, Evidence Matrix & Conclusion Traceability

## Release intent

v0.62.0 adds the claim-level accountability layer above the v0.61 scientific study lifecycle. Researchers can author bounded scientific claims, explicitly connect them to supporting and contradicting evidence, preserve uncertainty and limitations, review each claim, and trace final conclusions back to the reviewed claim set.

This release evaluates **traceability**, not truth. It does not infer claims from data, certify scientific validity, authorize causal conclusions, generate conclusions automatically, or publish research.

## Added

- `sc-lab-scientific-claim/0.62.0` governed claim record.
- `sc-lab-scientific-conclusion/0.62.0` governed conclusion record.
- `sc-lab-scientific-evidence-matrix/0.62.0` claim × evidence matrix.
- `sc-lab-scientific-claim-review/0.62.0` human claim-review record.
- `sc-lab-conclusion-traceability-packet/0.62.0` deterministic traceability packet.
- Eight claim types: descriptive, associational, comparative, predictive, mechanistic, causal, methodological, and null/no-effect.
- Explicit evidence roles: supports, contradicts, contextualizes, validates, uncertainty, and limitation.
- Metadata-only active-project evidence catalog covering datasets, analyses, models, experiments, figures, workflows, reproducibility records, audits, studies, and external references.
- Claim review decisions: accept, accept with qualification, block, reject, reopen.
- Conclusion review decisions: accept, block, reopen.
- Evidence matrix gates: blocked, needs-evidence, contested, needs-review, traceable.
- Conclusion traceability requires linked claims plus caveats/limitation context and human review.
- Contradicting evidence is retained and surfaced instead of being silently discarded.
- Orphan claims and unknown claim/conclusion references are explicitly surfaced.
- Causal claims are blocked when the v0.61 study design is not experimental or mixed.
- Claim/conclusion definitions stored in `scientificClaimsV0620` and `scientificConclusionsV0620`.
- Traceability packets saved to `analysisPackets` as `scientific-claims-evidence-matrix-v0620`.

## Scientific governance

The following remain disabled:

- automatic claim inference;
- automatic scientific certification;
- automatic causal-validity claims;
- automatic conclusion generation;
- automatic publication;
- arbitrary code/callback execution;
- raw scientific data in the claims traceability packet;
- credential/secret material in the traceability packet.

A `traceable` claim means that the evidence, contradiction, uncertainty, limitation, scope, and human-review lineage are explicit. It is not a declaration that the claim is objectively true.

Figures are preserved as context/presentation lineage and do not substitute for primary supporting evidence.

## Interface

The feature is contextual inside the existing Scientific Workflows workspace. The six primary rail destinations, Graph Studio front door, and three related application cards remain unchanged. No MutationObserver was introduced.

## Certification

The release gate extends the v0.61.0 scientific/security/runtime line with focused v0.62 claim/evidence tests, browser/PHP integration tests, FastAPI route assertions, WordPress runtime-integrity verification, syntax checks, and the complete governed release manifest.
