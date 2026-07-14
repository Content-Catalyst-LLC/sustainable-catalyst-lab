# Calibration, Validation, and Chain of Custody

Sustainable Catalyst Lab v0.25.3 adds auditable calibration,
instrument-readiness, sample-history, custody, deviation, and release
review above the v0.25.0-v0.25.2 instrumentation platform.

## Validation profiles

1. Instrument identity and configuration
2. Calibration acceptance
3. Sensor and channel readiness
4. Maintenance readiness
5. Measurement quality
6. Sample and specimen linkage
7. Chain-of-custody integrity
8. Laboratory release readiness

## Acceptance states

```text
draft
pending-review
accepted
conditionally-accepted
hold
rejected
expired
superseded
```

## Deterministic methods

The 16-method contract covers calibration error, percentage error,
bias, RMSE, linearity, repeatability, acceptance windows, calibration
and maintenance due states, measurement completeness, quality-flag
rates, custody completeness and sequence review, deviation rates,
weighted validation scores, and release dispositions.

## SHA-256 records

The module creates:

- Component-hashed validation manifests
- Parent-linked custody events
- Custody-chain verification records
- Tamper-evident validation dossiers

Changing a custody event after its hash is created causes verification
to fail.

## Focused shortcode

```text
[sc_lab_instrumentation_validation_custody]
```

## Browser API

```javascript
window.SCLab.InstrumentationValidationCustody.status()
window.SCLab.InstrumentationValidationCustody.execute(methodId, inputs)
await window.SCLab.InstrumentationValidationCustody.createManifest(
  components,
  metadata
)
await window.SCLab.InstrumentationValidationCustody.createCustodyEvent({
  sampleId,
  action,
  actor,
  location,
  timestamp,
  previousHash
})
await window.SCLab.InstrumentationValidationCustody.verifyCustodyChain(
  events
)
await window.SCLab.InstrumentationValidationCustody.createDossier({
  profileResults,
  manifest,
  custodyEvents,
  deviations,
  metadata
})
```

## WordPress REST

```text
GET  /wp-json/sc-lab/v1/compute/instrumentation/validation/profiles
GET  /wp-json/sc-lab/v1/compute/instrumentation/validation/health
POST /wp-json/sc-lab/v1/compute/instrumentation/validation/evaluate
POST /wp-json/sc-lab/v1/compute/instrumentation/validation/manifest
POST /wp-json/sc-lab/v1/compute/instrumentation/custody/event
POST /wp-json/sc-lab/v1/compute/instrumentation/custody/verify
POST /wp-json/sc-lab/v1/compute/instrumentation/validation/dossier
```

## FastAPI

```text
GET  /v1/instrumentation/validation/profiles
GET  /v1/instrumentation/validation/health
POST /v1/instrumentation/validation/evaluate
POST /v1/instrumentation/validation/manifest
POST /v1/instrumentation/custody/event
POST /v1/instrumentation/custody/verify
POST /v1/instrumentation/validation/dossier
```

## Boundaries

The module supports research, education, laboratory prototyping,
internal validation, and auditable sample-history workflows. It does
not grant GMP certification, clinical release authority, regulatory
approval, or automatic device-control authority.
