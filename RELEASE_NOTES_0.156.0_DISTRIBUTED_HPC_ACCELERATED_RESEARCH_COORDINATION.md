# Release Notes — Lab v0.156.0

**Distributed, HPC & Accelerated Research Coordination**

v0.156.0 adds the coordination layer required to move Lab campaign workloads toward workstation, GPU, cluster, batch-scheduler, and container-orchestrated execution without collapsing the boundary between research orchestration and execution.

Highlights include a credential-free compute-target registry, CPU/memory/GPU/MPI resource intent, accelerator-aware eligibility, bounded execution waves, HPC job-array planning, scheduler contracts for Workspace/Slurm/PBS/LSF/Kubernetes/manual execution, execution receipts, explicit v0.155.0 trial-state synchronization, advisory failed-work replanning, and digest-verifiable execution manifests.

Security and scientific boundaries remain conservative: no secret storage, no automatic scheduler submission, no automatic failover, no arbitrary code execution, and no automatic scientific-validity claims.
