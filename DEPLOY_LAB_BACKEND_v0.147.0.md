# Deploy Lab backend v0.147.0
Copy the backend ZIP and `DEPLOY_LAB_V01470_CONTABO.sh` to the Contabo host, then execute the deployment script with the ZIP path. The script backs up the current backend and `.env.production`, replaces backend runtime files, rebuilds/restarts the `sc-lab` container, and verifies v0.147.0, v0.146.0, v0.145.0, and Platform Core health.
