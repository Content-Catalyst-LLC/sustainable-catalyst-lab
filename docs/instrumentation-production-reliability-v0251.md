# Instrumentation Production Activation and Interface Reliability

Sustainable Catalyst Lab v0.25.1 activates and protects the v0.25.0
Laboratory Data and Instrumentation Platform in public WordPress and
application contexts.

## Activation

The production class explicitly enqueues the v0.25.0 engine and style,
then loads a dedicated v0.25.1 reliability runtime and stylesheet.
This removes dependence on page timing or a single template path.

## Canonical repair

The runtime identifies one canonical module using:

```text
data-lab-module="laboratory-data-instrumentation"
data-module-panel="laboratory-data-instrumentation"
```

It guarantees one canonical root:

```text
data-laboratory-instrumentation-root
```

It can create a missing panel, create or relocate a missing root, remove
duplicate roots, preserve an already rendered root, clear stale v0.25.0
markers or placeholders, and rerun the deterministic v0.25.0 renderer.

## Recovery triggers

Recovery runs after startup, navigation clicks, Lab module-open events,
pageshow restoration, focus, visibility restoration, popstate, online
reconnection, resize, orientation changes, hash changes, and relevant DOM
mutations.

## Browser API

```javascript
window.SCLab.InstrumentationProduction.status()
window.SCLab.InstrumentationProduction.health()
window.SCLab.InstrumentationProduction.repair()
window.SCLab.InstrumentationProduction.open()
```

## Health routes

```text
GET /wp-json/sc-lab/v1/compute/instrumentation/production-health
GET /v1/instrumentation/production-health
```

## Preserved contract

The release preserves 48 methods, 48 benchmarks, eight categories, nine
record types, eight connection profiles, eight quality flags, record and
manifest fingerprints, measurement ingestion, custody verification, and
Arduino/Raspberry Pi examples.

## Boundaries

The production layer does not grant automatic local-device access. It does
not claim clinical instrumentation status or regulated release authority.
Manual and file-based workflows remain local-first, and hardware bridges
require explicit user-controlled configuration.
