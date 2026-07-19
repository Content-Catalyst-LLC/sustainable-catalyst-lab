# Institutional Administration, Identity, and Governance — v0.39.0

## Purpose

The institutional governance control plane records who may act, where authority applies, which research classifications and retention references govern a workspace, and when an action requires auditable approval.

## Core records

- Institutions and organizational units
- Human and credential-free service principals
- Institution, unit, and workspace role bindings
- Workspace governance profiles and classifications
- Retention-policy references
- Approval requests, immutable decisions, and hash-chained governance events

## Authority model

Roles progress from institution viewer through researcher, steward, approver, auditor, institution administrator, and institution owner. Bindings may be institution-, unit-, or workspace-scoped. The final active institution owner cannot be revoked.

## Release boundary

v0.39.0 does not issue credentials, store service-account secrets, exchange SSO tokens, rotate keys, or automate destructive deletion. Those controls are reserved for v0.39.1.
