# Render Compute Dispatcher and Multi-Language Workers

Sustainable Catalyst Lab v0.10.0 adds an optional compute backend for curated, versioned method contracts. It does not accept arbitrary source code.

## Trust boundary

The browser calls WordPress at `/wp-json/sc-lab/v1/compute/*`. WordPress validates numerical inputs and allowlisted method/language identifiers, applies a rate limit, and proxies the request to Render. `SC_LAB_COMPUTE_API_KEY` stays in WordPress and Render environment settings; it is never localized into JavaScript.

## Render services

The root `render.yaml` provisions:

- `sustainable-catalyst-lab-compute-api` — FastAPI web service
- `sustainable-catalyst-lab-language-worker` — RQ background worker
- `sustainable-catalyst-lab-compute-queue` — Render Key Value queue

The Docker image includes Python, Node.js/TypeScript, GCC/G++, GFortran, Go, and Rust. R, Julia, SQL, and Haskell remain source-generation languages until their workers are added.

## API

- `GET /health`
- `GET /version`
- `GET /v1/methods`
- `GET /v1/languages`
- `POST /v1/validate`
- `POST /v1/execute`
- `POST /v1/compare`
- `POST /v1/jobs`
- `GET /v1/jobs/{job_id}`
- `DELETE /v1/jobs/{job_id}`

## Security controls

- Curated catalog only
- No source code accepted in public requests
- Strict Pydantic request models
- 64 KiB request limit
- Numerical input limits
- Per-client rate limiting
- Temporary isolated working directories
- Execution and compilation timeouts
- CPU, memory, file, process, and output limits
- No inherited secret-rich execution environment
- Structured output parsing and benchmark comparison

## WordPress configuration

Open **Settings → Sustainable Catalyst Lab** and configure:

1. Enable the curated Render compute dispatcher.
2. Set the Compute API URL to the Render web-service origin.
3. Copy the Render `SC_LAB_COMPUTE_API_KEY` value into the WordPress API-key field.
4. Keep TLS verification enabled.

## Execution modes

- **Local portable contract** evaluates the language-neutral expression tree in the browser.
- **Render native worker** compiles or runs the selected curated language implementation.
- **Direct execution** returns during the request.
- **Queued worker job** submits to RQ and polls for status.

Local mode remains available when Render is disabled, sleeping, or unavailable.
