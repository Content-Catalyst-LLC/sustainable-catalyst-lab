# Sustainable Catalyst Lab v0.28.2 — Reproducible Computational Runs

v0.28.2 freezes computational requests, outputs, environment fingerprints, package versions, checksums, warnings, and failure history into project-scoped reproducible-run records. Runs can be verified, rerun, compared within tolerances, and exported as portable bundles.

The browser remains the project-record store. The Python Compute Core supplies governed environment fingerprints, manifest verification, and numerical comparison; it does not become a permanent project database.
