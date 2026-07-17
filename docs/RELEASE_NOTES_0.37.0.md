# Sustainable Catalyst Lab v0.37.0 Release Notes

## Reproducibility Packages and Research Publication Studio

Sustainable Catalyst Lab v0.37.0 adds a workspace-governed research-publication layer above the existing shared-workspace, scientific-review, artifact, workflow, model, federation, and offline-field infrastructure.

### Reproducibility packages

- Draft package records for methods, environments, citations, provenance, and hashed resource references.
- Canonical immutable manifests and SHA-256 package identities.
- Package verification receipts that independently recompute the manifest and package hashes.
- Sealed-package immutability; later changes require a new package version rather than history rewriting.
- Logical bundles that reference verified artifacts and datasets without embedding restricted data bytes.

### Research publication studio

- Publication records tied to sealed reproducibility packages.
- Publication-ready Markdown, escaped HTML, JSON, README, environment, methods, provenance, manifest, and `CITATION.cff` outputs.
- Stable file hashes and a complete export hash.
- Reviewer readiness restricted to verified packages with authors, abstracts, and sections.
- Publication restricted to workspace administrators or owners and matched against an existing signed scientific approval.
- Canonical publication URI and immutable publication event history.

### Security boundaries

The release rejects arbitrary code, shell commands, executable expressions, unrestricted callbacks, secrets, credentials, private keys, binary payload fields, and embedded raw dataset bytes. WordPress forwards stable logged-in actor identity through the server-side compute proxy without exposing the compute API key.

### Interface and deployment

- New **Reproducibility Packages & Research Publication Studio** panel.
- 74 registered Lab panels.
- SQLite WAL publication storage with explicit instance-local or persistent-disk status.
- No paid Render disk is added by default.
