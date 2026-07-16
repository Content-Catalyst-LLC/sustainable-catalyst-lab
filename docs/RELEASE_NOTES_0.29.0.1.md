# Sustainable Catalyst Lab v0.29.0.1 — WordPress Integrity Manifest and Evidence Route Repair

This WordPress-only repair corrects the v0.29.0 integrity manifest schema and removes route aliases that displaced the existing Evidence & decisions and Source registry panels.

## Corrections

- Regenerates `build/sc-lab-release-manifest.json` using `releaseVersion`, `buildFingerprint`, and `wordpressCriticalFiles`, the fields consumed by the installed integrity runtime.
- Restores `evidence` and `decisions` to the canonical `evidence-decisions` panel.
- Preserves `sources` as the existing Source registry route.
- Keeps the v0.29.0 Evidence & provenance workspace available through `research-provenance`, `research-evidence`, `research-sources`, `evidence-sources`, and `provenance`.
- Does not modify or redeploy the Python Compute Core.
