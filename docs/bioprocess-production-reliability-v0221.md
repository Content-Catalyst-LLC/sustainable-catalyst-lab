# Bioprocess Production Activation and Interface Reliability

Sustainable Catalyst Lab v0.22.1 hardens the v0.22.0
Biotechnology and Bioprocess Engineering workspace for production
WordPress rendering.

## Ownership model

The v0.22.0 runtime remains the only calculator, simulation, batch,
and benchmark engine. v0.22.1 does not duplicate scientific
calculations. It owns production activation and interface repair.

## Reliability behavior

The production runtime:

- Loads the v0.22.0 engine and interface assets unconditionally on
  public Lab pages
- Finds and normalizes the canonical bioprocess panel
- Restores both `data-lab-module` and `data-module-panel`
- Creates a missing root mount
- Removes duplicate root mounts
- Clears stale `data-sc-bpe-version` markers
- Clears non-rendered placeholder content
- Retries rendering after startup, navigation, page restoration,
  hash changes, module-open events, and dynamic DOM changes
- Exposes explicit open and repair controls
- Reports detailed browser health state
- Improves mobile button, control, table, tab, and chart behavior

## Browser API

```javascript
window.SCLab.BioprocessProduction.status()
window.SCLab.BioprocessProduction.health()
window.SCLab.BioprocessProduction.repair()
window.SCLab.BioprocessProduction.open()
window.SCLab.BioprocessProduction.scheduleRepair()
```

## WordPress health endpoint

```text
GET /wp-json/sc-lab/v1/compute/bioprocess/production-health
```

## FastAPI health endpoint

```text
GET /v1/bioprocess/production-health
```

## Expected health contract

```json
{
  "ok": true,
  "status": "ready",
  "release": "0.22.1",
  "engineRelease": "0.22.0",
  "methodCount": 48,
  "benchmarkCount": 48,
  "categoryCount": 8
}
```

## Preserved scientific contract

- 48 bioprocess methods
- 48 deterministic benchmarks
- 8 method categories
- Batch, fed-batch, and continuous reactor simulations
- CSV batch analysis
- v0.21.3 validation and provenance handoffs
