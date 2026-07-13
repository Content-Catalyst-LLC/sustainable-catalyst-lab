# Render deployment — Sustainable Catalyst Lab v0.15.0

Deploy the existing Sustainable Catalyst Lab backend from the v0.15.0 GitHub commit.

No additional Render service, database, queue, or secret is required.

## New FastAPI routes

- `GET /v1/sustainable-cities/methods`
- `POST /v1/sustainable-cities/run`

The router uses the existing `SC_LAB_API_KEY` environment variable. When configured, requests must include the matching `X-SC-Lab-Key` header.

## WordPress proxy routes

- `GET /wp-json/sc-lab/v1/compute/sustainable-cities/methods`
- `POST /wp-json/sc-lab/v1/compute/sustainable-cities/run`

The Civil interface repair is browser-side and continues using the existing civil backend routes:

- `GET /v1/civil/methods`
- `POST /v1/civil/run`

No new Civil service or environment variable is required.
