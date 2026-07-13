# Molecular Analysis Validation and Provenance

Sustainable Catalyst Lab v0.21.3 adds explicit analytical
validation and tamper-evident provenance above the v0.21.0
Biochemistry method catalog and v0.21.2 visualization/batch layer.

## Validation protocols

The initial release includes eight protocol profiles:

1. Precision and repeatability
2. Accuracy and recovery
3. Calibration linearity
4. Detection and quantitation limits
5. Blank and background performance
6. Control performance
7. Robustness across conditions
8. Inter-run comparability

Every profile defines required dataset columns, default acceptance
thresholds, calculated metrics, individual acceptance checks, and a
final pass/fail decision.

## Validation dossiers

A dossier contains:

- Method and profile identity
- User-supplied acceptance thresholds
- Original source rows
- Derived metrics
- Check-by-check observed values and limits
- Pass/fail decision
- Engine and release versions
- Responsible-use boundaries
- Creation timestamp

## Provenance records

Each provenance record includes:

- Record ID and event type
- Timestamp
- Method and validation profile
- Analyst, organization, instrument, and sample set
- Source identifiers and evidence links
- Notes
- SHA-256 payload fingerprint
- Previous-record hash
- SHA-256 record fingerprint
- Embedded validation payload
- Engine versions

A ledger can be independently verified. Changing a payload,
metadata value, record order, or parent hash causes verification to
fail.

## WordPress REST routes

```text
GET  /wp-json/sc-lab/v1/compute/biochemistry/validation/profiles
POST /wp-json/sc-lab/v1/compute/biochemistry/validation/run
POST /wp-json/sc-lab/v1/compute/biochemistry/provenance/record
POST /wp-json/sc-lab/v1/compute/biochemistry/provenance/verify
```

## FastAPI routes

```text
GET  /v1/biochemistry/validation/profiles
POST /v1/biochemistry/validation/run
POST /v1/biochemistry/provenance/record
POST /v1/biochemistry/provenance/verify
```

## Focused shortcode

```text
[sc_lab_molecular_validation_provenance]
```

## Boundary

These computational checks support research planning,
documentation, education, and internal quality review. They do not
establish regulatory compliance, validate an instrument or assay,
replace controlled laboratory procedures, authorize clinical use,
or replace qualified scientific judgment.
