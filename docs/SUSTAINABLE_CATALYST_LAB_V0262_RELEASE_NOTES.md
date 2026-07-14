# Sustainable Catalyst Lab v0.26.2

## Legacy Laboratory Compatibility and Runtime Restoration

This patch restores laboratories that became inert or unreachable after the v0.25.5 isolated-module lifecycle was introduced. It retains the v0.26.x WordPress control plane, Python compute core, durable queue, and worker APIs.

### Restored runtime behavior

- Forces the complete legacy laboratory markup path on the public Lab page.
- Leaves `sc_lab_isolated=1` as an explicit diagnostic opt-in for the isolated lifecycle.
- Normalizes legacy names for Space Observations, Space Telescopes, Marine Biology, Astronomy Laboratory, and earlier engineering/science module slugs.
- Adds browser navigation that can switch among retained panels without losing project state.
- Reloads a focused laboratory with `sc_lab_legacy=1` when its panel is not yet present.
- Re-dispatches module-ready events and calls compatible legacy module initializers.
- Adds a visible runtime boundary instead of silently leaving a laboratory inert.
- Exposes `window.SCLabCompatibilityV0262.status()` for browser diagnostics.
- Adds `GET /wp-json/sc-lab/v1/runtime-compatibility`.

### Compatibility priority

The release specifically covers Astronomy, Space Telescope observations, Marine Biology, Earth and ocean systems, and every existing Lab panel represented in the current module navigation. It does not remove or replace the v0.26.0 compute foundation or v0.26.1 queue reliability work.

### Browser check

Open the Lab and run:

```javascript
window.SCLabCompatibilityV0262.status()
```

A healthy response reports `legacyMode: true`, a nonzero `panelCount`, and `activePanelFound: true`.
