# Lab v0.104.0 — Platform Core v3 Runtime Adapter

## Purpose

This release makes Research Lab a declared specialist runtime for Platform Core v3 while preserving the responsibility boundary between orchestration and scientific execution.

## Canonical identity

- Product: `product:sustainable-catalyst-lab`
- Lab release: `0.104.0`
- Adapter: `lab:adapter:platform-core-v3:0.104.0`
- Runtime binding: `lab:runtime:scientific-compute:0.104.0`
- Core runtime contract: `sc.research.unified-runtime-contract.v1`
- Core unified runtime: `sc.research.unified-research-scientific-investigation-runtime.v1`

## Backend surfaces

- `GET /v1/platform-core-v3-adapter/health`
- `GET /v1/platform-core-v3-adapter/manifest`
- `POST /v1/platform-core-v3-adapter/registrations/runtime-contract`
- `POST /v1/platform-core-v3-adapter/registrations/session`
- `POST /v1/platform-core-v3-adapter/runtime-context/normalize`
- `POST /v1/platform-core-v3-adapter/handoffs/validate`
- `POST /v1/platform-core-v3-adapter/compatibility/check`

The two GET endpoints are deployment/readiness surfaces. Mutation-oriented payload construction and validation endpoints retain Compute Core authentication.

## Registration behavior

The adapter constructs payloads that match Core's existing v2.96 runtime-contract registry and v3.0 unified-runtime session product-binding APIs. It does not submit those payloads automatically. Core therefore remains authoritative for registry writes and unified-session state.

## Boundary guarantees

- Core does not execute specialist scientific work.
- Lab remains authoritative for scientific execution and Lab-native scientific objects.
- The adapter does not auto-route research requests.
- The adapter does not auto-submit Core writes.
- A validated handoff does not itself execute a Lab workflow.
- The adapter does not infer findings, causality, truth, access rights, or scientific validity.

## Next integration release

Lab v0.105.0 — Canonical Research Object Mapping — should map Lab datasets, observations, experiments, models, workflows, evidence, artifacts, publications, reproducibility packages, scenarios, and scientific figures to Core v3 canonical object references.
