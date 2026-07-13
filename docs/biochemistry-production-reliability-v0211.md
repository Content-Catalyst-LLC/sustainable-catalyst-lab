# Lab v0.21.1 — Biochemistry Production Activation and Interface Reliability

This maintenance release keeps the 48-method Biochemistry and
Molecular Analysis engine at its validated v0.21.0 method contract
while hardening production activation in WordPress.

## Reliability changes

- Front-end asset activation no longer depends only on raw shortcode
  detection.
- Late page-builder and cached mounts are detected automatically.
- Empty mounts carrying stale initialization markers are repaired.
- Module-open, navigation-click, pageshow, and DOM-mutation retries
  are coordinated through one production runtime.
- The canonical Biochemistry panel and mount are restored when
  incomplete.
- Runtime diagnostics are exposed through
  `window.SCLab.BiochemistryProduction.status()`.
- A public health endpoint reports asset readiness and the expected
  48 methods and 48 benchmarks.
- Mobile controls, formulas, tables, and output scrolling are
  hardened.
- A version-aware release runner replaces repeated temporary manual
  edits to historical active-version assertions.

## Browser diagnostics

```javascript
window.SCLab?.BiochemistryProduction?.status()
```

## Health endpoint

```text
/wp-json/sc-lab/v1/compute/biochemistry/health
```
