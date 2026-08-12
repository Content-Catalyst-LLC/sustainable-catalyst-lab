import math
import pytest

from app.equation_builder import EquationBuilderError, catalog, compile_equation, evaluate, evaluate_rows, validate_definition


def definition(equation="y = a * exp(-k*x)"):
    return {
        "equation": equation,
        "variables": [{"symbol": "x"}, {"symbol": "y"}],
        "parameters": [{"symbol": "a"}, {"symbol": "k"}],
        "constants": [],
        "outputSymbol": "y",
    }


def test_catalog_exposes_safe_grammar_not_arbitrary_code():
    c = catalog()
    assert c["version"] == "0.42.0"
    assert "exp" in c["functions"]
    assert c["boundaries"]["arbitraryPython"] is False
    assert c["boundaries"]["attributes"] is False


def test_validate_and_evaluate_exponential_equation():
    v = validate_definition(definition())
    assert v["executable"] is True
    assert v["outputSymbol"] == "y"
    assert v["functions"] == ["exp"]
    rows = evaluate_rows({"definition": definition(), "values": {"a": 10, "k": 0.25}, "rows": [{"x": 0}, {"x": 2}]})
    assert rows["rowCount"] == 2
    assert rows["rows"][0]["y"] == 10
    assert rows["rows"][1]["y"] == pytest.approx(10 * math.exp(-0.5))


def test_caret_is_normalized_as_scientific_power():
    compiled = compile_equation("y = a*x^k", {"x", "y", "a", "k"}, "y")
    assert "**" in compiled.normalized
    assert evaluate(compiled, {"a": 2, "x": 3, "k": 2}) == 18


@pytest.mark.parametrize("equation", [
    "y = x.__class__",
    "y = x[0]",
    "y = unknown(x)",
    "y = z + 1",
    "y = (lambda q: q)(x)",
    "y = __import__('os')",
])
def test_rejects_unsafe_or_undeclared_syntax(equation):
    with pytest.raises(EquationBuilderError):
        validate_definition(definition(equation))


def test_rejects_algebraic_self_reference():
    with pytest.raises(EquationBuilderError, match="cannot reference itself"):
        validate_definition(definition("y = y + a*x"))


def test_rejects_nonfinite_preview_result():
    d = definition("y = a / x")
    with pytest.raises(EquationBuilderError):
        evaluate_rows({"definition": d, "values": {"a": 1, "k": 1}, "rows": [{"x": 0}]})
