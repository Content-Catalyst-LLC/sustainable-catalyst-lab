# Deploy Lab backend v0.135.8.1

Use `upgrade_lab_backend_v0_135_8_1_contabo.sh` with `sustainable-catalyst-lab-backend-v0.135.8.1.zip`.

The deployer preserves `/opt/sustainable-catalyst/lab/.env.production`, backs up the current backend, replaces application code, rebuilds the `lab` container, waits for health, verifies the retained v0.135.2–v0.135.8 visual-research stack, verifies the 16-route v0.135.8.1 Graph Studio canonical runtime contract, and confirms Platform Core v3 compatibility.
