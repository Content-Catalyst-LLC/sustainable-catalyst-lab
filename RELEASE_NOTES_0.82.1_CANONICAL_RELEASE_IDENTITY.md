# Sustainable Catalyst Lab v0.82.1 — Canonical Release Identity & Release Console Repair

v0.82.1 repairs product-version identity without changing the v0.82 Visualization Engine 2.9.0 scientific capability line.

## Canonical release identity
- `build/sc-lab-release-manifest.json` is the runtime authority for the Lab product release and feature release.
- the WordPress plugin header remains a static WordPress metadata marker and is certified against the manifest;
- `SC_LAB_RELEASE_VERSION` and `SC_LAB_FEATURE_VERSION` are derived from the manifest at bootstrap;
- `SC_LAB_PLATFORM_COMPAT_VERSION` explicitly names the independent 1.0.0 platform-compatibility line;
- `SC_LAB_VERSION` remains only as a deprecated compatibility alias for legacy modules and must never drive the public release display.

## Release Console
The System Status workspace now contains a dedicated Release Console whose large version number comes from `/runtime/health.releaseVersion`. It separately labels WordPress integration, release manifest, Visualization Engine, live Python Compute Core, Queue Gateway, and platform compatibility versions.

## Certification
`/runtime/health` exposes `releaseVersion`, `canonicalReleaseSource`, `componentVersions`, `releaseVersionConsistent`, and `releaseConsoleVersionConsistent`. Release validation fails if the manifest, plugin header, runtime release, or Release Console release identity diverge. A browser regression test proves that changing runtime release identity from 0.82.1 to 0.83.0 changes the visible Release Console version without editing the console module.
