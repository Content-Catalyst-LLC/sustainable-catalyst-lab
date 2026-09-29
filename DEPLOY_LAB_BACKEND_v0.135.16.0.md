# Deploy Lab backend v0.135.16.0

From the release directory on macOS, copy the backend ZIP and deployment script to the VPS, SSH to Contabo, then run the upgrade script. The script backs up `/opt/sustainable-catalyst/lab/backend` and `.env.production`, deploys the immutable backend source while preserving runtime `data/`, rebuilds the `lab` container, and checks v0.135.16.0 plus retained v0.135.15.0/v0.135.14.0 health contracts and Platform Core compatibility.

See `LAB_V0135160_TERMINAL_COMMANDS.txt` for exact commands.
