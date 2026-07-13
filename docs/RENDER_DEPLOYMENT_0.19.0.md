# Render deployment — Sustainable Catalyst Lab v0.19.0

Deploy the existing Sustainable Catalyst Lab backend from the v0.19.0 GitHub commit.

No additional Render service, database, queue, or secret is required.

## New FastAPI routes

- `GET /v1/rocket-spaceflight/methods`
- `POST /v1/rocket-spaceflight/run`

The router uses the existing `SC_LAB_API_KEY` environment variable. When configured, requests must include the matching `X-SC-Lab-Key` header.

## WordPress proxy routes

- `GET /wp-json/sc-lab/v1/compute/rocket-spaceflight/methods`
- `POST /wp-json/sc-lab/v1/compute/rocket-spaceflight/run`
