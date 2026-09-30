# Lab v0.152.0.13 — 4D Front-Door Layout & Visualization Render Recovery

## Problem repaired
The response-surface, uncertainty, linked-view, and persistence workspaces had accumulated inside the compact higher-dimensional control `<aside>`. That forced full scientific panels into a narrow rail and caused the grid row/canvas region to stretch dramatically. The canvas renderer also inherited `document.documentElement` color, which could resolve to a dark color against the black scientific canvas.

## Recovery architecture
- Compact rail contains only W hyperslice, XW/YW rotation, animation, demo selection, export, and compute-connection controls.
- Parameter Explorer, Uncertainty/Sensitivity/Ensemble, Linked Scientific Views, and Scene/Provenance are full-width sibling workspaces below the visualization body.
- Canvas height is bounded to 430–520px on desktop, 390px tablet, 330px mobile.
- Desktop control rail expands to 240–280px and becomes internally scrollable if needed.
- Renderer uses explicit `#d9e2ea` scientific grid lines and `#ff3842` selection/accent marks.
- Existing v0.152.0.12 browser scene storage key is preserved so saved scenes survive the patch.

## Scientific behavior
No backend scientific behavior changes. Compute remains explicit user action. Existing scientific-boundary statements remain in force.
