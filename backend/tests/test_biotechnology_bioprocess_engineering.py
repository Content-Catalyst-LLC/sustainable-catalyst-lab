from __future__ import annotations

import math

from app.biotechnology_bioprocess_engineering import (
    VERSION,
    catalog,
    run_batch,
    run_method,
    simulate,
)


def test_catalog_and_all_benchmarks() -> None:
    contract = catalog()

    assert VERSION == "0.22.0"
    assert contract["methodCount"] == 48
    assert contract["benchmarkCount"] == 48
    assert len(contract["methods"]) == 48
    assert len(contract["benchmarks"]) == 48
    assert len(contract["categories"]) == 8

    for benchmark in contract["benchmarks"]:
        result = run_method(
            benchmark["methodId"],
            benchmark["inputs"],
        )
        actual = result["outputs"]["result"]
        expected = benchmark["expected"]["result"]
        tolerance = benchmark["tolerance"] * max(
            1.0,
            abs(expected),
        )
        assert math.isclose(
            actual,
            expected,
            rel_tol=0.0,
            abs_tol=tolerance,
        ), benchmark["methodId"]


def test_batch_execution() -> None:
    result = run_batch(
        "bp.batch_productivity",
        [
            {
                "sample": "run-1",
                "product_concentration": 18,
                "batch_time": 36,
            },
            {
                "sample": "run-2",
                "product_concentration": 19,
                "batch_time": 36,
            },
            {
                "sample": "run-3",
                "product_concentration": 17,
                "batch_time": 36,
            },
        ],
    )

    assert result["rowCount"] == 3
    assert result["successCount"] == 3
    assert result["errorCount"] == 0
    assert result["statistics"]["n"] == 3


def test_reactor_simulations() -> None:
    batch = simulate(
        "batch",
        {
            "x0": 1,
            "mu": 0.3,
            "time": 24,
            "substrate0": 40,
            "yieldXs": 0.5,
            "yieldPs": 0.2,
        },
    )
    fed_batch = simulate(
        "fed-batch",
        {
            "initialVolume": 5,
            "initialFeedRate": 0.05,
            "muSet": 0.15,
            "feedConcentration": 500,
            "x0": 2,
            "time": 24,
        },
    )
    continuous = simulate(
        "continuous",
        {
            "volume": 10,
            "flowRate": 1.5,
            "muMax": 0.5,
            "ks": 0.5,
            "feedSubstrate": 20,
            "yieldXs": 0.5,
            "productConcentration": 12,
        },
    )

    assert len(batch["points"]) == 41
    assert batch["summary"]["biomass"] > 1
    assert len(fed_batch["points"]) == 41
    assert fed_batch["summary"]["volume"] > 5
    assert continuous["summary"]["washout"] is False
    assert continuous["summary"]["biomass"] > 0
