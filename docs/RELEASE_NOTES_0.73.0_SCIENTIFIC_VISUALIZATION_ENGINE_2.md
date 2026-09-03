# Sustainable Catalyst Lab v0.73.0 — Scientific Visualization Engine 2, Unified Graph Contract & Graph Studio Renderer Architecture

v0.73.0 is the architectural foundation for Lab's advanced scientific graphing and visualization roadmap. It does not replace the proven v0.44 SVG renderer or the v0.71 advanced canvas renderer. Instead, it places both behind one governed Visualization Engine 2 registry so Graph Studio can treat conventional 2D figures and higher-dimensional scientific surfaces as first-class saved figures with explicit renderer identity, state, publication metadata, and provenance.

## What changes

- Adds `sc-lab-scientific-visualization/0.73.0`, a renderer-aware visualization specification that becomes the common figure input for new Graph Studio work.
- Adds `sc-lab-scientific-figure/0.73.0` and `sc-lab-figure-workspace/0.73.0` for new saved figures and mixed-renderer workspaces.
- Adds Visualization Engine 2 (`2.0.0`) with an explicit renderer registry:
  - `svg2d` → existing Scientific Visualization Engine v0.44.0.
  - `canvas4d` → existing Advanced Visualization Front Door renderer v0.71.0.
- Preserves existing line, scatter, line-scatter, histogram, horizontal-bar, and heatmap behavior through the v0.44 compatibility adapter.
- Promotes `surface-4d` to a first-class Graph Studio visualization kind.
- Persists 4D hyperslice, XW/YW rotation, vector/uncertainty/contour layer state, profile identity, dimensional semantics, publication metadata, and renderer provenance in the saved Graph Studio figure.
- Adds a Graph Studio 4D biodiversity example that uses the same deterministic synthetic profile already established for the public Lab preview.
- Adds renderer-aware exports: SVG/PNG/CSV/JSON for `svg2d`; PNG/JSON for `canvas4d`.
- Keeps older `scientific-figure-v0470` project records visible and openable in Graph Studio.
- Moves scientific workflow `graph.normalize` and `figure.normalize` stages onto the new compatibility-aware visualization normalizer.
- Allows reproducible-model packages to normalize and preserve new v0.73 figures while retaining legacy graph compatibility.
- Adds WordPress and FastAPI health/schema/policy surfaces for the v0.73 visualization layer.

## Scientific boundary

v0.73.0 is an architecture release, not the arbitrary scientific-data surface-binding release. The current `surface-4d` renderer exposes the existing deterministic `generic` and `biodiversity` synthetic profiles. It must not be represented as measured, forecast, or project-derived scientific data. Project-data binding, variable mapping, transforms, and arbitrary structured dataset-to-visual-variable mapping are intentionally deferred to v0.75.0.

## Compatibility

- Stable platform compatibility remains `1.0.0`.
- Existing v0.44 SVG scientific rendering remains the authoritative 2D compatibility renderer.
- Existing v0.71 4D canvas rendering remains the authoritative higher-dimensional renderer in this release.
- Existing v0.47 project figures remain discoverable in the Graph Studio library and are upgraded in-memory when rendered through Visualization Engine 2.
- No arbitrary code, remote image fetching, or hidden scientific computation is introduced.

## Release gate

The v0.73.0 gate validates JavaScript/PHP/Python syntax, renderer registry wiring, first-class 4D saved-figure behavior, legacy Graph Studio normalization, reproducible-model-package compatibility, scientific workflow compatibility, Model Studio compatibility, preregistration regression coverage, FastAPI route topology, and the release manifest.
