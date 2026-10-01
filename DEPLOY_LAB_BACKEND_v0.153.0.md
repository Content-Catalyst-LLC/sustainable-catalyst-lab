# Lab backend deployment — v0.153.0

v0.153.0 adds the server-backed 4D Computational Research Workspace to the Python Compute Core.

The deployment keeps the existing `sc-lab-data` Docker volume mounted at `/app/data` and adds:

- `SC_LAB_4D_WORKSPACE_DB_PATH=/app/data/sc-lab-4d-computational-workspaces.sqlite3`
- `SC_LAB_4D_WORKSPACE_PERSISTENT_DISK_MOUNTED=1`

The deployment script rebuilds the existing `lab` compose service, verifies public Compute Core health, verifies the v0.153.0 workspace capability is advertised, and confirms the v0.152 dependency graph still reports 120 routes. The authenticated workspace API itself is exercised through the WordPress HMAC bridge.
