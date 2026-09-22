# Deploy Lab Backend v0.122.0

Upload `sustainable-catalyst-lab-backend-v0.122.0.zip` and `upgrade_lab_backend_v0_122_0_contabo.sh` to `/tmp` on the Lab VPS, then run the upgrade script. The script preserves the compose file, `.env.production`, and compose-managed data volume, rebuilds the Lab container, checks v0.121/v0.122 health, verifies Platform Core >=3.0.0, and exercises Bayesian Workbench fixtures. Total application route count is informational only.
