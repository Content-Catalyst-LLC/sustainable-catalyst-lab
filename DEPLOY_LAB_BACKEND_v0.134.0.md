# Deploy Lab Backend v0.134.0

From macOS, upload the backend ZIP and deployment script to the Contabo host, SSH into the server, then run `upgrade_lab_backend_v0_134_0_contabo.sh`.

The deployment preserves the compose file, `.env.production`, and compose-managed `backend/data` volume. It backs up the live backend before replacement, rebuilds/recreates only the Lab service, verifies Lab Compute Core 1.0.0, verifies retained v0.133 Statistical Assumption & Diagnostic Intelligence, verifies v0.134 Evidence Synthesis Intelligence II, checks Platform Core compatibility >=3.0.0, and exercises contradiction, quantitative synthesis, replication, and Core-reference fixtures.

Application-wide FastAPI route count is printed as informational status only. Deployment gates on the v0.134 release-specific route and behavior contract.
