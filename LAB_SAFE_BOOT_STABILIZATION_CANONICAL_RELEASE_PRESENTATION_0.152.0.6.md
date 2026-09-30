# Lab v0.152.0.6 — Safe-Boot Stabilization & Canonical Release Presentation

v0.152.0.6 is a production-recovery patch over the v0.152.0 feature line. It preserves the working v0.152.0.5 navigation shell while closing three remaining legacy-runtime leaks observed in production.

## Recovery scope

- Adds a second Lab JavaScript queue gate immediately before WordPress prints footer scripts. This catches historical Lab modules that are enqueued after `wp_enqueue_scripts`, including shortcode/render-time enqueue paths.
- Keeps only `sc-lab-safe-bootstrap-v015206.js` as executable Lab JavaScript on the canonical Lab front door while advanced scientific runtimes remain deferred.
- Prevents the legacy v0.26.6 production-stability front-end runtime from being enqueued on v0.152.0.6+, eliminating the obsolete 6,500-node production-budget banner on the safe shell.
- Prevents legacy v0.48 presentation JavaScript from rewriting the current product release badge.
- Makes the safe bootstrap authoritative for visible release identity and writes `v0.152.0.6` to the Lab release surfaces without using a MutationObserver.
- Replaces the old integrity admin-notice callback with a v0.152.0.6 notice authority backed by the canonical integrity health response. A verified runtime does not emit a warning.
- Retains all v0.152 cross-workspace research dependency graph backend behavior and all 120 routes unchanged.

## Intentional limitation

Advanced scientific module execution remains deferred. Navigation, panel visibility, canonical release presentation, and recovery-safe shell behavior are the target of this patch. Panel-aware scientific-runtime loading is a follow-on build and must not reintroduce eager execution of the historical module fleet.

## Scientific guardrails

This delivery repair changes browser/runtime orchestration only. It does not alter scientific validity, evidence status, provenance semantics, causal interpretation, model validation, or reproducibility claims.
