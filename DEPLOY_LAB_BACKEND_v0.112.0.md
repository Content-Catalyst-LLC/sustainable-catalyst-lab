# Lab v0.112.0 Backend Deployment

Upload `sustainable-catalyst-lab-backend-v0.112.0.zip` and `upgrade_lab_backend_v0_112_0_contabo.sh` to `/tmp` on the Contabo VPS, then run the upgrade script as `catalystadmin`.

The verifier requires Lab Compute Core health, retained v0.104–v0.111 integration health, the v0.112 integration-certification health contract, all 17 v0.112 endpoints, Core >= 3.0.0, and the Core platform-integration-certification readiness boundary when it is publicly reachable.

The deployment preserves compose-managed volumes and excludes mutable `backend/data/` stores from source replacement.
