# Lab v0.135.8.1 — Graph Studio Canonical Runtime & Interface Recovery

## Purpose

v0.135.8.1 repairs the accumulated Graph Studio presentation stack. It makes one canonical runtime the presentation owner for the scientific figure and the v0.135.1–v0.135.8 research surfaces.

## Canonical research views

Figure, Analysis, Provenance, Scene, Compare, Session, Narrative, and Review are mounted as mutually exclusive research views. Only one view is active at a time. View selection, layout, camera state, and focus are presentation state and never mutate scientific objects.

## Compatibility adapters

Historical v0.75–v0.88 visualization controls remain available for compatibility, but they are moved into a collapsed Advanced renderer & capability controls drawer. They do not own the primary Graph Studio stage. The canonical runtime records 13 isolated capability adapters: binding, adaptive rendering, scene engine, 4D state, linked views, spatial/raster, markup, uncertainty, provenance, GPU, WebGL2, WebGPU, and advanced 3D.

## Identity recovery

The public Graph Studio experience identifies as Lab v0.135.8.1. Runtime subsystem 0.26.3.1 remains an internal compatibility implementation detail rather than the public release identity.

## Scientific boundaries

The repair changes presentation ownership only. It does not infer joins, identities, causality, evidence weight, validity, truth, claim status, or Platform Core submissions. Existing v0.135.1–v0.135.8 scientific/reference contracts are retained.
