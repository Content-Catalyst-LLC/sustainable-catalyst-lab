# Deploy Sustainable Catalyst Lab backend v0.114.0

From macOS, upload `sustainable-catalyst-lab-backend-v0.114.0.zip` and `upgrade_lab_backend_v0_114_0_contabo.sh` to `/tmp`, SSH to the Contabo host, then run the deployment script. The script preserves the compose file, `.env.production`, and compose-managed `lab_data` volume, excludes mutable backend data from replacement, creates a timestamped backend backup, rebuilds `sc-lab`, waits for health, and verifies the v0.114 publication-grade visualization contract plus retained v0.109/v0.113 integration health.
