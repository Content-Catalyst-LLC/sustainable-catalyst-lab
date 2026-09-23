# Deploy Lab backend v0.129.0

From macOS, upload the backend ZIP and deployment script to the VPS, connect over SSH, then execute `/tmp/upgrade_lab_backend_v0_129_0_contabo.sh`.

The deployment preserves the existing compose file, compose-managed volumes, and `.env.production`, backs up the live backend first, rebuilds the Lab container, validates Lab Compute Core, verifies retained v0.128 health, checks Platform Core compatibility using the minimum-version contract, and exercises v0.129 artifact/tolerance/comparison/replication/Core fixtures.

Application-wide FastAPI route count is informational only and is not used as an exact deployment gate.
