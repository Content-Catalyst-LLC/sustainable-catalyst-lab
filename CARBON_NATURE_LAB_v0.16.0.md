# Carbon & Nature Intelligence v0.16.0 — Verification Evidence Ledger

Host release: **Sustainable Catalyst Lab v0.99.0**

## Purpose

The Verification Evidence Ledger converts MRV evidence from an informal collection of references into a governed, inspectable record. It links evidence items to explicit requirements inherited from the protocol and monitoring plan, records internal review state, preserves optional source SHA-256 digests, and constructs a deterministic SHA-256 chain across the ordered ledger.

## Core workflow

1. Declare evidence requirements explicitly.
2. Add structured evidence entries with source references.
3. Link each entry to one or more declared requirement keys.
4. Record internal review state without implying certification.
5. Build the deterministic evidence chain and ledger root hash.
6. Validate requirement coverage, evidence-type compatibility, review flags, and chain integrity.
7. Create a Carbon Project `verification-record` packet for downstream review.

## Evidence types

`field-observation`, `sample-record`, `chain-of-custody`, `laboratory-result`, `quality-control`, `calculation-output`, `model-run`, `monitoring-record`, `protocol`, `methodology-reference`, `document`, `image`, and `other`.

## Integrity model

Each normalized evidence entry receives a deterministic content fingerprint. The ordered ledger then stores, for every entry, its sequence number, the previous entry hash, and its own entry hash. The ledger root hash commits to the ordered set of entry hashes plus the explicit requirements.

A chain check recomputes these values and reports mismatches. This establishes integrity of the supplied ledger representation only. It does not prove the authenticity of an external source, the correctness of a laboratory result, or independent third-party verification.

## Review boundary

Internal review states are `unreviewed`, `accepted-for-internal-review`, `flagged`, and `rejected-for-internal-review`.

`ready-for-internal-review` means required evidence is linked with compatible evidence types, no evidence is flagged or rejected, and the chain recomputes. It does **not** mean methodology compliance, certification, verification, carbon-credit eligibility, or issuance.

## Provenance rules

External artifact SHA-256 values are accepted only when explicitly supplied. The software never claims to hash an external file that it cannot access. Required evidence types are never inferred: they must be declared from the governing protocol, monitoring plan, or methodology interpretation.

## API

- `GET /v1/carbon-nature/mrv/v1600/verification-ledger/health`
- `GET /v1/carbon-nature/mrv/v1600/verification-ledger/schema`
- `GET /v1/carbon-nature/mrv/v1600/verification-ledger/policies`
- `POST /v1/carbon-nature/mrv/v1600/verification-ledger/evidence-entry`
- `POST /v1/carbon-nature/mrv/v1600/verification-ledger/build`
- `POST /v1/carbon-nature/mrv/v1600/verification-ledger/validate`
- `POST /v1/carbon-nature/mrv/v1600/verification-ledger/chain-check`
- `POST /v1/carbon-nature/mrv/v1600/verification-ledger/project-packet`
