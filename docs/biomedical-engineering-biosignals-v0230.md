# Biomedical Engineering and Biosignals

Sustainable Catalyst Lab v0.23.0 introduces a non-clinical,
auditable biomedical signal-analysis workspace.

## Scientific contract

The release contains 48 methods and 48 deterministic reference
benchmarks across:

1. Acquisition and sampling
2. ECG and cardiac intervals
3. PPG and hemodynamics
4. Respiration
5. Electromyography
6. Electroencephalography
7. Filtering and signal conditioning
8. Signal quality

## Waveform analysis

The waveform analyzer calculates:

- Sample count and duration
- Mean and sample standard deviation
- RMS
- Minimum and maximum
- Peak-to-peak amplitude
- Zero-crossing count and rate
- Crest factor
- Native SVG waveform visualization

## Batch execution

The CSV batch workflow accepts:

```text
methodId,inputsJson
```

Every row executes independently. Invalid rows are reported without
preventing valid calculations from completing.

## Handoffs

The browser workspace dispatches project and notebook records and can
create a v0.22.3 SHA-256 provenance record when the validation and
provenance engine is available.

## WordPress shortcode

```text
[sc_lab_biomedical_engineering_biosignals]
```

## WordPress REST

```text
GET  /wp-json/sc-lab/v1/compute/biomedical/biosignals/methods
GET  /wp-json/sc-lab/v1/compute/biomedical/biosignals/health
POST /wp-json/sc-lab/v1/compute/biomedical/biosignals/run
POST /wp-json/sc-lab/v1/compute/biomedical/biosignals/analyze
POST /wp-json/sc-lab/v1/compute/biomedical/biosignals/batch
```

## FastAPI

```text
GET  /v1/biomedical/biosignals/methods
GET  /v1/biomedical/biosignals/health
POST /v1/biomedical/biosignals/run
POST /v1/biomedical/biosignals/analyze
POST /v1/biomedical/biosignals/batch
```

## Responsible-use boundary

The module supports research, education, prototyping, and non-clinical
signal analysis. It is not intended for diagnosis, treatment,
patient monitoring, alarm generation, or clinical decision-making.
Sensor validation, algorithm validation, regulatory review, and
qualified clinical interpretation remain outside the module.
