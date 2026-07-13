# Biochemistry and Molecular Analysis

Sustainable Catalyst Lab v0.21.0 adds a formula-visible biochemical
and molecular-analysis environment with 48 deterministic methods.

## Coverage

- Biomolecule composition, concentration, recovery, purity, and
  specific activity
- Protein and peptide absorbance, amount, protonation, and pI
- Michaelis–Menten kinetics, turnover, catalytic efficiency,
  inhibition, and cooperative response
- DNA and RNA concentration, molar amount, GC content, and
  short-oligonucleotide melting-temperature estimates
- Binding occupancy, Hill response, association constants,
  free energy, exact 1:1 complex formation, and bound/free ratios
- Henderson–Hasselbalch buffers, protonation fractions, buffer
  capacity, ionic strength, and temperature-adjusted pKa
- Beer–Lambert absorption, transmittance, blank correction,
  Stern–Volmer quenching, fluorescence correction, and relative
  quantum yield
- Chromatographic resolution and retention, gel mobility and
  molecular-weight calibration, centrifugal force, and assay CV

## Interfaces

WordPress shortcode:

```text
[sc_lab_biochemistry_molecular_analysis]
```

WordPress REST:

```text
GET  /wp-json/sc-lab/v1/compute/biochemistry/methods
POST /wp-json/sc-lab/v1/compute/biochemistry/run
```

FastAPI:

```text
GET  /v1/biochemistry/methods
POST /v1/biochemistry/run
```

## Responsible-use boundary

The methods support education, research planning, laboratory
documentation, quality control, and reproducible analysis. They do
not replace validated protocols, calibrated instrumentation,
biosafety review, clinical interpretation, regulated testing, or
qualified biochemical and molecular-science judgment.
