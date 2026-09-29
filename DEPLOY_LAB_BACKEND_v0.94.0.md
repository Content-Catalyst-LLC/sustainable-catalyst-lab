# Deploy Sustainable Catalyst Lab backend v0.94.0

Target runtime:

- `/opt/sustainable-catalyst/lab`
- container: `sc-lab`
- localhost port: `8092`
- environment: `/opt/sustainable-catalyst/lab/.env.production`
- persistent volume: `sc-lab-data`

Upload `sustainable-catalyst-lab-backend-v0.94.0.zip` and `upgrade_lab_backend_v0_94_0_contabo.sh` to `/tmp`, then run the upgrader as `catalystadmin`.

The upgrader backs up the current backend and `.env.production`, preserves runtime data, rebuilds/recreates only the Lab service, checks Compute Core health, verifies all Carbon & Nature SOC v0.6–v0.10 services remain available, verifies Whole-Farm GHG v0.11.0, and executes the governed 1,200 / 366.667 / 833.333 kg CO2e fixture inside the live container.

No database migration or new credential is required.
