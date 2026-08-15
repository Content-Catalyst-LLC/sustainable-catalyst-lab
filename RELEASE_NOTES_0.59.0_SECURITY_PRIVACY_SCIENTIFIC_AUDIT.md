# Sustainable Catalyst Lab v0.59.0 — Security, Privacy, Reproducibility & Scientific Audit

v0.59.0 is the pre-beta scientific governance and audit release. It builds on v0.58.0 compute hardening and the existing v0.39.1 encrypted-secret/privacy subsystem without changing the Lab navigation architecture.

## Added

- Recursive scientific threat-surface scanning for executable/callback fields and secret/credential leakage.
- Privacy findings that record paths/categories without echoing sensitive values.
- Data-minimization review for research datasets with explicit purpose and required-column evidence.
- Deterministic redacted research exports with source, redacted, and export hashes plus redaction manifests.
- Reproducibility auditing for v0.50 reproducible model packages and v0.57 scientific workflow run evidence.
- Tamper-evident v0.59 scientific audit reports.
- Contextual audit controls inside the existing Scientific Workflows workspace.
- Project `analysisPackets` integration for preserving audit evidence.

## Governance boundaries

Lab does not automatically certify research, publish results, delete source data, make high-stakes decisions, or execute arbitrary code as part of v0.59 auditing. A clean automated audit is evidence for review, not scientific certification.

## Compatibility

- Lab release: 0.59.0
- Platform compatibility: 1.0.0
- v0.58 compute hardening remains active.
- v0.57 Scientific Workflow Composer remains the scientific pipeline layer.
- v0.39.1 Security & Privacy Hardening remains the encrypted-secret, credential, replay-protection, audit-chain, and privacy-request foundation.
