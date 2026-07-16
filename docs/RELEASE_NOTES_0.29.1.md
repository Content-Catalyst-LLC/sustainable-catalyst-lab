# Sustainable Catalyst Lab v0.29.1 — Research Quality and Method Review

v0.29.1 adds a project-scoped method-review and research-quality governance layer on top of the v0.29.0 evidence/provenance system.

## Capabilities

- Method-review records with risk tier, status, ownership, and version metadata.
- Benchmark coverage and validation-evidence requirements.
- Links to sources, evidence records, reproducible runs, and research-provenance records.
- Assumption, limitation, known-issue, and reviewer-note capture.
- Calibration status, reference, last-calibrated date, and due date.
- Draft, under-review, changes-requested, conditional approval, approval, rejection, and deprecation states.
- Recorded reviewer decisions and immutable review-history events.
- High-consequence policy requiring stronger evidence and an independent reviewer.
- Governed Python normalization, policy evaluation, hash verification, and revision comparison.
- Portable method-review bundles retained by project checkpoints and project exports.
- Functional-health registry synchronized to all 51 current Lab panels.

## Integrity and compatibility

- Built from the verified v0.29.0.1 WordPress baseline.
- Preserves `evidence → evidence-decisions` and `sources → source-registry`.
- Keeps Evidence & provenance available through its non-conflicting aliases.
- Uses the corrected `releaseVersion` and `wordpressCriticalFiles` manifest schema.
- Does not enable arbitrary Python or arbitrary method execution.
