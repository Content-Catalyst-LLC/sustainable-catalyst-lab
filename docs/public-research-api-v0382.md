# Public Research API v0.38.2

The stable `/v1` integration surface exposes public catalog and SDK discovery plus scoped, workspace-governed webhook and embed operations. Integration keys use `X-SC-Lab-API-Key`; the WordPress server proxy may use the existing `X-SC-Lab-Key` header. Actor identity uses `X-SC-Lab-Actor`.

Webhook endpoints must use credential-free HTTPS and may not target local, private, link-local, reserved, or non-global addresses. Destinations are re-resolved before dispatch. Subscription secrets are disclosed once and are deterministically derived from the server master signing secret. Event identifiers are idempotent: an identical retry returns the original deliveries, while a conflicting payload is rejected.

Outbound delivery is disabled by default. Signed embed manifests expire and contain public references and metadata only. Python, TypeScript, and browser SDK source packages are included under `sdk/`.
