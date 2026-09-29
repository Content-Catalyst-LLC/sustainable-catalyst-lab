# Lab v0.55.0 — Scientific Data Transformation & Derived Variables

## Release purpose

v0.55.0 adds a governed scientific data-preparation layer without changing the Lab navigation architecture. The release extends the existing Dataset Inspector so source data can be transformed, joined, reviewed, promoted into modeling workflows, and preserved with reproducible lineage.

## Scientific transformation contract

The release introduces:

- `sc-lab-scientific-data-transformation-plan/0.55.0`
- `sc-lab-scientific-data-transformation-result/0.55.0`
- `sc-lab-scientific-data-join/0.55.0`

Each transformation result preserves the normalized plan, plan hash, input dataset hash, output dataset hash, operation-level hashes, row/column counts before and after each operation, warnings, units, derived-variable definitions, dataset profile, and final result hash.

## Supported operations

- **derive** — safe scientific expressions through the existing v0.42 equation grammar
- **filter** — explicit comparisons, membership, and missingness predicates
- **rename** — explicit variable renaming
- **select / drop** — bounded column projection
- **scale** — z-score, centering, and min-max scaling
- **unit-convert** — governed dimensional conversions for supported units
- **cast** — number, integer, string, or boolean coercion
- **impute** — explicit constant, mean, or median imputation with review warnings
- **join** — bounded left or inner joins with collision suffixing

## Unit governance

The built-in conversion catalog includes common length, mass, time, temperature, pressure, energy, power, and angle units. Unit conversion refuses incompatible dimensions and refuses a transformation when a dataset's declared source unit conflicts with the requested conversion. Temperature conversions are affine rather than treated as simple scale factors.

## Interface integration

The feature is intentionally contextual. It appears as a collapsed **Scientific data transformation & derived variables** section in the existing Dataset Inspector. Users can:

1. run a transformation plan against the current working dataset;
2. inspect transformed rows and operation lineage;
3. render a transformed numeric variable with the shared v0.44 graph engine;
4. hand that figure to Graph Studio;
5. promote the result to the working dataset;
6. save the derived dataset and its lineage into the active Lab project; and
7. perform a bounded left/inner join against explicitly supplied right-side rows.

Transformation evidence is also saved as a project `analysisPacket`, making it available to the v0.50 reproducible-model-package collector.

## Safety and scientific boundaries

The release does **not** provide arbitrary Python, JavaScript, SQL, filesystem access, network access, automatic unit inference, automatic imputation, or automatic feature engineering. Imputation is always explicit and emits a review warning. Joins are capped to prevent accidental multiplicative output growth. Derived variables reject unsupported syntax through the existing safe AST grammar.

## Interface continuity

- Six-destination v0.48.3 rail preserved.
- Graph Studio front door preserved.
- Prototyping Workbench / Decision Studio / Site Intelligence three-card row preserved.
- No new `MutationObserver` or document-wide responsiveness loop.
- Platform compatibility remains `1.0.0`.
