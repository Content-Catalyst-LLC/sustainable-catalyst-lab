# Long-Running Numerical Jobs and Checkpoint Recovery

Sustainable Catalyst Lab v0.27.2 extends the persistent Python Compute Core queue with deterministic checkpoints and resumable execution. It is intended for numerical workloads that outlive a normal HTTP request or may be interrupted by a browser reload, worker termination, or service restart.

## Capabilities

- SQLite WAL job and checkpoint persistence
- Chunked parameter sweeps and bootstrap calculations
- Partial-result inspection while a job is running or paused
- Pause and resume controls
- Restart recovery from the latest persisted checkpoint
- Priority scheduling from 0 to 100
- Per-project active-job limits
- Result caching with use, refresh, and bypass policies
- Progress, ETA, checkpoint sequence, result size, and resume-count reporting
- Bounded checkpoint retention and payload sizes

## Safety and governance

Only registered methods can run. Checkpoint state is validated and bounded. Public arbitrary Python execution remains disabled. The final result retains the standard compute-provenance manifest.

## WordPress interface

Use **Analyze → Long Jobs & Checkpoints** or the focused shortcode:

```text
[sc_lab_long_jobs]
```

The studio can submit governed examples, filter jobs by project, inspect partial output and checkpoint history, pause or resume work, cancel or retry jobs, manage result-cache policy, and save completed results to the active Lab project.

## Persistence note

SQLite recovery survives only while the configured database file survives. On Render, mount `SC_LAB_JOB_DB_PATH` under a persistent disk for recovery across instance replacement and redeployment.
