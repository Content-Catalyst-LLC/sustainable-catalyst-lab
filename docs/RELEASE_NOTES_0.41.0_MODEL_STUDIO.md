# Sustainable Catalyst Lab — Model Studio v0.41.0 Feature Layer

## Model Studio & Scientific Visualization Foundation

This build introduces the first unified scientific modeling workspace in Sustainable Catalyst Lab while preserving the uploaded repository's v1.0.0 stable-platform metadata. The v0.41.0 identifier applies to the new Model Studio feature layer and its contracts; it does not downgrade or remove the later GA operational modules already present in the source archive.

### What ships

- **Model Studio workspace** with a visible workflow from model definition and data binding through future fit, diagnostics, uncertainty, comparison, and registration stages.
- **Unified model contract** covering model identity, family, variables, parameters, units, parameter bounds, dataset bindings, assumptions, limitations, provenance, and execution adapters.
- **Scientific graph contract** designed to be shared by Lab and later Workbench integrations.
- **Shared browser visualization engine** with numerical axis ticks, gridlines, true scatter points, line/scatter overlays, legends, accessible focus targets, hover inspection, and SVG serialization.
- **Existing Scientific Visualization integration** so the v0.27.4 Numerical Visualization Studio delegates to the shared renderer when v0.41.0 is loaded.
- **FastAPI model-studio service** for policy/health inspection, model normalization, graph normalization, and bundle construction.
- **WordPress compute-core proxies** for the new backend routes.
- **Governed handoff records** from Model Studio to Model Calibration, Design Studies, Ensemble/Uncertainty, and the Scientific Model Registry. Workbench is included in the backend bundle target catalog for the planned cross-product integration.

### Safety and scope boundaries

- Arbitrary code execution remains disabled.
- Arbitrary formula execution remains disabled.
- Declarative equation text can be stored as model-definition metadata but is explicitly non-executable in v0.41.0.
- The existing registered model families continue to hand off to the governed v0.30.2 calibration runtime.
- Model Studio preview graphs visualize bound observations; they do not claim a fitted relationship unless a governed fitting workflow produces one.

### New contracts

- `sc-lab-model-studio-model/0.41.0`
- `sc-lab-scientific-graph/0.41.0`
- `sc-lab-model-studio-result/0.41.0`
- `sc-lab-model-studio-policy/0.41.0`

### New public Lab surface

- `[sc_lab_model_studio]`
- Lab module route: `model-studio`
- WordPress health: `/wp-json/sc-lab/v1/model-studio/v0410/health`
- WordPress schema: `/wp-json/sc-lab/v1/model-studio/v0410/schema`

### Backend routes

- `GET /v1/model-studio/health`
- `GET /v1/model-studio/policies`
- `POST /v1/model-studio/models/normalize`
- `POST /v1/model-studio/graphs/normalize`
- `POST /v1/model-studio/bundles/build`

### Validation target

The release gate covers the new Model Studio backend tests, the pre-existing calibration/visualization/design-study/model-registry/ensemble/surrogate suites, JavaScript syntax, PHP syntax, Python compilation, release-manifest integrity, and static wiring checks for the new Lab panel and shared renderer.
