# Sustainable Catalyst Lab v0.61.0 — End-to-End Scientific Study & Research Project Lifecycle

## Release intent

v0.61.0 turns the integrated Lab beta into a governed scientific study lifecycle inside the active Lab project. It does not add a new permanent navigation destination. The lifecycle is contextual inside Scientific Workflows / Workflow Orchestration and preserves the six-destination rail, Graph Studio front door, and three related application cards.

This release is distinct from the older v0.40 institutional guided-beta project feature. v0.61 is the scientific study record for the active Lab project.

## End-to-end lifecycle

The study lifecycle covers eleven governed stages:

1. Research question & hypotheses
2. Protocol & analysis plan
3. Data & provenance
4. Analysis / modeling
5. Validation & diagnostics
6. Uncertainty & limitations
7. Experimental evidence when required by study type
8. Scientific figures
9. Conclusions & limitations
10. Reproducibility package
11. Scientific audit

Study types are observational, experimental, computational, and mixed. Experimental evidence is required only for experimental and mixed studies.

## Human review boundary

Evidence completeness and human acceptance are separate states. Required scientific evidence does not automatically complete a stage. Required stages remain `needs-review` until a researcher records an explicit review decision. A reviewer can accept, block, or reopen a stage with a rationale. Blocking a required stage blocks the lifecycle.

`study-complete` is a governed project lifecycle state. It is not a claim that the study is scientifically correct, causally proven, publication-ready, or externally certified.

## Study record and evidence packet

v0.61.0 adds:

- `sc-lab-scientific-study/0.61.0`
- `sc-lab-scientific-study-lifecycle/0.61.0`
- `sc-lab-scientific-study-stage-review/0.61.0`
- `sc-lab-scientific-study-evidence-packet/0.61.0`

The study definition preserves research question, rationale, hypotheses, methods/protocol summary, analysis plan, uncertainty plan, researcher-entered conclusions, limitations, open questions, evidence references/hashes, and stage-review hashes.

The final study packet is metadata/evidence-reference only. Raw datasets, credentials, arbitrary executable payloads, and scientific input arrays are excluded.

## Project integration

Browser storage uses dynamic project collections:

- `scientificStudiesV0610`
- `analysisPackets` with record type `scientific-study-lifecycle-v0610`

The lifecycle reuses the v0.60 integrated-project evidence summary rather than creating a parallel source of truth for datasets, models, workflow runs, packages, figures, and audit evidence.

## Safety and scientific-governance boundaries

The following remain disabled:

- automatic scientific certification
- automatic causal claims
- automatic publication
- automatic registry promotion
- automatic physical experiment execution
- automatic high-stakes decisions
- arbitrary Python, JavaScript, shell, SQL, callbacks, or executable study stages

Conclusions and limitations are researcher-entered and require human stage review.

## API surface

FastAPI and WordPress proxy routes are available under `/scientific-studies/v0610/` for:

- health
- policies
- templates
- normalize
- evaluate
- review
- packet
- verify

## Interface continuity

v0.61.0 introduces no new permanent left-rail destination and no new `MutationObserver`. The existing six primary destinations, Graph Studio front door, and Prototyping Workbench / Decision Studio / Site Intelligence application row are preserved.
