# Sustainable Catalyst Lab v0.32.0 Release Notes

## Scientific Workflow Orchestration and Dependency Graphs

v0.32.0 introduces typed, persistent scientific workflows above the existing queue, worker, artifact, and dispatcher-operations layers.

### Added

- Directed acyclic workflow definitions and graph validation
- Stable definition fingerprints and immutable run snapshots
- Persistent workflow, run, node, and event records
- Parallel scheduling of independent ready nodes
- Dependency-aware downstream scheduling
- Safe result-path bindings into downstream requests
- Automatic dependency-artifact propagation
- Node-level dispatcher queue identifiers and state reconciliation
- Run completion, failure, blocking, cancellation, and timelines
- FastAPI workflow health, policy, validation, definition, run, reconciliation, cancellation, and timeline routes
- Administrator-only WordPress workflow proxies
- Scientific Workflows operations panel
- v0.32.0 workflow schemas and policy contract
- Deployment settings for workflow persistence and capacity

### Boundaries

- Only registered compute methods may execute.
- Workflows cannot contain arbitrary Python, shell commands, or callback URLs.
- Conditional branching and partial-run recovery are reserved for v0.32.1.
- A mounted persistent disk remains optional and is not added to the default Render blueprint.
