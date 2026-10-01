# Deploy Lab Backend v0.155.0

1. Generate the canonical artifacts with `./APPLY_AND_PACKAGE_LAB_V01550.sh`.
2. Copy `sustainable-catalyst-lab-backend-v0.155.0.zip` to the Contabo host, normally under `/tmp/`.
3. Copy `DEPLOY_LAB_V01550_CONTABO.sh` to the host and run it with the backend ZIP path.
4. The deployer creates a timestamped `/opt/sustainable-catalyst/lab` backup, preserves the data directory, installs the new backend source, adds the v0.155.0 campaign database environment variables if absent, rebuilds the `lab` service, and checks `/health`.
5. Verify authenticated campaign routes through the WordPress HMAC proxy after the WordPress package is installed.

Expected retained health capabilities include `reproducibleProtocolNotebookWorkspace.version=0.154.0` and `fourDComputationalResearchWorkspace.version=0.153.0`. The new global health capability is `batchExperimentSweepEnsemble.version=0.155.0` with `automaticDispatch=false` and `arbitraryCodeExecution=false`.
