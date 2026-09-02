# Sustainable Catalyst Lab v0.72.1 — Homepage Biodiversity Time-Sweep Loop

v0.72.1 is a focused homepage presentation patch over v0.72.0. It automatically starts the existing biodiversity time sweep when the 4D homepage widget loads, so the fourth dimension is visible without requiring a visitor to press the animation control.

## Behavior
- `[sc_lab_home_preview]` now defaults to `autoplay="true"`.
- The existing v0.71 4D renderer remains the only scientific renderer; no duplicate rendering engine is introduced.
- The existing sinusoidal biodiversity sweep continues to move smoothly through `t = 0 → 1 → 0`, producing a seamless loop rather than a hard reset.
- The existing pause button remains available and continues to satisfy the user-controlled pause/stop boundary.
- `prefers-reduced-motion: reduce` prevents autoplay and stops an active sweep if that preference becomes active.
- Autoplay can be disabled explicitly with `[sc_lab_home_preview autoplay="false"]`.
- The visualization remains deterministic synthetic interface data, not biodiversity observations, estimates, forecasts, or conservation conclusions.

## Scope
No backend compute contract, scientific model family, route topology, platform compatibility, or project data behavior changes in this patch.
