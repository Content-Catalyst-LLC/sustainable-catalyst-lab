# Platform Core v3 Findings, Claims, Evidence & Validation Bridge — Lab v0.108.0

## Architecture

Lab is the scientific authority. Core is the reference-first research-intelligence registry.

```text
Lab experiment/model/analysis
        │
        ├── execution lineage (v0.107)
        │
        ├── declared finding ────────────────► Core Finding Registry
        ├── declared scientific claim ───────► Core Claim Registry
        ├── evidence relation/grade ─────────► Core Evidence Link Registry
        ├── declared contradiction ──────────► Core Contradiction Registry
        ├── validation challenge ────────────► Core Validation/Challenge Registry
        └── replication attempt ─────────────► Core Replication Attempt Registry
```

## Core targets

- `/v1/research/intelligence/projects/{project_id}/findings`
- `/v1/research/intelligence/projects/{project_id}/claims`
- `/v1/research/intelligence/projects/{project_id}/evidence-links`
- `/v1/research/intelligence/projects/{project_id}/contradictions`
- `/v1/research/validation-challenges/challenges`
- `/v1/research/validation-challenges/replications`

The adapter creates request envelopes only. It never sends them automatically.

## Lab claim compatibility

Lab v0.62 types map conservatively to Core types. For example, Lab `associational` and `mechanistic` claims map to Core `interpretive`; Lab `causal` remains `causal`. Lab `active` maps to Core `proposed`, not `supported`, because the bridge must not infer evidentiary support.

Lab evidence roles also map conservatively. `supports`, `contradicts`, and `contextualizes` preserve their semantics; `validates`, `uncertainty`, and `limitation` map to Core `qualifies`, with the original Lab role retained in namespaced metadata.

## Validation boundary

A Lab evidence grade or review decision may be attached as declared assessment metadata. Core does not turn that declaration into a truth score or scientific certification. Replication attempts similarly remain declared records until reviewed under the appropriate scientific process.

## Deferred

Lab v0.109.0 will bridge Core visual reasoning objects and Lab scientific scenes/renderers. v0.108 deliberately does not add visual bindings.
