# Deploy Lab backend v0.157.0

The backend ZIP contains the complete Lab Python backend with the new `cross_study_replication_meta_experiment_v01570.py` module and tests.

Production storage defaults to `/app/data/sc-lab-cross-study-replication-v01570.sqlite3` when the supplied Contabo deploy script adds the compose environment variables.

Deploy with:

```bash
chmod +x /tmp/DEPLOY_LAB_V01570_CONTABO.sh
/tmp/DEPLOY_LAB_V01570_CONTABO.sh /tmp/sustainable-catalyst-lab-backend-v0.157.0.zip
```

The script backs up the current Lab service, installs the backend, rebuilds/restarts the Lab container, and verifies `/health` for v0.157.0 plus retained v0.156.0/v0.155.0/v0.154.0/v0.153.0 capabilities.
