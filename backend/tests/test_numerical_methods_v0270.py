from __future__ import annotations

import math

import numpy as np
import pytest

from app.compute import run_compute
from app.registry import catalog, resolve
from app.schemas import ComputeRequest


def run(method: str, inputs: dict, parameters: dict | None = None, seed: int | None = 7):
    return run_compute(
        ComputeRequest(method=method, inputs=inputs, parameters=parameters or {}, random_seed=seed),
        {"mode": "test", "client": "pytest"},
    ).outputs


def test_registry_exposes_numerical_methods_and_examples():
    rows = {row["id"]: row for row in catalog()}
    expected = {
        "numerics.root_scalar_polynomial",
        "numerics.adaptive_quadrature_polynomial",
        "numerics.interpolation",
        "numerics.ode_first_order",
        "numerics.eigen_analysis",
        "optimization.scalar_bounded",
        "optimization.linear_program",
        "signal.fft_spectrum",
        "uncertainty.monte_carlo_propagation",
        "uncertainty.bootstrap_mean_interval",
        "sensitivity.local_finite_difference",
        "simulation.parameter_sweep",
    }
    assert expected.issubset(rows)
    for method_id in expected:
        assert rows[method_id]["example_inputs"]
        assert rows[method_id]["recommended_execution"] in {"synchronous", "queued"}


def test_root_scalar_polynomial():
    output = run("numerics.root_scalar_polynomial", {"coefficients": [1, 0, -2], "bracket": [0, 2]})
    assert output["converged"] is True
    assert output["root"] == pytest.approx(math.sqrt(2), rel=1e-9)
    assert abs(output["functionValue"]) < 1e-9


def test_adaptive_quadrature_polynomial_matches_exact():
    output = run("numerics.adaptive_quadrature_polynomial", {"coefficients": [3, 0, 2], "lower": 0, "upper": 2})
    assert output["integral"] == pytest.approx(12.0, rel=1e-10)
    assert output["polynomialExactIntegral"] == pytest.approx(12.0)


def test_interpolation_pchip():
    output = run("numerics.interpolation", {"x": [0, 1, 2, 3, 4], "y": [0, 1, 4, 9, 16], "query": [0.5, 1.5]}, {"kind": "pchip"})
    assert output["kind"] == "pchip"
    assert len(output["values"]) == 2
    assert all(math.isfinite(value) for value in output["values"])


def test_logistic_ode_converges_toward_capacity():
    output = run("numerics.ode_first_order", {"model": "logistic", "initialValue": 10, "startTime": 0, "endTime": 20, "points": 101}, {"rate": 0.35, "carryingCapacity": 100})
    assert output["success"] is True
    assert 90 < output["finalValue"] < 100
    assert len(output["time"]) == 101


def test_eigen_analysis_residuals_are_small():
    output = run("numerics.eigen_analysis", {"matrix": [[2, 1], [1, 2]]})
    assert output["symmetric"] is True
    assert sorted(output["eigenvalues"]) == pytest.approx([1, 3])
    assert max(output["residualNorms"]) < 1e-10


def test_bounded_optimization_finds_quadratic_minimum():
    output = run("optimization.scalar_bounded", {"objective": "quadratic", "lower": -10, "upper": 10, "coefficients": [1, -4, 7]})
    assert output["success"] is True
    assert output["x"] == pytest.approx(2, abs=1e-5)
    assert output["minimum"] == pytest.approx(3, abs=1e-5)


def test_linear_program_solution():
    output = run("optimization.linear_program", {"objective": [-3, -2], "inequalityMatrix": [[2, 1], [1, 2]], "inequalityVector": [18, 16], "bounds": [[0, None], [0, None]]})
    assert output["success"] is True
    assert output["objectiveMinimum"] == pytest.approx(-29.3333333333, rel=1e-8)
    assert output["solution"] == pytest.approx([20 / 3, 14 / 3], rel=1e-8)


def test_fft_detects_expected_frequency():
    sample_rate = 128
    time = np.arange(128) / sample_rate
    values = np.sin(2 * np.pi * 12 * time)
    output = run("signal.fft_spectrum", {"values": values.tolist(), "sampleRate": sample_rate}, {"window": "hann"})
    assert output["peakFrequencyHz"] == pytest.approx(12, abs=1)


def test_monte_carlo_is_seed_reproducible():
    inputs = {"model": "product", "samples": 5000, "distributions": [{"name": "a", "distribution": "normal", "mean": 10, "stdDev": 1}, {"name": "b", "distribution": "uniform", "lower": 2, "upper": 4}]}
    first = run("uncertainty.monte_carlo_propagation", inputs, {"confidence": 0.95}, seed=17)
    second = run("uncertainty.monte_carlo_propagation", inputs, {"confidence": 0.95}, seed=17)
    assert first == second
    assert first["confidenceInterval"][0] < first["mean"] < first["confidenceInterval"][1]


def test_bootstrap_interval_is_seed_reproducible():
    inputs = {"values": [12.1, 11.8, 12.5, 12.0, 11.9, 12.3, 12.2, 11.7], "resamples": 1000}
    output = run("uncertainty.bootstrap_mean_interval", inputs, {"confidence": 0.95}, seed=22)
    assert output["confidenceInterval"][0] < output["sampleMean"] < output["confidenceInterval"][1]
    assert output["seed"] == 22


def test_local_sensitivity_product_derivatives():
    output = run("sensitivity.local_finite_difference", {"model": "product", "baseline": {"x": 2, "y": 3}})
    rows = {row["variable"]: row for row in output["sensitivities"]}
    assert output["baselineOutput"] == pytest.approx(6)
    assert rows["x"]["derivative"] == pytest.approx(3, rel=1e-5)
    assert rows["y"]["derivative"] == pytest.approx(2, rel=1e-5)


def test_parameter_sweep_returns_ordered_rows():
    output = run("simulation.parameter_sweep", {"model": "logistic_growth", "parameter": "rate", "values": [0.1, 0.2, 0.3], "fixed": {"initial": 10, "carryingCapacity": 100, "time": 10}})
    assert len(output["rows"]) == 3
    assert output["monotonicIncreasing"] is True


def test_aliases_resolve():
    assert resolve("ode").id == "numerics.ode_first_order"
    assert resolve("fft").id == "signal.fft_spectrum"
