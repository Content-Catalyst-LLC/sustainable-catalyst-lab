# Deploy Lab backend v0.113.0

From macOS, copy `sustainable-catalyst-lab-backend-v0.113.0.zip` and `upgrade_lab_backend_v0_113_0_contabo.sh` to `/tmp/` on the Contabo host, SSH to the host, make the script executable, and run it.

The deployment preserves the compose file, `.env.production`, and the `lab_data` volume. It verifies the retained v0.104–v0.112 integration health surfaces, the v0.113 production-runtime health contract, all required v0.113 routes/behaviors, and Platform Core >=3.0.0.

The deployment gate checks required routes and contract behavior rather than an exact application-wide FastAPI route count.
