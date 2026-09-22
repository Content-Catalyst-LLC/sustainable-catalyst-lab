# Deploy Lab backend v0.117.0

Upload the backend ZIP and `upgrade_lab_backend_v0_117_0_contabo.sh` to `/tmp`, SSH to the Lab VPS, make the script executable, and run it. The deployment preserves compose-managed volumes and `.env.production`, creates a backend backup, verifies Lab v0.114–v0.117 health plus Core >=3.0.0, and uses behavioral route fixtures rather than an exact global route count.
