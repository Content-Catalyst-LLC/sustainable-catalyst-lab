# Release notes — Lab v0.152.0.1

Hotfix for Lab front-end navigation availability after v0.152.0. Primary Lab navigation and Graph Studio access no longer depend on successful loading of every optional JavaScript module. Adds a fail-safe navigation bootstrap and breaks the cumulative module dependency chain while retaining all v0.152.0 backend and dependency-graph capabilities.
