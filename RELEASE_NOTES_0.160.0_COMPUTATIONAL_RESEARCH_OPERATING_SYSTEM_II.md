# Release Notes — Lab v0.160.0

**Computational Research Operating System II** is the milestone that unifies the Lab lifecycle introduced across v0.153–v0.159.

The release adds a persistent Research OS project model, a human-controlled lifecycle state machine, a reference-first project graph, command-center views, cross-module reference validation, dependency-integrity checks, reproducible research-package composition, digest verification, timelines, and explicit handoff envelopes.

The release intentionally does not create a new compute engine. Workspace remains execution authority; Platform Core remains canonical object authority. The Research OS records and coordinates lifecycle state rather than automatically performing scientific judgment or execution.

Publication-package progression requires the v0.159 review dossier to be `publication-ready` when the review-gate manager is available. Final package composition and downstream handoff both require explicit human authorization.

The backend is included and uses a persistent SQLite/WAL store with connection lifecycle safeguards retained from the v0.159.0 repair.
