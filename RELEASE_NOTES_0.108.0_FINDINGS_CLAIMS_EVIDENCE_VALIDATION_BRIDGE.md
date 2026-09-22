# Sustainable Catalyst Lab v0.108.0 — Findings, Claims, Evidence & Validation Bridge

Lab v0.108.0 bridges researcher-declared scientific findings, claims, evidence relationships, contradictions, evidence-boundary assessments, validation challenges, and replication attempts into Platform Core v3 research-intelligence contracts.

## What changed

- Added canonical Lab → Core finding envelopes for Core's `sc.research.finding-claim-evidence.v1` contract.
- Added Lab v0.62 scientific-claim mapping into Core claim envelopes without promoting an `active` Lab claim into Core `supported` status.
- Added evidence-link bindings with explicit relation translation and namespaced Lab assessment metadata.
- Added declared contradiction bindings that do not infer or resolve contradictions.
- Added validation/challenge envelopes for uncertainty, methodology, counterevidence, sensitivity, robustness, replication, reviewer challenges, alternatives, and other declared challenges.
- Added replication-attempt envelopes preserving protocol, execution, package, evidence, and provenance references without certifying replication.
- Added a compatibility bridge from Lab v0.62 scientific claims and evidence links.
- Added backend and WordPress health/manifest/schema surfaces.

## Scientific boundary

Platform Core records reference-first findings, claims, evidence links, contradiction declarations, validation challenges, and replication records. Lab remains authoritative for the underlying scientific work. The bridge does not generate findings or claims, infer support, rank/judge evidence, resolve contradictions, certify replication, certify scientific validity, or determine truth.

## Compatibility

- Lab: `0.108.0`
- Minimum compatible Platform Core: `3.0.0`
- Newer compatible Core v3 releases are accepted.
- Finding/Claim/Evidence contract: `sc.research.finding-claim-evidence.v1`
- Validation/Challenge contract: `sc.research.validation-challenge.v1`

## Validation

The release gate covers 93 integration/regression tests, 12 v0.108 FastAPI routes, retained v0.104–v0.107 Core-integration surfaces, mirrored JSON contracts, WordPress/PHP assertions, and manifest integrity.
