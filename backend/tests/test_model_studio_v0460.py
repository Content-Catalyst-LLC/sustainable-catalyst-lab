from app.model_studio import health, policies


def test_model_studio_advances_response_surface_contract():
    p = policies()
    assert p["version"] == "0.46.0"
    assert p["modelSchema"] == "sc-lab-model-studio-model/0.46.0"
    assert p["graphSchema"] == "sc-lab-scientific-graph/0.46.0"
    assert p["boundaries"]["responseSurfaces"] is True
    assert p["boundaries"]["boundedDesignSpaceOptimization"] is True


def test_model_studio_health_advertises_design_space_capability():
    h = health()
    assert h["version"] == "0.46.0"
    assert h["responseSurfaces"] is True
    assert h["designSpaceOptimization"] is True
    assert h["arbitraryCode"] is False
