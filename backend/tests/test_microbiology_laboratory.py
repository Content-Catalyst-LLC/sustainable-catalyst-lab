from __future__ import annotations

import math

from app.microbiology_laboratory import (
    METHODS,
    VERSION,
    public_catalog,
    run_method,
)


def test_catalog_has_48_methods() -> None:
    assert VERSION == "0.20.0"
    assert public_catalog()["methodCount"] == 48
    assert len(METHODS) == 48


def test_growth_culture_and_enumeration() -> None:
    generation = run_method(
        "mb.generation_time",
        {"specificGrowthRatePerHour": math.log(2)},
    )
    assert math.isclose(
        generation["outputs"]["generationTimeHours"],
        1,
    )

    monod = run_method(
        "mb.monod_growth_rate",
        {
            "maximumGrowthRatePerHour": 1,
            "substrateConcentrationMgL": 10,
            "halfSaturationMgL": 10,
        },
    )
    assert monod["outputs"]["specificGrowthRatePerHour"] == 0.5

    cfu = run_method(
        "mb.cfu_per_ml",
        {
            "colonyCount": 100,
            "platedVolumeMl": 0.1,
            "sampleDilution": 0.001,
        },
    )
    assert cfu["outputs"]["cfuPerMl"] == 1000000


def test_environmental_antimicrobial_and_ecology() -> None:
    removal = run_method(
        "mb.removal_efficiency",
        {
            "influentConcentration": 100,
            "effluentConcentration": 20,
        },
    )
    assert removal["outputs"]["removalFraction"] == 0.8

    fici = run_method(
        "mb.fic_index",
        {
            "micACombination": 1,
            "micAAlone": 4,
            "micBCombination": 2,
            "micBAlone": 8,
        },
    )
    assert fici["outputs"]["fractionalInhibitoryConcentrationIndex"] == 0.5

    diversity = run_method(
        "mb.simpson_diversity",
        {
            "proportion1": 0.25,
            "proportion2": 0.25,
            "proportion3": 0.25,
            "proportion4": 0.25,
        },
    )
    assert diversity["outputs"]["simpsonDiversity"] == 0.75
