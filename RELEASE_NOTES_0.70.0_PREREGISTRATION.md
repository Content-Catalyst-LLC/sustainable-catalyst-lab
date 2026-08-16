# Sustainable Catalyst Lab v0.70.0 — Research Questions, Hypothesis Registry & Preregistration

## Release intent

v0.70.0 adds a governed preregistration layer above the v0.61–v0.69 study, claims, scientific argumentation, causal/statistical modeling, and scientific-theory line. It lets a researcher register explicit research questions, hypotheses, outcome hierarchy, analysis plans, inclusion/exclusion rules, stopping rules, information-size rationale, missing-data handling, multiplicity boundaries, and sensitivity plans before outcome results are interpreted.

A `preregistration-bounded` result means the registered plan has an explicit pre-result attestation, a tamper-evident frozen snapshot, disclosed post-freeze deviations, and human review. It does not mean the hypothesis is true, the study is unbiased, the analysis is valid, or the result is confirmatory merely because a registration exists.

## Added

- Governed research-question records with descriptive, associational, causal, predictive, mechanistic, comparative, and custom types.
- Research-question population, exposure/intervention, comparator, outcome, and time-horizon boundaries.
- Governed hypothesis registry with primary, secondary, exploratory, null, alternative, mechanistic, and custom roles.
- Hypothesis direction, outcome/exposure references, expected effect/contrast, and explicit falsification boundaries.
- Reuse of v0.61 study context, v0.62 claims, v0.66 scientific hypotheses, and v0.69 theory/prediction records.
- Preregistration plans covering primary/secondary outcomes, analysis plan, inclusion/exclusion criteria, stopping rule, sample/information-size rationale, missing-data plan, multiplicity plan, sensitivity plan, scope, and limitations.
- Explicit `resultsAccessState` and researcher-authored pre-result attestation.
- Tamper-evident preregistration freeze containing deterministic hashes of registered questions, hypotheses, outcomes, analysis plan, exclusions, stopping rule, and other prespecified boundaries.
- Freeze verification that detects post-freeze mutation of the registered plan.
- Timestamped post-freeze deviation records with section, description, rationale, interpretation impact, and evidence references.
- Human preregistration review with accept-within-scope, accept-with-qualification, block, and reopen decisions.
- Tamper-evident metadata-only preregistration packets.
- Project collections `scientificResearchQuestionsV0700`, `scientificHypothesisRegistryV0700`, `scientificPreregistrationsV0700`, `scientificPreregistrationFreezesV0700`, and `scientificPreregistrationDeviationsV0700`.
- `analysisPackets` evidence records with `recordType: preregistration-v0700`.
- Contextual Preregistration workspace inside Scientific Workflows; no new primary navigation destination.

## Evaluation gates

- `needs-research-question`
- `research-question-incomplete`
- `needs-hypotheses`
- `hypothesis-registry-incomplete`
- `needs-primary-outcome`
- `needs-analysis-plan`
- `needs-exclusion-rules`
- `needs-stopping-rule`
- `needs-sample-size-rationale`
- `pre-result-attestation-required`
- `needs-freeze`
- `freeze-integrity-failure`
- `needs-deviation-rationale`
- `needs-review`
- `blocked`
- `preregistration-bounded`
- `preregistration-bounded-with-deviations`
- `preregistration-bounded-with-qualification`

## Scientific/governance boundaries

v0.70.0 does not authorize automatic hypothesis validation, automatic post-hoc preregistration, automatic outcome reclassification, automatic publication, network fetching during evaluation, participant-level data ingestion, raw scientific datasets in preregistration packets, or arbitrary code execution. A freeze is a provenance and integrity control, not proof that the researcher actually avoided all exposure to results or that the registered design is scientifically valid.

## Compatibility

- WordPress-facing release: `0.70.0`
- Internal platform compatibility: `1.0.0`
- Six primary Lab destinations preserved.
- Graph Studio front door preserved.
- Prototyping Workbench / Decision Studio / Site Intelligence application row preserved.
- v0.69 Scientific Theory & Conceptual Model Workspace remains intact.
- No `MutationObserver` introduced.
