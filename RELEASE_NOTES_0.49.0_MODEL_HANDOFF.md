# Sustainable Catalyst Lab v0.49.0

## Lab ↔ Workbench Model Handoff & Shared Computational Contract

v0.49.0 establishes a governed computational-model exchange boundary between Sustainable Catalyst Lab and Sustainable Catalyst Workbench without changing the validated v0.48.3 interface or the underlying v0.42–v0.48 scientific modeling stack.

### Added

- `sc-catalyst-computational-model/0.49.0` shared computational-model contract.
- `sc-catalyst-model-handoff/0.49.0` bidirectional handoff packet contract.
- Lab → Workbench handoff for interactive exploration of a current Model Studio model.
- Workbench → Lab import path that revalidates the incoming model through Model Studio before loading it.
- Preservation of model definition, variables, units, parameter values/bounds, constants, initial conditions, dataset bindings, assumptions, limitations, provenance, and integrity hashes.
- Same-origin browser transport through `sc_catalyst_model_handoff_v0490` plus compatibility with the historical `sc_workbench_handoff` key and `sc:workbench-handoff` event.
- Configured Workbench deep link using the existing Lab Workbench route.
- Downloadable JSON handoff package for portable/manual exchange.
- FastAPI health, policy, normalization, outbound, and inbound routes.
- WordPress compute-core proxies and v0.49 health/schema routes.
- Dedicated Model Studio exchange surface without increasing persistent left-navigation weight.

### Security and governance boundaries

- Arbitrary Python, JavaScript, shell, command, callback, and executable-code payloads are rejected.
- Declarative equations remain governed by the existing v0.42 safe scientific expression grammar.
- Imported Workbench models are normalized and revalidated before Model Studio accepts them.
- Model and packet integrity hashes are verified when present.
- Automatic remote delivery is disabled; the browser transport is same-origin/local and user initiated.
- The existing `sc-research-model/1.0` typed research contract remains a compatibility anchor.

### Compatibility

- WordPress-facing Lab release: **0.49.0**.
- Internal platform compatibility: **1.0.0**.
- v0.48.3 contextual navigation is unchanged.
- The three related-application cards are unchanged.
- Graph Studio front door and all v0.42–v0.48 modeling/visualization capabilities remain intact.

### Workbench boundary

This Lab release implements the shared contract, outbound transport, legacy compatibility transport, and inbound Workbench import adapter. It does not modify a separate Workbench repository in this package. A Workbench runtime that reads/writes the v0.49 contract (or the historical `sc_workbench_handoff` transport) can participate in the exchange.
