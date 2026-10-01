# Sustainable Catalyst Lab v0.155.0 Release Notes

**Release:** Batch Experiment, Sweep & Ensemble Orchestration

v0.155.0 is a backend-changing and frontend-changing release. It introduces a persistent campaign store and a new Lab front-door campaign workspace while preserving all v0.154.0 protocol/notebook and v0.153.0 4D workspace behavior.

The new campaign manager supports six campaign modes, deterministic trial/seed lineage, explicit Workspace execution handoffs, trial-state recording, partial-failure recovery, explicit retry, descriptive aggregation, event-chain provenance, and verified campaign manifests. No existing scientific compute method is changed.

Deployment requires both the WordPress package and Python backend package. The Contabo compose environment gains `SC_LAB_BATCH_EXPERIMENT_CAMPAIGN_DB_PATH` and `SC_LAB_BATCH_EXPERIMENT_CAMPAIGN_PERSISTENT_DISK_MOUNTED`.

Release boundaries remain explicit: automatic dispatch is disabled; arbitrary code execution is disabled; campaign aggregation is descriptive; human scientific review is required.
