# Sustainable Catalyst Lab v0.38.2 Validation Report

## Release

**Public API, Webhooks, Embeds, and Research SDK**

## Backend validation

- 325 current backend tests collected.
- 12 focused v0.38.2 API, authentication, role-boundary, URL-safety, signed-webhook, contract, embed, SDK, WordPress-bridge, dispatch, and idempotency tests passed.
- 24 retained v0.38.0–v0.38.1 interoperability and typed-handoff tests passed.
- 32 additional security, workspace, publication, and public-reproduction release-critical tests passed.
- 33 retained scientific-domain and instrumentation regression tests passed.
- 58 standalone compute, artifact, benchmark, campaign, dataset, design-study, and dispatcher tests passed.
- 159 tests were executed and passed across the release-critical, retained-domain, and standalone validation groups.

The retained monolithic backend process can remain open after completed assertions because several FastAPI, queue, and worker suites retain application lifespans or worker state. Release validation therefore uses fresh per-suite processes and isolated database paths, consistent with the established Lab validation method.

## Static and contract validation

- 145 Python files parsed.
- 111 PHP files passed syntax checks.
- 122 JavaScript files passed syntax checks.
- 428 JSON documents parsed.
- 310 JSON Schemas passed Draft 2020-12 meta-validation.
- The v0.38.2 webhook subscription, event, delivery, embed, and SDK records passed instance validation against their published contracts.
- 79 registered Lab modules and the public integration route aliases were confirmed.

## Live integration proof

The isolated proof completed:

1. Workspace and editor membership creation.
2. Public API catalog and SDK manifest hashing.
3. HTTPS webhook registration with one-time secret disclosure.
4. Canonical event creation and HMAC-SHA256 delivery signing.
5. Event-ID retry with the original delivery returned idempotently.
6. Conflicting retry rejection.
7. Signed, expiring embed creation and verification.
8. Recursive restricted-field rejection.

The proof contains no signing secret, API key, credential, restricted dataset byte, or executable payload.

## Security and governance assertions

- Protected routes fail closed when no API key is configured.
- WordPress uses the existing authenticated server-side proxy rather than exposing integration keys in browser code.
- Workspace minimum roles are enforced centrally for read, administration, event emission, dispatch, and embed creation.
- Private, loopback, link-local, reserved, local-domain, credential-bearing, and non-HTTPS webhook destinations are rejected.
- Webhook destinations are re-resolved immediately before outbound dispatch.
- Outbound webhook delivery is disabled by default.
- Webhook signing secrets are disclosed once and omitted from subsequent records.
- Public payloads reject secret, credential, token, code, callback, raw-data, and restricted-data fields recursively.
- Duplicate event identifiers are idempotent only when their canonical request content matches.
- Signed embed manifests expire and are integrity-checked before use.

## Installer validation

The cumulative `DIRECT_BRIDGE_V26` installer passed isolated installation proofs from both supported recent baselines:

- Packaged v0.38.1 → v0.38.2: 62 files changed, 2,381 insertions, and 59 deletions.
- Packaged v0.38.0 → v0.38.2: 79 files changed, 3,975 insertions, and 61 deletions.

Each proof verified the complete source checksum inventory, created a timestamped safety backup, installed the cumulative payload, validated the 1,122-file release manifest, passed the 36 focused v0.38.0–v0.38.2 tests, created the release commit, and generated WordPress, Compute Core, complete-source, Python SDK, TypeScript SDK, and browser-embed packages. Push behavior was intentionally disabled during the isolated proofs.

## Archive integrity

- The cumulative upgrade contains one intended release root and a complete checksum inventory for every source file.
- WordPress, Compute Core, complete-source, Python SDK, TypeScript SDK, browser-embed, and full release-bundle archives pass ZIP CRC validation.
- Every distributable archive contains one intended top-level root.
- Git metadata, caches, bytecode, local databases, WAL/SHM files, worker credentials, and generated writable state are excluded.
