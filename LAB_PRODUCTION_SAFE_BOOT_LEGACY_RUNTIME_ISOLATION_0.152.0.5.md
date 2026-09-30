# Lab v0.152.0.5 — Production Safe Boot, Legacy Runtime Isolation & Patch-Aware Integrity Repair

## Purpose

v0.152.0.5 is a production recovery release for the Lab front door. Production diagnostics on the canonical `/lab/` page showed that v0.152.0.4 correctly delivered its consolidated bundles but the rendered page still contained 22 separately enqueued historical Lab module scripts. The browser could therefore execute bundled and unbundled generations of the Lab simultaneously.

The recovery strategy is deliberately conservative: the canonical Lab page boots with one consolidated stylesheet and one small navigation runtime. Historical individual module scripts and the v0.152.0.4 optional mega-bundle are not executed eagerly.

## Runtime contract

- One front-door JavaScript runtime: `assets/js/sc-lab-safe-bootstrap-v015205.js`.
- No `MutationObserver`, polling loop, recurring timer, or background module mount in the safe bootstrap.
- Full-panel DOM contract from v0.152.0.2 is retained.
- Primary navigation can switch among existing Lab panels without a full-page reload.
- Advanced scientific module execution is intentionally deferred while the front door is stabilized.
- Historical module source remains in the repository; v0.152.0.5 changes delivery, not scientific records or backend computation.
- Backend behavior and the v0.152.0 cross-workspace dependency graph remain unchanged.

## Integrity repair

The Lab product release and feature line are different identities during patch recovery releases:

- release: `0.152.0.5`
- feature line: `0.152.0`
- platform compatibility: `1.0.0`

The integrity runtime now accepts an exact feature release or a numeric patch extension of that feature line. Plugin header, release manifest, runtime release, file hashes, plugin identity, platform compatibility, and canonical route checks must still match.

## Scientific boundary

This release changes front-end delivery only. It does not reinterpret scientific evidence, validate a model, establish causality, recompute findings, invalidate prior results, or modify provenance semantics.
