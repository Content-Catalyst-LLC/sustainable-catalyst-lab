# Platform Core v3 Reproducibility & Scholarly Package Integration — Lab v0.110.0

## Core contracts

- Unified research runtime: `sc.research.unified-research-scientific-investigation-runtime.v1`
- Scholarly interoperability: `sc.research.scholarly-interoperability-packaging.v1`
- Session package binding: `POST /v1/research/unified-runtime/package-bindings`
- Scholarly package registry: `/v1/research/scholarly-packages/*`

## Ownership

Lab owns package content, scientific artifacts, execution evidence, manuscript/figure content, and local scientific reproducibility checks. Core records package references, declared members, citations, descriptors, provenance, publication bindings, and external/declarative validation evidence.

## Two-stage scholarly plan

The package creation operation must execute first. Core returns the package database identifier. Follow-up citation/descriptor/provenance/publication/validation operations replace the plan placeholder `$CORE_PACKAGE_ID` with that identifier. The Lab bridge constructs these plans but does not submit them automatically.
