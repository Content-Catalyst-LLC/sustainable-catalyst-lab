# Sustainable Catalyst Lab v0.47.0 — Graph Studio, Scientific Figure Workspace & Interface Reorganization

## Release intent

Lab v0.47.0 turns scientific visualization into a first-class workspace. The release adds a dedicated Graph Studio with a large interactive figure canvas, project figure library, publication metadata, governed figure persistence, and cross-module graph handoffs. It also reorganizes the Lab shell so model-building and visualization are easier to find without removing the existing specialist modules.

## Graph Studio

- Adds a dedicated `Graph Studio` Lab panel and `[sc_lab_graph_studio]` shortcode.
- Adds a large scientific figure canvas backed by the shared Scientific Visualization Engine v0.44.0.
- Supports line, scatter, line+scatter, histogram, horizontal-bar, and heatmap figure workflows.
- Accepts structured row data, x/y/z bindings, and explicit series definitions.
- Preserves shared zoom, pan, crosshair, keyboard navigation, accessible point inspection, series visibility, annotations, confidence/error rendering when supplied by the graph specification, and publication exports.
- Adds publication metadata for title, subtitle, axis labels, units, caption, source, method, notes, aspect ratio, grid visibility, and legend visibility.
- Keeps SVG, PNG, CSV, and JSON exports in the shared renderer.

## Scientific Figure Workspace

- Adds `sc-lab-scientific-figure/0.47.0` and `sc-lab-figure-workspace/0.47.0` contracts.
- Adds deterministic Graph Studio normalization and workspace-building services in FastAPI.
- Adds a project-scoped figure library using the existing `visualizations` project collection.
- Figures can be saved, reopened, duplicated as drafts, referenced from Notebook, and queued for Report Studio.
- Figure records preserve their scientific graph specification and presentation metadata rather than flattening the result into an image-only artifact.
- Adds governed FastAPI and WordPress compute-core endpoints for graph, figure, and workspace normalization.

## Model Studio handoff

- Adds `Open in Graph Studio` to the active v0.46 Model Studio surface.
- Graph handoffs transfer the existing governed scientific graph object rather than recomputing or silently altering model results.
- Graph Studio presentation edits remain distinct from the underlying model evidence.

## Lab interface reorganization

- Adds top-level `MODEL` and `VISUALIZE` navigation groups.
- Moves Model Studio, Model Calibration, Design Studies, Scientific Model Registry, Ensembles/Sensitivity/Uncertainty, and Surrogate/Reduced-Order analysis into `MODEL`.
- Places Graph Studio, Scientific Visualization, and Visualization & Export into `VISUALIZE`.
- Makes sidebar groups collapsible and preserves group state in the browser.
- Adds four operational Overview front doors: Model, Graph, Experiment, and Observe.
- Preserves command search so specialist modules remain directly discoverable even when navigation groups are collapsed.

## Architecture and safety

- Graph Studio is a workspace over the shared Scientific Visualization Engine v0.44.0; it does not create a second graph renderer.
- The governed graph contract remains `sc-lab-scientific-graph/0.46.0` so v0.46 response-surface and earlier model outputs remain compatible.
- Graph Studio does not enable arbitrary Python, JavaScript, shell execution, remote image fetching, or arbitrary code embedded in figure specifications.
- WordPress-facing release version advances to `0.47.0` while internal platform compatibility remains `1.0.0`; runtime integrity verifies those version lines independently.

## Validation

The v0.47.0 release gate includes Graph Studio backend tests plus the full focused modeling regression line from v0.46. It also checks the browser workspace, interface reorganization, Model Studio handoff, PHP integration, FastAPI routes, JavaScript/PHP/Python syntax, and WordPress runtime integrity before Git operations are allowed.

## Deferred deliberately

This release does not attempt a second rendering engine, arbitrary custom JavaScript charts, remote chart plugins, collaborative real-time figure editing, 3-D WebGL surfaces, or automatic scientific interpretation. Those capabilities require separate contracts and evidence boundaries.
