# Render deployment — Sustainable Catalyst Lab v0.14.0

Deploy the existing Sustainable Catalyst Lab backend from the v0.14.0 GitHub commit.

No additional Render service, database, queue, or secret is required.

## New FastAPI routes

- `GET /v1/urban-planning/methods`
- `POST /v1/urban-planning/run`

The router uses the existing `SC_LAB_API_KEY` environment variable. When the variable is configured, requests must include the matching `X-SC-Lab-Key` header.

## WordPress proxy routes

- `GET /wp-json/sc-lab/v1/compute/urban-planning/methods`
- `POST /wp-json/sc-lab/v1/compute/urban-planning/run`

The WordPress proxy retains the backend key server-side.
