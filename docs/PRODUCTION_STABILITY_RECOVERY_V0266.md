# Production Stability and Recovery — v0.26.6

Sustainable Catalyst Lab v0.26.6 adds a production reliability layer above the isolated single-panel lifecycle.

## Runtime protection

- Browser DOM, storage, JavaScript heap-growth, long-task, and runtime-error budgets.
- Early project-storage validation before the project model initializes.
- Corrupt or oversized project JSON is quarantined in session storage instead of silently discarded.
- `?sc_lab_safe=1&sc_lab_recovery=1` starts an in-memory project lifecycle without reading or modifying persisted projects.
- Active Python Compute Core job identifiers survive page reloads and are reconciled with the backend.
- Online/offline and backend-interruption recovery includes automatic retry and visible state.
- Incident exports exclude project contents and capture only runtime, performance, errors, source state, active job identifiers, and environment diagnostics.

## Production dashboard

Open **Settings → Lab Production Readiness** to run an isolated lifecycle audit or a repeated switching stress test. The runner cycles through core Observe, science, engineering, and microbiology modules in same-origin frames and records load failures, node peaks, storage footprint, errors, long tasks, and available heap measurements.

## Safe Start

```
https://sustainablecatalyst.com/lab/?sc_lab_safe=1&sc_lab_recovery=1
```

Safe Start always opens Overview and keeps project reads and writes in memory for that browser lifecycle.

## Runtime API

```javascript
window.SCLabProductionV0266.status()
window.SCLabProductionV0266.incident()
window.SCLabProductionV0266.exportIncident()
window.SCLabProductionV0266.checkBackend(true)
window.SCLabProductionV0266.restoreJobs()
```

## Server health

```
/wp-json/sc-lab/v1/production/v0266/health
```
