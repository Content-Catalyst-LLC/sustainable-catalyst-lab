# Lab v0.155.0 — Batch Experiment, Sweep & Ensemble Orchestration

v0.155.0 turns individual reproducible notebook/compute specifications into reproducible **campaigns**. A campaign is a project-scoped immutable definition plus a deterministic set of trial specifications. The campaign layer owns planning, identity, provenance, trial state, retry lineage, aggregation, and reproduction manifests. It does not own the scientific compute runtime.

### Campaign modes

`parameter-sweep`, `hyperparameter-search`, `monte-carlo`, `factorial`, `repeated-trials`, and `ensemble` are first-class modes. Grid campaigns expand declared value sets/ranges; random campaigns use deterministic per-sample RNG seeds; repeated trials and ensemble members retain repeat/member identity.

### Execution contract

`GET /v1/batch-experiment-sweep-ensemble/v01550/campaigns/{id}/execution-batch` returns explicit `sc-lab-workspace-execution-handoff/0.155.0` objects. Each handoff carries campaign/trial identity, method/workflow/model references, inputs, parameters, requested outputs, random seed, trial hash, and a handoff digest. `dispatchRequested` is always false in this release.

### Recovery and analysis

Trial states are recorded explicitly. Mixed success/failure becomes `partial-failure`. Failed trials can be reset to `planned` only through the retry endpoint; the attempt counter is incremented and the retry is written to the event chain. Aggregation is descriptive only: count, mean, sample standard deviation, minimum, 5th percentile, median, 95th percentile, and maximum for numeric metrics on successful trials.

### Reproducibility

Campaign definitions, trial specs, seeds, attempts, execution/result references, and hashes are included in a campaign manifest. The manifest carries a SHA-256 digest and can be verified independently by the backend.
