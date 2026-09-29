# Deploy Sustainable Catalyst Lab backend v0.91.0

Carbon & Nature Intelligence v0.8.0 adds the SOC Change & Sequestration Model to the existing Lab Compute Core. There is no database migration and no new credential requirement.

The production topology remains:
- Lab root: `/opt/sustainable-catalyst/lab`
- Backend source: `/opt/sustainable-catalyst/lab/backend`
- Environment: `/opt/sustainable-catalyst/lab/.env.production`
- Container: `sc-lab`
- Local backend port: `8092`
- Persistent data volume: `sc-lab-data`

Upload `sustainable-catalyst-lab-backend-v0.91.0.zip` and `upgrade_lab_backend_v0_91_0_contabo.sh` to `/tmp`, then execute the upgrader. The script backs up the current backend and environment file, replaces source only, preserves runtime data, rebuilds the Lab container, checks Compute Core health, verifies v0.6/v0.7 retention and v0.8 health, and executes the 78.0 → 85.8 Mg C/ha stock-change fixture inside the running container.

A successful deployment ends with:

`PASS - Sustainable Catalyst Lab v0.91.0 / Carbon & Nature Intelligence v0.8.0 is active.`
