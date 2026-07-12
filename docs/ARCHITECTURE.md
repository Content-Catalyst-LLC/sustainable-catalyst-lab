# Lab v0.4.0 Architecture

WordPress renders the scientific interface and proxies public source APIs through REST routes. Browser modules normalize feed records into observations and datasets, preserve provenance, and store project records locally. Specialized scientific modules expose pure numerical methods that are independently testable and connect their results to the shared Lab project model.

## Browser modules

- `core.js`: identifiers, timestamps, escaping, downloads, fingerprints, and fetch helpers.
- `projects.js`: compatible project storage, normalization, import, export, and activity records.
- `feeds.js`: normalized scientific-source records and project routing.
- `climate-map.js`: NASA GIBS map state and metadata.
- `periodic-table.js`: element loading, filtering, property visualization, and detail records.
- `stoichiometry.js`: formula parsing, exact balancing, molar mass, limiting reagents, yield, and dilution.
- `chemistry-lab.js`: composition, solutions, acid–base, thermochemistry, electrochemistry, kinetics, empirical/molecular formulas, and analytical calibration.
- `spectrometry.js`: raw x–y processing, transformations, peak characterization, calibration, plotting, and export.
- `physics-lab.js`: physics constants, particle reference, 35 pure numerical methods, plot generation, UI binding, and project-record routing.
- `calculators.js`: general scientific and engineering calculator registry.
- `datasets.js`: source-agnostic dataset inspection.
- `observations.js`: telescope, marine, and observation summaries.
- `workspace.js`: command catalog, quick tools, module search, and traceability.
- `sc-lab-app.js`: application orchestration and shared project-connected actions.

## Physics record flow

```text
Physics input
→ unit and domain validation
→ pure numerical method
→ result and optional series
→ browser visualization
→ project collection
→ experiment or notebook
→ generated documentation
```

Different analysis types are stored in discipline-specific collections so documentation and later Workbench routing can distinguish field models, circuits, waveforms, particle events, detector analyses, nuclear records, and optical analyses.

## Project record

Version 0.4.0 adds:

```text
physicsRecords
waveforms
circuitAnalyses
fieldModels
particleEvents
detectorAnalyses
nuclearRecords
opticalAnalyses
```

The original browser storage keys remain unchanged. Existing projects are normalized in place when loaded, changed, imported, or exported.

Full Workbench, Decision Studio, and Site Intelligence applications remain separate and are reached through configured routes.
