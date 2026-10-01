# Deploy Lab backend v0.163.1

Upload `sustainable-catalyst-lab-backend-v0.163.1.zip` and `DEPLOY_LAB_V01631_CONTABO.sh` to `/tmp` on the Contabo host, then run:

```bash
chmod +x /tmp/DEPLOY_LAB_V01631_CONTABO.sh
/tmp/DEPLOY_LAB_V01631_CONTABO.sh /tmp/sustainable-catalyst-lab-backend-v0.163.1.zip
```

The deployer backs up the current Lab tree, synchronizes the backend, rebuilds the Lab container, verifies the v0.163.1 health marker and prior capabilities, and rolls back automatically if health verification fails.
