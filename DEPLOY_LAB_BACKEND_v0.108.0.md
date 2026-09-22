# Deploy Lab backend v0.108.0

From the Mac release directory, upload the backend ZIP and upgrade script to `/tmp`, then SSH into Contabo.

```bash
scp -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  sustainable-catalyst-lab-backend-v0.108.0.zip \
  upgrade_lab_backend_v0_108_0_contabo.sh \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

On the VPS:

```bash
chmod +x /tmp/upgrade_lab_backend_v0_108_0_contabo.sh
/tmp/upgrade_lab_backend_v0_108_0_contabo.sh
```

The deployment preserves compose-managed volumes and the existing `.env.production`, excludes mutable backend `data/` from replacement, creates a backend backup, rebuilds/restarts `sc-lab`, checks Lab v0.104–v0.108 integration health, accepts Platform Core `>=3.0.0`, and verifies the 12 v0.108 routes and non-determinative scientific boundaries.
