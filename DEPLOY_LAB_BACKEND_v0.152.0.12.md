# Lab v0.152.0.12 backend deployment

Backend scientific behavior is unchanged. Deploy the synchronized archive with `DEPLOY_LAB_V015212_CONTABO.sh`; the script rebuilds the `lab` compose service and verifies Compute Core health plus the 120-route v0.152 dependency graph. `/v1/capabilities` remains HMAC-protected and is not called anonymously.
