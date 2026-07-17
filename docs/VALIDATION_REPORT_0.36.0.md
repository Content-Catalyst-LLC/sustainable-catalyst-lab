# Sustainable Catalyst Lab v0.36.0 Validation Report

## Release

- Version: 0.36.0
- Name: Scientific Artifact Repository and Data Federation
- Registered Lab panels: 71
- Artifact repository database schema: 1

## Automated tests

- Current backend tests: 238 passed
- Retained scientific and instrumentation regressions: 33 passed
- Total: 271 passed
- Focused artifact repository and federation tests: 10 passed

The backend matrix was validated in isolated application processes where necessary so persistent queues, FastAPI lifespans, and temporary SQLite databases could not leak state between suites.

## Live proof

A governed federation scenario completed through the real workspace, artifact transport, and scientific artifact repository managers:

1. Created a shared research workspace with owner, reviewer, and contributor roles.
2. Created a workspace-governed artifact collection.
3. Uploaded a real JSON dataset into the content-addressed artifact transport store.
4. Registered the transport artifact in the scientific repository.
5. Verified its byte hash and generated a verification hash.
6. Exported a self-verifying canonical collection manifest.
7. Registered a strict federated institutional source.
8. Imported a remote artifact through a verified manifest.
9. Replayed the same manifest and recorded an idempotent unchanged result.
10. Submitted a divergent remote version, recorded a conflict, and resolved it with the governed retain-both policy.
11. Verified SHA-256 event and synchronization hashes across the retained timeline.

The proof is included as `SUSTAINABLE_CATALYST_LAB_V0360_LIVE_PROOF.json`.

## Installer proofs

The packaged DIRECT_BRIDGE_V18 ZIP completed both supported installation scenarios:

- Current-baseline v0.35.2 → v0.36.0 installation passed
- Historical v0.31.1 → v0.36.0 cumulative installation passed

Both runs verified all 949 source checksums, created timestamped safety backups, produced release commits, skipped network push under test mode, and generated the WordPress, backend, and source deployment archives.

## Static validation

- Python files parsed: 126
- PHP files linted: 103
- JavaScript files syntax-checked: 113
- JSON documents parsed: 326
- JSON Schema documents validated: 232
- YAML deployment files parsed: 1

## Release integrity

- Registered Lab panels: 71 unique module routes
- Critical integrity hashes: 498
- Clean source-payload files: 949
- Generated databases, credentials, caches, bytecode, WAL files, and Git metadata: 0


The final package is rebuilt after removing generated databases, caches, bytecode, WAL files, credentials, and Git metadata. The installer verifies every source-payload checksum before modifying a repository.
