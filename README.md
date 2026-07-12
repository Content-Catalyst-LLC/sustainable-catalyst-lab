# Sustainable Catalyst Lab v0.9.1

Sustainable Catalyst Lab is a modular, substance-first scientific and engineering workspace for WordPress. Version 0.9.1 adds shared **Universal Visualization, Export, Dimensional Imaging, and Workspace Data Management** infrastructure while preserving the scientific feeds, climate maps, chemistry, spectrometry, physics, biology, astronomy, materials, Earth systems, energy, project, experiment, notebook, and documentation systems from earlier releases.

## Universal visualization and export

Every completed calculation can be normalized into the same `sc-lab-analysis/1.0` contract. The contract records the method, version, project, inputs, outputs, equation, assumptions, warnings, validation state, source context, chart specification, optional dimensional scene, and audit fingerprints.

The shared toolbar supports:

- Visualization Studio
- Three-dimensional and projected four-dimensional scene view
- SVG download
- High-resolution PNG download
- Single-figure PDF download
- CSV data download
- Structured analysis JSON
- Complete analysis-package ZIP
- Project visualization records
- Notebook routing
- Decision Studio handoff packets

The analysis-package ZIP contains the structured result, chart data, SVG, PNG, PDF, audit record, Decision Studio packet, README, and scene JSON when applicable.

## Three-dimensional and projected four-dimensional viewer

The dimensional viewer includes:

- True `(x, y, z)` and `(x, y, z, w)` scene contracts
- 3D cube reference model
- 4D tesseract with 16 vertices and 32 edges
- 4D simplex / 5-cell
- 4D 16-cell
- Rotation in all six 4D coordinate planes: XY, XZ, XW, YZ, YW, and ZW
- Perspective projection from 4D to 3D and from 3D to the browser figure
- Depth-sorted edges and vertices
- Interactive camera rotation, scale, perspective, labels, and animation
- Custom scene JSON
- Direct data-field mapping when calculations return three- or four-coordinate records
- Clearly labeled derived result-space glyphs when a calculation does not have physical dimensional geometry
- SVG, PNG, PDF, JSON, package, project, and Decision Studio outputs

## Workspace backup, restore, and reset

Workspace Data provides:

- Complete workspace JSON export
- Browser-generated workspace ZIP
- Per-project JSON, notebook Markdown, observation CSV, visualization JSON, and analysis-packet JSON
- Restore as copies
- Merge by project identifier
- Replace workspace
- Reset interface and visualization settings
- Clear notes and observations
- Clear analysis history
- Reset the active project
- Delete the active project
- Factory-reset the complete local Lab workspace

Destructive reset actions display the selected record count, offer a backup first, require the user to type `RESET`, and create only a minimal deletion receipt without preserving removed scientific content.

## WordPress installation

Upload `sustainable-catalyst-lab-plugin-v0.9.1.zip` through **Plugins → Add New Plugin → Upload Plugin**, replace the current plugin, activate it, and keep this shortcode on the Lab page:

```text
[sc_lab_app]
```

Focused infrastructure shortcodes are also available:

```text
[sc_lab_visualization]
[sc_lab_workspace_data]
```

The existing focused discipline shortcodes remain available.

## Project compatibility

The original browser-storage keys remain unchanged:

```text
scLabProjectsV010
scLabActiveProjectV010
```

Projects from v0.1.x through v0.9.0 are normalized in place to schema version `0.9.1`. No destructive migration is performed.

Version 0.9.1 adds:

```text
visualizations
dimensionalScenes
chartExports
analysisPackets
```

## Contracts

```text
contracts/analysis.schema.json
contracts/scene.schema.json
contracts/decision-studio-packet.schema.json
contracts/project.schema.json
```

## Validation

Run:

```bash
chmod +x scripts/test_release.sh
./scripts/test_release.sh
```

The suite validates PHP and JavaScript syntax, WordPress template rendering, legacy scientific modules, all existing discipline benchmarks, project migration, analysis contracts, SVG rendering, PDF generation, workspace ZIP round trips, selective reset and restore, 3D geometry, 4D rotation norm preservation, polytope topology, projected SVG output, and Decision Studio scene packets.

## Boundaries

- The v0.9.1 PDF is a single-figure export; structured multi-page reports belong to the later PDF Reporting and Decision Studio Report Composer releases.
- Four-dimensional figures are projections. The original four-coordinate scene is retained in JSON and handoff packets.
- Analysis-derived result-space glyphs are labeled as normalized visual abstractions and are not physical or causal models.
- Workspace data remain browser-local in this release unless explicitly exported or handed off.
