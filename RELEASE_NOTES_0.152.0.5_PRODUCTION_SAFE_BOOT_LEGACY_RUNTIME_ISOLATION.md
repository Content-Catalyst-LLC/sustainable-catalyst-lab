# Release notes — Sustainable Catalyst Lab v0.152.0.5

**Release:** Production Safe Boot, Legacy Runtime Isolation & Patch-Aware Integrity Repair

v0.152.0.5 responds to a production browser-crash condition observed after v0.152.0.4. Server-side inspection showed the consolidated v0.152.0.4 assets were healthy and publicly accessible, but the live Lab HTML still contained 22 individual historical Lab module scripts in addition to the new bundles.

This release makes the Lab front door deterministic: a late WordPress asset gate removes all historical Lab JavaScript requests and serves a bounded safe navigation bootstrap. The optional v0.152.0.4 module mega-bundle is no longer eager. The consolidated Lab CSS remains the sole Lab stylesheet on the front door.

The release also repairs a false integrity-warning condition by treating `0.152.0.5` as a valid patch of feature line `0.152.0`. All other release identity, file hash, plugin folder, platform, and route checks remain enforced.

The Python backend is unchanged from the v0.152.0 scientific capability line. Backend deployment is packaged for release synchronization but is not required to recover the WordPress page.
