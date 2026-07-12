# Sustainable Catalyst Lab Architecture — v0.1.1

## Application boundary

The WordPress plugin supplies the public Lab interface, source proxy, transient caching, project export, and routes into larger Sustainable Catalyst applications. Computation currently runs in browser modules, while external scientific records are normalized through WordPress REST endpoints.

## Scientific workflow

```text
Observe → Save evidence → Form hypothesis → Calculate or experiment → Decide → Document
```

The v0.1.1 interface expresses this workflow through grouped navigation, the project command bar, the signal board, and the interactive traceability map.

## Project model

Projects remain browser-local and use the same storage keys as v0.1.0. The model normalizes previous records into schema version 0.1.1 and preserves evidence, experiments, hypotheses, decisions, notes, calculations, documents, map states, and activity.

## Application routing

Lab exposes focused modules and links to the full Prototyping Workbench, Decision Studio, and Site Intelligence routes configured in WordPress settings. Feed records with coordinates can be routed to Site Intelligence with latitude, longitude, source, and record identifiers.

## Future persistence

A later Platform Core or FastAPI service can persist the same project contract, add authenticated collaboration, index technical files, and provide larger numerical or geospatial workloads without redesigning the browser interface.
