# Laboratory Data and Instrumentation Platform

Sustainable Catalyst Lab v0.25.0 provides a shared, auditable data and instrumentation layer for all scientific domains.

## Core contract

The release contains 48 deterministic methods and 48 benchmarks across acquisition design, calibration, statistics, signal conditioning, unit normalization, temporal normalization, data quality, and operational integrity.

## Records

Nine record types are supported: instrument, sensor, sample, specimen, run, calibration, maintenance, measurement, and custody event. Every record can be fingerprinted and included in a component-hashed manifest.

## Connections

Connection profiles describe manual entry, CSV, JSON, serial streams, HTTP push, MQTT bridges, Arduino, and Raspberry Pi. They are configuration records; the WordPress browser interface does not silently access local hardware.

## Measurement ingestion

Rows preserve source timestamps, instrument and sample identifiers, original units and values, normalized values, quality flags, and source order. Dataset hashes make downstream snapshots reproducible.

## Custody

Custody events are parent-linked with SHA-256 hashes. Verification recalculates every event hash and confirms chain continuity.

## Shortcode

```text
[sc_lab_laboratory_data_instrumentation]
```

## WordPress REST

```text
GET  /wp-json/sc-lab/v1/compute/instrumentation/methods
GET  /wp-json/sc-lab/v1/compute/instrumentation/health
POST /wp-json/sc-lab/v1/compute/instrumentation/run
POST /wp-json/sc-lab/v1/compute/instrumentation/records
POST /wp-json/sc-lab/v1/compute/instrumentation/manifest
POST /wp-json/sc-lab/v1/compute/instrumentation/custody
POST /wp-json/sc-lab/v1/compute/instrumentation/custody/verify
POST /wp-json/sc-lab/v1/compute/instrumentation/measurements/ingest
```

Equivalent FastAPI routes are available under `/v1/instrumentation/`.

## Boundary

The platform supports research, education, laboratory prototyping, and non-clinical instrumentation. It does not replace a validated LIMS, regulated chain-of-custody system, clinical device, qualified laboratory personnel, or formal quality review.
