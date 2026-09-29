# Lab v0.135.21.0 — Graph Studio Review Workspace Consolidation & Runtime Certification

This release consolidates the Graph Studio review stack created from v0.135.12.0 through v0.135.20.0 into a single visible review workspace with deterministic hydration, runtime ownership checks, restore plans, state digests, listener diagnostics, Project Workspace handoff, and backend certification APIs.

The release preserves the canonical v0.135.8.x renderer/provenance owners and the v0.135.20.0 closure package. It does not duplicate those systems or rewrite historical review records.

The release includes a Chromium headless certification harness. Chromium is installed in the build environment, but its headless process does not complete even for a blank local HTML page, so automated Chromium certification is recorded as environment-unavailable rather than passed. Node-based executable DOM/runtime certification passed.

Runtime certification is operational/reproducibility certification only and does not establish scientific truth, validity, causal correctness, evidentiary weight, reviewer consensus, or publication acceptance.
