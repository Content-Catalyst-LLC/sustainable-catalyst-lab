# Sustainable Catalyst Lab v0.26.3.2 — Installation, Version, and Asset Integrity

This release adds a non-destructive integrity layer. It does not rewrite the legacy `asset_version()` method.

## Guarantees

- The canonical plugin identity is `sustainable-catalyst-lab/sustainable-catalyst-lab.php`.
- Every Lab JavaScript and CSS URL receives a SHA-256-derived cache token.
- A generated build manifest records the source commit, build fingerprint, and critical file hashes.
- `/wp-json/sc-lab/v1/runtime/health` reports plugin, header, panel-runtime, compute, manifest, route, and asset state together.
- Duplicate Lab plugin folders and partial upgrades produce explicit diagnostics.
- The installer is idempotent and can finish an interrupted v0.26.3.2 installation.

## Rollback

Use the timestamped safety ZIP created before the patch, or upload the previous verified WordPress plugin ZIP. Do not delete the Git repository before preserving a backup. WordPress settings, uploads, and the Python Compute Core database are not removed by the plugin rollback.
