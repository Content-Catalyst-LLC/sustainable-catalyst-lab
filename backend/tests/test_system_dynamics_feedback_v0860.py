import math
import pytest

from app.system_dynamics_feedback_v0860 import (
    SystemDynamicsV0860Error, analyze_feedback, analyze_leverage, build_workspace,
    health, normalize_causal_loop, normalize_stock_flow, policies, simulate_stock_flow,
)


def causal_model():
    return {
        "title":"Population-resource feedback",
        "variables":[
            {"id":"population"},{"id":"demand"},{"id":"resource"},{"id":"births"}
        ],
        "links":[
            {"id":"l1","source":"population","target":"demand","polarity":"+"},
            {"id":"l2","source":"demand","target":"resource","polarity":"-","delay":True},
            {"id":"l3","source":"resource","target":"population","polarity":"+"},
            {"id":"l4","source":"population","target":"births","polarity":"+"},
            {"id":"l5","source":"births","target":"population","polarity":"+"},
        ]
    }


def stock_flow_model():
    return {
        "title":"Renewable resource",
        "stocks":[{"id":"resource","initial":1000,"unit":"tonnes"}],
        "parameters":[{"id":"regen_rate","value":0.05},{"id":"harvest","value":30}],
        "auxiliaries":[{"id":"regeneration","equation":"regen_rate * resource"}],
        "flows":[
            {"id":"regen","equation":"regeneration","targetStock":"resource"},
            {"id":"extraction","equation":"harvest","sourceStock":"resource"},
        ],
        "time":{"start":0,"end":10,"dt":0.25,"method":"rk4"}
    }


def test_health_and_boundaries():
    h=health(); p=policies()
    assert h["ok"] and h["status"]=="system-dynamics-feedback-stock-flow-ready"
    assert h["v0850WebGL2Compatibility"] is True
    assert p["boundaries"]["causalLinkInference"] is False
    assert p["boundaries"]["automaticLeveragePointRanking"] is False
    assert p["boundaries"]["arbitraryCode"] is False


def test_causal_loop_normalization_and_feedback_classification():
    m=normalize_causal_loop(causal_model())
    assert len(m["fingerprint"])==64
    result=analyze_feedback(m)
    kinds={x["type"] for x in result["loops"]}
    assert "reinforcing" in kinds and "balancing" in kinds
    assert any(x["containsDelay"] for x in result["loops"])


def test_polarity_must_be_explicit():
    p=causal_model(); del p["links"][0]["polarity"]
    with pytest.raises(SystemDynamicsV0860Error): normalize_causal_loop(p)


def test_stock_flow_normalization_and_rk4_simulation():
    m=normalize_stock_flow(stock_flow_model())
    assert m["time"]["method"]=="rk4"
    r=simulate_stock_flow({"model":m})
    assert r["rowCount"]==41
    expected=600 + 400*math.exp(0.5)  # dR/dt=.05R-30, R(0)=1000
    assert abs(r["finalStocks"]["resource"]-expected) < 0.05
    assert r["boundaries"]["silentStockClamping"] is False


def test_euler_and_parameter_override():
    m=stock_flow_model(); m["time"].update({"end":2,"dt":0.1,"method":"euler"})
    r=simulate_stock_flow({"model":m,"parameterValues":{"harvest":0}})
    assert r["finalStocks"]["resource"] > 1000


def test_auxiliary_algebraic_cycle_rejected():
    m=stock_flow_model(); m["auxiliaries"]=[{"id":"a","equation":"b+1"},{"id":"b","equation":"a+1"}]
    m["flows"][0]["equation"]="a"
    with pytest.raises(SystemDynamicsV0860Error, match="algebraic dependency cycle"):
        normalize_stock_flow(m)


def test_no_silent_stock_clamp():
    m=stock_flow_model(); m["parameters"][1]["value"]=1000; m["time"].update({"end":2,"dt":1,"method":"euler"})
    r=simulate_stock_flow(m)
    assert r["finalStocks"]["resource"] < 0


def test_structural_leverage_is_not_normative_ranking():
    r=analyze_leverage({"causalModel":causal_model(),"interventions":[{"target":"demand","category":"information-flows"}]})
    assert r["indicators"]
    assert all(x["structuralIndicatorOnly"] for x in r["indicators"])
    assert r["boundaries"]["automaticLeveragePointRanking"] is False
    assert r["boundaries"]["policyRecommendation"] is False


def test_workspace_links_to_graph_studio_without_changing_semantics():
    r=build_workspace({"title":"Meadows model","causalModel":causal_model(),"stockFlowModel":stock_flow_model()})
    w=r["workspace"]
    assert w["graphStudio"]["compatible"] is True
    assert w["graphStudio"]["preferredRenderer"]=="webgl2"
    assert len(w["fingerprint"])==64
