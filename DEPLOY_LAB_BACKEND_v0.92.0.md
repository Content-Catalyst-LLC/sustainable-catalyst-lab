# Deploy Sustainable Catalyst Lab backend v0.92.0

Target: `/opt/sustainable-catalyst/lab`, container `sc-lab`, localhost port `8092`.

Upload `sustainable-catalyst-lab-backend-v0.92.0.zip` and `upgrade_lab_backend_v0_92_0_contabo.sh` to `/tmp`, then run the upgrader. The script preserves `.env.production` and the `sc-lab-data` Docker volume, backs up the current backend, installs source only, rebuilds the Lab service, verifies retained Carbon & Nature v0.6/v0.7/v0.8 health, verifies v0.9.0 uncertainty health, and executes replicate and paired-change uncertainty fixtures inside the running container.

No database migration and no new credentials are required.
