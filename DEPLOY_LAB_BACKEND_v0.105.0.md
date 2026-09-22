# Deploy Lab backend v0.105.0

## Files

- `sustainable-catalyst-lab-backend-v0.105.0.zip`
- `upgrade_lab_backend_v0_105_0_contabo.sh`

## Mac → Contabo

```bash
cd ~/Downloads/sc-lab-v0.105.0-release

scp -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  sustainable-catalyst-lab-backend-v0.105.0.zip \
  upgrade_lab_backend_v0_105_0_contabo.sh \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

## On Contabo

```bash
chmod +x /tmp/upgrade_lab_backend_v0_105_0_contabo.sh
/tmp/upgrade_lab_backend_v0_105_0_contabo.sh
```

The upgrader backs up the current backend, preserves `.env.production` and Compose-managed volumes, rebuilds `sc-lab`, validates the retained v0.104 Core-v3 adapter, validates the v0.105 canonical object mapping routes and invariants, and confirms the public Platform Core health endpoint reports v3.0.0.

The route verifier is safe when FastAPI includes internal router objects without a `.path` attribute. There is no Lab database migration and no new credential requirement in v0.105.0.
