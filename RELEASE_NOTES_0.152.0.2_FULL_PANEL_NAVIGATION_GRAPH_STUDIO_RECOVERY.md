# Release Notes — Lab v0.152.0.2

**Full-Panel Navigation & Graph Studio Recovery**

This patch fixes the remaining navigation regression after v0.152.0.1. The legacy compatibility shell no longer removes inactive Lab panels from the rendered page. All panels remain mounted and visibility is controlled with `hidden`, restoring the navigation contract expected by `sc-lab-app.js` and the fail-safe navigator.

The v0.152.0 Cross-Workspace Research Dependency Graph backend is unchanged.
