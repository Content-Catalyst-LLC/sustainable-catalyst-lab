# Sustainable Catalyst Lab v0.30.1 — Parameter Studies and Design of Experiments

v0.30.1 adds project-scoped parameter studies and governed design generation for factorial screening, Latin-hypercube exploration, response-surface studies, sensitivity ranking, and registered-method batch planning.

## Design boundary

The service generates bounded design matrices and analyzes supplied responses. It does not execute arbitrary formulas or arbitrary Python. Batch records are queue handoff plans for registered Compute Core methods.

## Storage boundary

Studies, matrices, analyses, sensitivities, and bundles remain browser-local project records. The Python service normalizes, generates, fits, verifies, and recommends but is not a permanent project database.
