from __future__ import annotations

import json
import math
from pathlib import Path

from app.biosignal_visualization_comparison import (
    VERSION,
    annotation_coverage,
    best_lag_correlation,
    compare_runs,
    contract,
    execute,
    linear_resample,
)


def equivalent(actual, expected):
    if isinstance(expected, float):
        return math.isclose(float(actual), expected, rel_tol=1e-8, abs_tol=1e-8)
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(equivalent(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(equivalent(actual[key], value) for key, value in expected.items())
    return actual == expected


def test_contract_and_benchmarks():
    data = contract()
    assert VERSION == "0.23.2"
    assert len(data["modes"]) == 8
    assert len(data["analysisMethods"]) == 16
    assert len(data["benchmarks"]) == 16
    assert len(data["annotationTypes"]) == 6
    assert data["preservedEngine"] == {"version":"0.23.0","methodCount":48,"benchmarkCount":48,"categoryCount":8}
    for benchmark in data["benchmarks"]:
        result = execute(benchmark["methodId"], benchmark["inputs"])
        assert equivalent(result["value"], benchmark["expected"]), benchmark["methodId"]


def test_resample_and_lag_detection():
    assert linear_resample([0, 1, 0], 2, 4) == [0.0, 0.5, 1.0, 0.5, 0.0]
    lag = best_lag_correlation([1,4,2,5,0,3], [4,2,5,0,3,9], 2)
    assert lag["bestLagSamples"] == 1
    assert math.isclose(lag["bestCorrelation"], 1.0)


def test_annotations_and_comparison():
    coverage = annotation_coverage(
        [
            {"type":"artifact","startSeconds":1,"endSeconds":3},
            {"type":"event","startSeconds":2,"endSeconds":4},
        ], 0, 10
    )
    assert coverage["coveredSeconds"] == 3
    assert coverage["coveragePercent"] == 30
    comparison = compare_runs([0,1,2,3], [0,1.2,1.8,3.1], 100)
    assert comparison["sampleCount"] == 4
    assert comparison["correlation"] > 0.99
    assert comparison["rootMeanSquareError"] > 0
