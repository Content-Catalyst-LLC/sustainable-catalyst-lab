# SC-FIG-04 — Geospatial figures with MapLibre GL JS

**State:** 0.163.1.8. Behind `sc_lab_fig04_maplibre_enabled` (default off; needs the figure-bundle
renderer on). Presentation only: Lab verifies and draws, it never approves or publishes.

## Path

```
Site Intelligence evidence objects (normalize_evidence_object) ─► SI reproducible spatial package (sealed)
  ─► Workspace dataset (rows derived from the objects, pinned) ─► notebook calculation
  ─► Workbench MapLibre adapter (verifies package, objects, rows; emits view 1.1 + sc.figure-bundle.v1)
  ─► Lab figure-bundle renderer (this module) ─► private Research governance ─► Research Hub
```

Lab checks the parts it can see: every SI content digest, the view's canonical hash against the bundle
artifact, the evidence-class rules, the licence of every cited source, and the policy below.

## View 1.1 (`sc-lab-maplibre-view/1.1`)

Everything in 1.0 (see [SC-FIG-03A](SC-FIG-03A_MAPLIBRE_PREPARATION.md)) plus:

| Property | Rule |
|---|---|
| `fields.<f>.uncertainty`, `uncertaintyKind` | Property holding each value's uncertainty; kind is `standard-error`, `standard-deviation` or `ci95-half-width`. Values must be non-negative numbers. |
| layer `classify {field, breaks, colors}` | Points and polygons. Declared numeric field, 1–8 ascending breaks, one more `#rrggbb` colour than breaks. Missing values draw grey ("not reported"). |
| layer `geometry: heatmap`, `weight {field, max}`, `ramp` | Points only. Weight scaled 0..max. Ramps: viridis, cividis, magma (light = low density). Legend states it is a kernel density, not interpolated values. |
| `time {property: observed_at, label, steps, initial}` | Steps must equal the objects' distinct SI `observed_at` values, sorted. |
| `comparison {field, from, to, match, label}` | Two steps, earlier first. Change per matched object with root-sum-square uncertainty (independence assumed, and stated). |
| `calculations[]` | Label, value, unit, method, optional uncertainty and kind, and `calculationRef` pointing at a bundle `calculationRefs` entry with an output hash. |
| `rasterLayers[]` | Earth-observation layers. Refused unless the provider is approved (none is), its licence is `verified-for-use` in the bundle, tiles are HTTPS `{z}/{x}/{y}` templates on the provider's approved hosts, and product id, acquisition time, processing baseline and tile-manifest hash are given. |

Also for 1.1: every bundle source must be `verified-for-use`.

### Earth-observation adapter

`eoCandidates()` lists Copernicus Sentinel-2 L2A, Sentinel-1 GRD and CLMS CORINE Land Cover with their
licence, required attribution and what approval needs. `approvedProviders()` is empty. Approving a
provider is a code change to the frozen `PROVIDERS` registry (reviewed), together with the CSP
`img-src`/`connect-src` for its host; the unit tests show a raster layer passing only with a
test-only registry.

## Renderer

`graph-studio-maplibre-renderer-fig04.js` (`SCLabMapLibreFIG04`):

- MapLibre GL JS 5.24.0 CSP build from `assets/lib/maplibre-gl-5.24.0/` (SHA-256 pinned in PHP).
- Worker: same-origin fetch, SHA-384 check (value from PHP), started from a `blob:` URL.
- Style: one inline GeoJSON source; no glyphs, sprite, tiles or basemap. Requests MapLibre makes are
  counted (`data-map-requests`, expected 0).
- Controls: layer checkboxes, time slider with previous/next and `aria-valuetext`, comparison toggle
  (second synced map), feature details on click (text only).
- Legend with units, classes, ramp meaning and evidence class; calculation results; a sources line;
  the full data table and the comparison table.
- No WebGL or worker refused: `data-map-state="unavailable"` with the reason; legend and tables stay.

CSP for a page with map views: `script-src 'self'`, `worker-src blob:`, `img-src 'self' blob: data:`,
`connect-src 'self'`. plotly.js (loaded for Plotly views) injects style elements, so Lab pages that
also show Plotly need `style-src 'unsafe-inline'` as before; map views alone do not.

## Tests

`scripts/test_fig04_maplibre.sh` runs:

- `tests/test-maplibre-fig03a.js` (1.0, unchanged) and `tests/test-maplibre-fig04.js` (1.1: accepted
  view, styles, legend, table, comparison, EO gate, 20 refusals, generic renderer dispatch);
- the vendored-file check against `SOURCE.json`;
- `tests/test-maplibre-fig04.php` and the same with a tampered worker (nothing served);
- `tests/chromium-fig04-maplibre.html` in headless Chrome under a strict CSP with SwiftShader WebGL
  (`scripts/run_chromium_fig04.py`): draws the map and exercises layers, legend, time, comparison,
  worker-hash refusal, SI-digest refusal, EO refusal, restricted licence, same-origin network.

Fixtures: `tests/fixtures/fig04-wexford/build_fixtures.py <site-intelligence checkout>`. Synthetic
Wexford: six invented field parcels (modelled SOC with standard error, pH with one value missing) and
eight hypothetical nitrate monitoring sites, each over four quarters. Nothing is a measured Wexford
value.

## SC-FIG-04.1 — Static export, calculation intervals, styling, pairing

### Static PNG export

The export captures the frame or frames on screen. They are read inside a MapLibre `render` event, so
`preserveDrawingBuffer` is not needed. The frames are composed on a 2D canvas with:
- the title;
- the evidence class and measurement status;
- the time step, or the comparison steps;
- the visible layers;
- a legend of the visible layers with units;
- the calculation lines;
- attribution;
- provenance: figure and version, the view SHA-256, and the sources.

The receipt (`sc-lab-static-map-export/1.0`, canonical JSON) records:
- the bundle SHA-256 (bytes);
- the view, source and calculation hashes;
- the state;
- the legend, units, calculation text and attribution;
- the renderer;
- the image size.

The receipt is embedded as one `tEXt` chunk named `sc:static-map-receipt`. The JSON receipt adds the PNG's
SHA-256 and length.

`verifyExport(png, receiptFile, {spec, bundle, bundleSha256})` refuses:
- malformed chunks or CRCs, and trailing bytes;
- a missing or duplicate receipt;
- a size mismatch;
- a hash mismatch;
- an embedded receipt that differs from the file;
- another view, figure revision, bundle, sources or calculations;
- unknown layers or time steps.

The renderer runs it before offering the downloads.

### Calculation intervals

View 1.1 calculations may add these fields:

```
interval: {semantics: "confidence-interval", level, lower, upper, method, distribution,
           degreesOfFreedom, computedBy: "runtime",
           consistency: "estimate-plus-minus-t-standard-error" | "not-checked"}
assumptions: {declaredBy: "model-revision", checked: false, statements: [..]}
```

- They come from the Workspace export through the Workbench adapter.
- Lab requires:
  - that the interval contains the value;
  - that it is bound by `intervalsSha256`;
  - that the assumptions are bound by `assumptionRefs`.
- A "checked" consistency claim needs a reported standard error.
- When a result has neither a standard error nor an interval, the display says **"Trend uncertainty
  unavailable"**.

### Styling under Astra

The FIG-04 controls had picked up three rules:
- the Lab UI bundle's `.sc-lab-app input { width: 100%; padding; border }`, plus a 44px minimum height;
- Astra's checked-checkbox and button colours;
- Astra's `input[type=range] { appearance: none }`.

The FIG-04 stylesheet now restores native checkboxes (1.125rem) and the native range control. Labels and
buttons are 44px targets, and every control has a `:focus-visible` outline. Every selector starts with
`.sc-lab-fig04-` (the Node test checks this).

### Pairing with the Research bridge

| Lab | Bridge | Result |
|---|---|---|
| 0.163.1.7 | 0.3.x | supported (SC-FIG-03B) |
| 0.163.1.8 | 0.4.x | supported (SC-FIG-04) |
| 0.163.1.8 | 0.3.x | Lab activation refused (409); bridge activation refused; renderer off if swapped in |
| 0.163.1.7 | 0.4.x | refused by bridge 0.4.0 (Research) |
| 0.163.1.8 | < 0.3 | not affected (those bridges pin no Lab release) |
