# Deploy Sustainable Catalyst Lab backend v0.98.0

Backend target: `/opt/sustainable-catalyst/lab/backend` on the Contabo VPS, Compose service `lab`, container `sc-lab`, local port `8092`.

The upgrader backs up the existing backend, preserves `.env.production` and the existing Compose/volume configuration, replaces backend code only, rebuilds the `lab` service, verifies Carbon & Nature v0.6.0 through v0.15.0, and executes uncertainty/detection reference fixtures inside the live container.

No database migration and no new credentials are required.

Mac upload:

```bash
cd ~/Downloads
unzip -q upgrade_lab_backend_v0_98_0_contabo.zip
scp -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  sustainable-catalyst-lab-backend-v0.98.0.zip \
  upgrade_lab_backend_v0_98_0_contabo.sh \
  catalystadmin@94.72.113.77:/tmp/
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes catalystadmin@94.72.113.77
```

VPS:

```bash
chmod +x /tmp/upgrade_lab_backend_v0_98_0_contabo.sh
/tmp/upgrade_lab_backend_v0_98_0_contabo.sh
```
