# Observe and Domain Module Activation Repair — v0.26.3.3

v0.26.3.3 separates observation interfaces from the legacy all-module initializer. Climate Maps, Scientific Feeds, Space & Astronomy Observations, and Marine Biology are mounted by `sc-lab-observe-domain-v02633.js`. Microbiology receives the active project instance and participates in the runtime fallback mount map.

## Canonical routes

- `astronomy-observations` → `space-telescopes`
- `space-observations` → `space-telescopes`
- `marine` → `marine-biology`
- `climate` → `climate-maps`
- `astronomy` remains the analytical calculator laboratory.

## Diagnostics

- REST: `/wp-json/sc-lab/v1/runtime/v02633/health`
- Browser: `window.SCLabObserveDomainV02633.status()`
- Microbiology mount: `[data-microbiology-laboratory-root][data-sc-lab-controller-ready="1"]`
