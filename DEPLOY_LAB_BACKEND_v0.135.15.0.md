# Deploy Lab backend v0.135.15.0

From macOS, upload the v0.135.15.0 backend ZIP and upgrade script to `/tmp`, SSH to the Contabo host, and run the upgrader. The upgrader backs up the live backend and environment, replaces the backend source, rebuilds the `sc-lab` container, verifies the new verification-artifact health and acceptance contracts, confirms v0.135.14.0 remains available, checks native provenance, and verifies Platform Core v3 compatibility.
