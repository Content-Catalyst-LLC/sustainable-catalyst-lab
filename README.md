# Sustainable Catalyst Lab v0.1.1

A modular, substance-first scientific workspace for WordPress. Lab coordinates focused scientific capabilities from Sustainable Catalyst Prototyping Workbench, Decision Studio, and Site Intelligence without embedding their full interfaces.

## v0.1.1 workspace upgrades

- Sticky project and scientific command bar.
- Search across Lab modules, chemistry tools, spectrometry, and all registered calculators.
- Workflow-grouped navigation: Project, Observe, Analyze, Record, and System.
- Data-driven Overview with live scientific signals, quick scientific tools, active work, recent activity, and interactive traceability.
- Dedicated project activity ledger with search and CSV export.
- Actionable feed records with inspect, source, evidence, notebook, experiment, and Site Intelligence routing actions.
- Mobile module drawer and compact responsive layouts.
- Browser-local v0.1.0 project migration into the v0.1.1 schema without changing the existing storage keys.

## Scientific modules

- Scientific Signal Board: USGS earthquakes, NASA EONET, PubMed, arXiv, NASA space-image releases, and OBIS marine biodiversity.
- NASA GIBS climate and Earth-observation imagery.
- Complete 118-element interactive periodic table.
- Formula parser, molar mass, exact equation balancing, limiting reagent, theoretical yield, and dilution tools.
- Spectrometry data import, baseline correction, smoothing, peak detection, integration, charting, and CSV export.
- 34 calculators across chemistry, physics, electromagnetism, particle physics, mechanics, thermodynamics, fluids, biology, astronomy, materials science, Earth science, energy, and uncertainty.
- Projects, evidence, hypotheses, decisions, experiments, notebook entries, calculations, map states, activity, and JSON import/export.
- Data-connected Markdown and HTML documentation generation with source fingerprints and stale-document detection.

## Installation

Upload `sustainable-catalyst-lab-plugin-v0.1.1.zip` through **Plugins → Add New → Upload Plugin**, activate it, and place this shortcode on the Lab page:

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

v0.1.1 retains the browser storage keys used by v0.1.0. Existing projects are normalized on read and receive `schemaVersion: 0.1.1` when saved or exported.

## Scientific boundaries

The calculators and generated documents support research, education, preliminary analysis, and prototyping. Results require validation against source data, accepted methods, instrument calibration, uncertainty, standards, and qualified professional review where applicable.
