# Sustainable Catalyst Lab v0.19.0 — Rocket Propulsion and Spaceflight

Version 0.19.0 adds a first-class Rocket Propulsion and Spaceflight workspace with 48 auditable methods and 45 deterministic browser benchmarks.

## Workspaces

- Rocket propulsion fundamentals
- Nozzle flow and engine performance
- Launch-vehicle mass and staging
- Ascent and launch dynamics
- Orbital mechanics and transfers
- Spacecraft and mission systems

## Capabilities

The release covers effective exhaust velocity, specific impulse, thrust, mass flow, the ideal rocket equation, mass ratio, propellant fraction, mixture ratio, nozzle throat and expansion geometry, isentropic exit conditions, momentum and pressure thrust, thrust coefficient, characteristic velocity, structural coefficient, payload fraction, stage delta-v, staging totals, burnout acceleration, burn duration, liftoff thrust-to-weight, dynamic pressure, ballistic coefficient, ascent drag, gravity and drag losses, net ascent delta-v, circular and escape velocity, orbital period, vis-viva velocity, Hohmann transfers, plane changes, mission delta-v budgets, propellant reserve, solar-array area, battery capacity, radiator sizing, equilibrium temperature, free-space path loss, and mission reliability.

## Formula-visible interface

Every method displays:

- a human-readable propulsion, flight-dynamics, orbital, or spacecraft-system equation
- each executable output expression
- input labels and units
- output labels and units
- assumptions and engineering-screening warnings
- deterministic validation and audit metadata
- project, notebook, and visualization handoffs

## Focused shortcode

`[sc_lab_rocket_propulsion_spaceflight]`

The main `[sc_lab_app]` interface also receives the workspace.

## Project schema

The project schema advances to `0.19.0` and adds:

- `rocketPropulsionSpaceflightAnalyses`
- `spaceflightSystemsRecords`
- `rocketSpaceflightValidationRecords`
- `propulsionFundamentalsRecords`
- `nozzleEngineRecords`
- `launchVehicleStagingRecords`
- `ascentDynamicsRecords`
- `orbitalMechanicsRecords`
- `spacecraftMissionRecords`
- `spaceflightReliabilityRecords`
- `missionDeltaVRecords`

## Responsible-use boundary

These methods support transparent education, documentation, and preliminary civil-space systems analysis. They do not replace tested engine data, detailed combustion or turbomachinery models, structural and thermal qualification, range-safety analysis, launch licensing, flight-software verification, mission assurance, operational launch procedures, or qualified propulsion, aerospace, and spaceflight engineering judgment. The workspace is not intended for weapon design or targeting.
