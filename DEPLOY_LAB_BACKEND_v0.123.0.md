# Deploy Lab backend v0.123.0

Upload `sustainable-catalyst-lab-backend-v0.123.0.zip` and `upgrade_lab_backend_v0_123_0_contabo.sh` to `/tmp` on the Lab VPS, then run the upgrade script there.

The deployment script preserves compose-managed volumes and `.env.production`, backs up the previous backend, rebuilds/recreates only the Lab service, checks Lab Compute Core, retained v0.122 Bayesian Workbench health, v0.123 Simulation Studio health, and Platform Core compatibility (`>=3.0.0`), then exercises v0.123-specific simulation behavior. Application-wide route totals are informational only.
