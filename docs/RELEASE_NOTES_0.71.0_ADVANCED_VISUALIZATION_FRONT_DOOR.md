# Sustainable Catalyst Lab v0.71.0 — Advanced Scientific Visualization Front Door & 4D Projection

v0.71.0 upgrades the Lab landing experience from the older two-series Graph Studio preview to a browser-rendered multidimensional scientific visualization environment. The front door now demonstrates a projected 4D response field while keeping computed project results explicitly separate from illustrative interface content.

## Advanced landing visualization

- Replaces the legacy illustrative line/scatter landing preview with an interactive response-surface renderer.
- Adds a projected 4D `x, y, z, w` context with a controllable W hyperslice.
- Adds genuine XW and YW 4D rotation controls for the projected hypercube inset.
- Adds response-surface mesh, vector-field arrows, uncertainty-envelope guides, projected contours, axes, peak marker, coordinate inspection, and a 4D tesseract projection.
- Adds an optional 4D sweep animation and respects the browser as the renderer; the landing visualization does not require Python Compute Core.
- Keeps Graph Studio as the authoritative workspace for saved scientific figures and project-derived visualizations.

## Scientific integrity boundary

The landing visualization is labeled **Illustrative**. Its values are generated deterministically in the browser to demonstrate higher-dimensional scientific visualization controls. They are not presented as experimental measurements, model fits, posterior estimates, or computed project results.

## Compute recovery repair

The existing v0.26.6 production-recovery layer previously escalated a single Python Compute Core health failure directly to a **Lab recovery** warning. This was too aggressive for transient backend wake-up or network latency.

v0.71.0 preserves that proven recovery layer but changes its behavior:

- first and second failures are shown as **Compute reconnecting**, not a Lab-wide failure;
- browser-local tools and the new landing visualization remain explicitly available;
- retries use bounded exponential backoff: 5s, 10s, 20s, 40s, then 60s;
- a persistent **Lab recovery** warning is reserved for repeated failures;
- successful compute health checks clear the transient recovery state;
- compute state is exposed to the landing visualization as Online, Reconnecting, Offline, or Browser-only;
- active queued jobs continue to be preserved and rechecked through the existing recovery machinery.

## Compatibility

- WordPress release: `0.71.0`
- Stable platform compatibility marker: `1.0.0`
- Inherits v0.70.0 / v0.70.0 R1 preregistration and runtime-health repairs.
- No backend scientific method contract is removed or weakened.
- No new arbitrary-code execution path is introduced.
