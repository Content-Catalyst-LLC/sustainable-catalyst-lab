# Deploy Lab backend v0.104.0

## Files

- `sustainable-catalyst-lab-backend-v0.104.0.zip`
- `upgrade_lab_backend_v0_104_0_contabo.sh`

## Mac → Contabo

```bash
cd ~/Downloads

scp -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  sustainable-catalyst-lab-backend-v0.104.0.zip \
  upgrade_lab_backend_v0_104_0_contabo.sh \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

## On Contabo

```bash
chmod +x /tmp/upgrade_lab_backend_v0_104_0_contabo.sh
/tmp/upgrade_lab_backend_v0_104_0_contabo.sh
```

The upgrader backs up the current Lab backend, preserves `.env.production` and Compose-managed volumes, rebuilds `sc-lab`, validates the v0.104.0 adapter endpoints and invariants, and verifies that the public Platform Core health endpoint reports v3.0.0.

There is no Lab database migration and no new credential requirement in v0.104.0.
