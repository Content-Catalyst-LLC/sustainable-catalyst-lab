# Bioprocess Validation and Batch Provenance

Sustainable Catalyst Lab v0.22.3 converts monitoring and process
results into explicit validation decisions and traceable batch
records.

## Validation profiles

1. Batch record completeness
2. Critical process parameter conformance
3. Critical quality attribute conformance
4. Cross-batch consistency
5. Monitoring and control performance
6. Excursion disposition
7. Hold-time stability
8. Batch release readiness

Each profile has configurable acceptance criteria and returns:

- Calculated metrics
- Individual acceptance checks
- Pass/fail decision
- Failed-check count
- Release or hold recommendation

## Batch provenance

Records include:

- Batch, lot, and run identifiers
- Analyst, reviewer, organization, and instrument
- Source record identifiers
- Evidence links
- Disposition and notes
- SHA-256 payload hash
- SHA-256 complete-record hash
- Parent record hash
- Component release versions

Ledger verification recalculates both payload and complete-record
hashes and confirms the parent-link sequence.

## Dossiers

A dossier combines validation results, batch metadata, the
provenance ledger, ledger verification, disposition, responsible-use
boundaries, and a final dossier hash.

## Browser API

```javascript
window.SCLab.BioprocessValidationProvenance.status()
window.SCLab.BioprocessValidationProvenance.evaluate(
  profileId,
  rows,
  thresholds
)
window.SCLab.BioprocessValidationProvenance.createRecord(
  payload,
  metadata,
  previousHash
)
window.SCLab.BioprocessValidationProvenance.verifyLedger(records)
window.SCLab.BioprocessValidationProvenance.createDossier(
  validationResults,
  batch,
  records,
  disposition
)
```

## WordPress shortcode

```text
[sc_lab_bioprocess_validation_provenance]
```

## WordPress REST

```text
GET  /wp-json/sc-lab/v1/compute/bioprocess/validation/profiles
POST /wp-json/sc-lab/v1/compute/bioprocess/validation/evaluate
POST /wp-json/sc-lab/v1/compute/bioprocess/provenance/record
POST /wp-json/sc-lab/v1/compute/bioprocess/provenance/verify
POST /wp-json/sc-lab/v1/compute/bioprocess/validation/dossier
```

## FastAPI

```text
GET  /v1/bioprocess/validation/profiles
POST /v1/bioprocess/validation/evaluate
POST /v1/bioprocess/provenance/record
POST /v1/bioprocess/provenance/verify
POST /v1/bioprocess/validation/dossier
```

## Boundary

The workspace supports research, education, process development, and
quality-system prototyping. It does not replace validated
manufacturing systems, qualified personnel, regulatory review, or
formal batch-release authority.
