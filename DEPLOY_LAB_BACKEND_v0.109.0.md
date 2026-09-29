# Deploy Lab backend v0.109.0

Upload `sustainable-catalyst-lab-backend-v0.109.0.zip` and `upgrade_lab_backend_v0_109_0_contabo.sh` to `/tmp` on the Lab VPS, then run the upgrade script.

The script preserves compose configuration and the `lab_data` volume, backs up the live backend and production environment, installs immutable backend code while preserving `backend/data`, rebuilds/recreates `sc-lab`, verifies retained v0.104-v0.108 Core integration health, checks the v0.109 visual-scene bridge, confirms Platform Core >=3.0.0, and runs behavioral fixtures for the 12 v0.109 routes.

Global FastAPI route totals are informational only.
