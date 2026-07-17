# Bayesian Optimization, Active Learning, and Resource-Aware Search — v0.33.1

Sustainable Catalyst Lab v0.33.1 extends adaptive experiment campaigns with an inspectable Gaussian-process surrogate and governed acquisition policies. The implementation remains workflow-backed: proposed parameter sets can launch only saved workflows and registered Lab methods.

## Surrogate model

Continuous and integer parameters are normalized to the unit interval. Categorical parameters are encoded as deterministic one-hot features. The campaign engine supports RBF, Matérn 3/2, and Matérn 5/2 kernels with bounded length scale, observation noise, and numerical jitter. Model diagnostics include observation and feature counts, condition number, objective normalization, feature names, and a reproducible model hash.

## Acquisition policies

- Expected improvement
- Probability of improvement
- Confidence bound
- Maximum predictive variance for active learning

Candidate pools are seeded and deterministic for a campaign sequence. They combine global random candidates with bounded local candidates around the current best design. Existing parameter hashes are removed before scoring.

## Resource-aware search

A campaign may declare a base cost, normalized numeric parameter weights, categorical cost increments, a maximum estimated cost per trial, a total campaign cost budget, and an optional workflow result path for observed cost. Cost-aware strategies divide acquisition value by estimated cost raised to the configured exponent. Estimated and observed costs remain distinct in trial provenance.

## Safety and governance

The optimizer produces only values that conform to the typed campaign parameter space. It cannot execute Python, JavaScript, shell commands, callbacks, or arbitrary expressions. Proposal previews do not reserve trials or mutate the campaign. Every launched trial retains the campaign definition hash, parameter hash, model hash, prediction, acquisition, resource estimate, workflow run ID, objective extraction record, and event timeline.
