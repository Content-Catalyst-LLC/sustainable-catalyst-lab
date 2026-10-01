# Lab v0.161.0 — Research Program & Portfolio Orchestration

This release introduces the first program- and portfolio-scale orchestration layer above Computational Research Operating System II.

A **research program** groups existing Research OS projects under explicit purpose, workstreams, objectives, milestones, and human-controlled lifecycle state. Project membership is reference-first: v0.161.0 resolves the project against Research OS rather than copying the project record or becoming its lifecycle authority.

A **research portfolio** groups research programs and provides descriptive cross-program status views. Portfolio aggregation deduplicates Research OS projects when reporting project-stage counts, but does not score, rank, prioritize, fund, schedule, or allocate resources.

## Program capabilities

- create/list/read research programs
- attach Research OS projects with explicit roles and workstreams
- withdraw/reactivate memberships explicitly
- define program objectives
- allocate active member projects to objectives
- define milestones with optional evidence references
- human-authored objective and milestone status
- procedural readiness evaluation
- human-authorized state transitions: draft → active → review → completed, with explicit archive
- program command-center view
- manifest, timeline, and immutable snapshot

## Portfolio capabilities

- create/list/read research portfolios
- attach research programs by reference
- descriptive program-state and unique-project-stage aggregation
- procedural readiness evaluation
- human-authorized state transitions
- portfolio command-center view
- manifest, timeline, and immutable snapshot

## Authority boundaries

Platform Core remains canonical object authority. Workspace remains execution authority. Research OS v0.160.0 remains the authority for individual project lifecycle state. Lab v0.161.0 coordinates explicit program/portfolio structure only and does not infer scientific validity, replication success, causal truth, program priority, funding decisions, staffing, compute allocation, or publication merit.
