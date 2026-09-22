# Deploy Lab backend v0.118.0

Upload `sustainable-catalyst-lab-backend-v0.118.0.zip` and `upgrade_lab_backend_v0_118_0_contabo.sh` to `/tmp`, then run the upgrade script on the Lab VPS.

The deployment preserves the compose file, production environment, and compose-managed volumes. Mutable backend `data/` is not overwritten. Validation checks retained v0.114–v0.117 visualization health, v0.118 narrative health, Platform Core >= 3.0.0, all required v0.118 routes, and representative narrative/figure/provenance/export/Core fixtures. Total FastAPI route count is informational only.
