import math

import pytest

from app.dynamic_systems import DynamicSystemError, estimate_parameters, health, normalize_definition, policies, simulate, templates


def exponential_system(k=0.4):
    return {
        "title": "Decay",
        "independentVariable": {"symbol": "t", "label": "Time", "unit": "s"},
        "states": [{"symbol": "X", "label": "Quantity", "initial": 10.0}],
        "parameters": [{"symbol": "k", "role": "estimated", "value": k, "bounds": {"lower": 0.0, "upper": 2.0}}],
        "equations": [{"state": "X", "rhs": "-k*X"}],
        "timeSpan": {"start": 0, "end": 5, "points": 101},
        "solver": {"method": "RK45", "rtol": 1e-8, "atol": 1e-10},
    }


def test_health_and_policy_boundaries():
    assert health()["status"] == "dynamic-systems-ready"
    p = policies()
    assert p["version"] == "0.45.0"
    assert p["capabilities"]["coupledODEs"] is True
    assert p["capabilities"]["boundedParameterEstimation"] is True
    assert p["boundaries"]["arbitraryCode"] is False
    assert "BDF" in p["solvers"]


def test_normalizes_safe_derivative_equation():
    model = normalize_definition(exponential_system())
    assert model["schema"] == "sc-lab-dynamic-system/0.45.0"
    assert model["equations"][0]["equation"] == "dX_dt = -k*X"
    assert model["boundaries"]["arbitraryCode"] is False
    assert len(model["systemHash"]) == 64


def test_rejects_unsafe_attribute_access():
    payload = exponential_system()
    payload["equations"][0]["rhs"] = "X.__class__"
    with pytest.raises(DynamicSystemError):
        normalize_definition(payload)


def test_rejects_unknown_state_equation():
    payload = exponential_system()
    payload["equations"][0]["state"] = "Y"
    with pytest.raises(DynamicSystemError):
        normalize_definition(payload)


def test_exponential_decay_simulation_matches_analytic_solution():
    result = simulate({"system": exponential_system(0.4)})["simulation"]
    rows = result["rows"]
    assert len(rows) == 101
    assert rows[0]["X"] == pytest.approx(10.0)
    assert rows[-1]["X"] == pytest.approx(10.0 * math.exp(-2.0), rel=2e-5)
    assert result["solver"]["success"] is True
    assert result["graphs"]["trajectory"]["schema"] == "sc-lab-scientific-graph/0.45.0"
    assert result["graphs"]["phasePortrait"] is None


def test_logistic_growth_remains_bounded_and_monotonic():
    system = templates()["templates"]["logistic-growth"]
    result = simulate({"system": system})["simulation"]
    vals = [row["N"] for row in result["rows"]]
    assert vals[0] == pytest.approx(10.0)
    assert vals[-1] < 100.0001
    assert vals[-1] > 99.0
    assert all(b >= a for a, b in zip(vals, vals[1:]))


def test_sir_conserves_population_and_builds_phase_portrait():
    system = templates()["templates"]["sir"]
    result = simulate({"system": system})["simulation"]
    for row in result["rows"][::40]:
        assert row["S"] + row["I"] + row["R"] == pytest.approx(1000.0, abs=1e-4)
    assert result["graphs"]["phasePortrait"] is not None
    assert len(result["graphs"]["trajectory"]["series"]) == 3


def test_parameter_estimation_recovers_decay_rate():
    true_k = 0.4
    observations = []
    for i in range(11):
        t = i * 0.5
        observations.append({"t": t, "X": 10.0 * math.exp(-true_k * t)})
    system = exponential_system(0.18)
    result = estimate_parameters({"system": system, "observations": observations, "observedStates": ["X"], "loss": "linear", "maxEvaluations": 500})["estimation"]
    estimate = result["estimatedParameters"][0]
    assert estimate["symbol"] == "k"
    assert estimate["value"] == pytest.approx(true_k, rel=2e-4)
    assert result["metrics"]["rmse"] < 1e-5
    assert result["metrics"]["rSquared"] > 0.999999
    assert result["identifiability"]["jacobianRank"] == 1
    assert result["graphs"]["fit"]["series"][0]["mode"] == "line"
    assert result["graphs"]["fit"]["series"][1]["mode"] == "scatter"


def test_fixed_parameter_is_not_estimated():
    system = exponential_system(0.4)
    system["parameters"][0]["role"] = "fixed"
    observations = [{"t": 0, "X": 10}, {"t": 1, "X": 7}, {"t": 2, "X": 4.5}]
    with pytest.raises(DynamicSystemError, match="At least one parameter"):
        estimate_parameters({"system": system, "observations": observations})


def test_observations_cannot_precede_initial_time():
    system = exponential_system()
    with pytest.raises(DynamicSystemError, match="precede"):
        estimate_parameters({"system": system, "observations": [{"t": -1, "X": 11}, {"t": 0, "X": 10}, {"t": 1, "X": 6}]})


def test_templates_include_core_dynamic_system_families():
    keys = set(templates()["templates"])
    assert {"exponential-decay", "logistic-growth", "sir", "predator-prey"}.issubset(keys)
