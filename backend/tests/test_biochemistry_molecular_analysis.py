from __future__ import annotations

import math

import pytest

from app.biochemistry_molecular_analysis import (
    CATALOG,
    BiochemistryMolecularAnalysisError,
    run_method,
)


def close_enough(
    actual: float,
    expected: float,
    absolute: float,
    relative: float,
) -> bool:
    difference = abs(actual - expected)
    scale = max(abs(actual), abs(expected), 1.0)
    return (
        difference <= absolute
        or difference <= relative * scale
    )


def test_catalog_has_48_formula_visible_methods() -> None:
    assert CATALOG["version"] == "0.21.0"
    assert len(CATALOG["methods"]) == 48
    assert len(CATALOG["benchmarks"]) == 48

    for method in CATALOG["methods"]:
        assert method["id"].startswith("bc.")
        assert method["equation"]
        assert method["inputs"]
        assert method["outputs"]


def test_all_benchmarks() -> None:
    for benchmark in CATALOG["benchmarks"]:
        result = run_method(
            benchmark["methodId"],
            benchmark["inputs"],
        )

        for key, expected in benchmark["expected"].items():
            actual = result["outputs"][key]

            assert math.isfinite(actual)
            assert close_enough(
                actual,
                expected,
                benchmark["absoluteTolerance"],
                benchmark["relativeTolerance"],
            ), benchmark["id"]


def test_michaelis_menten_reference() -> None:
    result = run_method(
        "bc.michaelis_menten",
        {
            "vmax": 100,
            "substrate": 2,
            "km": 0.5,
        },
    )

    assert result["outputs"]["velocity"] == pytest.approx(80)


def test_unknown_method_is_rejected() -> None:
    with pytest.raises(BiochemistryMolecularAnalysisError):
        run_method("bc.unknown", {})
