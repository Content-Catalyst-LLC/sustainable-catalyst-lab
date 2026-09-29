# Sustainable Catalyst Lab

Sustainable Catalyst Lab is the scientific experimentation, modeling, visualization, review, reproducibility, and neural-research workspace of the Sustainable Catalyst platform.

**Current release:** v0.141.8 — Reproducible Neural Research Package

## Architecture

Lab combines governed scientific workspaces with a Python compute backend and browser/WordPress research interfaces.

- **Lab / WordPress interface** — scientific workflows, Graph Studio, research review, experiment interfaces, and interactive analysis.
- **Python backend** — scientific computation, model analysis, reproducibility services, and runtime APIs.
- **Workspace** — execution authority for managed jobs and neural-training workloads used by Lab.
- **Platform Core** — governed research objects, provenance, evidence, visual contracts, and cross-product exchange.
- **Contracts / SDK** — stable integration surfaces for scientific objects and downstream platform components.

Lab remains the scientific experimentation and analysis layer; it does not replace Platform Core's governance contracts or Workspace's managed execution responsibilities.

## Repository layout

- `assets/` — browser and WordPress assets.
- `backend/` — Python backend, runtime services, and compute integration.
- `build/` — build support retained by the source tree.
- `contracts/` — Lab and cross-product contracts.
- `docs/` — current architecture and product documentation.
- `examples/` — example payloads and workflows.
- `includes/` — WordPress/PHP application code.
- `scripts/` — operational, validation, release, and deployment tooling.
- `sdk/` — integration SDK material.
- `templates/` — interface templates.
- `tests/` — active regression and release validation.
- `sustainable-catalyst-lab.php` — canonical WordPress plugin entry point.
- `compose.yml` — current container orchestration definition.

See `CHANGELOG.md` for release history.

## Release history

Historical release notes, deployment guides, generated validation reports, terminal-command files, and per-version release scripts are intentionally not retained at the root of `main`.

The exact pre-cleanup repository state is preserved on:

`archive/pre-root-cleanup-2026-09-29-lab`

Git history and release tags continue to preserve prior release artifacts. For example:

```bash
git show v0.141.8:RELEASE_NOTES_0.141.8_REPRODUCIBLE_NEURAL_RESEARCH_PACKAGE.md
git show v0.141.8:REPRODUCIBLE_NEURAL_RESEARCH_PACKAGE_0.141.8.md
```

Generated release artifacts should be packaged with releases or placed in ignored staging directories instead of accumulating in the source-tree root.
