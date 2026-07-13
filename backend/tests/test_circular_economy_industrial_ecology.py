from __future__ import annotations

import math

from app.circular_economy_industrial_ecology import (
    METHODS,
    VERSION,
    public_catalog,
    run_method,
)


def test_catalog_has_48_methods() -> None:
    assert VERSION == "0.16.0"
    assert public_catalog()["methodCount"] == 48
    assert len(METHODS) == 48


def test_material_product_and_recovery_methods() -> None:
    dmc = run_method(
        "ce.domestic_material_consumption",
        {
            "domesticExtractionTonnes": 60,
            "importsTonnes": 40,
            "exportsTonnes": 20,
        },
    )
    assert dmc["outputs"]["domesticMaterialConsumptionTonnes"] == 80

    repair = run_method(
        "ce.repair_rate",
        {"repairedUnits": 80, "failedUnits": 100},
    )
    assert repair["outputs"]["repairFraction"] == 0.8

    diversion = run_method(
        "ce.diversion_rate",
        {"divertedTonnes": 60, "generatedTonnes": 100},
    )
    assert diversion["outputs"]["diversionFraction"] == 0.6


def test_symbiosis_lifecycle_and_transition_methods() -> None:
    density = run_method(
        "ce.symbiosis_network_density",
        {"exchangeLinks": 12, "participantCount": 4},
    )
    assert density["outputs"]["networkDensity"] == 1

    carbon = run_method(
        "ce.embodied_carbon",
        {
            "virginMassKg": 10,
            "virginFactorKgCO2eKg": 2,
            "recycledMassKg": 10,
            "recycledFactorKgCO2eKg": 1,
        },
    )
    assert carbon["outputs"]["embodiedCarbonKgCO2e"] == 30

    rebound = run_method(
        "ce.rebound_adjusted_savings",
        {"grossSavingsTonnes": 100, "reboundFraction": 0.2},
    )
    assert math.isclose(
        rebound["outputs"]["adjustedSavingsTonnes"],
        80,
    )
