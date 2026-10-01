# Deploy Lab Backend v0.163.0.1

Upload `sustainable-catalyst-lab-backend-v0.163.0.1.zip` and `DEPLOY_LAB_V016301_CONTABO.sh` to `/tmp` on the Lab VPS, then run:

```bash
chmod +x /tmp/DEPLOY_LAB_V016301_CONTABO.sh
/tmp/DEPLOY_LAB_V016301_CONTABO.sh /tmp/sustainable-catalyst-lab-backend-v0.163.0.1.zip
```

The deployer creates a backup, adds the dedicated `SC_LAB_INSTITUTIONAL_REVIEW_FEDERATION_*` compose settings, rebuilds the Lab container, verifies health/capabilities, and attempts an automatic rollback if the repaired backend does not become healthy.
