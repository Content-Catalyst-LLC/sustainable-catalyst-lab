# Lab v0.135.8.4.1 — Provenance Interaction Lifecycle & Graph Control Recovery

## Purpose
Repair the live provenance graph interaction lifecycle after v0.135.8.4 successfully restored one hydrated Renderer 3.1 workspace but layout and node controls could be lost during renderer redraws.

## Runtime changes
- No programmatic `.click()` is used to restore provenance layout.
- Layout restoration updates the existing SVG node transforms and edge coordinates directly.
- One delegated click/change lifecycle is attached to the persistent Graph Studio stage.
- Node selection survives renderer node replacement and updates the scientific-object inspector.
- Layered, Radial and Swimlane remain presentation layouts only.
- All / Upstream / Downstream / Focus and relation filtering operate on declared edges only.
- Missing edges are never inferred; structural paths are never promoted to causal paths.

## Scientific boundary
Interaction state can alter visibility, layout, focus and inspector context. It cannot alter source rows, evidence weight, finding/claim status or Platform Core scientific objects.
