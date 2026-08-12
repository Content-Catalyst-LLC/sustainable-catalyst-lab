from __future__ import annotations

import ast
from dataclasses import dataclass
import math
import re
from typing import Any, Callable

VERSION = "0.42.0"
EQUATION_SCHEMA = "sc-lab-scientific-equation/0.42.0"
SYMBOL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
MAX_EXPRESSION_LENGTH = 2000
MAX_AST_NODES = 256
MAX_CALL_ARGS = 4


class EquationBuilderError(ValueError):
    pass


@dataclass(frozen=True)
class CompiledEquation:
    lhs: str
    rhs: str
    normalized: str
    symbols: tuple[str, ...]
    functions: tuple[str, ...]
    tree: ast.Expression


_ALLOWED_FUNCTIONS: dict[str, Callable[..., float]] = {
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "abs": abs,
    "min": min,
    "max": max,
}
_ALLOWED_CONSTANTS = {"pi": math.pi, "e": math.e}
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)
_ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)
_FORBIDDEN_TOKENS = ("__", "lambda", "import", "exec", "eval", "open(", "globals", "locals")


def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": EQUATION_SCHEMA,
        "functions": sorted(_ALLOWED_FUNCTIONS),
        "constants": sorted(_ALLOWED_CONSTANTS),
        "operators": ["+", "-", "*", "/", "^", "**", "%"],
        "limits": {
            "expressionCharacters": MAX_EXPRESSION_LENGTH,
            "astNodes": MAX_AST_NODES,
            "callArguments": MAX_CALL_ARGS,
        },
        "boundaries": {
            "arbitraryPython": False,
            "attributes": False,
            "subscripts": False,
            "comprehensions": False,
            "assignments": False,
            "userDefinedFunctions": False,
            "network": False,
            "filesystem": False,
        },
    }


def _symbol(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not SYMBOL_RE.fullmatch(text):
        raise EquationBuilderError(f"{name} must be a safe scientific symbol.")
    return text


def _split_equation(equation: str, output_symbol: str | None) -> tuple[str, str]:
    text = str(equation or "").strip()
    if not text:
        raise EquationBuilderError("Equation is required.")
    if len(text) > MAX_EXPRESSION_LENGTH:
        raise EquationBuilderError(f"Equation exceeds {MAX_EXPRESSION_LENGTH} characters.")
    lowered = text.lower()
    if any(token in lowered for token in _FORBIDDEN_TOKENS):
        raise EquationBuilderError("Equation contains a forbidden token.")
    if "=" in text:
        parts = text.split("=")
        if len(parts) != 2:
            raise EquationBuilderError("Equation must contain at most one '=' assignment marker.")
        lhs = _symbol(parts[0].strip(), "Equation output")
        rhs = parts[1].strip()
    else:
        if not output_symbol:
            raise EquationBuilderError("An output symbol is required when the equation omits '='.")
        lhs = _symbol(output_symbol, "Equation output")
        rhs = text
    if not rhs:
        raise EquationBuilderError("Equation right-hand side is required.")
    return lhs, rhs.replace("^", "**")


def _validate_tree(tree: ast.AST, declared: set[str], lhs: str) -> tuple[set[str], set[str]]:
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_AST_NODES:
        raise EquationBuilderError(f"Equation is too complex ({len(nodes)} AST nodes; maximum {MAX_AST_NODES}).")
    symbols: set[str] = set()
    functions: set[str] = set()
    allowed_names = declared | set(_ALLOWED_CONSTANTS)

    for node in nodes:
        if isinstance(node, (ast.Expression, ast.Load)):
            continue
        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, _ALLOWED_BINOPS):
                raise EquationBuilderError("Equation contains an unsupported binary operator.")
            continue
        if isinstance(node, _ALLOWED_BINOPS):
            continue
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, _ALLOWED_UNARYOPS):
                raise EquationBuilderError("Equation contains an unsupported unary operator.")
            continue
        if isinstance(node, _ALLOWED_UNARYOPS):
            continue
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCTIONS:
                raise EquationBuilderError("Equation calls an unregistered scientific function.")
            if node.keywords or len(node.args) > MAX_CALL_ARGS:
                raise EquationBuilderError("Scientific function call has unsupported arguments.")
            functions.add(node.func.id)
            continue
        if isinstance(node, ast.Name):
            if node.id in _ALLOWED_FUNCTIONS:
                continue
            if node.id not in allowed_names:
                raise EquationBuilderError(f"Undeclared symbol in equation: {node.id}.")
            if node.id not in _ALLOWED_CONSTANTS:
                symbols.add(node.id)
            continue
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise EquationBuilderError("Equation constants must be numeric.")
            if not math.isfinite(float(node.value)):
                raise EquationBuilderError("Equation constants must be finite.")
            continue
        # Explicitly reject attributes, subscripts, comparisons, boolean logic, comprehensions, etc.
        raise EquationBuilderError(f"Unsupported equation syntax: {type(node).__name__}.")

    if lhs in symbols:
        raise EquationBuilderError("Equation output cannot reference itself in an algebraic definition.")
    return symbols, functions


def compile_equation(equation: str, declared_symbols: list[str] | tuple[str, ...] | set[str], output_symbol: str | None = None) -> CompiledEquation:
    declared = {_symbol(v, "Declared symbol") for v in declared_symbols}
    lhs, rhs = _split_equation(equation, output_symbol)
    try:
        parsed = ast.parse(rhs, mode="eval")
    except SyntaxError as exc:
        raise EquationBuilderError("Equation syntax is invalid.") from exc
    symbols, functions = _validate_tree(parsed, declared, lhs)
    normalized = f"{lhs} = {rhs}"
    return CompiledEquation(lhs=lhs, rhs=rhs, normalized=normalized, symbols=tuple(sorted(symbols)), functions=tuple(sorted(functions)), tree=parsed)


def _eval_node(node: ast.AST, env: dict[str, float]) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, env)
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTANTS:
            return float(_ALLOWED_CONSTANTS[node.id])
        if node.id not in env:
            raise EquationBuilderError(f"Missing numeric value for symbol: {node.id}.")
        return float(env[node.id])
    if isinstance(node, ast.UnaryOp):
        value = _eval_node(node.operand, env)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left, right = _eval_node(node.left, env), _eval_node(node.right, env)
        if isinstance(node.op, ast.Add): return left + right
        if isinstance(node.op, ast.Sub): return left - right
        if isinstance(node.op, ast.Mult): return left * right
        if isinstance(node.op, ast.Div): return left / right
        if isinstance(node.op, ast.Pow): return left ** right
        if isinstance(node.op, ast.Mod): return left % right
    if isinstance(node, ast.Call):
        fn = _ALLOWED_FUNCTIONS[node.func.id]
        return float(fn(*[_eval_node(arg, env) for arg in node.args]))
    raise EquationBuilderError("Equation contains an unsupported executable node.")


def evaluate(compiled: CompiledEquation, values: dict[str, Any]) -> float:
    env: dict[str, float] = {}
    for symbol in compiled.symbols:
        raw = values.get(symbol)
        try:
            value = float(raw)
        except (TypeError, ValueError) as exc:
            raise EquationBuilderError(f"Missing numeric value for symbol: {symbol}.") from exc
        if not math.isfinite(value):
            raise EquationBuilderError(f"Value for {symbol} must be finite.")
        env[symbol] = value
    try:
        result = float(_eval_node(compiled.tree, env))
    except (ArithmeticError, OverflowError, ValueError) as exc:
        raise EquationBuilderError(f"Equation evaluation failed: {exc}.") from exc
    if not math.isfinite(result):
        raise EquationBuilderError("Equation evaluation produced a non-finite result.")
    return result


def validate_definition(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise EquationBuilderError("Equation definition must be an object.")
    equation = str(payload.get("equation") or "").strip()
    variables = [_symbol(v.get("symbol") if isinstance(v, dict) else v, "Variable symbol") for v in (payload.get("variables") or [])]
    parameters = [_symbol(v.get("symbol") if isinstance(v, dict) else v, "Parameter symbol") for v in (payload.get("parameters") or [])]
    constants = [_symbol(v.get("symbol") if isinstance(v, dict) else v, "Constant symbol") for v in (payload.get("constants") or [])]
    declared = variables + parameters + constants
    output_symbol = payload.get("outputSymbol")
    compiled = compile_equation(equation, declared, str(output_symbol).strip() if output_symbol else None)
    return {
        "ok": True,
        "schema": EQUATION_SCHEMA,
        "version": VERSION,
        "equation": compiled.normalized,
        "outputSymbol": compiled.lhs,
        "referencedSymbols": list(compiled.symbols),
        "functions": list(compiled.functions),
        "declaredSymbols": sorted(set(declared)),
        "executable": True,
        "arbitraryCode": False,
    }


def evaluate_rows(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise EquationBuilderError("Equation evaluation request must be an object.")
    definition = payload.get("definition") or payload
    if not isinstance(definition, dict):
        raise EquationBuilderError("definition must be an object.")
    validated = validate_definition(definition)
    compiled = compile_equation(validated["equation"], validated["declaredSymbols"], validated["outputSymbol"])
    fixed_values = payload.get("values") or {}
    if not isinstance(fixed_values, dict):
        raise EquationBuilderError("values must be an object.")
    rows = payload.get("rows") or []
    if not isinstance(rows, list):
        raise EquationBuilderError("rows must be an array.")
    if len(rows) > 5000:
        raise EquationBuilderError("Equation preview is limited to 5,000 rows.")
    output = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise EquationBuilderError(f"rows[{index}] must be an object.")
        env = dict(fixed_values)
        env.update(row)
        y = evaluate(compiled, env)
        output.append({**row, compiled.lhs: y})
    return {
        "ok": True,
        "schema": EQUATION_SCHEMA,
        "version": VERSION,
        "equation": compiled.normalized,
        "outputSymbol": compiled.lhs,
        "rows": output,
        "rowCount": len(output),
        "arbitraryCode": False,
    }
