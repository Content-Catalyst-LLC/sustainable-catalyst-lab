# Sustainable Catalyst Lab v0.32.1 Release Notes

## Workflow Checkpoints, Conditional Execution, and Partial Recovery

v0.32.1 adds durable recovery semantics to the v0.32.0 scientific workflow engine.

### Added

- Declarative conditions over run inputs, run context, and prior node state/results
- Nested `all`, `any`, and `not` condition groups with bounded operators
- Explicit conditional skip state, reason, detail, and timeline records
- Persistent checkpoint history and latest-checkpoint pointers
- Checkpoint hashes, artifact references, progress, messages, and sources
- Automatic checkpoint capture from dispatcher result envelopes
- Recovery planning for failed and operator-selected branches
- Downstream dependency closure and successful-node reuse
- New recovery runs with source lineage and generation tracking
- Checkpoint-aware resumed workloads
- Administrator recovery, restart, checkpoint-listing, and checkpoint-recording routes
- Expanded Scientific Workflows operations interface
- Workflow registry schema migration from version 1 to version 2
- v0.32.1 workflow, run, checkpoint, recovery-plan, and policy contracts

### Boundaries

- Conditions cannot execute code.
- Recovery creates a new run instead of mutating history.
- Only terminal runs may be recovered.
- Only registered compute methods may execute.
- A persistent disk remains optional in the default Render blueprint.
