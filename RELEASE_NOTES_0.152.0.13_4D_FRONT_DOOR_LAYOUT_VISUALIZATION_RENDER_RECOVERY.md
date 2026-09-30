# Release Notes — Lab v0.152.0.13

**4D Front-Door Layout & Visualization Render Recovery**

This blocking frontend repair addresses the production layout shown after v0.152.0.12: the 4D illustration area was visually empty/black and the advanced scientific controls were compressed into a narrow vertical column.

Changes:
- moves v0.152.0.9–v0.152.0.12 scientific panels outside the compact 4D control rail;
- adds a dedicated responsive full-width workspace region;
- bounds canvas height so the black visualization region cannot stretch with panel content;
- widens the desktop dimensional-control rail;
- replaces inherited canvas foreground color with explicit high-contrast grid/accent colors;
- updates the front-door runtime label to v0.152.0.13;
- preserves existing scene localStorage keys and all compute/selection/provenance/handoff behavior;
- retains the PHP output-safety release gate and legacy-runtime isolation.

Backend scientific behavior is unchanged.
