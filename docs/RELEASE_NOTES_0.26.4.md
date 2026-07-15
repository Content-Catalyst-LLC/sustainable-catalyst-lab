# Sustainable Catalyst Lab v0.26.4

## Cross-Laboratory Functional Validation

This release adds a browser-driven functional-health system for the entire Lab. It verifies that panels render through the isolated lifecycle, required controllers are present, safe primary actions are wired, expected result areas change, and runtime errors are captured.

The **Settings → Lab Functional Health** dashboard can run the 14 priority scientific and engineering laboratories or all 41 panels. Each module is loaded in a separate same-origin frame so listeners, project state, source requests, and errors do not leak between checks.

Results distinguish functional code from environmental degradation:

- Functional
- Functional with captured errors
- External source unavailable
- Optional backend required
- Panel missing
- Controller missing
- Primary action missing
- Output target missing
- Calculation failed
- Result not observed

Reports can be saved in WordPress and exported as versioned JSON using `sc-lab-functional-health/1.0`.
