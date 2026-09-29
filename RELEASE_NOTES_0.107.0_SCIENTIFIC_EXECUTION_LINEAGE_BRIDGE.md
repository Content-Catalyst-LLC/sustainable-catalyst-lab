# Sustainable Catalyst Lab v0.107.0

## Scientific Execution Lineage Bridge

This release extends the v0.104 Core runtime adapter, v0.105 canonical object mapping, and v0.106 project/session context with a governed scientific-execution lineage bridge.

Lab can now normalize a scientific run and build the exact Platform Core v3 execution-binding envelope for `session_id`, `execution_ref`, `runtime`, `environment_ref`, `method_ref`, `input_refs`, and `output_refs`. Parameters, assumptions, environment details, status/timestamps, code/software/seed references, deterministic hashes, project/session context, and provenance remain namespaced Lab metadata on the Core binding.

### Boundaries

- Lab remains the scientific execution authority.
- Core records execution references and declared lineage; Core does not execute the scientific work.
- Underlying execution records and artifacts remain authoritative in Lab.
- No automatic Core submission, mutation, or scientific execution.
- Lineage checks validate declared structural continuity; they do not certify scientific validity.
- Core compatibility uses minimum release 3.0.0 rather than exact equality.
- Findings/claims/evidence/validation integration remains v0.108.0 scope.
