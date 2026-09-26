# Deploy Lab backend v0.135.14.0

From macOS, upload the backend ZIP and upgrade script to `/tmp`, SSH to the Contabo host, and run the upgrader. The script backs up the live backend and environment, rebuilds the `sc-lab` container, verifies the v0.135.14.0 health contract, confirms v0.135.13.0 remains available, checks native provenance, and verifies Platform Core compatibility.
