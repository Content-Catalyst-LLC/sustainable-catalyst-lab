# Application Startup and Runtime Stability — v0.25.4

## Problem corrected

The main `[sc_lab_app]` page previously rendered every laboratory panel into one browser document. Closed panels were visually hidden but remained present in the DOM, and their JavaScript runtimes could initialize, observe, retry, and attach listeners during the same startup cycle.

## Stable runtime

v0.25.4 uses a balanced-tag panel parser that does not depend on the optional PHP DOM extension. It retains the existing application chrome and navigation while keeping only one `data-module-panel` element in the browser at a time. Selecting another laboratory:

1. Dispatches `sc:lab:module-unmounting`.
2. Removes the prior panel immediately.
3. Cancels an older in-flight request.
4. Fetches the selected panel from the WordPress REST API.
5. Removes the panel’s historical `hidden` state and activates it.
6. Inserts exactly one returned panel.
7. Dispatches `sc:lab:module-mounted`.

## Recovery controls

- `?sc_lab_safe=1` always opens Overview.
- `?sc_lab_module=chemistry` opens a named laboratory without loading every other panel.
- `?sc_lab_legacy=1` restores the historical all-at-once page only for administrators. It is diagnostic and may still overload the browser.
- The runtime bar provides Overview, Reload module, and Safe start controls.

## Runtime endpoints

```text
GET /wp-json/sc-lab/v1/runtime/v0254/health
GET /wp-json/sc-lab/v1/runtime/v0254/module/{module}
```

The module endpoint is read-only and returns only an existing `data-module-panel` from the canonical application output.

## Compatibility boundary

This patch does not replace calculation engines, focused shortcodes, REST calculation routes, project records, exports, notebooks, or existing laboratory contracts. It changes only the main application startup and module lifecycle.
