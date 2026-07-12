# Lab v0.9.1 Architecture

WordPress renders the scientific interface and proxies allowlisted public source APIs through REST routes. Browser modules normalize feed records, execute deterministic analytical methods, preserve provenance, and store projects locally. Version 0.9.1 introduces shared result, visualization, dimensional-scene, export, handoff, backup, restore, and reset infrastructure.

## Browser modules

- `core.js`: identifiers, timestamps, escaping, downloads, fingerprints, and fetch helpers.
- `projects.js`: compatible project storage, normalization, import, export, and activity records.
- `feeds.js`: normalized scientific-source records and project routing.
- `climate-map.js`: NASA GIBS map state and metadata.
- `periodic-table.js`: element loading, filtering, visualization, and detail records.
- `stoichiometry.js`: formula parsing, exact balancing, molar mass, limiting reagents, yield, and dilution.
- `chemistry-lab.js`: composition, solutions, acid-base, thermochemistry, electrochemistry, kinetics, and calibration.
- `spectrometry.js`: x-y processing, transformations, peak characterization, calibration, plotting, and export.
- `physics-lab.js` and `physics-validation.js`: physics methods, particles, validation, visualization, and measurement consistency.
- `biology-lab.js`: sequence analysis, proteins, genetics, populations, ecology, physiology, and validation.
- `astronomy-lab.js`: coordinates, orbits, stars, photometry, spectra, galaxies, cosmology, telescopes, and validation.
- `materials-lab.js`: mechanical, thermal, electrical, magnetic, optical, crystallographic, phase, corrosion, polymer, composite, microscopy, and validation methods.
- `earth-lab.js`: solid Earth, atmosphere, climate, hydrology, ocean, marine systems, remote sensing, hazards, carbon cycle, and validation methods.
- `energy-lab.js`: energy balances, solar, wind, hydro, storage, grid, thermal, fuels, hydrogen, emissions, economics, reliability, and validation.
- `visualization.js`: universal analysis contract, chart inference, SVG renderer, PNG/PDF/CSV/JSON/package export, project records, and Decision Studio packets.
- `dimensional-visualization.js`: 3D and 4D scene contracts, polytope presets, rotations, projections, animation, custom scenes, and dimensional exports.
- `data-management.js`: complete workspace backup, ZIP packaging, restore modes, selective resets, record counting, and deletion receipts.
- `calculators.js`: general scientific and engineering calculator registry.
- `datasets.js`: source-agnostic dataset inspection.
- `observations.js`: telescope, marine, and observation summaries.
- `workspace.js`: command catalog, quick tools, module search, and traceability.
- `sc-lab-app.js`: application orchestration and shared project-connected actions.

## Universal analytical flow

```text
Calculation or analytical method
→ normalized sc-lab-analysis/1.0 result
→ chart inference or explicit chart specification
→ SVG canonical figure
→ PNG / PDF / CSV / JSON / package export
→ optional 3D or projected 4D scene
→ project visualization and notebook records
→ Decision Studio analysis packet
```

## Dimensional projection flow

```text
3D or 4D scene specification
→ validate vertices and edge references
→ rotate in coordinate planes
→ project 4D to 3D when applicable
→ rotate 3D camera
→ project 3D to 2D
→ depth-sort geometry
→ accessible SVG
→ image, PDF, project, package, or Decision Studio output
```

## Workspace data flow

```text
Local projects and preferences
→ count and preview
→ JSON or ZIP backup
→ optional restore as copy, merge, or replace
→ selective reset or complete reset
→ minimal deletion receipt
```

## Project record

Version 0.9.1 retains every earlier collection and adds:

```text
visualizations
dimensionalScenes
chartExports
analysisPackets
```

The original `scLabProjectsV010` and `scLabActiveProjectV010` browser-storage keys remain unchanged. Existing projects are normalized in place when loaded, changed, imported, restored, or exported.

Full Workbench, Decision Studio, and Site Intelligence applications remain separate and are reached through configured routes. Decision Studio handoff currently uses a structured downloadable packet and local handoff cache; authenticated server exchange belongs to a later integration release.
