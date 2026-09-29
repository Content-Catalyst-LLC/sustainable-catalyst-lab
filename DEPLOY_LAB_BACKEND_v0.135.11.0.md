# Deploy Lab backend v0.135.11.0

Copy `sustainable-catalyst-lab-backend-v0.135.11.0.zip` and `upgrade_lab_backend_v0_135_11_0_contabo.sh` to `/tmp` on the Lab VPS, then run:

```bash
chmod +x /tmp/upgrade_lab_backend_v0_135_11_0_contabo.sh
/tmp/upgrade_lab_backend_v0_135_11_0_contabo.sh /tmp/sustainable-catalyst-lab-backend-v0.135.11.0.zip
```

The deployer backs up the live backend and `.env.production`, replaces immutable backend source while preserving runtime data, rebuilds the Lab container, waits for health, validates the v0.135.11.0 route family, verifies retained v0.135.10.0 path analysis and native provenance health, and confirms a compatible Platform Core v3+ endpoint.
