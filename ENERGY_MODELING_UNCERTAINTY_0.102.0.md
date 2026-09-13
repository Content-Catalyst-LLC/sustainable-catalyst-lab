# Lab 0.102.0 — Energy Modeling & Uncertainty

Lab 0.102.0 activates the Energy Systems v1.4.0 modeling-and-uncertainty target runtime. It converts one explicit Workbench calculation request plus explicit probability distributions into a reproducible evaluation design, then analyzes the Workbench result packet.

The implementation reuses the Lab probabilistic sampling engine introduced in v0.48.0. Supported v1.4 designs are Monte Carlo and Latin hypercube; supported distributions are uniform, normal, lognormal, and triangular. A seed is mandatory.

Lab does not reimplement the 14 Workbench calculation formulas. `/v1/energy-modeling/plan` emits a Workbench-compatible handoff packet for `/v1/energy-runtime/execute`; the caller performs that explicit handoff. `/v1/energy-modeling/analyze` then computes empirical summary statistics, central uncertainty intervals, explicit threshold probabilities, and Pearson/Spearman/standardized-regression input-influence sensitivity.

No technology ranking, recommendation, market-price lookup, automatic persistence, avoided-emissions inference, or carbon-credit claim is introduced.
