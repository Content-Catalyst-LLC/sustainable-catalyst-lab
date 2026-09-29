# Deploy Lab backend v0.119.0

From macOS, copy `sustainable-catalyst-lab-backend-v0.119.0.zip` and `upgrade_lab_backend_v0_119_0_contabo.sh` to `/tmp` on the Contabo VPS, SSH into the VPS, then run the upgrade script. The script preserves compose-managed volumes and `.env.production`, verifies Platform Core >= 3.0.0, and validates v0.114–v0.119 visualization health and v0.119 behavior.
