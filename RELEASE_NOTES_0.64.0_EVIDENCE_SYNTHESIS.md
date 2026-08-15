# Sustainable Catalyst Lab v0.64.0 — Replication, Systematic Evidence Synthesis & Meta-Analysis

## Release intent

v0.64.0 extends the v0.63 literature provenance graph into a governed evidence-synthesis layer for aggregate study effects, replication comparison, heterogeneity diagnostics, fixed/random-effects meta-analysis, leave-one-out sensitivity, and human-reviewed synthesis packets.

## Added

- Systematic evidence synthesis protocols linked to v0.62 claim IDs.
- Aggregate study effect records linked to reviewed v0.63 literature sources.
- Fixed-effect and DerSimonian–Laird random-effects pooling.
- Q, I², tau², approximate pooled confidence intervals, and normalized weights.
- Leave-one-out sensitivity for 3+ eligible studies.
- Explicit original/replication linkage and disagreement classification.
- Human synthesis review with qualified acceptance for high heterogeneity.
- Metadata-only, deterministic, tamper-evident synthesis packet.
- Project collections `scientificEvidenceSynthesisProtocolsV0640` and `scientificStudyEffectsV0640`; final evidence also enters `analysisPackets`.

## Scientific boundaries

- Aggregate study estimates only; participant-level/raw study data are rejected.
- Sources must be reviewed upstream in v0.63 before pooling.
- Retracted/withdrawn/excluded sources are not silently pooled.
- Effect metrics must be harmonized explicitly; Lab does not auto-convert incompatible effect measures.
- High heterogeneity remains visible and requires qualified human review.
- No automatic study-quality scoring, publication-bias correction, truth inference, causal certification, or publication.
- No network fetching or arbitrary code execution during synthesis.

## Interface

The feature is contextual inside Scientific Workflows. The six primary rail destinations, Graph Studio front door, and three related application cards remain unchanged.
