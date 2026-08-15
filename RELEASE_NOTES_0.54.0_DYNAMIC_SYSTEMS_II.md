# Sustainable Catalyst Lab v0.54.0
## Dynamic Systems II — Events, Regime Changes, Bifurcation & Advanced Phase Analysis

v0.54.0 extends the deterministic ODE foundation introduced in v0.45.0 without changing the Lab navigation or presentation architecture.

### New capabilities

- Safe declarative event functions evaluated against time, states, parameters, and declared constants.
- Event direction filters (`-1`, `0`, `1`) and optional terminal stopping.
- Scheduled regime changes with evidence notes.
- Piecewise-constant parameter profiles that remain inside declared parameter bounds.
- Governed state resets at scheduled regime boundaries.
- Event/regime annotations on shared-engine trajectory figures.
- Bounded numerical parameter sweeps for candidate bifurcation/regime-transition evidence.
- Tail minimum, mean, maximum, standard deviation, and terminal-state summaries after a declared transient fraction.
- Two-state autonomous phase-plane analysis.
- Phase-speed heatmaps.
- Approximate numerical nullclines.
- Numerical equilibrium search inside a declared phase domain.
- Finite-difference Jacobians and local eigenvalue-based equilibrium classification.
- Graph Studio handoff for Dynamic Systems II figures.
- Project-scoped `analysisPackets` records compatible with v0.50 reproducible model packages.

### Scientific boundaries

The v0.54 numerical bifurcation scan is exploratory evidence, not a formal bifurcation proof. Local eigenvalue classifications are not global stability proofs. Phase-equilibrium analysis requires exactly two state variables and an autonomous system with no explicit time term in the derivative expressions.

Delay differential equations, stochastic differential equations, partial differential equations, arbitrary Python/code, automatic regime inference, automatic control actions, and automatic scientific claims remain disabled.

### Interface

Dynamic Systems II appears as a collapsed contextual section inside the existing Dynamic Systems / ODE area in Model Studio. It does not add a new permanent navigation destination. The six-destination v0.48.3 rail, Graph Studio front door, and Workbench / Decision Studio / Site Intelligence application-card row remain intact.

### Compatibility line

- Lab release: `0.54.0`
- Dynamic Systems II: `0.54.0`
- Correlated uncertainty: `0.53.0`
- Bayesian inference: `0.52.0`
- Advanced statistical modeling: `0.51.0`
- Reproducible model packages: `0.50.0`
- Lab ↔ Workbench model contract: `0.49.0`
- Contextual navigation: `0.48.3`
- Scientific visualization engine: `0.44.0`
- Base deterministic dynamic systems: `0.45.0`
- Internal platform compatibility: `1.0.0`
