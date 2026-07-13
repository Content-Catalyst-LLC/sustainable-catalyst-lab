# Biosignal Production Activation and Interface Reliability

Sustainable Catalyst Lab v0.23.1 activates and protects the
v0.23.0 Biomedical Engineering and Biosignals interface in public
WordPress and application contexts.

## Activation

The production class explicitly enqueues:

- The v0.23.0 biomedical interface stylesheet
- The v0.23.0 biomedical browser engine
- The v0.23.1 reliability stylesheet
- The v0.23.1 production repair runtime

The v0.23.0 interface no longer depends solely on template timing or
a page-specific enqueue path.

## Canonical interface repair

The browser runtime identifies one canonical panel using:

```text
data-lab-module="biomedical-engineering-biosignals"
data-module-panel="biomedical-engineering-biosignals"
```

It then guarantees one canonical root:

```text
data-biomedical-biosignals-root
```

The runtime can:

- Add missing canonical panel attributes and classes
- Create a missing mount inside the canonical panel
- Remove duplicate mounts
- Prefer an already rendered mount when duplicates compete
- Remove stale v0.23.0 render markers
- Clear empty or invalid placeholder content
- Re-run the scientific interface renderer
- Reveal and open the biomedical workspace

## Recovery triggers

Repairs run after:

- Initial page load
- Lab navigation clicks
- Lab module-open events
- Browser history restoration
- Window focus restoration
- Visibility restoration
- Hash changes
- Popstate navigation
- Dynamic DOM and page-builder mutations

## Browser diagnostics

```javascript
window.SCLab.BiosignalProduction.status()
window.SCLab.BiosignalProduction.health()
window.SCLab.BiosignalProduction.repair()
window.SCLab.BiosignalProduction.open()
```

## WordPress health

```text
GET /wp-json/sc-lab/v1/compute/biomedical/biosignals/production-health
```

## FastAPI health

```text
GET /v1/biomedical/biosignals/production-health
```

## Responsible-use boundary

The production layer preserves the v0.23.0 research-only boundary.
It does not authorize diagnostic use, patient monitoring, alarm
generation, treatment decisions, or clinical interpretation.
