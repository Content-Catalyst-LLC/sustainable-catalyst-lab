# Lab v0.135.8.5.3 — Context-Aware Relationship Filtering

This patch keeps the v0.135.8.5.2 incremental provenance runtime and hardens relationship filtering against traversal-direction ambiguity.

- Relationship availability is computed from the selected node, traversal direction, and declared edge relations.
- The selected relationship is never silently reset merely because a traversal direction has zero matches.
- Zero-match states are explicit in the Graph Studio controls and diagnostics.
- Incompatible unselected relationship options are disabled; the currently selected zero-match relation remains visible so the user's state does not appear to unstick.
- Relationship context updates remain incremental and do not increase the full graph render count.
- No scientific relation, claim, evidence status, or causal interpretation is inferred.
