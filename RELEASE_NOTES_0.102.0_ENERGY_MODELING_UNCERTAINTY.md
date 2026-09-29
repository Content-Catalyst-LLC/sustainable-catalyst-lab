# Sustainable Catalyst Lab 0.102.0

## Energy Modeling & Uncertainty

- Adds `/v1/energy-modeling/framework`.
- Adds `/v1/energy-modeling/plan`.
- Adds `/v1/energy-modeling/analyze`.
- Adds `/v1/energy-modeling/validate-result`.
- Advances the Energy Systems target consumer identity to 0.102.0.
- Reuses existing Lab probabilistic design primitives; Workbench 6.2.0 remains the arithmetic execution authority.
- Requires explicit uncertainty distributions, sample count, seed, Workbench operation inputs, and output result path.
- Preserves provenance and human-review context.
- Keeps execution orchestration pull-oriented and non-automatic.
