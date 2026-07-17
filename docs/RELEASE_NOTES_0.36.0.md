# Sustainable Catalyst Lab v0.36.0 Release Notes

## Scientific Artifact Repository and Data Federation

Sustainable Catalyst Lab v0.36.0 adds a governed repository and federation layer for scientific artifacts. Research teams can organize versioned artifacts into shared collections, bind repository records to the content-addressed transport store, export canonical manifests, register trusted institutional nodes, synchronize supplied manifests, and resolve cross-node conflicts without losing provenance or history.

## Capabilities

- Workspace-governed scientific artifact collections
- Immutable, versioned repository records with SHA-256 identities
- Optional binding to content-addressed Lab transport artifacts
- Transport-backed integrity verification and verification hashes
- Canonical collection manifests and manifest hashes
- Federated source registration with trust and conflict policies
- HTTPS-only metadata endpoint records
- Idempotent delta synchronization
- Imports, updates, unchanged records, tombstones, and cursors
- Conflict records with keep-local, accept-remote, retain-both, and dismiss resolutions
- Durable sync history and hashed repository timelines
- Workspace resource links for artifact collections and federated sources
- SQLite WAL persistence and explicit deployment-durability reporting
- Administrator-only WordPress proxy controls
- New Scientific Artifact Repository & Data Federation workspace
- 71 registered Lab panels

## Safety and governance

The federation coordinator does not execute arbitrary Python, shell commands, expressions, device instructions, or callbacks. It does not automatically fetch remote manifests. Authenticated operators or separately governed connectors submit canonical manifests. Existing workspace roles independently govern reading, registration, synchronization, source administration, conflict resolution, and archiving.

## Compatibility

The cumulative DIRECT_BRIDGE_V18 installer accepts Lab repositories reporting v0.31.0 through v0.36.0 and carries forward the complete distributed compute, workflow, campaign, model, collaboration, review, and version-history stack.
