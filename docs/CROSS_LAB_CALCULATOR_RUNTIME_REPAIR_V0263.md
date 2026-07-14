# Cross-Laboratory Calculator Activation and Runtime Repair — v0.26.3

## Failure repaired

The isolated single-panel runtime intentionally removes inactive laboratory markup. The global application bootstrap still initialized the shared calculator selector, however, and received a missing-element proxy rather than an actual `<select>`. The proxy did not implement `HTMLSelectElement.add()`, causing startup to stop before later controllers—including Astronomy, Earth/Marine, Biology, Materials, Energy, and Engineering—could mount.

## Runtime changes

- The missing-element proxy now implements a safe `add()` operation.
- Domain controllers mount only when their active panel is present.
- Every controller is wrapped in an independent error boundary.
- Runtime errors are recorded in `window.SCLabRuntimeV0263`.
- The active application emits `sc-lab:app-ready` or `sc-lab:app-error`.
- Core and runtime assets use file-based cache-busting.
- Project storage falls back to memory when local storage is blocked or exceeds quota.
- Module changes use full-page teardown to guarantee release of legacy global resources.

## Diagnostics

Browser console:

```javascript
window.SCLabRuntimeV0263.status()
```

REST health endpoint:

```text
/wp-json/sc-lab/v1/runtime/v0263/health
```

A healthy active module reports one retained panel, `appReady: true`, no recorded runtime errors, and the matching PHP/plugin/runtime version `0.26.3`.
