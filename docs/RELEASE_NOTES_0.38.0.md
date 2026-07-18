# Sustainable Catalyst Lab v0.38.0 Release Notes

## Sustainable Catalyst Research Interoperability Layer

Sustainable Catalyst Lab v0.38.0 adds typed, workspace-governed exchange between Lab and other Sustainable Catalyst products or institutional research systems.

## New capabilities

- Product interoperability profiles with supported contracts, capabilities, lifecycle state, and immutable profile hashes.
- Contract-version and capability negotiation before a handoff is sealed.
- Canonical `sc-research-handoff-envelope/0.38.0` documents.
- Typed handoffs for datasets, workflows, runs, experiments, models, artifacts, publications, reproducibility packages, manuscripts, decision packets, evidence records, and related governed research entities.
- SHA-256 identities for resources, envelopes, bundles, profiles, negotiations, receipts, and events.
- Hash-verified and idempotent imports.
- Accepted, rejected, and needs-changes receipts with optional HMAC-SHA256 signatures.
- Retained withdrawal records and complete workspace timelines.
- Compatibility profiles and aliases for cross-product handoff routing.
- A dedicated **Research Interoperability** WordPress operations workspace.
- **77 registered Lab modules.**

## Final governance hardening

- Profile identifiers cannot be reassigned across workspace boundaries.
- Source and target profiles must match the products declared by the handoff.
- Draft handoffs cannot receive final acceptance or rejection receipts.
- Accepted handoffs remain immutable and must be superseded rather than withdrawn.

## Safety boundary

The interoperability layer does not execute arbitrary code, embed restricted dataset bytes, expose credentials, or invoke unrestricted callbacks. It exchanges metadata, references, hashes, provenance, compatibility declarations, and governed receipts.

## Compatibility

The cumulative V24 installer accepts repositories reporting v0.31.0 through v0.38.0 and preserves all earlier release contracts.
