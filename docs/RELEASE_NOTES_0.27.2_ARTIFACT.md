# Sustainable Catalyst Lab v0.27.2

## Long-Running Numerical Jobs and Checkpoint Recovery

Version 0.27.2 extends the governed Python Compute Core with durable progress checkpoints for selected intensive numerical workloads. Parameter sweeps and bootstrap uncertainty runs can expose partial results, pause, resume, recover from an interrupted worker or service restart, and complete through the existing WordPress control plane.

### WordPress

- Adds **Analyze → Long Jobs & Checkpoints**.
- Adds `[sc_lab_long_jobs]` for a focused long-job workspace.
- Adds queue, checkpoint, cache, pause, resume, retry, and project-filter controls.
- Preserves one-panel lifecycle isolation, Safe Start, production recovery, functional validation, and accessibility layers.

### Python Compute Core

- Upgrades the persistent queue schema in place to `sc-lab-compute-job/1.1`.
- Adds checkpoint history and latest partial results.
- Adds pause and resume controls.
- Adds restart recovery from the latest valid checkpoint.
- Adds priority scheduling from 0 through 100.
- Adds deterministic result caching with `use`, `refresh`, and `bypass` policies.
- Adds per-project active-job limits.
- Adds progress messages, estimated remaining time, resume counts, result sizes, and cache-hit records.

### Checkpointable methods

- `simulation.parameter_sweep`
- `uncertainty.bootstrap_mean_interval`

The release continues to prohibit arbitrary public Python execution. Only registered, schema-constrained methods can run.
