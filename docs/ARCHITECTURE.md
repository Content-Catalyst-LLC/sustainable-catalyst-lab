# Lab v0.4.1 Architecture

WordPress renders the scientific interface and proxies public source APIs through REST routes. Browser modules normalize feed records into observations and datasets, preserve provenance, and store project records locally. Specialized scientific modules expose pure numerical methods that are independently testable and connect results to the shared Lab project model.

## Browser modules

- `core.js`: identifiers, timestamps, escaping, downloads, fingerprints, and fetch helpers.
- `projects.js`: compatible project storage, normalization, import, export, and activity records.
- `feeds.js`: normalized scientific-source records and project routing.
- `climate-map.js`: NASA GIBS map state and metadata.
- `periodic-table.js`: element loading, filtering, property visualization, and detail records.
- `stoichiometry.js`: formula parsing, exact balancing, molar mass, limiting reagents, yield, and dilution.
- `chemistry-lab.js`: composition, solutions, acid–base, thermochemistry, electrochemistry, kinetics, empirical/molecular formulas, and calibration.
- `spectrometry.js`: raw x–y processing, transformations, peak characterization, calibration, plotting, and export.
- `physics-lab.js`: physics constants, particle reference, pure numerical methods, core UI binding, and project routing.
- `physics-validation.js`: method registry, domain validation, benchmark cases, advanced SVG visualization, comparison/export controls, and measurement-consistency methods.
- `calculators.js`: general scientific and engineering calculator registry.
- `datasets.js`: source-agnostic dataset inspection.
- `observations.js`: telescope, marine, and observation summaries.
- `workspace.js`: command catalog, quick tools, module search, and traceability.
- `sc-lab-app.js`: application orchestration and shared project-connected actions.

## Validated physics record flow

```text
Physics input
→ numerical/domain validation
→ pure analytical method
→ result and optional series
→ method metadata and warnings
→ browser visualization/comparison
→ physics project collection
→ validation record
→ experiment or notebook
→ generated documentation
```

## Project record

Version 0.4.1 retains all v0.4.0 physics collections and adds:

```text
physicsValidationRecords
```

The original browser-storage keys remain unchanged. Existing projects are normalized in place when loaded, changed, imported, or exported.

Full Workbench, Decision Studio, and Site Intelligence applications remain separate and are reached through configured routes.
