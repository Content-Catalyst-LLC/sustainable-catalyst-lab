# SC-FIG-01 — Generic `sc.figure-bundle.v1` renderer in Graph Studio

**State:** release candidate 0.163.1.5, default off. Not deployed. Preview only.

Lab renders governed figure bundles from any producer (Workbench, Workspace, Research, Lab) inside
the existing Graph Studio stage. It does not create a second Graph Studio or a figure store: the
bundle's producer stays the authority, and Lab neither recomputes nor reviews nor publishes.

## Input: a figure package

One `sc.figure-bundle.v1` JSON file plus the view files it references in `artifacts[]`. A package
arrives from the local file chooser (multiple files) or from another Lab module via the
`sc-lab:figure-bundle:render` event (`detail.files = [{name, bytes}]`, optional
`detail.expectedBundleSha256`). Nothing is fetched or uploaded.

## Verification (all in the browser)

| Check | Result on failure |
|---|---|
| Exactly one bundle; Data schema minimum (required fields, enums, figureId, hashes) | refused |
| `evidenceClass` and `scientificContext.measurementStatus` agree on `observed` (no promotion) | refused |
| No markup, `href=`, `src=` or `javascript:` in any bundle string | refused |
| Optional `expectedBundleSha256` (registered Workspace output / Research object hash) equals the bundle bytes | refused |
| Each supplied file matches an artifact `sha256` by raw bytes or canonical JSON (sorted keys, compact, Python float spelling) | refused (file "not referenced") |
| `rendering.visualizationSpecSha256`, when present, is one of the artifacts | refused |
| Plotly view passes the FIG-02A figure policy; loaded plotly.js is 3.3.1 | refused |
| `image/png` view is raw-byte verified and starts with the PNG signature | refused |

## View states

| State | Meaning |
|---|---|
| `rendered-plotly` | `application/vnd.plotly.v1+json`, drawn with vendored plotly.js 3.3.1; accessible table derived from the traces (`not reported` for missing values) |
| `static-png` | verified PNG bytes shown through a local blob URL, with the bundle's alt text |
| `unsupported` | integrity verified, but Lab has no renderer for that media type (e.g. Vega-Lite, SVG); nothing drawn |
| `missing` | referenced by the bundle but not supplied; nothing drawn |

The card is `rendered` when at least one view is drawn, otherwise `metadata-only`. Evidence class,
measurement status, review state, interpretation, limitations, do-not-infer statements, sources and
provenance are always shown.

## Files

| File | Role |
|---|---|
| `assets/js/modules/graph-studio-figure-bundle-renderer.js` | Package verification and rendering |
| `assets/css/sc-lab-graph-studio-figure-bundle-renderer.css` | Styles (extends the FIG-02A panel) |
| `includes/class-sc-lab-graph-studio-figure-bundle-renderer.php` | Default-off loader (`sc_lab_figure_bundle_renderer_enabled`), health route `sc-lab/v1/graph-studio/figure-bundle-renderer/health` |
| `tests/test-figure-bundle-renderer.{js,php}`, `tests/chromium-figure-bundle-renderer.html` | Contracts and browser harness |
| `tests/fixtures/figure-bundle-generic/` | Synthetic packages derived from the amd64 Workbench staging body |
| `scripts/test_figure_bundle_renderer.sh` | Runs all of the above |

The loader reuses the FIG-02A module as a library and the same vendored, hash-pinned plotly.js; if
that file is modified, nothing is served. FIG-02A's own panel mounts only when its own switch is on.

## Not done here

- Reading bundles directly from Workspace or Research over HTTP (needs SC-UP-01 owner sessions).
- Vega-Lite, MapLibre, SVG or 3D renderers (reported as `unsupported` until each adapter is vendored and tested).
- Saving, reviewing or publishing figures.

## Release context (SC-FIG-03A, 0.163.1.7)

Lab renders figures; it never approves or releases them. Publication approval happens in Workspace
(four signed dimensions on the exact revision). Release state is held by Sustainable Catalyst
Research. A host that serves released figures passes Research's record as
`render(out, files, expectedBundleSha256, {releaseContext})`:

```json
{"authority": "sc-research", "state": "released", "label": "…", "bundleSha256": "<64 hex>",
 "articleRevision": 1, "releasedAt": "2026-11-11T12:00:00+00:00"}
```

The card shows the record (`data-release-state="released"`) only when it names the exact bundle hash
Lab just verified. A record for another bundle (`mismatch`), or a malformed one (`invalid`), is
ignored, and the card says so. Without a record, the card reads "Not released here"
(`data-release-state="none"`). The bundle's own `review.*` fields are shown as producer review notes
and never count as approval.
