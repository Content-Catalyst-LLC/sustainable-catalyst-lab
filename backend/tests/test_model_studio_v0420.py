import pytest
from pathlib import Path

from app.model_studio import ModelStudioError, build_bundle, health, normalize_model, policies, preview_equation_model, validate_equation


def model():
    return {
        "title": "Exponential decay model",
        "family": "declarative-expression",
        "definition": {"equation": "y = a * exp(-k*x)"},
        "variables": [
            {"symbol": "x", "label": "Time", "unit": "h", "role": "input"},
            {"symbol": "y", "label": "Concentration", "unit": "mg/L", "role": "response"},
        ],
        "parameters": [
            {"symbol": "a", "role": "estimated", "value": 10, "bounds": {"lower": 0, "upper": 20}},
            {"symbol": "k", "role": "estimated", "value": 0.25, "bounds": {"lower": 0, "upper": 2}},
        ],
        "constants": [{"symbol": "scale", "value": 1}],
        "datasetBindings": [
            {"column": "x", "symbol": "x", "role": "feature", "unit": "h"},
            {"column": "y", "symbol": "y", "role": "response", "unit": "mg/L"},
        ],
        "assumptions": ["First-order decay over the modeled range."],
        "limitations": ["Illustrative preview parameters."],
        "provenance": {"projectId": "project-1"},
    }


def test_health_and_policy_enable_safe_declarative_execution():
    assert health()["status"] == "interactive-visualization-ready"
    assert health()["version"] == "0.46.0"
    p = policies()
    assert p["boundaries"]["safeDeclarativeExpressionExecution"] is True
    assert p["boundaries"]["arbitraryCode"] is False
    assert p["boundaries"]["arbitraryFormulaExecution"] is False


def test_model_normalization_validates_equation_and_constants():
    m = normalize_model(model())
    assert m["schema"] == "sc-lab-model-studio-model/0.46.0"
    assert m["definition"]["safeExecution"] is True
    assert m["definition"]["outputSymbol"] == "y"
    assert m["definition"]["functions"] == ["exp"]
    assert m["constants"][0]["value"] == 1
    assert len(m["modelHash"]) == 64


def test_equation_validation_endpoint_contract():
    v = validate_equation({"equation": "y = a*x^b", "variables": [{"symbol": "x"}, {"symbol": "y"}], "parameters": [{"symbol": "a"}, {"symbol": "b"}], "outputSymbol": "y"})
    assert v["ok"] is True
    assert v["executable"] is True
    assert "**" in v["equation"]


def test_preview_equation_model_builds_governed_graph():
    result = preview_equation_model({"model": model(), "rows": [{"x": 0}, {"x": 1}, {"x": 2}, {"x": 3}]})
    assert result["evaluation"]["rowCount"] == 4
    assert result["graph"]["kind"] == "line-scatter"
    assert result["graph"]["series"][0]["points"][0]["y"] == 10
    assert result["boundaries"]["arbitraryCode"] is False


def test_declarative_equation_rejects_undeclared_symbol():
    payload = model()
    payload["definition"]["equation"] = "y = a * z"
    with pytest.raises(ModelStudioError, match="Undeclared symbol"):
        normalize_model(payload)


def test_bundle_is_v0420_and_preserves_handoffs():
    b = build_bundle({"model": model()})
    assert b["schema"] == "sc-lab-model-studio-bundle/0.46.0"
    assert b["boundaries"]["safeDeclarativeExpressionExecution"] is True
    assert "workbench" in b["handoffTargets"]


def test_fastapi_routes_include_equation_validation_and_preview():
    text = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert "/v1/model-studio/equations/validate" in text
    assert "/v1/model-studio/equations/preview" in text
