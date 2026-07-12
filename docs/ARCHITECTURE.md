# Lab v0.7.0 Architecture

WordPress renders the scientific interface and proxies public source APIs through REST routes. Browser modules normalize feed records into observations and datasets, preserve provenance, and store project records locally. Specialized scientific modules expose pure numerical methods that are independently testable and connect results to the shared Lab project model.

## Browser modules

- `core.js`: identifiers, timestamps, escaping, downloads, fingerprints, and fetch helpers.
- `projects.js`: compatible project storage, normalization, import, export, and activity records.
- `feeds.js`: normalized scientific-source records and project routing.
- `climate-map.js`: NASA GIBS map state and metadata.
- `periodic-table.js`: element loading, filtering, visualization, and detail records.
- `stoichiometry.js`: formula parsing, exact balancing, molar mass, limiting reagents, yield, and dilution.
- `chemistry-lab.js`: composition, solutions, acid–base, thermochemistry, electrochemistry, kinetics, and calibration.
- `spectrometry.js`: x–y processing, transformations, peak characterization, calibration, plotting, and export.
- `physics-lab.js` and `physics-validation.js`: physics methods, particles, validation, visualization, and measurement consistency.
- `biology-lab.js`: sequence analysis, proteins, genetics, populations, ecology, physiology, and validation.
- `astronomy-lab.js`: coordinates, orbits, stars, photometry, spectra, galaxies, cosmology, telescopes, and validation.
- `materials-lab.js`: mechanical, thermal, electrical, magnetic, optical, crystallographic, phase, corrosion, polymer, composite, microscopy, and validation methods.
- `calculators.js`: general scientific and engineering calculator registry.
- `datasets.js`: source-agnostic dataset inspection.
- `observations.js`: telescope, marine, and observation summaries.
- `workspace.js`: command catalog, quick tools, module search, and traceability.
- `sc-lab-app.js`: application orchestration and shared project-connected actions.

## Materials analysis flow

```text
Material or specimen record
→ method and unit validation
→ pure analytical method
→ result and optional series
→ assumptions, limitations, and warnings
→ browser visualization
→ materials-specific project collection
→ experiment or notebook
→ generated documentation
```

## Project record

Version 0.7.0 retains all earlier collections and adds:

```text
materialsRecords
materialSamples
mechanicalRecords
thermalRecords
electricalRecords
magneticRecords
opticalRecords
crystallographyRecords
phaseRecords
corrosionRecords
polymerRecords
compositeRecords
microscopyRecords
materialsValidationRecords
```

The original browser-storage keys remain unchanged. Existing projects are normalized in place when loaded, changed, imported, or exported.

Full Workbench, Decision Studio, and Site Intelligence applications remain separate and are reached through configured routes.
