# Lab v0.105.0 — Platform Core v3 Canonical Research Object Mapping

Lab v0.105.0 adds the first canonical object bridge between Sustainable Catalyst Lab and Platform Core v3.0.0.

## Architectural rule

Platform Core remains reference-first. Lab remains authoritative for scientific content, computation, experiment state, data payloads, and scientific artifacts. v0.105.0 maps identity and lineage metadata into Core; it does not duplicate scientific payloads in Core and does not automatically submit remote writes.

## Canonical object families

The mapping catalog covers 20 Lab object families: dataset, observation-set, workflow, workflow-run, experiment, campaign, model, surrogate-model, artifact, evidence-record, citation-set, publication, reproducibility-package, manuscript, decision-packet, scenario, indicator-set, research-brief, workspace-snapshot, and scientific-figure.

`evidence-record` maps to Core object type `evidence`. Scientific figures receive first-class object identity now, while the dedicated Core visual-binding bridge remains scheduled for Lab v0.109.0.

## Core target

Generated object bindings target:

`POST /v1/research/unified-runtime/object-bindings`

The Core router expects a request body shaped as `{"data": <binding>}`. Lab generates both the binding and the exact request envelope but does not submit it automatically.

## Stable object references

When an existing object reference is not supplied, Lab creates a deterministic reference of the form:

`lab:<canonical-type>:<url-escaped-local-id>`

Version references are derived from the object reference when a version label is provided. Optional SHA-256 content hashes can be supplied directly or calculated from an explicitly supplied content object; the content itself is not included in the Core binding.

## Legacy bridge

The retained v0.38.1 typed handoff contract can now be translated into a Core v3 object binding while preserving the legacy resource SHA-256, source contract, handoff identity, source/target product metadata, and provenance.

## Deferred specialized bindings

- Execution binding: Lab v0.107.0
- Visual binding: Lab v0.109.0
- Scholarly/reproducibility package binding: Lab v0.110.0

These are intentionally not inferred in v0.105.0.
