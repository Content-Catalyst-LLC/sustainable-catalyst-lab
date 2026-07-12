# Sustainable Catalyst Lab v0.1.0

A modular, substance-first scientific workspace for WordPress. Lab coordinates focused scientific capabilities from Sustainable Catalyst Workbench, Decision Studio, and Site Intelligence without embedding their full interfaces.

## Included modules

- Scientific Signal Board: USGS earthquakes, NASA EONET, PubMed, arXiv, NASA space-image releases, and OBIS marine biodiversity.
- NASA GIBS climate and Earth-observation map.
- Complete 118-element interactive periodic table.
- Formula parser, molar mass, exact equation balancing, limiting reagent, theoretical yield, and dilution tools.
- Spectrometry data import, baseline correction, smoothing, peak detection, integration, charting, and CSV export.
- Scientific calculators for chemistry, physics, electromagnetism, particle physics, mechanics, thermodynamics, fluids, biology, astronomy, materials science, Earth science, energy, and uncertainty.
- Browser-local projects, evidence, hypotheses, decisions, experiments, notebook entries, calculations, climate-map records, activity, and JSON import/export.
- Data-connected Markdown/HTML documentation generation with source fingerprints and stale-document detection.

## Installation

Upload `sustainable-catalyst-lab-plugin-v0.1.0.zip` through **Plugins → Add New → Upload Plugin**, activate it, and place this shortcode on the Lab page:

```text
[sc_lab_app]
```

Focused interfaces are also available:

```text
[sc_lab_periodic_table]
[sc_lab_stoichiometry]
[sc_lab_spectrometry]
[sc_lab_climate_map]
```

## Architecture

WordPress supplies the application shell, public REST proxy, caching, source configuration, and routes into the larger Sustainable Catalyst applications. The v0.1.0 project record is stored locally in the browser and can be exported or imported as JSON. Future releases can migrate the same record contract to Platform Core or a FastAPI persistence service.

## Scientific boundaries

The calculators and generated documents support research, education, preliminary analysis, and prototyping. Results require validation against source data, accepted methods, instrument calibration, uncertainty, standards, and qualified professional review where applicable.
