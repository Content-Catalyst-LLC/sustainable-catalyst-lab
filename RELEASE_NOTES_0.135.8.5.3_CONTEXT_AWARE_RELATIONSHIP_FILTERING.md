# Sustainable Catalyst Lab v0.135.8.5.3

## Context-Aware Relationship Filtering & Provenance Interaction Hardening

Fixes the remaining Graph Studio relationship-filter ambiguity after v0.135.8.5.2. `sourced-from` now remains selected when traversal changes to a direction that yields zero matching edges, and Graph Studio reports that state explicitly instead of making the selection appear to revert. Relationship options expose match counts and context compatibility without replacing the selector or rebuilding the provenance graph.
