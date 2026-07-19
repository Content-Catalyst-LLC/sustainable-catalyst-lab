# Sustainable Catalyst Lab v0.38.1 Validation Report

## Release

**Typed Cross-Product Research Handoffs**

## Backend validation

- 313 backend tests collected across 41 files.
- The complete suite reached the 100% assertion marker with no reported failures.
- 11 focused v0.38.1 adapter, route-planning, persistence, safety, profile-aware sealing, and FastAPI tests passed.
- 13 retained v0.38.0 interoperability tests passed independently.
- As in v0.38.0, the monolithic pytest process can remain open after assertions because retained FastAPI and worker suites keep application lifespans alive. Release validation uses a clean timeout only after the complete 100% marker appears.

## Live typed-handoff proof

The live proof completed:

1. Workspace creation.
2. Lab and Decision Studio profile registration.
3. Executable adapter resolution.
4. Dataset route planning with contract inference.
5. Target-binding normalization for Decision Studio.
6. SHA-256 route and plan identity generation.
7. Governed handoff creation and profile-aware sealing.
8. Canonical v0.38.0 interoperability bundle export.

The proof contains no secrets, credentials, executable payloads, callbacks, or restricted dataset bytes.

## Static and contract validation

- 140 Python files parsed.
- 110 PHP files passed syntax checks.
- 120 JavaScript files passed syntax checks.
- 412 JSON documents parsed.
- 300 JSON Schemas passed Draft 2020-12 schema checks.
- 10 explicit template HTML identifiers were checked with no duplicates.
- 13 product adapters and 83 Lab outbound routes were confirmed.
- 78 registered Lab modules are expected in the release manifest.

## Security and governance assertions

- Product adapters plan locally and do not call remote systems.
- Every route has a deterministic SHA-256 identity.
- Every plan records source and target adapter hashes.
- Unsupported source, target, entity, and contract combinations are rejected.
- Unsafe callback, credential, executable, and embedded-byte fields remain rejected by the governed interoperability engine.
- Profile-aware creation requires both profiles and editor authority before sealing.
- Persisted handoffs retain the v0.38.0 envelope, receipt, workspace, and immutable-history guarantees.

## Installer proof

A clean packaged v0.38.0 source repository was upgraded with the standalone DIRECT_BRIDGE_V25 installer using `--no-push`.

- Safety backup created successfully.
- Full source checksum inventory verified before and after installation.
- Manifest, route aliases, file hashes, Python, JSON, PHP, and JavaScript validation passed.
- 11 v0.38.1 tests and 13 retained v0.38.0 interoperability tests passed from the installed repository.
- Release commit created: 46 files changed, 1,641 insertions, and 60 deletions.
- WordPress, Python Compute Core, and complete-source deployment archives were generated successfully.
