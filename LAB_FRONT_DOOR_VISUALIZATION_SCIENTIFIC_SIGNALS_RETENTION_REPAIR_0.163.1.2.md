# Sustainable Catalyst Lab v0.163.1.2

## Front-Door Visualization & Scientific Signals Retention Repair

This patch preserves the successful v0.163.1.1 page-length consolidation while restoring the Lab front door.

### Repair contract

- The live 4D visualization (`[data-v0710-visualizer]`) is persistent Overview content and is never adopted by the specialist workspace shell.
- Scientific signals (`[data-overview-signals]`) are retained on Overview, their disclosure is opened, and the existing Refresh signals action is requested once on page startup.
- The specialist shell is appended **after** the canonical Lab front door rather than injected at the app opening tag.
- Ten specialist workspaces remain progressive: Notebook/Protocol, Batch, HPC, Cross-Study, Replication, Review, Research OS, Programs, Resources, Governance.
- v0.163.1.1 page-length behavior is retained for those specialist workspaces.
- Backend package is included; scientific compute/backend semantics are unchanged.

## Authority boundaries

The patch changes presentation and navigation only. Platform Core remains canonical object authority; Workspace remains execution authority; Research OS and governance layers retain their existing lifecycle and human-authorization boundaries.
