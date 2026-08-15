# Lab v0.56.0 — Advanced Experimental Design & Sequential Experimentation

## Release purpose

v0.56.0 deepens the existing Design Studies workspace with bounded optimal-design and sequential-experiment planning. It does not change the Lab navigation architecture and does not authorize experiment execution or automatic stopping.

## Advanced design contract

The release introduces:

- `sc-lab-advanced-experimental-design/0.56.0`
- `sc-lab-sequential-experiment-plan/0.56.0`
- `sc-lab-design-optimality-diagnostics/0.56.0`

Design and sequential-plan records preserve factor bounds, model order, candidate-pool limits, randomization seed, blocking, replication, objective, evidence notes, diagnostics, proposal status, and SHA-256 integrity hashes.

## Initial design capabilities

- **D-optimal candidate selection** using a bounded numerical information-matrix search.
- **Maximin space-filling design** for broad factor-space coverage.
- Linear, interaction, and quadratic model-order declarations.
- Balanced block assignment.
- Explicit center-point replication.
- Optional deterministic run randomization from a declared seed.
- Rank, conditioning, information determinant, leverage, D-efficiency index, and minimum pairwise-distance diagnostics.

The D-optimal procedure is a numerical candidate-search heuristic. Lab does not claim a formal proof of global optimality.

## Sequential experimentation

The release supports two proposal-only strategies:

1. **Information gain** — proposes unused candidate points that increase the declared model's information matrix.
2. **Response-guided** — uses completed responses and a bounded local regression model to balance the declared objective with predictive uncertainty.

Response-guided planning is explicitly labeled a local model-based heuristic. It does not guarantee a global optimum and requires sufficient completed response evidence.

## Stopping evidence

Sequential plans record evidence for human review, including:

- maximum total run budget;
- proposed relative information gain;
- user-declared minimum information-gain threshold;
- remaining bounded candidate availability; and
- proposal warnings.

Lab does **not** automatically stop an experiment. The plan records `automaticStoppingAuthorized: false` and `automaticExecutionAuthorized: false`.

## Interface integration

The new capability is a collapsed **Advanced experimental design & sequential experimentation** section inside the existing Design Studies workspace. The v0.30.1 factor definition remains the factor source of truth. Users can:

- generate an advanced initial design;
- enter observed responses directly in the design table;
- inspect optimality diagnostics;
- propose the next sequential batch;
- inspect stopping/review evidence;
- save design and sequential-plan evidence into the active project; and
- render the coded design space with the shared v0.44 scientific visualization engine and hand it to Graph Studio.

Saved records also enter project `analysisPackets`, making them available to the v0.50 reproducible-model-package collector.

## Scientific and safety boundaries

- No arbitrary Python, JavaScript, SQL, shell, or executable formulas.
- No automatic experiment execution.
- No automatic stopping.
- No automatic factor-bound inference.
- No claim that D-optimal search proves a global optimum.
- No claim that response-guided proposals establish causality or a global response optimum.
- All candidate pools, run counts, factors, and sequential batch sizes are bounded.

## Interface continuity

- Six-destination v0.48.3 rail preserved.
- Graph Studio front door preserved.
- Prototyping Workbench / Decision Studio / Site Intelligence three-card row preserved.
- No new `MutationObserver` or document-wide responsiveness loop.
- Platform compatibility remains `1.0.0`.
