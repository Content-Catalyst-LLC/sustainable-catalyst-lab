# Release Notes — Lab v0.159.0

## Integrated Scientific Review, Validation & Publication Gate

- Project-scoped integrated review dossiers.
- Evidence snapshots from v0.157 cross-study/meta-experiment and v0.158 replication-network layers.
- Ten explicit validation checklist classes covering provenance, methods, data, reproducibility, statistics, replication, contradictions, limitations, sign-off and publication artifacts.
- Review findings with severity, resolution and revision-action lineage.
- Human reviewer roles, approvals, revision requests, abstention and preserved dissent.
- Procedural readiness evaluation with explicit blockers.
- Controlled dossier state machine through review-complete and publication-ready.
- Publication-ready requires explicit human authorization and at least one recorded human approval.
- Publication packet is a handoff only; no automatic publication.
- Digest-verifiable review/publication manifests.
- v0.157.0.1 front-door authorization repair retained and extended to v0.159.0.


## Release engineering repair
The final builder closes SQLite connections on context exit across the v0.155.0-v0.159.0 persistent research managers, preventing file-descriptor exhaustion during cumulative validation and long-running service operation.
