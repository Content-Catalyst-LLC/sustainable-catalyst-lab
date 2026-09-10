# Carbon & Nature Intelligence v0.10.0
## SOC Management Scenario Studio

**Host product:** Sustainable Catalyst Lab v0.93.0  
**Compute Core:** 1.0.0  
**Primary scientific unit:** Mg C/ha

### Purpose

The SOC Management Scenario Studio lets researchers explore how explicitly declared management assumptions would change an SOC stock trajectory through time. It builds on the v0.6 stock engine, v0.7 sampling records, v0.8 observed stock-change model, and v0.9 uncertainty layer without converting scenario assumptions into evidence.

### Models

1. `constant-annual-change` — a supplied annual change in Mg C/ha/yr.
2. `compound-relative-change` — a supplied annual relative change in %/yr.
3. `annual-change-schedule` — an explicit Mg C/ha change for every year in the horizon.

No model has a hidden default rate. Measure registry references are descriptive/provenance links only.

### Outputs

The service returns a year-indexed trajectory, final stock, cumulative projected stock change, mean annual projected stock change, optional parcel-scale totals, optional user-defined assumption envelope, deterministic fingerprints, interpretation flags, and a provenance-ready project packet.

### Boundary

**Scenario projection ≠ forecast ≠ verified sequestration.** The Studio does not establish causality, additionality, leakage, permanence, verification, methodology eligibility, credit eligibility, soil saturation capacity, CO2e, or whole-farm GHG balance.
