# Scientific Workflow Orchestration and Dependency Graphs v0.32.0

Sustainable Catalyst Lab v0.32.0 adds a persistent orchestration layer above the distributed dispatcher. It turns registered scientific methods into typed workflow nodes connected by explicit dependencies.

## Definition contract

A workflow definition includes a stable identifier, project, typed nodes, dependencies, registered methods, governed requests, resource requirements, artifact declarations, and optional result bindings. The orchestrator normalizes the definition and calculates a SHA-256 `definitionHash`.

Validation rejects duplicate node IDs, missing methods, unknown dependencies, self-dependencies, invalid bindings, oversized graphs, and dependency cycles. A successful definition records a deterministic topological order plus its entry and terminal nodes.

## Run lifecycle

Starting a run creates an immutable snapshot of the normalized definition. Root nodes are submitted to the persistent dispatcher immediately. Other nodes remain `waiting` until all dependencies are `completed`.

The orchestrator reconciles dispatcher queue records into workflow node states:

- `queued`
- `running`
- `completed`
- `failed`
- `skipped`
- `cancelled`

When a node completes, the orchestrator stores its result and schedules newly ready downstream nodes. A terminal dispatcher failure fails the node and blocks downstream work. Cancelling a workflow also cancels active dispatcher queue items.

## Result and artifact handoffs

Bindings use three explicit fields: `fromNode`, `sourcePath`, and `targetPath`. They copy bounded JSON values from completed dependency results into a downstream request. No expressions or executable code are evaluated.

Artifact IDs discovered in upstream results are appended to downstream `artifactInputs` with their source node and workflow role. The existing artifact transport and active-lease access controls remain authoritative.

## Persistence and provenance

Workflow definitions, runs, node runs, and events use a dedicated SQLite WAL database. Every run retains:

- workflow and project IDs
- definition hash and immutable definition snapshot
- run inputs and context
- node definitions and dispatcher queue IDs
- results, errors, and timestamps
- a complete workflow event timeline

The default Render blueprint remains free of a paid disk declaration. Health responses explicitly report whether workflow persistence is instance-local or backed by a mounted persistent disk.
