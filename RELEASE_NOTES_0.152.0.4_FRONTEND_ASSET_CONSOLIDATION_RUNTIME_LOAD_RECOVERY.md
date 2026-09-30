# Release notes — Lab v0.152.0.4

**Front-End Asset Consolidation & Runtime Load Recovery**

This patch addresses the production Lab page failing to finish loading despite a healthy backend and current WordPress plugin. The prior front door could enqueue hundreds of individual Lab CSS and JavaScript assets. v0.152.0.4 collapses the main plugin fleet into three deterministic resources: a UI bundle, a critical bootstrap bundle, and an optional scientific-module bundle. Historical handles remain available as compatibility aliases.

The backend remains functionally identical to v0.152.0.
