# Scientific Model Registry and Environment Reproduction — v0.34.0

Sustainable Catalyst Lab v0.34.0 introduces a durable scientific model registry with immutable semantic versions, reproducible environment locks, promotion and deprecation governance, and portable reproduction manifests.

## Added

- SQLite-WAL model, version, environment, alias, and event registries.
- Immutable model versions with canonical SHA-256 model hashes.
- Runtime, operating-system, architecture, container, dependency, source-revision, and build environment capture.
- Dependency version and optional artifact-hash locking.
- Environment deduplication through stable lock hashes.
- Draft, candidate, production, deprecated, and archived channels.
- Candidate and production aliases with explicit operator reasons.
- Required deprecation reasons and preserved event histories.
- Portable reproduction manifests and cryptographic verification.
- Environment-drift comparison for runtime, system, container, and dependency changes.
- Authenticated FastAPI routes and administrator-only WordPress proxies.
- A dedicated Scientific Model Registry panel, bringing Lab to 65 registered panels.

## Security

The registry does not execute model code. Arbitrary Python, shell commands, callbacks, and executable payloads are rejected by design. Model references remain limited to registered methods, saved workflows, governed surrogates, calibrated models, and retained artifact records.

## Deployment

The default Render blueprint stores the registry at `/app/data/sc-lab-model-registry.sqlite3` and reports whether storage is instance-local or backed by an optional persistent disk.


## Reference validation

Unknown registered compute methods and unknown saved workflows are rejected before validation or registration. Environment IDs are immutable and cannot be reused for a different dependency/runtime lock.
