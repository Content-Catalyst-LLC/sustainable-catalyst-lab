# Sustainable Catalyst Lab v0.72.0 — Homepage 4D Biodiversity Modeling Preview

v0.72.0 turns the Lab homepage presence into an actual scientific-capability demonstration. It adds a dedicated public homepage shortcode that reuses the existing v0.71.0 browser-rendered 4D visualization renderer and applies it to an explicitly synthetic biodiversity scenario.

## Homepage widget

- Adds `[sc_lab_home_preview]` and alias `[sc_lab_home_biodiversity]`.
- Renders a compact public-facing 4D biodiversity response surface directly on the homepage.
- Uses the same v0.71.0 4D renderer used by the Lab scientific front door instead of introducing a second visualization engine.
- Keeps the homepage module independent of Python Compute Core and makes no network request for the illustrative surface.
- Loads only the visualization assets required for the shortcode rather than the full Lab application bundle.

## Biodiversity demonstration

The illustrative model represents four dimensions together:

1. habitat quality;
2. climate stress;
3. relative biodiversity response;
4. time / disturbance progression.

The public preview includes:

- a deterministic response-surface mesh;
- projected contours;
- gradient/vector-field arrows;
- uncertainty-guide lines;
- synthetic sample markers;
- a projected 4D tesseract inset;
- time-slice control;
- XW and YW 4D projection controls;
- optional time-sweep animation;
- pointer inspection of habitat, climate stress, biodiversity response, and time state.

## Scientific boundary

All values in the homepage visualization are deterministic synthetic interface values. They are not observations, species counts, ecological measurements, conservation-status estimates, forecasts, or policy conclusions. The widget is designed to demonstrate Lab modeling and visualization capability while keeping the distinction between illustration and evidence explicit.

## Public presentation

- Uses the Sustainable Catalyst black / white / red institutional system.
- Keeps the visualization visually prominent while remaining substantially more compact than the full Lab application.
- Adds four capability pathways: Model, Graph, Experiment, and Observe.
- Provides direct calls to enter the Lab and open the Lab/Graph Studio pathway.
- Provides responsive desktop, tablet, mobile, and reduced-motion behavior.

## Compatibility

- WordPress release: `0.72.0`
- 4D renderer: `0.71.0` with reusable biodiversity profile support
- Stable platform compatibility marker: `1.0.0`
- No backend scientific method contract changes.
- No database migration.
- No arbitrary-code execution.
