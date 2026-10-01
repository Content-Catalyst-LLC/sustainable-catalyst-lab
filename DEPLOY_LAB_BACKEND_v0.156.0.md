# Lab Backend Deployment — v0.156.0

Deploy `sustainable-catalyst-lab-backend-v0.156.0.zip` with `DEPLOY_LAB_V01560_CONTABO.sh`.

The deployment adds the persistent coordination database environment variables when absent, rebuilds the Lab container, and verifies `/health` reports `distributedHpcAcceleratedCoordination.version = 0.156.0` while retaining the v0.155.0 campaign, v0.154.0 protocol/notebook, and v0.153.0 4D-workspace capability markers.

The new database stores capability descriptions, plans, receipts and provenance events. Cluster credentials are intentionally excluded from the v0.156.0 object model.
