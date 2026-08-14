from app.model_studio import health, policies


def test_model_studio_advances_release_contract():
    p = policies()
    assert p["version"] == "0.46.0"
    assert p["modelSchema"] == "sc-lab-model-studio-model/0.46.0"
    assert p["graphSchema"] == "sc-lab-scientific-graph/0.46.0"
    assert p["boundaries"]["dynamicSystems"] is True
    assert p["boundaries"]["boundedDynamicParameterEstimation"] is True


def test_model_studio_health_advertises_ode_capability():
    h = health()
    assert h["version"] == "0.46.0"
    assert h["dynamicSystems"] is True
    assert h["odeParameterEstimation"] is True
    assert h["arbitraryCode"] is False
