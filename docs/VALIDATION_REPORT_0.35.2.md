# Sustainable Catalyst Lab v0.35.2 Validation Report

## Release

- Version: 0.35.2
- Name: Version History, Branching, Merge, and Conflict Resolution
- Registered Lab panels: 70
- Workspace database schema: 3

## Automated tests

- Current backend tests: 228 passed
- Retained scientific and instrumentation regressions: 33 passed
- Total: 261 passed
- Focused collaboration and version-control tests: 29 passed

All backend test files were validated in isolated application processes where needed so FastAPI lifespans, background queues, and temporary SQLite databases could not leak state between suites.

## Live proof

A governed publication scenario completed through the real workspace, review, and version-control managers:

1. Created a shared research workspace and role-scoped members.
2. Created an immutable baseline snapshot.
3. Created a publication branch and a divergent protected-main change.
4. Opened a three-way merge request and recorded a path-level conflict.
5. Resolved the conflict with a reviewer-authored custom scientific value.
6. Recorded a review assignment and approval decision.
7. Issued an immutable scientific sign-off.
8. Attached the signed approval to the protected merge.
9. Finalized a new merge snapshot retaining both parent lineages.

The resulting sign-off and snapshot hashes are 64-character SHA-256 values. The proof is included as `SUSTAINABLE_CATALYST_LAB_V0352_LIVE_PROOF.json`.

## Static validation

- Python files parsed: 124
- PHP files linted: 102
- JavaScript files syntax-checked: 112
- JSON documents parsed: 309
- JSON Schema documents validated: 218

## Release integrity

The final package is rebuilt after removing generated databases, caches, bytecode, WAL files, credentials, and Git metadata. The source inventory and release-manifest checks are verified during installation.
