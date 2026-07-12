# Sustainable Catalyst Lab v0.9.4 Render Deployment
## Compute, Vector PDF Reports, and Decision Studio Validation

Version 0.9.4 uses the existing Render Blueprint and adds ReportLab to the API image. No additional Render service is required for the initial report release.

## Blueprint services

```text
sustainable-catalyst-lab-compute-api
sustainable-catalyst-lab-language-worker
sustainable-catalyst-lab-compute-queue
```

The compute API now handles direct compute requests plus bounded report generation and Decision Studio packet validation. The worker continues to handle queued curated-language jobs.

## Deploy

1. Push the v0.9.4 repository to GitHub.
2. Open the existing Render Blueprint or API service.
3. Deploy the latest `main` commit.
4. Deploy the language worker from the same commit.
5. Keep the current Key Value queue.
6. Keep the current `SC_LAB_COMPUTE_API_KEY` value.
7. Wait for the API health check to pass.

## Required environment variables

```text
SC_LAB_COMPUTE_API_KEY
SC_LAB_CORS_ORIGINS=https://sustainablecatalyst.com
SC_LAB_RATE_LIMIT_PER_MINUTE=60
SC_LAB_ENABLE_DOCS=true
SC_LAB_QUEUE_NAME=sc-lab-compute
REDIS_URL=<provided by the Blueprint>
```

## Verify

```text
GET /health
GET /version
```

The version response should report `0.9.4`.

Test the report routes with an authenticated request:

```text
POST /v1/reports/validate
POST /v1/reports/pdf
POST /v1/handoffs/decision-studio/validate
```

`/v1/reports/pdf` returns JSON containing `dataBase64`, `pageCount`, `byteLength`, `reportFingerprint`, `pdfFingerprint`, and `engine: reportlab-vector-pdf`.

## WordPress configuration

The existing WordPress compute settings remain valid:

```text
Settings -> Sustainable Catalyst Lab -> Render compute dispatcher
```

- Enable remote execution.
- Use the API service origin without `/v1`.
- Use the same `SC_LAB_COMPUTE_API_KEY` value.
- Keep TLS verification enabled.

The browser calls same-origin WordPress report routes. The API key remains server-side.

## Resource considerations

Report generation is CPU and memory bounded by the web service plan and WordPress proxy limits. The initial release permits one to twelve analyses and a two-megabyte structured handoff packet. Large image-heavy reports, animation rendering, and long-running report jobs should be moved to queued workers in a later release.

## Production checks

- Confirm the API and worker deploy the same commit.
- Confirm ReportLab installs during Docker build.
- Confirm report requests do not appear in general compute job queues.
- Confirm the API key is absent from browser configuration and request bodies.
- Confirm WordPress enforces authentication, rate limits, payload sanitation, and response-size limits.
- Confirm generated PDFs open in the browser, Preview, and Acrobat-compatible readers.
- Confirm Decision Studio packets validate before handoff.
