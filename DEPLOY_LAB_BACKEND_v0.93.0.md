# Deploy Sustainable Catalyst Lab backend v0.93.0

This release advances **Carbon & Nature Intelligence to v0.10.0 — SOC Management Scenario Studio** while retaining Python Compute Core 1.0.0 and all prior SOC endpoints.

## VPS target

- Lab root: `/opt/sustainable-catalyst/lab`
- Container: `sc-lab`
- Local service port: `8092`
- Environment: `/opt/sustainable-catalyst/lab/.env.production`
- Persistent Docker volume: `sc-lab-data`

No database migration and no new credentials are required.

Upload `sustainable-catalyst-lab-backend-v0.93.0.zip` and `upgrade_lab_backend_v0_93_0_contabo.sh` to `/tmp`, then run the upgrader. It creates timestamped backend and environment backups, preserves the persistent volume, rebuilds the Lab service, validates retained SOC v0.6–v0.9 health contracts, validates the new v0.10 scenario service, and executes the 78 → 98 Mg C/ha reference scenario inside the live container.
