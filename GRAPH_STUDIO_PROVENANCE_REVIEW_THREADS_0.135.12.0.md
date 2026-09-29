# Graph Studio Provenance Review Threads — v0.135.12.0

## Purpose

v0.135.12.0 turns the v0.135.11.0 competing-path comparison surface into a reviewable research record. A reviewer can create a provenance review thread, attach explicit annotations to the active path, individual edges, nodes, Object A, or Object B, and link an annotation to an explicit claim or record reference.

## Runtime ownership

The v0.135.8.5.x native provenance controller remains the sole provenance renderer. v0.135.12.0 does not own graph layout, traversal, selection, or redraw. It subscribes to the v0.135.11.0 comparison context and applies annotation markers incrementally to existing SVG objects.

## Annotation model

Supported annotation kinds are `observation`, `question`, `limitation`, `claim-link`, and `evidence-note`. Supported scopes are `path`, `edge`, `node`, `object-a`, and `object-b`. A `claim-link` requires an explicit claim or record reference; the Lab does not infer claim linkage from text or graph topology.

Annotations retain the candidate-path index active when they were authored. Switching to another competing path preserves prior annotations while moving the visible markers to annotations that belong to the newly active path.

## Project persistence

Saving is explicit. `Save to project` writes or updates a `graph-studio-provenance-review-thread` record in the active Lab project collection `graphStudioReviewThreads`. Merely viewing, switching paths, or adding an unsaved annotation does not mutate scientific records elsewhere in the Lab.

## Cross-workspace handoff

`Open review context` creates a review packet containing the thread, comparison snapshot, annotation summary, and explicit claim references. Project Workspace renders that packet as review context. The handoff has both an in-memory runtime reference and a session-storage copy for normal browser navigation.

## Scientific boundary

Review threads are reviewer-authored descriptive context. An annotation does not establish truth, causal strength, evidentiary weight, scientific validity, or a preferred explanation. Claim linkage is explicit-only.
