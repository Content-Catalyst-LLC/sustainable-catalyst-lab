# Render deployment — Sustainable Catalyst Lab v0.17.0

Deploy the existing Sustainable Catalyst Lab backend from the v0.17.0 GitHub commit.

No additional Render service, database, queue, or secret is required.

## New FastAPI routes

- `GET /v1/development-economics/methods`
- `POST /v1/development-economics/run`

The router uses the existing `SC_LAB_API_KEY` environment variable. When configured, requests must include the matching `X-SC-Lab-Key` header.

## WordPress proxy routes

- `GET /wp-json/sc-lab/v1/compute/development-economics/methods`
- `POST /wp-json/sc-lab/v1/compute/development-economics/run`
