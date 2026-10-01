# Sustainable Catalyst Lab v0.154.0

## Reproducible Protocol & Computational Notebook Workspace

### Added

- Server-backed project protocols.
- Immutable protocol revision history.
- Server-backed project computational notebooks.
- Immutable notebook revision history.
- Typed notebook cells for notes, parameters, registered compute calls, result references, figure references, protocol references, and 4D workspace references.
- Explicit execution of registered Compute Core calls from notebook drafts.
- Binding to v0.153.0 4D workspace assets.
- Content-digest compute-result references when a compute response does not expose a durable repository identifier.
- Reproduction-manifest generation and SHA-256 verification.
- Archive-with-history semantics for protocols and notebooks.

### Preserved

- v0.152.0.13 visual/layout recovery.
- Interactive 4D response field.
- Response-surface, uncertainty, sensitivity, and ensemble workflows.
- Linked scientific views.
- Browser-local scene migration compatibility.
- v0.153.0 project 4D workspace assets, revisions, forks, lineage, and comparisons.
- PHP output-safety release gate.

### Scientific/runtime boundaries

- No arbitrary code execution.
- No automatic compute execution.
- No automatic Platform Core submission.
- No automatic scientific-validity determination.
- Restoring a notebook revision does not rerun computation.
