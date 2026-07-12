# Sustainable Catalyst Lab v0.3.0

A modular, substance-first scientific workspace for WordPress. Lab coordinates focused scientific capabilities from Sustainable Catalyst Workbench, Decision Studio, and Site Intelligence without embedding their full interfaces.

## v0.3.0 focus

Version 0.3.0 expands the Chemistry Laboratory and Spectrometry Studio while preserving the live scientific observation, climate-map, telescope, marine, dataset, experiment, notebook, and documentation systems introduced in earlier releases.

### Chemistry Laboratory

- Complete interactive 118-element periodic table.
- Formula parsing, molar mass, and percent composition.
- Empirical- and molecular-formula derivation.
- Exact reaction balancing.
- Limiting-reagent, reaction-extent, product, and theoretical-yield calculations.
- Structured reaction records with conditions and observations.
- Molarity, molality, mass-percent, grams-per-liter, dilution, and Ksp solubility calculations.
- Strong and weak acid/base calculations.
- Buffer and strong acid/base titration models.
- Calorimetry, Gibbs free energy, equilibrium constant, and Hess-law calculations.
- Nernst cell potential and Faraday electrolysis calculations.
- Arrhenius and integrated rate-law calculations.
- Linear analytical calibration with R², residual standard deviation, LOD, LOQ, and unknown estimation.

### Spectrometry Studio

- UV–visible, infrared, Raman, fluorescence, mass-spectrometry, and generic x–y method profiles.
- Raw CSV or whitespace x–y import.
- Linear and rolling-minimum baseline correction.
- Moving-mean and moving-median smoothing.
- Maximum, area, and min–max normalization.
- First-derivative transformation.
- Absorbance/transmittance conversion.
- Peak threshold, minimum-distance, and prominence controls.
- Peak position, prominence, and FWHM characterization.
- Area, centroid, noise, x/y range, and processing metrics.
- Calibration fitting and unknown estimation.
- Raw data, processed data, peak list, and transformation-history project records.
- CSV export and notebook handoff.

## Other included modules

- Scientific Observation Board with USGS, NASA EONET, PubMed, arXiv, NASA space/telescope, and OBIS marine records.
- NASA GIBS climate and Earth-observation map.
- Scientific Dataset Inspector.
- 34 general scientific and engineering calculators.
- Browser-local projects, evidence, hypotheses, decisions, experiments, notebook entries, calculations, datasets, observations, maps, chemical records, reactions, spectra, calibrations, activity, and JSON import/export.
- Data-connected Markdown and HTML documentation generation.

## Installation

Upload `sustainable-catalyst-lab-plugin-v0.3.0.zip` through **Plugins → Add New Plugin → Upload Plugin**, activate it, and place this shortcode on the Lab page:

```text
[sc_lab_app]
```

Focused interfaces remain available:

```text
[sc_lab_periodic_table]
[sc_lab_stoichiometry]
[sc_lab_spectrometry]
[sc_lab_climate_map]
```

## Project compatibility

The plugin deliberately preserves the original browser-storage keys:

```text
scLabProjectsV010
scLabActiveProjectV010
```

Existing v0.1.x and v0.2.0 projects are normalized to schema version `0.3.0` when read, changed, imported, or exported. No destructive migration is performed.

## Scientific boundaries

The calculators and generated documents support research, education, preliminary analysis, and prototyping. They do not replace validated laboratory methods, instrument calibration, certified reference materials, safety review, regulatory methods, uncertainty analysis, or qualified professional judgment.
