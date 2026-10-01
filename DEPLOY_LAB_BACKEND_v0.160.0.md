# Deploy Lab backend v0.160.0

Upload `sustainable-catalyst-lab-backend-v0.160.0.zip` and `DEPLOY_LAB_V01600_CONTABO.sh` to `/tmp` on the Contabo host, then execute the deployment script. The deployer backs up `/opt/sustainable-catalyst/lab`, installs the backend while preserving `/app/data`, adds the v0.160.0 Research OS persistent database settings to `compose.yml`, rebuilds the Lab service, and verifies the v0.160.0 health contract plus retained v0.159–v0.153 capabilities.
