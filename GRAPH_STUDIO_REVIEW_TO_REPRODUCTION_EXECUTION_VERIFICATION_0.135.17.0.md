# Lab v0.135.17.0 — Review-to-Reproduction Bridge & Execution Verification

This release connects the Graph Studio review/revision chain to the existing v0.129.0 Research Reproduction & Replication Studio. It does not introduce a second reproduction engine.

## Flow

review annotation → resolution action → v0.135.16 revision impact → v0.135.17 reproduction bridge → v0.129 reproduction plan → explicit external/runtime execution → declared-tolerance comparison → v0.135.15 verification artifact bundle → v0.135.14 verification audit event draft

## Boundaries

A rerun, artifact match, or numerical result inside a declared tolerance is reproducibility evidence only. It does not automatically confirm a claim, establish causal validity, determine truth, weight evidence, or resolve a review item. Human confirmation is required before a verification outcome is appended to the review audit.
