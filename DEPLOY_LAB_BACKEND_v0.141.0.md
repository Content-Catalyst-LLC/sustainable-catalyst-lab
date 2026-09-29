# Deploy Lab backend v0.141.0

From macOS, copy both the backend ZIP and deploy script to Contabo `/tmp`, SSH to the server, make the script executable, and run it with the ZIP path.

The deployer backs up the current backend and environment, replaces the backend while preserving runtime data, rebuilds the `lab` Docker service, waits for health, and validates v0.141.0 plus v0.140.0, v0.139.0.1, v0.139.0, and Platform Core neural-foundation compatibility.
