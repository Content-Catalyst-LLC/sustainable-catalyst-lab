# Lab v0.163.1 — Unified Workspace Shell & Progressive Module Navigation

The Lab page had accumulated each specialist workspace sequentially, producing a very long application surface. v0.163.1 introduces a single shell that stages those workspaces behind explicit navigation while preserving their existing DOM state, event bindings, APIs, provenance rules, authentication boundaries, and scientific guardrails.

The default shell state is **Overview**. Opening a workspace makes that specialist surface visible and hides the other managed workspaces. Hidden workspaces remain stateful but no longer consume page height. The shell manages the v0.153 4D Workspace, v0.154 Notebook/Protocol, v0.155 Batch Experiments, v0.156 Compute/HPC, v0.157 Cross-Study, v0.158 Replication Network, v0.159 Scientific Review, v0.160 Research OS, v0.161 Programs, v0.162 Resources, and v0.163 Governance surfaces.

Module-specific boundary text is preserved and surfaced in the contextual **Methods & governance** drawer. No scientific semantics or authority boundaries are changed.
