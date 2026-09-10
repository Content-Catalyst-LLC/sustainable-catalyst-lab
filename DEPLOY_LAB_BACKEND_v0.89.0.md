# Deploy Sustainable Catalyst Lab v0.89.0 on Contabo

This release upgrades the Lab source/backend while preserving the existing `.env.production` and `sc-lab-data` Docker volume. No new credential is required and no database migration is introduced by the SOC v0.6.0 foundation.

The live target is `/opt/sustainable-catalyst/lab`, container `sc-lab`, localhost port `8092`. The upgrader makes a timestamped backend backup, rebuilds the container, checks `/health` and `/v1/carbon-nature/soc/v0600/health`, and runs the 78 Mg C/ha reference fixture inside the container.
