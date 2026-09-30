# Lab backend deployment — v0.152.0.6

Backend scientific behavior is unchanged from the v0.152.0 feature release. The synchronized backend package is included for release-line consistency. Deploy with `DEPLOY_LAB_V015206_CONTABO.sh`; the script rebuilds the `lab` compose service and verifies `/health` plus the v0.152.0 cross-workspace dependency graph health route.
