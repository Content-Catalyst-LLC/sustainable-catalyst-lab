# Deploy Sustainable Catalyst Lab backend v0.96.0

Target: `/opt/sustainable-catalyst/lab`, container `sc-lab`, local port `8092`.

The upgrader preserves `.env.production` and does not modify the compose file or its named-volume declarations. It creates a timestamped backend backup, replaces only backend source files, rebuilds/recreates the `lab` service, then verifies Carbon & Nature v0.6.0 through v0.13.0 and executes a complete MRV Protocol Builder fixture. No database migration and no new credentials are required.

Use the ZIP-wrapped upgrader when downloading through a browser.

## WordPress deployment

The v0.96.0 WordPress ZIP remains a slim runtime package. It contains the PHP runtime, templates, browser assets, governed contracts, static application data, and canonical release manifest; backend source and virtual environments are excluded. It may be installed through WordPress Admin after the old accidental `.venv` tree has been removed, or extracted directly under `wp-content/plugins/sustainable-catalyst-lab` from the Bluehost terminal.
