# Lab v0.107.0 — Platform Core v3 Scientific Execution Lineage

Platform Core v3 exposes `/v1/research/unified-runtime/execution-bindings` as a reference-first execution registry. Lab v0.107.0 constructs compatible envelopes without automatically submitting them.

## Core binding fields

- `session_id`
- `execution_ref`
- `runtime`
- `environment_ref`
- `method_ref`
- `input_refs[]`
- `output_refs[]`
- `visibility`
- `metadata`

## Lab lineage metadata

Lab preserves `context_ref`, project/workflow/project-state references, parameters, assumptions, environment details, execution status and timestamps, code/software/seed references, input/parameter/assumption/environment/output hashes, and a deterministic `lineage_hash`.

The bridge can normalize individual executions, build single or batch Core envelopes, map common legacy Lab run records, and validate declared lineage continuity. It never treats a structural lineage check as scientific validation.

Minimum compatible Platform Core release: 3.0.0.
