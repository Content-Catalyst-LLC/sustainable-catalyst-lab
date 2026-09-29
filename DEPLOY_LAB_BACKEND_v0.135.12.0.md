# Deploy Lab backend v0.135.12.0

From the Mac, upload `sustainable-catalyst-lab-backend-v0.135.12.0.zip` and `upgrade_lab_backend_v0_135_12_0_contabo.sh` to `/tmp` on the Contabo host, then execute the upgrade script with the ZIP path.

The deployer preserves `/opt/sustainable-catalyst/lab/.env.production`, creates a timestamped backup of the current backend, rebuilds the `lab` container, waits for Docker health, validates the v0.135.12.0 review-thread health endpoint, verifies v0.135.11.0 competing paths and the native provenance engine remain available, and checks Platform Core compatibility.
