# Sustainable Catalyst Lab v0.99.0 — Verification Evidence Ledger

Carbon & Nature Intelligence advances from v0.15.0 to **v0.16.0**.

This release adds structured MRV evidence entries, explicit evidence-requirement linkage, internal review states, optional external-artifact SHA-256 digests, deterministic chained entry hashes, a ledger root hash, tamper checks, readiness validation, and Carbon Project `verification-record` handoff.

The release deliberately separates **record integrity** from **verification outcome**. A valid hash chain only shows that the supplied ledger representation recomputes. `ready-for-internal-review` is an internal workflow state, not a claim of third-party verification, certification, methodology compliance, credit eligibility, or issuance.

The governed reference fixture contains three required evidence classes—sampling, laboratory, and uncertainty—with three linked evidence entries. The complete ledger is internally review-ready and its hash chain validates. Altering a stored source reference without rebuilding the chain produces a tamper-detected result.
