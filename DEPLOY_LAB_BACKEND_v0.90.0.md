# Deploy Sustainable Catalyst Lab backend v0.90.0

**Carbon & Nature Intelligence:** v0.7.0 — SOC Sampling & Field Measurement Studio  
**Compute Core:** v1.0.0  
**Production root:** `/opt/sustainable-catalyst/lab`  
**Container:** `sc-lab`  
**Local port:** `8092`  
**Persistent volume:** `sc-lab-data`

## Deployment boundary

This upgrade replaces Lab backend source only. It preserves the existing `.env.production`, Docker Compose topology, and the `sc-lab-data` persistent volume. `backend/data/` is excluded from source synchronization. There is no database migration and no new credential requirement.

## Upload from macOS

```bash
cd ~/Downloads

scp -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  sustainable-catalyst-lab-backend-v0.90.0.zip \
  upgrade_lab_backend_v0_90_0_contabo.sh \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

## Run on Contabo

```bash
chmod +x /tmp/upgrade_lab_backend_v0_90_0_contabo.sh
/tmp/upgrade_lab_backend_v0_90_0_contabo.sh
```

The upgrader creates timestamped source and environment backups, rebuilds the `sc-lab` container, waits for Docker health, verifies Compute Core v1.0.0, verifies Carbon & Nature v0.7.0 / Lab v0.90.0, and executes the 1.300 g/cm³ bulk-density and 78.0 Mg C/ha profile-handoff reference fixtures inside the deployed container.

## Public WordPress step

After the backend passes, update the Sustainable Catalyst Lab WordPress plugin with `sustainable-catalyst-lab-v0.90.0-wordpress.zip`.
