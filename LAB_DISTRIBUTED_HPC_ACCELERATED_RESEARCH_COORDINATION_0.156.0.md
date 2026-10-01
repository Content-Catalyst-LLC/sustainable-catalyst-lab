# Lab v0.156.0 — Distributed, HPC & Accelerated Research Coordination

This release turns the deterministic execution handoffs introduced in Lab v0.155.0 into explicit, capability-aware distributed execution plans.

A **compute target** is a capability descriptor rather than a credential container. Targets can represent a Workspace execution broker, Slurm cluster, PBS cluster, LSF cluster, Kubernetes compute environment, or a manually managed external executor. Target records declare bounded capacity such as CPU cores, memory, GPU count and memory, supported accelerator families, MPI support, scheduler array limits, walltime limits, and parallel-job limits.

An **execution plan** binds a v0.155.0 campaign's explicit handoffs to one declared target and one resource-intent contract. Lab validates that the selected target can satisfy the declared requirements, partitions work into execution waves, creates scheduler-neutral submission bundles, and hashes the resulting plan and wave contracts. Nothing is submitted automatically.

An **execution receipt** records what an external execution authority reports back: trial ID, state, execution reference, result reference, worker/target reference, and bounded details. Synchronizing a receipt back into the v0.155.0 campaign trial ledger is optional and occurs only when explicitly requested.

Failed work can be inspected against active target capabilities to produce replan candidates. The output is advisory. Lab does not choose or trigger a failover target on its own.

The release preserves reproducibility through target hashes, task hashes, wave hashes, scheduler-contract hashes, receipt hashes, event-chain hashes, and a final manifest digest.
