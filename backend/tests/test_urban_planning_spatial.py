from __future__ import annotations

import math

from app.urban_planning_spatial import (
    METHODS,
    VERSION,
    public_catalog,
    run_method,
)


def test_catalog_has_48_methods() -> None:
    assert VERSION == "0.14.0"
    assert public_catalog()["methodCount"] == 48
    assert len(METHODS) == 48


def test_land_use_accessibility_and_networks() -> None:
    density = run_method(
        "up.gross_population_density",
        {"population": 1000, "grossAreaHa": 20},
    )
    assert density["outputs"]["personsPerHa"] == 50

    accessible = run_method(
        "up.cumulative_opportunities",
        {
            "opportunitiesZone1": 100,
            "timeZone1Min": 10,
            "opportunitiesZone2": 200,
            "timeZone2Min": 40,
            "opportunitiesZone3": 300,
            "timeZone3Min": 20,
            "thresholdMin": 30,
        },
    )
    assert accessible["outputs"]["accessibleOpportunities"] == 400

    network = run_method(
        "up.network_beta_index",
        {"edges": 30, "vertices": 20},
    )
    assert network["outputs"]["betaIndex"] == 1.5


def test_gis_services_and_scenarios() -> None:
    ndvi = run_method(
        "up.ndvi",
        {"nirReflectance": 0.6, "redReflectance": 0.2},
    )
    assert math.isclose(ndvi["outputs"]["ndvi"], 0.5)

    response = run_method(
        "up.emergency_response_time",
        {
            "dispatchDelayMin": 2,
            "networkDistanceKm": 6,
            "averageSpeedKmH": 36,
        },
    )
    assert response["outputs"]["responseTimeMin"] == 12

    growth = run_method(
        "up.population_growth_rate",
        {
            "startPopulation": 100,
            "endPopulation": 121,
            "years": 2,
        },
    )
    assert math.isclose(
        growth["outputs"]["annualGrowthRate"],
        0.1,
    )
