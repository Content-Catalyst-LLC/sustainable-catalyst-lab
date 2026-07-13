from __future__ import annotations

import math

from app.rocket_propulsion_spaceflight import (
    METHODS,
    VERSION,
    public_catalog,
    run_method,
)


def test_catalog_has_48_methods() -> None:
    assert VERSION == "0.19.0"
    assert public_catalog()["methodCount"] == 48
    assert len(METHODS) == 48


def test_propulsion_nozzle_and_staging() -> None:
    delta_v = run_method(
        "rp.ideal_rocket_delta_v",
        {
            "effectiveExhaustVelocityMps": 1000,
            "initialMassKg": math.e,
            "finalMassKg": 1,
        },
    )
    assert math.isclose(delta_v["outputs"]["idealDeltaVMps"], 1000)

    nozzle = run_method(
        "rp.nozzle_total_thrust",
        {
            "massFlowKgS": 10,
            "exitVelocityMps": 100,
            "exitPressurePa": 2,
            "ambientPressurePa": 1,
            "exitAreaM2": 5,
        },
    )
    assert nozzle["outputs"]["totalThrustN"] == 1005

    stage = run_method(
        "rp.stage_ideal_delta_v",
        {
            "specificImpulseS": 100,
            "standardGravityMps2": 10,
            "initialStageMassKg": math.e,
            "finalStageMassKg": 1,
        },
    )
    assert math.isclose(stage["outputs"]["stageIdealDeltaVMps"], 1000)


def test_ascent_orbit_and_spacecraft_systems() -> None:
    ascent = run_method(
        "rp.net_ascent_delta_v",
        {
            "idealDeltaVMps": 1000,
            "gravityLossMps": 100,
            "dragLossMps": 50,
            "steeringLossMps": 25,
        },
    )
    assert ascent["outputs"]["netAscentDeltaVMps"] == 825

    orbit = run_method(
        "rp.circular_orbit_velocity",
        {
            "gravitationalParameterM3S2": 100,
            "orbitalRadiusM": 4,
        },
    )
    assert orbit["outputs"]["circularVelocityMps"] == 5

    power = run_method(
        "rp.solar_array_area",
        {
            "requiredElectricalPowerW": 100,
            "solarFluxWm2": 100,
            "cellEfficiency": 0.5,
            "degradationFactor": 1,
            "incidenceFactor": 1,
        },
    )
    assert power["outputs"]["requiredSolarArrayAreaM2"] == 2
