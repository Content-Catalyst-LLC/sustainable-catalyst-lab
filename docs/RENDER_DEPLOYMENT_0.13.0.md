# Render deployment — Sustainable Catalyst Lab v0.13.0

Deploy the existing Sustainable Catalyst Lab backend from the v0.13.0 GitHub commit.

No additional Render service, database, queue, or secret is required.

## New routes

- `GET /v1/architecture/methods`
- `POST /v1/architecture/run`

The new router honors the existing `SC_LAB_API_KEY` environment variable. When the variable is configured, requests must provide the matching `X-SC-Lab-Key` header.

## WordPress proxy routes

- `GET /wp-json/sc-lab/v1/compute/architecture/methods`
- `POST /wp-json/sc-lab/v1/compute/architecture/run`

The WordPress proxy retains the API key server-side.
