# Lab v0.152.0.9 backend synchronization

The v0.152.0.9 feature is a WordPress/front-end response-surface release. Backend scientific behavior remains the v0.152.0 Python Compute Core and cross-workspace dependency-graph line.

A synchronized backend ZIP and Contabo deploy script are included so release artifacts remain aligned. The deployment script verifies the public local `/health` endpoint and the v0.152 dependency-graph health endpoint. It deliberately does not call the protected `/v1/capabilities` endpoint without HMAC authentication.

After deployment, verify the authenticated WordPress proxy from Bluehost:

```bash
curl -sS https://sustainablecatalyst.com/wp-json/sc-lab/v1/compute/core/health | python3 -m json.tool
curl -sS https://sustainablecatalyst.com/wp-json/sc-lab/v1/compute/core/capabilities | python3 -m json.tool
```
