# Biochemistry Visualization and Batch Analysis

Sustainable Catalyst Lab v0.21.2 adds applied visualization,
replicate analysis, quality-control summaries, and reproducible
exports above the validated v0.21.0 Biochemistry calculation
catalog.

## Visualization studio

Seven first-release visualization profiles are included:

1. Standard curve and linear regression
2. Michaelis–Menten kinetics
3. Hill binding response
4. Buffer protonation profile
5. Absorbance comparison
6. Fluorescence comparison
7. Chromatography trace

Charts use native SVG and do not require an external visualization
library.

## Batch analysis

Any of the 48 Biochemistry methods can be applied to multiple
samples through CSV data. A batch result contains:

- Row-level input and output records
- Isolated calculation failures
- Mean
- Sample standard deviation
- Coefficient of variation
- Minimum and maximum
- CV review flags above 20%
- Project and notebook handoffs
- CSV result export
- JSON audit export

## WordPress routes

```text
GET  /wp-json/sc-lab/v1/compute/biochemistry/visualizations
POST /wp-json/sc-lab/v1/compute/biochemistry/batch
```

## FastAPI routes

```text
GET  /v1/biochemistry/visualizations
POST /v1/biochemistry/batch
```

## Focused shortcode

```text
[sc_lab_biochemistry_visualization_batch]
```

## Responsible-use boundary

The visualization and batch layers support research planning,
education, laboratory documentation, and quality-control review.
They do not replace validated assay procedures, calibrated
instrumentation, regulated laboratory systems, clinical
interpretation, or qualified biochemical judgment.
