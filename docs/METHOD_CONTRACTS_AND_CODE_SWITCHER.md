# Universal Code Switcher and Method Contracts

## Design objective

A scientific method should not be independently rewritten twelve times without a shared source of truth. Version 0.9.2 introduced `sc-lab-method/1.0`; version 0.9.3 connects those contracts to curated execution workers, a portable contract containing the inputs, units, constants, validation boundaries, derived values, output expression graph, assumptions, and supported language targets.

## Supported languages

- Python
- R
- Julia
- JavaScript
- TypeScript
- SQL
- C
- C++
- Fortran
- Rust
- Go
- Haskell

Python notebooks are generated from the Python implementation.

## Expression graph

Portable expressions are represented as structured nodes:

```json
{
  "op": "mul",
  "args": [
    { "number": 0.5 },
    { "var": "mass" },
    { "op": "pow", "args": [{ "var": "velocity" }, { "number": 2 }] }
  ]
}
```

The browser evaluates this graph directly and each language generator renders it using that language's numerical syntax and standard-library functions.

## Execution states

```text
local portable contract
  Language-neutral expression evaluation in the browser

Render native worker
  Curated Python, JavaScript, TypeScript, C, C++, Fortran, Rust, or Go execution

source only
  Generated R, Julia, SQL, or Haskell reference implementation
```

Code Studio discovers the runtimes actually available on the connected worker. When Render is disabled or unavailable, the browser retains the local portable-contract result and labels it as a fallback rather than pretending that native code executed.

## Parity validation

For contracts that correspond to an existing general calculator, Code Studio can compare:

```text
Portable contract result
↔ Current JavaScript calculator result
↔ Absolute numerical difference
↔ Pass/fail tolerance
```

Parity records can be stored in `implementationComparisons`.

## Expansion rule

A method is added to the portable catalog only when it has:

1. Explicit input and output units.
2. Machine-readable expressions.
3. Domain validation rules.
4. Deterministic reference inputs and outputs.
5. Generated source in every supported language.
6. At least one parity or benchmark test.

Complex methods can remain native to their discipline module until they meet this standard.
