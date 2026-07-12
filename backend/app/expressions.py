from __future__ import annotations

import math
import re
from typing import Any


class ContractValidationError(ValueError):
    """Raised when method inputs violate a portable contract."""


def snake(value: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    text = re.sub(r"[^A-Za-z0-9_]+", "_", text)
    return text.strip("_").lower() or "value"


def validate_inputs(contract: dict[str, Any], supplied: dict[str, float]) -> dict[str, float]:
    known = {field["id"] for field in contract.get("inputs", [])}
    unknown = sorted(set(supplied) - known)
    if unknown:
        raise ContractValidationError(f"Unknown input fields: {', '.join(unknown)}")

    values: dict[str, float] = {}
    for field in contract.get("inputs", []):
        field_id = field["id"]
        raw = supplied.get(field_id, field.get("default"))
        try:
            number = float(raw)
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(f"{field_id} must be numeric.") from exc
        if not math.isfinite(number):
            raise ContractValidationError(f"{field_id} must be finite.")
        rule = field.get("validation") or {}
        if "min" in rule:
            minimum = float(rule["min"])
            if rule.get("exclusive") and number <= minimum:
                raise ContractValidationError(f"{field_id} must be greater than {minimum}.")
            if not rule.get("exclusive") and number < minimum:
                raise ContractValidationError(f"{field_id} must be at least {minimum}.")
        if "max" in rule:
            maximum = float(rule["max"])
            if rule.get("exclusiveMax") and number >= maximum:
                raise ContractValidationError(f"{field_id} must be less than {maximum}.")
            if not rule.get("exclusiveMax") and number > maximum:
                raise ContractValidationError(f"{field_id} must be no greater than {maximum}.")
        values[field_id] = number
    return values


def evaluate_node(node: dict[str, Any], context: dict[str, float]) -> float:
    if "number" in node:
        return float(node["number"])
    if "var" in node:
        return float(context[node["var"]])
    if "constant" in node:
        if node["constant"] == "pi":
            return math.pi
        return float(context[node["constant"]])
    arguments = [evaluate_node(item, context) for item in node.get("args", [])]
    operation = node.get("op")
    if operation == "add":
        return sum(arguments)
    if operation == "sub":
        return arguments[0] - arguments[1]
    if operation == "mul":
        product = 1.0
        for value in arguments:
            product *= value
        return product
    if operation == "div":
        return arguments[0] / arguments[1]
    if operation == "pow":
        return arguments[0] ** arguments[1]
    function = node.get("fn")
    functions = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "exp": math.exp,
        "log": math.log,
        "abs": abs,
    }
    if function not in functions:
        raise ContractValidationError(f"Unsupported expression function: {function}")
    return float(functions[function](*arguments))


def evaluate_contract(contract: dict[str, Any], supplied: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
    inputs = validate_inputs(contract, supplied)
    context = dict(inputs)
    context.update({key: float(value) for key, value in (contract.get("constants") or {}).items()})
    context["pi"] = math.pi
    for derived in contract.get("derived", []) or []:
        context[derived["id"]] = evaluate_node(derived["expression"], context)
    outputs: dict[str, float] = {}
    for output in contract.get("outputs", []):
        value = evaluate_node(output["expression"], context)
        if not math.isfinite(value):
            raise ContractValidationError(f"Output {output['id']} is not finite.")
        outputs[output["id"]] = value
    return inputs, outputs


def literal(value: float, language: str) -> str:
    number = float(value)
    if language == "fortran":
        return f"{number:.17e}".replace("e", "d")
    if language in {"c", "cpp", "rust", "go", "haskell"} and number.is_integer():
        return f"{int(number)}.0"
    return f"{number:.17g}"


def emit(node: dict[str, Any], language: str) -> str:
    if "number" in node:
        return literal(float(node["number"]), language)
    if "var" in node:
        return snake(node["var"])
    if "constant" in node:
        constant = node["constant"]
        if constant == "pi":
            return {
                "python": "math.pi",
                "javascript": "Math.PI",
                "typescript": "Math.PI",
                "c": "acos(-1.0)",
                "cpp": "std::numbers::pi",
                "fortran": "acos(-1.0d0)",
                "rust": "std::f64::consts::PI",
                "go": "math.Pi",
                "r": "pi",
                "julia": "pi",
                "sql": "PI()",
                "haskell": "pi",
            }[language]
        return snake(constant)
    arguments = [emit(item, language) for item in node.get("args", [])]
    operation = node.get("op")
    if operation == "pow":
        left, right = arguments
        if language in {"python", "javascript", "typescript"}:
            return f"({left}) ** ({right})"
        if language in {"r", "julia"}:
            return f"({left}) ^ ({right})"
        if language == "sql":
            return f"POWER({left}, {right})"
        if language == "c":
            return f"pow({left}, {right})"
        if language == "cpp":
            return f"std::pow({left}, {right})"
        if language == "fortran":
            return f"({left}) ** ({right})"
        if language == "rust":
            return f"({left}).powf({right})"
        if language == "go":
            return f"math.Pow({left}, {right})"
        if language == "haskell":
            return f"({left}) ** ({right})"
    operators = {"add": " + ", "sub": " - ", "mul": " * ", "div": " / "}
    if operation in operators:
        return f"({operators[operation].join(arguments)})"
    function = node.get("fn")
    if language == "rust":
        return f"({arguments[0]}).{function}()"
    function_name = {
        "python": f"math.{function}",
        "javascript": f"Math.{function}",
        "typescript": f"Math.{function}",
        "c": str(function),
        "cpp": f"std::{function}",
        "fortran": str(function),
        "go": f"math.{str(function).capitalize()}",
        "r": str(function),
        "julia": str(function),
        "sql": str(function).upper(),
        "haskell": str(function),
    }[language]
    return f"{function_name}({', '.join(arguments)})"


def assignments(contract: dict[str, Any], language: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    positions: dict[str, int] = {}
    for item in contract.get("derived", []) or []:
        row = {
            "id": item["id"],
            "name": snake(item["id"]),
            "expression": emit(item["expression"], language),
            "output": False,
        }
        positions[row["name"]] = len(rows)
        rows.append(row)
    for item in contract.get("outputs", []) or []:
        name = snake(item["id"])
        expression = item.get("expression") or {}
        if name in positions and expression.get("var") == item["id"]:
            rows[positions[name]]["output"] = True
            continue
        row = {
            "id": item["id"],
            "name": name,
            "expression": emit(expression, language),
            "output": True,
        }
        if name in positions:
            rows[positions[name]] = row
        else:
            positions[name] = len(rows)
            rows.append(row)
    return rows
