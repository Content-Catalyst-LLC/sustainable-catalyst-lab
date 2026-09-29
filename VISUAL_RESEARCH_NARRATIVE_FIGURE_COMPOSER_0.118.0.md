# Lab v0.118.0 — Visual Research Narrative & Figure Composer

## Purpose

Lab v0.118.0 adds a reference-first visual research narrative layer over the publication-grade visualization stack introduced in v0.114–v0.117. It composes existing scientific figures, dashboards, small multiples, maps, and 3D/4D scenes into research narratives without changing the underlying scientific artifacts.

## Core objects

- visual research narrative
- section and narrative block
- immutable figure reference
- multi-panel figure plate
- declared caption package
- evidence-aware annotation layer
- methods/findings/evidence/citation link set
- provenance trace
- layout plan
- export plan
- publication package
- deterministic narrative revision snapshot
- Platform Core visual binding plan

## Supported narrative formats

Journal article, research report, technical memo, methods note, slide narrative, web story, and supplement.

## Scientific boundaries

The composer does not generate scientific conclusions, infer captions from unseen data, mutate figures, infer relationships, weight evidence, approve publication, submit to Core automatically, certify scientific validity, or determine truth. Visual prominence is not treated as evidentiary weight.

## Reproducibility

Every normalized narrative has a deterministic narrative hash. Figure references carry stable fingerprints, sections carry fingerprints, and revision snapshots record narrative, figure, and section hashes. Publication packages include provenance, layout, and export plans without automatically writing or publishing files.

## Visualization stack integration

- v0.114 publication design system remains the presentation authority.
- v0.115 advanced statistical figures remain authoritative for statistical graphics.
- v0.116 dashboards remain authoritative for linked interactive multi-view state.
- v0.117 remains authoritative for 3D/4D scientific scene geometry and rendering semantics.
- v0.118 composes those artifacts by reference.
