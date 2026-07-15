# Sustainable Catalyst Lab v0.26.6 — Production Stability and Recovery

- Adds early project-storage validation and quarantine before project initialization.
- Adds a true in-memory Safe Start that does not load or modify persisted projects.
- Adds DOM, storage, JavaScript heap-growth, long-task, and runtime-error budgets.
- Adds persistent tracking and reload restoration for queued Python compute jobs.
- Adds backend interruption, offline, online, and retry states.
- Adds privacy-preserving incident bundle export.
- Adds Settings → Lab Production Readiness with isolated lifecycle and repeated-switch stress tests.
- Adds a versioned `sc-lab-production-readiness/1.0` report contract and REST health/report endpoints.
