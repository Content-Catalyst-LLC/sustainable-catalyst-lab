# Release Notes — Lab v0.135.8.4

## Live Scientific Object Binding, Project-State Persistence & Advanced Provenance Exploration

- Adds project-scoped Graph Studio figure binding that survives reloads.
- Restores the bound project figure before falling back to the latest declared project figure.
- Persists renderer mode and provenance exploration state without mutating scientific records.
- Adds a live project-binding bar to the Renderer 3.1 workspace.
- Adds provenance node focus, upstream/downstream traversal, relation filtering and layout persistence.
- Keeps structural lineage distinct from causal inference.
- Retains v0.135.8.3.1 bootstrap/finalization and v0.135.8.3 Renderer 3.1 recovery beneath the new binding layer.
