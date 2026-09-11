# Deploy Sustainable Catalyst Lab backend v0.95.0

Target: `/opt/sustainable-catalyst/lab`, container `sc-lab`, local port `8092`.

The upgrader preserves `.env.production` and the existing persistent Lab data volume, creates a timestamped backend backup, replaces only the backend source, rebuilds the container, and verifies Carbon & Nature v0.12.0. No database migration and no new credentials are required.

Use the ZIP-wrapped upgrader when downloading through a browser.

## WordPress deployment

The v0.95.0 WordPress ZIP is a slim runtime package rather than a full repository mirror. It may be installed through WordPress Admin or extracted directly under `wp-content/plugins/sustainable-catalyst-lab` using the Bluehost terminal. The Python backend is not bundled inside the WordPress ZIP.
