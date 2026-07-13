from __future__ import annotations

import math

from app.aerospace_engineering_flight_systems import (
    METHODS,
    VERSION,
    public_catalog,
    run_method,
)


def test_catalog_has_48_methods() -> None:
    assert VERSION == "0.18.0"
    assert public_catalog()["methodCount"] == 48
    assert len(METHODS) == 48


def test_aerodynamics_and_performance() -> None:
    dynamic_pressure = run_method(
        "af.dynamic_pressure",
        {"densityKgM3": 1, "trueAirspeedMps": 10},
    )
    assert dynamic_pressure["outputs"]["dynamicPressurePa"] == 50

    stall = run_method(
        "af.stall_speed",
        {
            "weightN": 1000,
            "densityKgM3": 1,
            "wingAreaM2": 10,
            "maximumLiftCoefficient": 2,
        },
    )
    assert stall["outputs"]["stallSpeedMps"] == 10

    turn = run_method(
        "af.coordinated_turn_load_factor",
        {"bankAngleDeg": 60},
    )
    assert math.isclose(turn["outputs"]["loadFactor"], 2)


def test_controls_propulsion_structures_and_systems() -> None:
    stability = run_method(
        "af.static_margin",
        {
            "neutralPointM": 3.2,
            "centerOfGravityM": 3.0,
            "meanAerodynamicChordM": 2,
        },
    )
    assert math.isclose(
        stability["outputs"]["staticMarginFraction"],
        0.1,
    )

    efficiency = run_method(
        "af.propeller_efficiency",
        {
            "thrustN": 1000,
            "flightSpeedMps": 50,
            "shaftPowerW": 62500,
        },
    )
    assert math.isclose(
        efficiency["outputs"]["propellerEfficiency"],
        0.8,
    )

    reliability = run_method(
        "af.dual_channel_reliability",
        {
            "channel1Reliability": 0.9,
            "channel2Reliability": 0.9,
        },
    )
    assert math.isclose(
        reliability["outputs"]["dualChannelReliability"],
        0.99,
    )
