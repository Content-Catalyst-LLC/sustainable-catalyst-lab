# Sustainable Catalyst Lab v0.161.0

## Research Program & Portfolio Orchestration

v0.161.0 builds directly on Computational Research Operating System II v0.160.0 and adds a governed coordination layer for multiple Research OS projects.

Primary capabilities:

- explicit research program registry
- explicit research portfolio registry
- Research OS project membership by reference
- program workstreams and project roles
- program objectives and project-to-objective allocations
- program milestones and evidence references
- human-controlled program lifecycle
- human-controlled portfolio lifecycle
- program command center
- portfolio command center
- immutable program/portfolio snapshots
- digest-verifiable manifests
- cumulative preservation of v0.153.0 through v0.160.0

Scientific/governance boundaries:

- no automatic project ranking
- no automatic funding allocation
- no automatic resource allocation
- no automatic scientific-validity inference
- no automatic project creation or execution
- no automatic publication
- Research OS v0.160.0 remains project-lifecycle authority
- Workspace remains execution authority
- Platform Core remains canonical object authority

Backend persistence is included and uses a separate SQLite database with WAL mode and explicit connection closure.
