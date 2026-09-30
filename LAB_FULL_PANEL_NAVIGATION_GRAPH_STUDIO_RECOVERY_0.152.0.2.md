# Lab v0.152.0.2 — Full-Panel Navigation & Graph Studio Recovery

## Purpose
Restore reliable in-page Lab navigation after v0.152.0.1 by correcting the legacy v0.26.3.1 single-module compatibility shell.

## Root cause
The compatibility shell parsed every `data-lab-module` panel but emitted only the initially selected panel. Modern navigation expects destination panels to remain in the DOM and toggles their `hidden` state.

## Repair
- Preserve every Lab panel in rendered HTML.
- Keep only the selected initial panel visible.
- Mark every other panel `hidden` rather than deleting it.
- Retain the v0.152.0.1 early app bootstrap and optional-module dependency decoupling.
- Retain the fail-safe navigation listener.
- No backend scientific/runtime behavior changes.
