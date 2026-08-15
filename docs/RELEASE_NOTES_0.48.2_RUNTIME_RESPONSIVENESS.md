# Sustainable Catalyst Lab v0.48.2 — UI Runtime Responsiveness & Event Loop Repair

v0.48.2 is a narrow runtime repair over v0.48.1. It preserves the three-card related-application row, Graph Studio front door, scientific workspace reorganization, and the complete v0.48 scientific stack.

## Repair

- Removes the v0.48.1 document-wide presentation `MutationObserver` from the loaded runtime.
- Prevents outer-version synchronization from rewriting identical DOM text.
- Uses the existing `sc-lab:app-ready` event instead of observing the entire page for startup.
- Coalesces Graph Studio overview refreshes with `requestAnimationFrame`.
- Re-renders the graph-forward Overview only while the Overview is active.
- Attaches to the project store after core app initialization and coalesces project-change rendering.
- Preserves all v0.48.1 presentation structure and the three related-application cards.

## Root cause

The v0.48.1 presentation module observed all child-list mutations on `document.documentElement`. Its bootstrap synchronized the outer version badge by assigning `textContent` on every callback. That write created another DOM mutation, so ordinary graph rendering, navigation, and panel updates could repeatedly re-enter the bootstrap path and create UI churn.

## Scientific scope

No scientific methods, model contracts, probabilistic analysis, Graph Studio schemas, or backend compute behavior changed in this patch.
