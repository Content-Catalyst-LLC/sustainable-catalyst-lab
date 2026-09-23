# Deploy Lab backend v0.135.2

Upload `sustainable-catalyst-lab-backend-v0.135.2.zip` and `upgrade_lab_backend_v0_135_2_contabo.sh` to `/tmp`, then run the upgrade script on the Contabo host. The deployer preserves `backend/data`, the production environment and compose-managed volumes, validates retained v0.135.1, verifies Platform Core >=3.0.0, and exercises real v0.135.2 graph behavior. The application-wide FastAPI route count is informational only.
