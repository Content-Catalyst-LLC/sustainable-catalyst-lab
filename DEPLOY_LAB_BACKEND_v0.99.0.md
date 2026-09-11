# Deploy Sustainable Catalyst Lab backend v0.99.0

This release adds Carbon & Nature Intelligence v0.16.0 — Verification Evidence Ledger. It is an application-code upgrade only: no database migration and no new credential are required.

Upload `sustainable-catalyst-lab-backend-v0.99.0.zip` and `upgrade_lab_backend_v0_99_0_contabo.sh` to `/tmp` on the Contabo VPS, then execute the upgrader. The script backs up the current backend, preserves `/opt/sustainable-catalyst/lab/.env.production` and the existing Compose configuration, replaces backend application code, rebuilds `sc-lab`, and validates the v0.16.0 health, ledger, chain-check, and retained MRV endpoints.

The deployment does not rename or recreate a data volume. Existing volume behavior remains controlled by the live Compose file.
