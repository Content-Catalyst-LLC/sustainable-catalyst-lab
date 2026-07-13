# Lab v0.10.0 Architecture

WordPress renders the scientific interface and proxies allowlisted public source APIs through REST routes. Browser modules normalize feed records, execute deterministic analytical methods, preserve provenance, and store projects locally. Version 0.10.0 adds structured PDF reports, ReportLab vector output, and Decision Studio report packets on top of the portable method contracts, curated multi-language execution, shared result, visualization, dimensional-scene, export, backup, restore, and reset infrastructure.

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
- `method-contracts.js`: portable scientific expression contracts, language-neutral evaluation, twelve source generators, notebooks, catalogs, and parity validation.
- `code-switcher.js`: Code Studio controls, generated-source downloads, local/Render execution, project records, and cross-language comparison.
- `compute-client.js`: same-origin WordPress compute, report, job, and handoff client.
- `reporting.js`: report contracts, browser PDF composition, Report Studio, project records, Render PDF requests, and Decision Studio packet 2.0.
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
→ sc-lab-report/1.0 report
→ browser PDF or Render ReportLab vector PDF
→ sc-decision-studio-analysis-packet/2.0 handoff
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

Version 0.10.0 retains every earlier collection and adds or formalizes:

```text
visualizations
dimensionalScenes
chartExports
analysisPackets
methodContracts
codeArtifacts
implementationComparisons
reports
reportFigures
reportExports
decisionStudioHandoffs
```

The original `scLabProjectsV010` and `scLabActiveProjectV010` browser-storage keys remain unchanged. Existing projects are normalized in place when loaded, changed, imported, restored, or exported.

Full Workbench, Decision Studio, and Site Intelligence applications remain separate and are reached through configured routes. Decision Studio handoff uses a structured packet, local handoff cache, configured route, and optional backend validation. Authenticated cross-application persistence remains a later integration boundary.

## Portable code flow

```text
Method contract
→ validate inputs and units
→ evaluate language-neutral expression graph
→ generate Python / R / Julia / JavaScript / TypeScript / SQL / C / C++ / Fortran / Rust / Go / Haskell
→ compare with current JavaScript adapter when available
→ download source, method JSON, notebook, or catalog
→ save contract and code artifact to project
```

## WordPress update identity

The installable archive always uses `sustainable-catalyst-lab/sustainable-catalyst-lab.php`. The repository and release-bundle ZIPs are intentionally not WordPress installer packages. The settings page reports duplicate plugin paths and can deactivate duplicate instances without deleting their folders.
