# Sustainable Catalyst Lab v0.67.0 — Causal Inference & Quasi-Experimental Methods

## Release intent
v0.67.0 adds a governed causal-inference workspace above the v0.66 competing-hypotheses layer. It supports explicit quasi-experimental designs and aggregate causal estimates while keeping identification assumptions, diagnostics, sensitivity checks, limitations, and human review visible.

## Added
- Matching and weighting design records with exchangeability, overlap, consistency, balance, overlap, and sensitivity boundaries.
- Difference-in-differences with explicit parallel-trends, no-anticipation, stable-composition, placebo, and sensitivity requirements.
- Interrupted time series with stable-pretrend, concurrent-intervention, measurement-stability, placebo, and sensitivity boundaries.
- Regression discontinuity with continuity-at-cutoff, manipulation, local-comparability, bandwidth, continuity, manipulation, and sensitivity diagnostics.
- Aggregate causal-estimate records with standard errors or confidence intervals.
- Method-specific diagnostic records with pass / caution / fail / inconclusive states.
- Human causal review: Accept assumptions within scope, Accept with qualification, Block causal interpretation, Reopen.
- Deterministic design, assumption, estimate, diagnostic, evaluation, review, and packet hashes.
- Contextual project collections `scientificCausalDesignsV0670`, `scientificCausalEstimatesV0670`, and `scientificCausalDiagnosticsV0670`.
- Tamper-evident `causal-inference-v0670` evidence packets in `analysisPackets`.

## Scientific boundaries
A `causal-estimate-bounded` gate means the recorded estimate is conditionally interpretable under the stated design assumptions and diagnostics after human review. It is not automatic proof of causation. Raw participant-level data, treatment/outcome vectors, hidden assumption satisfaction, automatic causal certification, automatic publication, network fetching during evaluation, and arbitrary code remain disabled.

## Interface
The capability is contextual inside the existing Scientific Workflows workspace. The six-destination rail, Graph Studio front door, and Prototyping Workbench / Decision Studio / Site Intelligence card row remain unchanged.
