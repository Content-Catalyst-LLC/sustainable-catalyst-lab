# Carbon & Nature Intelligence v0.17.0 — MRV Reporting & Audit Packets

**Host product:** Sustainable Catalyst Lab v0.100.0  
**Phase:** Carbon & Nature Intelligence Phase III — Measurement, Reporting & Verification (MRV)

## Purpose

v0.17.0 converts governed MRV components into a structured reporting and audit-preparation layer. It assembles project identity, reporting period, protocol, monitoring plan, uncertainty assessment, verification-evidence ledger, declared metrics, deviations, source references, and supporting artifacts into an inspectable MRV report and deterministic audit packet.

The release intentionally remains an **internal research and audit-preparation system**. A report marked `ready-for-internal-review` or a packet marked `ready-for-internal-audit-preparation` is not an external verifier opinion, certification, methodology-compliance decision, or carbon-credit eligibility determination.

## Internal report structure

The governed Sustainable Catalyst internal report template contains eight sections:

1. project boundary and reporting period
2. methodology, assumptions, and references
3. monitoring activities and sampling implementation
4. reported quantities and calculation lineage
5. uncertainty and detection assessment
6. verification evidence and supporting records
7. deviations, limitations, and corrective actions
8. internal review summary

These sections are an internal documentation scaffold. The system does not claim that they reproduce the reporting template of any external carbon program or methodology.

## Reported metrics

Reported metric values are preserved exactly as caller-supplied values with explicit units and source references. v0.17.0 does not silently recalculate SOC change, GHG balances, uncertainty, or other scientific results. Recalculation remains the responsibility of the governed engines that produced those results.

## Verification-evidence integration

A v0.16.0 Verification Evidence Ledger may be supplied as a full object. When present, v0.17.0 recomputes its declared SHA-256 evidence chain and carries forward:

- ledger reference
- ledger root hash
- entry count
- chain checked status
- chain validity
- tamper-detection status

A valid chain establishes only the integrity of the supplied ledger representation. It does not prove source authenticity or external verification.

## Audit packet

The audit packet contains:

- report identity and fingerprint
- reporting period
- governed component index
- section fingerprint index
- explicit supporting-artifact index
- optional artifact SHA-256 digests
- unresolved report issues
- verification-ledger root and chain status
- deterministic packet fingerprint

`ready-for-internal-audit-preparation` requires an internally review-ready report and a supplied verification ledger whose chain recomputes successfully.

## Guardrails

v0.17.0 does not:

- assert external verification or auditor approval
- determine certification or methodology compliance
- determine credit eligibility or issuance
- fabricate or infer external reporting requirements
- silently recalculate reported metrics
- infer artifact digests
- equate hash-chain integrity with source authenticity

## API

- `GET /v1/carbon-nature/mrv/v1700/reporting/health`
- `GET /v1/carbon-nature/mrv/v1700/reporting/schema`
- `GET /v1/carbon-nature/mrv/v1700/reporting/policies`
- `GET /v1/carbon-nature/mrv/v1700/reporting/template/{report_type}`
- `POST /v1/carbon-nature/mrv/v1700/reporting/report/build`
- `POST /v1/carbon-nature/mrv/v1700/reporting/report/validate`
- `POST /v1/carbon-nature/mrv/v1700/reporting/audit-packet/build`
- `POST /v1/carbon-nature/mrv/v1700/reporting/project-packet`

## Version-line note

The Lab host version advances from `0.99.0` to **`0.100.0`** rather than reusing `1.0.0`. The repository already contains an earlier historical Lab `1.0.0` release identity and connected-platform v1.0.0 artifacts. Using `0.100.0` preserves the active modern Lab lineage without colliding with that historical version/tag namespace.
