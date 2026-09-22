# Deploy Lab Backend v0.111.0

From macOS, upload `sustainable-catalyst-lab-backend-v0.111.0.zip` and `upgrade_lab_backend_v0_111_0_contabo.sh` to `/tmp`, SSH to the Contabo VPS, then execute the upgrade script. The script preserves compose-managed volumes and `.env.production`, creates a backend backup, rebuilds `sc-lab`, checks retained v0.104-v0.110 integration health, validates the v0.111 scientific-investigation surfaces, and accepts Platform Core releases >= 3.0.0.
