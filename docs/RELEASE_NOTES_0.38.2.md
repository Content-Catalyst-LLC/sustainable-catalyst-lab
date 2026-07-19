# Sustainable Catalyst Lab v0.38.2 Release Notes

## Public API, Webhooks, Embeds, and Research SDK

Sustainable Catalyst Lab v0.38.2 turns the governed research interoperability stack into a stable external integration surface. It exposes versioned discovery, scoped integration authentication, safe webhook operations, signed research embeds, and dependency-light SDKs while preserving workspace roles, hashes, provenance, and the v0.38.0–v0.38.1 handoff contracts.

## New capabilities

- Stable `/v1/public-research-api` catalog with contract and endpoint discovery.
- Protected integration routes using `X-SC-Lab-API-Key` or the existing server-side `X-SC-Lab-Key` bridge.
- Explicit `research:*`, `webhooks:*`, and `embeds:*` scopes.
- HTTPS-only webhook subscriptions with local, private, reserved, and credential-bearing destinations rejected.
- One-time webhook secret disclosure and deterministic HMAC-SHA256 event signatures.
- Durable webhook event and delivery records with event-ID idempotency and conflicting-retry detection.
- Optional guarded HTTPS dispatch with response status and bounded response excerpts.
- Signed, expiring research embed manifests limited to references and public metadata.
- Python, TypeScript, and browser embed SDK packages with no runtime dependencies.
- A WordPress Public Research Integration Studio for API discovery, webhook administration, event emission, delivery review, and embed creation.
- 79 registered Lab modules.

## Safety boundary

- Protected integration routes return a configuration error until a public or compute API key is configured.
- Webhook and embed signing requires a server-side signing secret.
- Outbound webhook delivery is disabled by default.
- Webhook URLs are re-resolved and revalidated immediately before dispatch.
- Public payloads reject secret, credential, token, executable, callback, raw-data, and restricted-data fields recursively.
- Embed manifests contain references and policy-approved metadata rather than restricted dataset bytes.
- Signing secrets are never returned by list or delivery endpoints.

## Compatibility

The cumulative DIRECT_BRIDGE_V26 installer accepts Sustainable Catalyst Lab repositories reporting v0.31.0 through v0.38.2 and preserves all earlier scientific-compute, collaboration, federation, publication, verification, interoperability, and typed-handoff contracts.
