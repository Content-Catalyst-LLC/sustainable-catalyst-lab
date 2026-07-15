# Sustainable Catalyst Lab v0.28.0 — Project and Workspace Data Architecture

The Lab now uses one compatibility-preserving project model across all laboratories. Existing browser projects are normalized in place from the v0.20.0 baseline while unknown fields and domain-specific collections are retained.

## Canonical records

Experiments, datasets, models, calculations, notes, sources, reports, and compute jobs receive shared identifiers, titles, statuses, timestamps, collection metadata, and schema versions. Domain-specific records remain available through their original collections.

## Workspace services

- Immediate autosave through the existing local project store
- Project-wide record index and search
- Record relationships
- Manual checkpoints with bounded retention
- Project bundle import and export
- Migration history and storage diagnostics
- Safe Start memory-only operation

Server-backed project persistence is deliberately deferred. v0.28.0 defines the boundary and reports `serverBacked: false`; it does not silently send project content to WordPress or the Python Compute Core.
