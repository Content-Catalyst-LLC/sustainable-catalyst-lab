# Deploy Lab backend v0.154.0

v0.154.0 changes the backend and therefore requires deployment.

It adds `reproducible_protocol_notebook_v01540.py` and authenticated `/v1/reproducible-protocol-notebook-workspace/v01540/*` routes.

The persistent database defaults to:

`/app/data/sc-lab-protocol-notebook-v01540.sqlite3`

The deployment script preserves the existing `/app/data` volume, rebuilds the `lab` compose service, verifies Compute Core health, preserves the 120-route v0.152 dependency graph, and confirms the v0.154 capability is reported by public `/health`. Authenticated protocol/notebook routes should be verified through the WordPress HMAC proxy after deployment.
