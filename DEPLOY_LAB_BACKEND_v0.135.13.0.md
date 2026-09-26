# Lab v0.135.13.0 backend deployment

From the Mac, copy `sustainable-catalyst-lab-backend-v0.135.13.0.zip` and `upgrade_lab_backend_v0_135_13_0_contabo.sh` to `/tmp/` on the Contabo host, then run:

```bash
chmod +x /tmp/upgrade_lab_backend_v0_135_13_0_contabo.sh
/tmp/upgrade_lab_backend_v0_135_13_0_contabo.sh \
  /tmp/sustainable-catalyst-lab-backend-v0.135.13.0.zip
```

The deployer backs up the current backend and production environment, rebuilds the Lab container, verifies v0.135.13.0, verifies the retained v0.135.12.0 review-thread surface and native provenance engine, and checks Platform Core compatibility.
