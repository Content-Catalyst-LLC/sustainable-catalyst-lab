# Lab backend deployment — v0.141.8

Upload `sustainable-catalyst-lab-backend-v0.141.8.zip` and `DEPLOY_LAB_V01418_CONTABO.sh` to `/tmp` on the Contabo VPS, then execute the deployment script with the ZIP path. The script backs up the current backend and production environment, verifies required v0.141.x modules, rebuilds/recreates the `sc-lab` container, and checks the new package health endpoint plus predecessor and Platform Core health.
