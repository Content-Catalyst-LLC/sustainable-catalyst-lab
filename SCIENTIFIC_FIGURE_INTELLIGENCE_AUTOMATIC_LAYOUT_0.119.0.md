# Lab v0.119.0 — Scientific Figure Intelligence & Automatic Layout

This release adds deterministic, explainable figure layout intelligence to Sustainable Catalyst Lab. It consumes declared figure metadata and produces reproducible layout plans for axes, legends, panels, annotations, responsive breakpoints, print profiles, accessibility, and publication quality.

## Scientific boundary

The layout engine does not inspect unseen datasets, infer axis domains or scales, transform data, alter statistical semantics, drop annotations or series, reorder scientific panels, assign evidentiary weight, infer claims, certify scientific validity, or submit to Platform Core automatically.

## Major capabilities

- Axis label strategy without domain/scale mutation
- Legend placement without series reordering or entry deletion
- Panel grid packing without panel omission or reordering
- Annotation collision displacement with unresolved-collision reporting
- Responsive reflow preserving panel order and scale semantics
- Print/publication layout planning
- Figure quality and accessibility audits
- Explainable layout reasons
- Deterministic layout snapshots and hashes
- Reference-first Platform Core visual-binding plans
