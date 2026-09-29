# Lab v0.135.8.4 — Live Scientific Object Binding, Project-State Persistence & Advanced Provenance Exploration

v0.135.8.4 moves Graph Studio from recovery into stable project-aware use.

## Runtime contract
- Renderer 3.1 remains the only primary visualization owner.
- The active Lab project is the binding namespace.
- A persisted figure ID is restored only when it exists in that same project.
- Missing project figures remain unbound or fall back to an explicitly illustrative bootstrap; IDs and scientific values are never invented.
- Renderer mode, provenance layout, focused node, traversal mode and relation filter are presentation state only.

## Provenance explorer
The recovered computational provenance graph now supports persisted layered/radial/swimlane layouts, node focus, upstream/downstream traversal, relation filtering and clear-focus recovery. Traversal is structural lineage only and never represents causal inference.

## Boundaries
This layer does not create evidence, change evidence weight, promote findings or claims, infer missing relationships, certify validity, or submit to Platform Core automatically.
