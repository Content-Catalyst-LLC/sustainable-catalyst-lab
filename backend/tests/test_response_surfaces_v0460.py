import math
import pytest

from app.response_surfaces import ResponseSurfaceError, explore, fit, health, normalize_study, optimize, policies


def study():
    return {
        "title": "Catalyst yield response surface",
        "factors": [
            {"symbol": "T", "label": "Temperature", "unit": "C", "low": 20, "high": 80},
            {"symbol": "P", "label": "Pressure", "unit": "bar", "low": 1, "high": 9},
        ],
        "response": {"symbol": "Yield", "label": "Yield", "unit": "%"},
    }


def coded(v, lo, hi):
    return (v - (lo + hi) / 2) / ((hi - lo) / 2)


def rows():
    data = []
    for T in (20, 50, 80):
        for P in (1, 5, 9):
            x = coded(T, 20, 80)
            y = coded(P, 1, 9)
            response = 100 - 10 * x * x - 5 * y * y + 2 * x - y + 1.5 * x * y
            data.append({"T": T, "P": P, "Yield": response})
    # Center replicates create pure-error degrees of freedom for lack-of-fit testing.
    data += [{"T": 50, "P": 5, "Yield": 100.1}, {"T": 50, "P": 5, "Yield": 99.9}]
    return data


def test_health_and_policy_contract():
    assert health()["version"] == "0.46.0"
    p = policies()
    assert p["capabilities"]["quadraticTerms"] is True
    assert p["capabilities"]["boundedOptimization"] is True
    assert p["boundaries"]["arbitraryCode"] is False


def test_normalize_requires_bounded_factors():
    s = normalize_study(study())
    assert s["schema"] == "sc-lab-response-surface-study/0.46.0"
    assert len(s["factors"]) == 2
    with pytest.raises(ResponseSurfaceError, match="Upper bound"):
        normalize_study({"factors": [{"symbol": "a", "low": 1, "high": 1}, {"symbol": "b", "low": 0, "high": 1}], "response": "y"})


def test_full_second_order_fit_and_inference():
    result = fit({"study": study(), "rows": rows()})["result"]
    assert result["schema"] == "sc-lab-response-surface-result/0.46.0"
    assert result["metrics"]["r2"] > 0.9999
    assert len(result["coefficients"]) == 6
    assert result["designMatrix"]["rank"] == 6
    assert result["lackOfFit"]["available"] is True
    assert result["graphs"]["observedPredicted"]["kind"] == "line-scatter"
    assert result["graphs"]["coefficients"]["kind"] == "horizontal-bars"


def test_design_space_heatmap_and_feasibility():
    result = fit({"study": study(), "rows": rows()})["result"]
    e = explore({"result": result, "xFactor": "T", "yFactor": "P", "gridSize": 21, "responseConstraint": {"minimum": 90}})["exploration"]
    assert e["schema"] == "sc-lab-design-space-exploration/0.46.0"
    assert e["totalCells"] == 441
    assert 0 < e["feasibleFraction"] < 1
    assert e["graph"]["kind"] == "heatmap"
    assert len(e["graph"]["cells"]) == 441


def test_bounded_optimization_finds_interior_quadratic_optimum():
    result = fit({"study": study(), "rows": rows()})["result"]
    o = optimize({"result": result, "goal": "maximize", "seed": 7, "maxIterations": 120})["optimization"]
    assert o["schema"] == "sc-lab-design-space-optimization/0.46.0"
    # Analytic optimum in coded space is near x=.094, y=-.086 for this surface.
    assert 45 < o["optimumFactors"]["T"] < 60
    assert 3 < o["optimumFactors"]["P"] < 6
    assert o["predictedResponse"] > 99
    assert o["solver"]["functionEvaluations"] > 0


def test_fit_rejects_out_of_design_space_rows():
    bad = rows() + [{"T": 100, "P": 5, "Yield": 80}]
    with pytest.raises(ResponseSurfaceError, match="outside the declared design-space"):
        fit({"study": study(), "rows": bad})
