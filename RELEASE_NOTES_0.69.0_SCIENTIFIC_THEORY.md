# Sustainable Catalyst Lab v0.69.0 — Scientific Theory & Conceptual Model Workspace

## Release intent

v0.69.0 adds a governed scientific-theory layer above the v0.61–v0.68 study, claims, literature, synthesis, argumentation, causal-inference, and multilevel-modeling line. The release lets a researcher represent constructs, mechanisms, theoretical relations, hypotheses, model/equation references, testable predictions, falsification conditions, evidence links, and scope boundaries as one explicit conceptual model.

A `theory-bounded` result means the conceptual structure is explicit, internally referentially coherent, linked to governed project evidence, and human reviewed within a stated scope. It does not mean the theory is scientifically proven, causally certified, or universally generalizable.

## Added

- Scientific theory records with conceptual-model, mechanistic-theory, systems-theory, causal-theory, integrative-framework, and custom types.
- Typed theory constructs with definitions, empirical operationalization boundaries, units/scales, roles, and evidence references.
- Typed construct relations including causal, associative, mediation, moderation, inhibition, enabling, dependency, feedback, transformation, and constraint relationships.
- Explicit mechanism requirement for causal relations.
- Equation/model and causal-assumption references without executable code.
- Testable predictions linked to hypotheses, rival hypotheses, expected direction, governed evidence, and falsification conditions.
- Deterministic conceptual graph construction and graph hashing.
- Human theory review with accept-within-scope, accept-with-qualification, block, and reopen decisions.
- Tamper-evident metadata-only scientific-theory packets.
- Project collections `scientificTheoriesV0690`, `scientificTheoryConstructsV0690`, `scientificTheoryRelationsV0690`, and `scientificTheoryPredictionsV0690`.
- `analysisPackets` evidence records with `recordType: scientific-theory-v0690`.
- Contextual Scientific Theory workspace inside the existing Scientific Workflows surface; no new primary navigation destination.

## Evaluation gates

- `needs-constructs`
- `needs-construct-definitions`
- `needs-operationalization`
- `needs-relations`
- `unresolved-construct-reference`
- `needs-mechanism`
- `needs-predictions`
- `needs-falsification-boundary`
- `needs-evidence-linkage`
- `needs-scope-boundary`
- `needs-review`
- `blocked`
- `theory-bounded`
- `theory-bounded-with-qualification`

## Scientific/governance boundaries

v0.69.0 does not authorize automatic theory proof, automatic causal certification, universal generalization, automatic publication, network fetching during theory evaluation, participant-level data ingestion, raw scientific datasets in theory packets, or arbitrary code execution. Construct definitions and mechanisms remain researcher-authored theoretical commitments subject to empirical challenge and revision.

## Compatibility

- WordPress-facing release: `0.69.0`
- Internal platform compatibility: `1.0.0`
- Six primary Lab destinations preserved.
- Graph Studio front door preserved.
- Prototyping Workbench / Decision Studio / Site Intelligence application row preserved.
- v0.68 Hierarchical, Multilevel & Cross-Study Modeling remains intact.
- No `MutationObserver` introduced.
