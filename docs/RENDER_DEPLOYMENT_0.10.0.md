# Lab v0.10.0 Render deployment

No additional Render service, database, queue, or secret is required. Deploy the existing compute API and language worker from the v0.10.0 GitHub commit while retaining the current `SC_LAB_COMPUTE_API_KEY` and queue configuration.

Verify:

```text
GET  /health
GET  /version
GET  /v1/electrical/methods
POST /v1/electrical/run
```

`GET /version` should return `0.10.0`. The electrical routes are protected by the same API-key dependency as the existing curated compute routes.

Example structured request:

```json
{
  "methodId": "electrical.ohms-law",
  "inputs": {"voltage": 12, "resistance": 6}
}
```

The expected current is 2 A and power is 24 W. The endpoint does not accept arbitrary code and does not communicate with physical hardware.
