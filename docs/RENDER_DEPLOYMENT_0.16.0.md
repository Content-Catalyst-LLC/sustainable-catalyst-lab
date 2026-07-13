# Render deployment — Sustainable Catalyst Lab v0.16.0

Deploy the existing Sustainable Catalyst Lab backend from the v0.16.0 GitHub commit.

No additional Render service, database, queue, or secret is required.

## New FastAPI routes

- `GET /v1/circular-economy/methods`
- `POST /v1/circular-economy/run`

The router uses the existing `SC_LAB_API_KEY` environment variable. When configured, requests must include the matching `X-SC-Lab-Key` header.

## WordPress proxy routes

- `GET /wp-json/sc-lab/v1/compute/circular-economy/methods`
- `POST /wp-json/sc-lab/v1/compute/circular-economy/run`

The WordPress proxy retains the backend key server-side.
