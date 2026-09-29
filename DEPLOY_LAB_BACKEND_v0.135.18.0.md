# Deploy Lab backend v0.135.18.0

Copy `sustainable-catalyst-lab-backend-v0.135.18.0.zip` and `upgrade_lab_backend_v0_135_18_0_contabo.sh` to `/tmp` on Contabo, then run the upgrade script with the ZIP path.

The deployment preserves the live backend `data/` directory and verifies the new 18-route multi-reviewer API, retained v0.135.17.0 review-to-reproduction API, v0.135.14.0 review audit, and Platform Core health.
