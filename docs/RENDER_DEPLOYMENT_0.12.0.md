# Render deployment — Lab v0.12.0

Deploy the existing Lab compute service from the v0.12.0 commit. No additional service, database, queue, or secret is required.

Verify `GET /v1/civil/methods` and `POST /v1/civil/run`. The existing `X-SC-Lab-Key` protects both routes.
