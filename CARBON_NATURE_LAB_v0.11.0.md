# Carbon & Nature Intelligence v0.11.0 — Whole-Farm GHG Balance

**Host:** Sustainable Catalyst Lab v0.94.0  
**Compute Core compatibility:** 1.0.0

## Purpose

Whole-Farm GHG Balance combines explicit emissions/removals records into a transparent farm-scale greenhouse-gas accounting result while preserving the evidence and factor provenance required to inspect how each number was produced.

## Calculation bases

1. **Direct CO2e** — a user-supplied kg CO2e quantity with explicit emission/removal direction.
2. **Gas mass** — gas mass in kg multiplied by an explicit GWP factor. CO2 is identity-converted at 1. Non-CO2 GWP factors must be supplied and sourced.
3. **Activity factor** — activity value multiplied by a user-supplied kg CO2e/unit emission factor with a required factor source reference.

## SOC integration

An optional SOC stock-change input may be converted from Mg C/ha to farm-scale CO2e using the exact mass ratio 44/12. It requires explicit area and one of these bases: `measured-change`, `scenario`, or `user-supplied-estimate`. The contribution enters the net GHG balance only when `include_in_net=true`.

This conversion does not establish causal attribution, additionality, permanence, verification, or credit eligibility.

## Main API

- `GET /v1/carbon-nature/ghg/v1100/balance/health`
- `GET /v1/carbon-nature/ghg/v1100/balance/schema`
- `GET /v1/carbon-nature/ghg/v1100/balance/policies`
- `POST /v1/carbon-nature/ghg/v1100/balance/entry`
- `POST /v1/carbon-nature/ghg/v1100/balance/calculate`
- `POST /v1/carbon-nature/ghg/v1100/balance/project-packet`

## Next build

Carbon & Nature v0.12.0 — Carbon MRV Method Registry.
