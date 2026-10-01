# Build Lab v0.156.0

Release: **Distributed, HPC & Accelerated Research Coordination**

Lab v0.156.0 extends the v0.155.0 batch campaign layer with resource-aware distributed execution planning while preserving the architectural boundary that Lab coordinates and Workspace/runtime infrastructure executes.

## Added

- server-backed compute-target capability registry without credential storage;
- declared CPU, memory, GPU/accelerator, walltime, MPI and scratch resource intent;
- accelerator-aware target eligibility and placement validation;
- execution-wave and HPC job-array planning for large v0.155.0 campaign handoff sets;
- scheduler-neutral contracts for Workspace broker, Slurm, PBS, LSF, Kubernetes and manual/external execution;
- execution receipt capture with immutable receipt hashes;
- optional **explicit** receipt synchronization into v0.155.0 campaign trial state;
- descriptive reconciliation of queued/running/succeeded/failed/cancelled work;
- advisory failed-work replan candidates without automatic failover;
- digest-verifiable distributed execution manifests.

## Boundaries

v0.156.0 does not store passwords, API tokens, private keys or cluster credentials. It does not submit scheduler jobs, automatically dispatch Workspace work, automatically fail over a failed task, execute arbitrary code, or infer scientific validity. Scheduler bundles are plans/contracts only. Workspace/runtime fabric and external cluster schedulers remain execution authorities.

## Predecessor retention

v0.155.0 batch campaigns, v0.154.0 reproducible protocols/notebooks, v0.153.0 4D research workspace behavior, and earlier visual-recovery protections remain intact.
