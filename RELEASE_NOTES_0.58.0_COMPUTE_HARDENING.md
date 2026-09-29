# Sustainable Catalyst Lab v0.58.0 — Large-Model, Large-Dataset & Compute Hardening

## Purpose

v0.58.0 hardens the scientific workspace for larger datasets, longer model runs, and composed workflows without expanding Lab's permanent navigation. It builds directly on the v0.57 Scientific Workflow Composer and keeps the v0.48.3 six-destination rail, Graph Studio front door, and three related-application cards intact.

## New compute-hardening layer

- bounded asynchronous execution for registered Lab scientific adapters;
- deterministic, TTL-governed result caching keyed to semantic requests;
- explicit workload assessment with interactive, async-recommended, and reject dispositions;
- hard limits for workflow stages, rows, columns, cells, payload size, and browser preview windows;
- bounded dataset windowing for large browser previews;
- job status, result retrieval, queue inspection, and cooperative cancellation;
- cache statistics and administrator-controlled cache clearing;
- no arbitrary code execution, automatic remote compute, or silent horizontal scaling.

## Scientific operations available to hardened compute

The v0.58 backend can dispatch only explicitly registered adapters, including workflow execution, statistical fitting, Bayesian fitting, probabilistic analysis, correlated uncertainty, Dynamic Systems II simulation, advanced experimental design, and governed data transformations.

## Cancellation semantics

Queued jobs can be cancelled before they start. Running scientific code is not force-killed because abrupt process termination can corrupt scientific state or produce ambiguous partial results. A running cancellation request is recorded and its eventual result is discarded rather than promoted as a completed user result.

## Caching semantics

Cache keys exclude ephemeral UI/request identifiers but retain the scientific payload and operation identity. Cached results carry hashes, TTLs, size limits, and bounded record counts. Oversized results are returned but are not persisted in the result cache.

## Interface

A collapsed **Large workload & compute hardening** section now appears inside the existing Scientific Workflows workspace. It can assess the current v0.57 workflow, queue it asynchronously, refresh recent compute jobs, request cancellation, and inspect completed results. The interface uses timer-based polling only while jobs are active and introduces no MutationObserver.

## Compatibility

- Lab release: `0.58.0`
- Platform compatibility: `1.0.0`
- Scientific Workflow Composer: `0.57.0`
- Advanced Experimental Design: `0.56.0`
- Data Transformations: `0.55.0`
- Dynamic Systems II: `0.54.0`
- Correlated Uncertainty: `0.53.0`
- Bayesian Inference: `0.52.0`
- Advanced Statistical Modeling: `0.51.0`
- Reproducible Model Packages: `0.50.0`
- Lab ↔ Workbench model contract: `0.49.0`
- Graph Studio: `0.47.0`
- Shared visualization engine: `0.44.0`

## Safety boundary

v0.58.0 does not authorize arbitrary Python, JavaScript, SQL, shell execution, arbitrary callbacks, force termination of active scientific code, automatic remote compute, automatic scaling, automatic publication, automatic experiment execution, or automatic model-registry promotion.
