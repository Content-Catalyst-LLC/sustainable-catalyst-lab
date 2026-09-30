# Lab v0.152.0.4 — Front-End Asset Consolidation & Runtime Load Recovery

## Purpose
Recover the Lab front door from request saturation and incomplete browser startup by consolidating the historical front-end fleet without removing scientific capabilities.

## Changes
- Consolidates 184 Lab CSS sources into one immutable UI bundle.
- Consolidates the five critical bootstrap modules plus navigation recovery and the main app into one boot bundle.
- Consolidates 231 optional module scripts into one isolated bundle, preserving execution order and catching failures per module.
- Preserves historical WordPress asset handles as zero-request compatibility aliases.
- Enqueues Lab assets during `wp_enqueue_scripts` when the Lab shortcode is present, rather than waiting for shortcode rendering.
- Retains the v0.152.0 dependency graph and v0.152.0.3 bootstrap guards.
- Does not change backend scientific behavior.

## Boundary
Asset consolidation changes delivery and startup behavior only. It does not alter scientific objects, evidence semantics, computation authority, or validation status.
