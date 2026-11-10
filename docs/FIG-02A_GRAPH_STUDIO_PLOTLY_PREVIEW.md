# SC-FIG-01 / FIG-02A — Graph Studio Plotly preview

**State:** source candidate, default off. Not deployed. Preview only.

Renders a Workbench FIG-02A compile response (`sc-workbench-plotly-figure-adapter/1.0`, Workbench PR #40)
inside the existing Graph Studio stage. It is not a second Graph Studio: it mounts one panel on
`#sc-lab-graph-studio-renderer-root [data-gs13583-stage]` (or `[data-lab-module="graph-studio"]`).
Workbench remains the numerical authority; Lab does not recompute, store, review or publish figures.

## Files

| File | Role |
|---|---|
| `assets/lib/plotly-3.3.1/plotly.min.js` | plotly.js 3.3.1, byte-identical to `plotly==6.5.2` `package_data/plotly.min.js` (the file the Workbench export worker uses). sha256 `e2b0f77e…848968` |
| `assets/lib/plotly-3.3.1/SOURCE.json`, `LICENSE.txt` | Provenance (wheel RECORD hash) and MIT licence |
| `assets/js/modules/graph-studio-plotly-preview-fig02a.js` | Hash verification, content policy, rendering, accessible tables |
| `assets/css/sc-lab-graph-studio-plotly-preview-fig02a.css` | Panel styles |
| `includes/class-sc-lab-graph-studio-plotly-preview-fig02a.php` | Default-off loader and `sc-lab/v1/graph-studio-plotly-preview/fig02a/health` |
| `tests/test-fig02a-plotly-preview.{js,php}`, `tests/chromium-fig02a-plotly-preview.html` | Contracts and browser harness |
| `tests/fixtures/fig02a-preview-synthetic.json` | Synthetic Workbench compile responses (no scientific meaning) |
| `scripts/test_fig02a_plotly_preview.sh` | Runs all of the above |

## Enabling

Off unless the option `sc_lab_fig02a_plotly_preview_enabled` is `'1'` (or the filter of the same name
returns boolean `true`). While off nothing is enqueued, including plotly.js. When on, only Lab pages load
it, and only if the vendored file's sha256 matches the pinned value (fail closed).

## What the preview enforces

- The response's `plotly.specSha256` and `resultHash` are recomputed in the browser with Web Crypto
  using Workbench's canonical JSON (sorted keys, compact separators, Python float spelling preserved).
  Any mismatch refuses the preview and nothing is drawn.
- `plotlyJsVersion` must be `3.3.1` and the loaded `Plotly.version` must be `3.3.1`.
- No `layout.images`, `template`, `updatemenus`, `sliders` or frames; trace types limited to scatter,
  bar, box, histogram, heatmap; no links, `src=`, `javascript:` or script/iframe/img/svg markup in any
  string.
- The evidence class is shown above the plot and stays in the figure subtitle; review state and
  "Not publication-approved" are shown. Missing values render as `not reported`.
- The accessible table is built from the structured rows with text nodes. Workbench's HTML is never
  injected.
- Responses are read from a local file chooser (or a `sc-lab:fig02a:preview` event carrying
  `detail.responseText`). Nothing is uploaded, persisted or fetched. The mode-bar download is a browser
  convenience, not the authoritative Workbench static export.

## Tests

```sh
scripts/test_fig02a_plotly_preview.sh
```

The fixtures are synthetic Workbench outputs. These tests show that the preview is correct and
safe. They do not validate any study. Private scientific acceptance (Wexford SC-07/SC-08) runs on
the Workbench side against the private Data repository.

## Not done here

- Server-side bridge from Lab to Workbench compile: it needs UP-01 owner authentication, and the
  Workbench route has none.
- Saving previews to Lab projects or Workspace (UP-01/UP-03), and review or publication actions
  (UP-04).
- Release-version bump and inclusion in a Lab release package.
