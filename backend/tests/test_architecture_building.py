from __future__ import annotations

import math

from app.architecture_building import (
    METHODS,
    VERSION,
    public_catalog,
    run_method,
)


def test_catalog_has_48_methods() -> None:
    assert VERSION == "0.13.0"
    assert public_catalog()["methodCount"] == 48
    assert len(METHODS) == 48


def test_geometry_and_envelope() -> None:
    floor = run_method(
        "ab.floor_area",
        {"lengthM": 10, "widthM": 5, "floorCount": 2},
    )
    assert floor["outputs"]["grossFloorAreaM2"] == 100

    conduction = run_method(
        "ab.conduction_heat_loss",
        {
            "uValueWm2K": 1,
            "areaM2": 10,
            "temperatureDifferenceK": 5,
        },
    )
    assert conduction["outputs"]["heatTransferW"] == 50


def test_daylight_ventilation_energy_and_resilience() -> None:
    daylight = run_method(
        "ab.daylight_factor",
        {
            "insideIlluminanceLux": 500,
            "outsideIlluminanceLux": 10000,
        },
    )
    assert math.isclose(
        daylight["outputs"]["daylightFactor"],
        0.05,
    )

    ach = run_method(
        "ab.air_changes",
        {"airflowM3S": 1, "volumeM3": 3600},
    )
    assert ach["outputs"]["airChangesPerHour"] == 1

    eui = run_method(
        "ab.energy_use_intensity",
        {
            "annualEnergyKWh": 100000,
            "floorAreaM2": 1000,
        },
    )
    assert eui["outputs"]["euiKWhM2Year"] == 100

    resilience = run_method(
        "ab.passive_survivability",
        {"habitableHours": 60, "outageHours": 72},
    )
    assert math.isclose(
        resilience["outputs"]["autonomyFraction"],
        5 / 6,
    )
