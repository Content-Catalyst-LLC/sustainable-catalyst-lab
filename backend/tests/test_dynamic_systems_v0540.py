import math
import pytest

from app.dynamic_systems_v0540 import (
    DynamicSystemsV0540Error,
    bifurcation_scan,
    health,
    normalize_study,
    phase_analysis,
    policies,
    simulate,
)


def logistic():
    return {
        "title":"Logistic growth","independentVariable":{"symbol":"t","label":"Time","unit":"day"},
        "states":[{"symbol":"N","label":"Population","initial":10.0}],
        "parameters":[
            {"symbol":"r","value":0.5,"bounds":{"lower":0.0,"upper":2.0}},
            {"symbol":"K","value":100.0,"bounds":{"lower":20.0,"upper":200.0}},
        ],
        "equations":[{"state":"N","rhs":"r*N*(1-N/K)"}],
        "timeSpan":{"start":0.0,"end":20.0,"points":121},
    }


def predator_prey():
    return {
        "title":"Predator prey","independentVariable":{"symbol":"t","label":"Time"},
        "states":[{"symbol":"X","initial":4.0},{"symbol":"Y","initial":2.0}],
        "parameters":[
            {"symbol":"a","value":1.0,"bounds":{"lower":0.1,"upper":2.0}},
            {"symbol":"b","value":0.5,"bounds":{"lower":0.1,"upper":2.0}},
            {"symbol":"d","value":0.5,"bounds":{"lower":0.1,"upper":2.0}},
            {"symbol":"g","value":1.0,"bounds":{"lower":0.1,"upper":2.0}},
        ],
        "equations":[{"state":"X","rhs":"a*X-b*X*Y"},{"state":"Y","rhs":"d*X*Y-g*Y"}],
        "timeSpan":{"start":0.0,"end":15.0,"points":151},
    }


def test_policy_contract_exposes_advanced_dynamics_without_code_execution():
    p=policies(); h=health()
    assert p["version"] == "0.54.0"
    assert p["capabilities"]["safeStateEvents"] is True
    assert p["capabilities"]["numericalBifurcationScans"] is True
    assert p["boundaries"]["arbitraryCode"] is False
    assert h["status"] == "dynamic-systems-ii-ready"


def test_normalize_accepts_safe_events_and_regimes():
    study=normalize_study({"system":logistic(),"events":[{"label":"Half capacity","expression":"N-50","direction":1}],"regimes":[{"time":10,"label":"Policy shift","parameterValues":{"r":0.2},"evidence":"scenario record"}]})
    assert study["schema"].endswith("/0.54.0")
    assert study["events"][0]["normalizedExpression"].startswith("event_0 =")
    assert study["regimes"][0]["parameterValues"]["r"] == 0.2


def test_event_expression_rejects_arbitrary_python():
    with pytest.raises(DynamicSystemsV0540Error):
        normalize_study({"system":logistic(),"events":[{"expression":"__import__('os').system('id')"}]})


def test_regime_change_must_respect_parameter_bounds():
    with pytest.raises(DynamicSystemsV0540Error):
        normalize_study({"system":logistic(),"regimes":[{"time":10,"parameterValues":{"r":9.0}}]})


def test_advanced_simulation_detects_event_and_applies_regime():
    result=simulate({"system":logistic(),"events":[{"label":"N50","expression":"N-50","direction":1}],"regimes":[{"time":10,"parameterValues":{"r":0.2},"evidence":"declared scenario"}]})["simulation"]
    assert result["rowCount"] >= 100
    assert any(e["label"] == "N50" for e in result["eventsDetected"])
    assert result["regimesApplied"][0]["parameterValues"]["r"] == 0.2
    assert result["graphs"]["trajectory"]["annotations"]


def test_terminal_event_stops_simulation():
    result=simulate({"system":logistic(),"events":[{"label":"Stop at 30","expression":"N-30","direction":1,"terminal":True}]})["simulation"]
    assert result["terminalEventReached"] is True
    assert result["terminalTime"] < 20
    assert result["rows"][-1]["t"] <= result["terminalTime"] + 1e-6


def test_bifurcation_scan_is_bounded_and_returns_tail_evidence():
    result=bifurcation_scan({"system":logistic(),"sweep":{"parameter":"r","lower":0.1,"upper":1.0,"points":7,"state":"N","transientFraction":0.7}})["analysis"]
    assert len(result["rows"]) == 7
    assert all(math.isfinite(r["tailMean"]) for r in result["rows"])
    assert "formal bifurcation proof" in result["interpretationBoundary"]


def test_bifurcation_scan_blocks_events_and_regime_schedule():
    with pytest.raises(DynamicSystemsV0540Error):
        bifurcation_scan({"system":logistic(),"events":[{"expression":"N-50"}],"sweep":{"parameter":"r","lower":0.1,"upper":1.0,"points":5}})


def test_phase_analysis_finds_equilibria_and_local_stability_evidence():
    result=phase_analysis({"system":predator_prey(),"domain":{"x":{"min":0,"max":5,"points":17},"y":{"min":0,"max":4,"points":17}}})["analysis"]
    assert result["equilibriumCount"] >= 2
    assert any(abs(e["stateValues"]["X"]-2.0) < 1e-3 and abs(e["stateValues"]["Y"]-2.0) < 1e-3 for e in result["equilibria"])
    assert result["graphs"]["speedHeatmap"]["kind"] == "heatmap"
    assert result["graphs"]["phasePlane"]["kind"] == "line-scatter"
