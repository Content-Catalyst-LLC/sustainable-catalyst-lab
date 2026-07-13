from __future__ import annotations

import math

from app.sustainable_cities_resilience import (
    METHODS,
    VERSION,
    public_catalog,
    run_method,
)


def test_catalog_has_48_methods() -> None:
    assert VERSION == "0.15.0"
    assert public_catalog()["methodCount"] == 48
    assert len(METHODS) == 48


def test_resources_mitigation_and_adaptation() -> None:
    energy = run_method(
        "sc.energy_per_capita",
        {
            "annualEnergyMWh": 8000,
            "population": 1000,
        },
    )
    assert energy["outputs"]["energyMWhPerCapitaYear"] == 8

    emissions = run_method(
        "sc.community_emissions",
        {
            "electricityTonnes": 1,
            "fuelTonnes": 2,
            "transportTonnes": 3,
            "wasteTonnes": 4,
        },
    )
    assert emissions["outputs"]["totalEmissionsTonnes"] == 10

    retention = run_method(
        "sc.stormwater_retention",
        {
            "stormDepthM": 0.05,
            "treatedAreaM2": 10000,
            "retentionFraction": 0.8,
        },
    )
    assert retention["outputs"]["retainedVolumeM3"] == 400


def test_resilience_equity_and_scenarios() -> None:
    autonomy = run_method(
        "sc.backup_autonomy",
        {
            "usableStoredEnergyKWh": 1000,
            "criticalLoadKW": 100,
        },
    )
    assert autonomy["outputs"]["autonomyHours"] == 10

    equity = run_method(
        "sc.transit_access_equity",
        {
            "priorityAccessFraction": 0.6,
            "citywideAccessFraction": 0.75,
        },
    )
    assert math.isclose(
        equity["outputs"]["accessEquityRatio"],
        0.8,
    )

    robustness = run_method(
        "sc.scenario_robustness",
        {
            "scenario1Score": 80,
            "scenario2Score": 60,
            "scenario3Score": 70,
            "targetScore": 80,
        },
    )
    assert math.isclose(
        robustness["outputs"]["robustnessFraction"],
        0.75,
    )
