# Deploy Lab backend v0.161.0

Upload `sustainable-catalyst-lab-backend-v0.161.0.zip` and `DEPLOY_LAB_V01610_CONTABO.sh` to `/tmp` on the Lab VPS, then run:

```bash
chmod +x /tmp/DEPLOY_LAB_V01610_CONTABO.sh
/tmp/DEPLOY_LAB_V01610_CONTABO.sh /tmp/sustainable-catalyst-lab-backend-v0.161.0.zip
```

The deployer backs up `/opt/sustainable-catalyst/lab`, synchronizes the backend, adds the persistent program/portfolio SQLite path to `compose.yml` when needed, rebuilds the Lab container, and verifies cumulative health through v0.161.0.
