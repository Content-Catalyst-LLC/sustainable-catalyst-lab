# Deploy Lab backend v0.110.0

From macOS, upload `sustainable-catalyst-lab-backend-v0.110.0.zip` and `upgrade_lab_backend_v0_110_0_contabo.sh` to `/tmp`, SSH to the Contabo host, then run:

```bash
chmod +x /tmp/upgrade_lab_backend_v0_110_0_contabo.sh
/tmp/upgrade_lab_backend_v0_110_0_contabo.sh
```

The script preserves compose-managed volumes and `/opt/sustainable-catalyst/lab/.env.production`, creates a backend backup, accepts Platform Core >=3.0.0, and verifies the retained v0.104-v0.109 integration surfaces plus the thirteen v0.110 package/scholarly endpoints.
