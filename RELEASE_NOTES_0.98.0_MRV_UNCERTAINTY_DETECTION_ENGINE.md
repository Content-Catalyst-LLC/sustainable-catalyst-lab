# Sustainable Catalyst Lab v0.98.0 — MRV Uncertainty & Detection Engine

Carbon & Nature Intelligence advances from v0.14.0 to v0.15.0.

This release adds a governed MRV uncertainty budget, observed-change detection calculations for paired and independent monitoring designs, detection-oriented sample-size planning, assessment validation, monitoring-plan/protocol linkage, and Carbon Project `model-run` handoff.

The engine requires explicit scientific assumptions. It does not silently choose confidence levels, coverage factors, power targets, correlation structures, or uncertainty deductions. Detection means only that an observed change meets the supplied statistical threshold; it does not establish verification, methodology compliance, additionality, permanence, or credit eligibility.

Reference fixtures include a 3/4 uncertainty-component budget producing combined standard uncertainty 5 and expanded uncertainty 10 at explicit coverage factor 2; paired change 4 with SD 8 and n=16 producing SE 2 and threshold 3.92 at critical value 1.96; and paired detection planning with MDD 4, z-alpha 1.96, z-power 0.84, and SD 8 producing n=32.
