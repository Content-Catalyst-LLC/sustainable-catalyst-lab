# Numerical Precision and Solver Governance v0.27.3

Sustainable Catalyst Lab v0.27.3 adds a governance layer between a scientific request and the registered Python method. It makes solver choice, tolerance, numerical conditioning, units, uncertainty standards, and comparison behavior inspectable rather than implicit.

## Precision profiles

- **Fast exploratory** uses relaxed tolerances for rapid investigation.
- **Balanced scientific** is the default for routine work.
- **Strict validation** tightens tolerances and favors rejection of invalid units or unreliable conditioning.
- **Diagnostic comparison** enables detailed solver and reference-method checks.

The compute service reports IEEE-754 binary64 machine epsilon, smallest normal value, largest finite value, effective tolerances, and the exact registered solver used.

## Governance boundaries

Manual solver selection is limited to registered solvers. Arbitrary Python, arbitrary SciPy functions, and arbitrary package loading remain disabled. Unit validation can warn or reject. Linear systems can reject an ill-conditioned matrix or use a governed least-squares fallback.

## Reference comparisons

Registered comparisons include bracketed root solvers, analytic polynomial integration, alternate ODE integration, direct versus least-squares linear systems, and analytic quadratic minima. Comparisons are advisory validation records, not a substitute for domain-specific scientific review.
