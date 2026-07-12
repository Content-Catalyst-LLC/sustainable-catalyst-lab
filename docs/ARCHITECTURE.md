# Lab v0.3.0 Architecture

WordPress renders the scientific interface and proxies public source APIs through REST routes. Browser modules normalize feed records into observations and datasets, preserve provenance, and store project records locally.

## Browser modules

- `core.js`: identifiers, timestamps, escaping, downloads, fingerprints, and fetch helpers.
- `projects.js`: compatible project storage, normalization, import, export, and activity records.
- `feeds.js`: normalized scientific-source records and project routing.
- `climate-map.js`: NASA GIBS map state and metadata.
- `periodic-table.js`: element loading, filtering, property visualization, and detail records.
- `stoichiometry.js`: formula parsing, exact balancing, molar mass, limiting reagents, yield, and dilution.
- `chemistry-lab.js`: composition, solutions, acid–base, thermochemistry, electrochemistry, kinetics, empirical/molecular formulas, and analytical calibration.
- `spectrometry.js`: raw x–y processing, transformations, peak characterization, method metadata, calibration, plotting, and export.
- `calculators.js`: general scientific and engineering calculator registry.
- `datasets.js`: source-agnostic dataset inspection.
- `observations.js`: telescope, marine, and observation summaries.
- `workspace.js`: command catalog, quick tools, module search, and traceability.
- `sc-lab-app.js`: application orchestration and project-connected actions.

## Project record

Version 0.3.0 extends the project schema with:

```text
chemicalRecords
reactions
spectra
calibrations
methods
```

Spectrum records can include raw data, processed data, processing history, method, sample identifier, peaks, numerical summary, and review state. Released analytical results should be exported or documented as fixed snapshots rather than silently overwritten.

Full Workbench, Decision Studio, and Site Intelligence applications remain separate and are reached through configured routes.
