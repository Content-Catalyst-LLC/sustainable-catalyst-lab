# Release notes — Lab v0.135.8.4.1

**Provenance Interaction Lifecycle & Graph Control Recovery**

This patch fixes non-responsive provenance nodes and layout controls in the v0.135.8.4 Graph Studio workspace. Synthetic layout-button restoration was removed and replaced with direct SVG geometry updates, while node/layout/traversal/filter controls now use event delegation from the persistent Renderer 3.1 stage.

The patch retains v0.135.8.4 project binding and persistence, v0.135.8.3.1 bootstrap finalization, v0.135.8.3 recovery, and v0.135.8.2 renderer compatibility. Presentation state remains isolated from scientific records.
