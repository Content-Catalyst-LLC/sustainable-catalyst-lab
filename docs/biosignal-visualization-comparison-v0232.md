# Biosignal Visualization, Annotation, and Comparative Analysis

Sustainable Catalyst Lab v0.23.2 completes the first visual analysis
layer for the Biomedical Engineering and Biosignals domain.

## Visualization modes

1. Synchronized multi-channel visualization
2. Raw and filtered overlays
3. Annotation and region overlays
4. Event and interval analysis
5. Channel alignment
6. Lag and correlation scanning
7. Run overlay comparison
8. Comparative analysis summaries

## Deterministic analysis methods

The JavaScript, PHP, and Python implementations share 16 methods and
16 reference benchmarks:

- Descriptive waveform features
- Min-max and z-score normalization
- Moving-average smoothing
- Linear resampling
- Pearson correlation
- Mean absolute error
- Root mean square error
- Normalized RMSE
- Integer-lag channel shifting
- Best-lag correlation scanning
- Event rate
- Interval summaries and burden
- Annotation union coverage
- Common time-window calculation
- Multi-metric run comparison

## Data and exports

The browser workspace imports multi-channel CSV data with a required
`timeSeconds` column. It exports:

- Synchronized SVG visualizations
- Source CSV records
- JSON analysis records
- Project records
- Notebook entries
- v0.22.3 provenance records

## WordPress shortcode

```text
[sc_lab_biosignal_visualization_comparison]
```

## WordPress REST

```text
GET  /wp-json/sc-lab/v1/compute/biomedical/biosignals/visualization/methods
GET  /wp-json/sc-lab/v1/compute/biomedical/biosignals/visualization/health
POST /wp-json/sc-lab/v1/compute/biomedical/biosignals/visualization/analyze
POST /wp-json/sc-lab/v1/compute/biomedical/biosignals/visualization/compare
POST /wp-json/sc-lab/v1/compute/biomedical/biosignals/visualization/annotations
```

## FastAPI

```text
GET  /v1/biomedical/biosignals/visualization/methods
GET  /v1/biomedical/biosignals/visualization/health
POST /v1/biomedical/biosignals/visualization/analyze
POST /v1/biomedical/biosignals/visualization/compare
POST /v1/biomedical/biosignals/visualization/annotations
```

## Responsible-use boundary

This release supports research, education, prototyping, and
non-clinical comparison. It does not diagnose, monitor patients,
generate clinical alarms, recommend treatment, or replace validated
medical-device software and qualified interpretation.
