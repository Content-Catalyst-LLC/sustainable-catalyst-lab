# Sustainable Catalyst Lab v0.42.0 — Scientific Equation Builder & Model Definition

## Purpose

v0.42.0 turns the Model Studio foundation into a governed equation-building environment. Researchers can define algebraic scientific models with declared variables, parameters, constants, units, parameter bounds, and initial-condition metadata; validate those definitions against a safe expression grammar; evaluate deterministic preview rows; render the resulting model curve with the shared scientific visualization engine; save the model to the active project; and prepare handoffs to Lab calibration, design studies, uncertainty analysis, the model registry, or Workbench.

## Safe scientific equation grammar

Supported operators: `+`, `-`, `*`, `/`, `^` / `**`, and `%`.

Registered functions: `exp`, `log`, `log10`, `sqrt`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `abs`, `min`, and `max`.

Registered mathematical constants: `pi`, `e`.

The parser is AST-based and does not use Python `eval`. Arbitrary Python, JavaScript, shell code, imports, attributes, subscripts, comprehensions, lambdas, user-defined functions, and undeclared symbols are rejected. Preview results must remain finite.

## Model-definition improvements

- v0.42.0 model, graph, result, bundle, and scientific-equation contracts.
- Explicit parameter values and bounds.
- Scientific constants.
- Initial-condition metadata for future dynamic-system/ODE handoff.
- Unit-bearing variables and dataset bindings.
- Equation templates for linear, exponential, logistic, Michaelis-Menten, and power-law models.
- Equation validation report showing output symbol, referenced symbols, and registered functions.
- Deterministic equation preview over supplied data rows.
- Evaluated-row inspection and graph-spec inspection.

## API additions

- `POST /v1/model-studio/equations/validate`
- `POST /v1/model-studio/equations/preview`
- WordPress proxy equivalents under `/wp-json/sc-lab/v1/compute/core/model-studio/...`

## Version contract

- WordPress release: `0.42.0`
- Model Studio feature release: `0.42.0`
- Internal platform compatibility: `1.0.0`
- Shared Scientific Visualization Engine: `0.41.0` foundation retained

## Deliberate boundaries

v0.42.0 evaluates algebraic declarative expressions only. It does not introduce arbitrary code execution, user-defined functions, symbolic solving, automatic parameter calibration for custom expressions, ODE integration, or dimensional-consistency inference. Those remain separate governed milestones.
