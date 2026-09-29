# Deploy Lab backend v0.100.0

## Files

- `sustainable-catalyst-lab-backend-v0.100.0.zip`
- `upgrade_lab_backend_v0_100_0_contabo.sh`

## Mac → Contabo

```bash
cd ~/Downloads
unzip -q upgrade_lab_backend_v0_100_0_contabo.zip

scp -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  sustainable-catalyst-lab-backend-v0.100.0.zip \
  upgrade_lab_backend_v0_100_0_contabo.sh \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

## On Contabo

```bash
chmod +x /tmp/upgrade_lab_backend_v0_100_0_contabo.sh
/tmp/upgrade_lab_backend_v0_100_0_contabo.sh
```

The upgrader backs up the current backend, preserves `.env.production` and the existing Compose/volume configuration, rebuilds `sc-lab`, validates Carbon & Nature v0.6.0 through v0.17.0 health contracts, and runs an MRV reporting/audit-packet fixture inside the live container.

There is no database migration and no new credential requirement.
