# Render deployment — Lab v0.11.0

Deploy the existing compute API and worker from the same v0.11.0 commit.

No additional service, queue, database, or secret is required.

Verify:

- `GET /health`
- `GET /version`
- `GET /v1/mechanical/methods`
- `POST /v1/mechanical/run`

The existing `X-SC-Lab-Key` protects the two new `/v1/` routes.
