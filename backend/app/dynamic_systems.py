from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from .equation_builder import EquationBuilderError, compile_equation, evaluate

VERSION = "0.45.0"
SYSTEM_SCHEMA = "sc-lab-dynamic-system/0.45.0"
SIMULATION_SCHEMA = "sc-lab-dynamic-system-simulation/0.45.0"
ESTIMATION_SCHEMA = "sc-lab-dynamic-parameter-estimation/0.45.0"
GRAPH_SCHEMA = "sc-lab-scientific-graph/0.45.0"
SYMBOL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
SOLVERS = {"RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA"}
LOSSES = {"linear", "soft_l1", "huber", "cauchy", "arctan"}
MAX_STATES = 12
MAX_PARAMETERS = 24
MAX_POINTS = 5000
MAX_OBSERVATIONS = 20000
MAX_NFEV = 4000


class DynamicSystemError(ValueError):
    pass


@dataclass(frozen=True)
class CompiledSystem:
    definition: dict[str, Any]
    state_symbols: tuple[str, ...]
    parameter_symbols: tuple[str, ...]
    constant_values: dict[str, float]
    equations: tuple[Any, ...]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, name: str, max_len: int = 240, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise DynamicSystemError(f"{name} is required.")
    if len(text) > max_len:
        raise DynamicSystemError(f"{name} exceeds {max_len} characters.")
    return text


def _symbol(value: Any, name: str) -> str:
    text = _text(value, name, 64, True)
    if not SYMBOL_RE.fullmatch(text):
        raise DynamicSystemError(f"{name} must be a safe scientific symbol.")
    return text


def _finite(value: Any, name: str, required: bool = False) -> float | None:
    if value is None or value == "":
        if required:
            raise DynamicSystemError(f"{name} is required.")
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DynamicSystemError(f"{name} must be numeric.") from exc
    if not math.isfinite(number):
        raise DynamicSystemError(f"{name} must be finite.")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "systemSchema": SYSTEM_SCHEMA,
        "simulationSchema": SIMULATION_SCHEMA,
        "estimationSchema": ESTIMATION_SCHEMA,
        "solvers": sorted(SOLVERS),
        "losses": sorted(LOSSES),
        "limits": {
            "states": MAX_STATES,
            "parameters": MAX_PARAMETERS,
            "trajectoryPoints": MAX_POINTS,
            "observations": MAX_OBSERVATIONS,
            "optimizerEvaluations": MAX_NFEV,
        },
        "capabilities": {
            "coupledODEs": True,
            "boundedParameterEstimation": True,
            "robustLosses": True,
            "multiStateObservations": True,
            "confidenceIntervals": True,
            "identifiabilityDiagnostics": True,
            "phasePortraits": True,
            "publicationGraphs": True,
        },
        "boundaries": {
            "arbitraryCode": False,
            "arbitraryPython": False,
            "safeDeclarativeDerivativeExpressions": True,
            "events": False,
            "delays": False,
            "stochasticDifferentialEquations": False,
            "partialDifferentialEquations": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "dynamic-systems-ready",
        "version": VERSION,
        "solverCount": len(SOLVERS),
        "safeDerivativeGrammar": True,
        "parameterEstimation": True,
        "identifiabilityDiagnostics": True,
        "arbitraryCode": False,
    }


def _normalize_time_span(payload: dict[str, Any]) -> dict[str, Any]:
    span = payload.get("timeSpan") if isinstance(payload.get("timeSpan"), dict) else {}
    start = _finite(span.get("start", payload.get("start", 0.0)), "timeSpan.start", True)
    end = _finite(span.get("end", payload.get("end", 10.0)), "timeSpan.end", True)
    if end <= start:
        raise DynamicSystemError("timeSpan.end must be greater than timeSpan.start.")
    points_raw = span.get("points", payload.get("points", 201))
    try:
        points = int(points_raw)
    except (TypeError, ValueError) as exc:
        raise DynamicSystemError("timeSpan.points must be an integer.") from exc
    if points < 2 or points > MAX_POINTS:
        raise DynamicSystemError(f"timeSpan.points must be between 2 and {MAX_POINTS}.")
    return {"start": start, "end": end, "points": points}


def _normalize_solver(payload: dict[str, Any]) -> dict[str, Any]:
    src = payload.get("solver") if isinstance(payload.get("solver"), dict) else {}
    method = _text(src.get("method") or "RK45", "solver.method", 16, True)
    if method not in SOLVERS:
        raise DynamicSystemError("Unsupported ODE solver.")
    rtol = _finite(src.get("rtol", 1e-6), "solver.rtol", True)
    atol = _finite(src.get("atol", 1e-9), "solver.atol", True)
    if not (0 < rtol <= 0.1) or not (0 < atol <= 0.1):
        raise DynamicSystemError("Solver tolerances must be positive and no greater than 0.1.")
    max_step = _finite(src.get("maxStep"), "solver.maxStep")
    if max_step is not None and max_step <= 0:
        raise DynamicSystemError("solver.maxStep must be positive when supplied.")
    return {"method": method, "rtol": rtol, "atol": atol, "maxStep": max_step}


def normalize_definition(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DynamicSystemError("Dynamic-system definition must be an object.")
    src = deepcopy(payload)
    iv_raw = src.get("independentVariable") or {"symbol": "t", "label": "Time", "unit": ""}
    if isinstance(iv_raw, str):
        iv_raw = {"symbol": iv_raw}
    if not isinstance(iv_raw, dict):
        raise DynamicSystemError("independentVariable must be an object or symbol.")
    time_symbol = _symbol(iv_raw.get("symbol") or "t", "independentVariable.symbol")
    independent = {
        "symbol": time_symbol,
        "label": _text(iv_raw.get("label") or "Time", "independentVariable.label", 120, True),
        "unit": _text(iv_raw.get("unit"), "independentVariable.unit", 80),
    }

    states_src = src.get("states") or []
    if not isinstance(states_src, list) or not states_src:
        raise DynamicSystemError("At least one state variable is required.")
    if len(states_src) > MAX_STATES:
        raise DynamicSystemError(f"Dynamic systems are limited to {MAX_STATES} state variables.")
    states: list[dict[str, Any]] = []
    state_seen: set[str] = set()
    for index, row in enumerate(states_src):
        if not isinstance(row, dict):
            raise DynamicSystemError("states must contain objects.")
        symbol = _symbol(row.get("symbol") or row.get("name"), f"states[{index}].symbol")
        if symbol == time_symbol or symbol in state_seen:
            raise DynamicSystemError(f"Duplicate or reserved state symbol: {symbol}.")
        state_seen.add(symbol)
        initial = _finite(row.get("initial", row.get("initialCondition", row.get("value"))), f"states[{index}].initial", True)
        states.append({
            "symbol": symbol,
            "label": _text(row.get("label") or symbol, f"states[{index}].label", 120, True),
            "unit": _text(row.get("unit"), f"states[{index}].unit", 80),
            "initial": initial,
        })

    params_src = src.get("parameters") or []
    if not isinstance(params_src, list) or len(params_src) > MAX_PARAMETERS:
        raise DynamicSystemError(f"parameters must be an array with no more than {MAX_PARAMETERS} entries.")
    parameters: list[dict[str, Any]] = []
    param_seen: set[str] = set()
    for index, row in enumerate(params_src):
        if not isinstance(row, dict):
            raise DynamicSystemError("parameters must contain objects.")
        symbol = _symbol(row.get("symbol") or row.get("name"), f"parameters[{index}].symbol")
        if symbol in state_seen or symbol == time_symbol or symbol in param_seen:
            raise DynamicSystemError(f"Duplicate or reserved parameter symbol: {symbol}.")
        param_seen.add(symbol)
        bounds = row.get("bounds") if isinstance(row.get("bounds"), dict) else {}
        lower = _finite(bounds.get("lower", row.get("lower")), f"{symbol} lower bound")
        upper = _finite(bounds.get("upper", row.get("upper")), f"{symbol} upper bound")
        if lower is not None and upper is not None and lower > upper:
            raise DynamicSystemError(f"Lower bound exceeds upper bound for {symbol}.")
        value = _finite(row.get("value"), f"{symbol} value")
        if value is None:
            if lower is not None and upper is not None:
                value = (lower + upper) / 2.0
            elif lower is not None:
                value = max(lower, 1.0)
            elif upper is not None:
                value = min(upper, 1.0)
            else:
                value = 1.0
        if lower is not None and value < lower:
            raise DynamicSystemError(f"Initial value for {symbol} is below its lower bound.")
        if upper is not None and value > upper:
            raise DynamicSystemError(f"Initial value for {symbol} is above its upper bound.")
        role = _text(row.get("role") or "estimated", f"parameters[{index}].role", 24, True)
        if role not in {"estimated", "fixed"}:
            raise DynamicSystemError("Dynamic-system parameter role must be estimated or fixed.")
        parameters.append({
            "symbol": symbol,
            "label": _text(row.get("label") or symbol, f"parameters[{index}].label", 120, True),
            "unit": _text(row.get("unit"), f"parameters[{index}].unit", 80),
            "role": role,
            "value": value,
            "bounds": {"lower": lower, "upper": upper},
        })

    constants_src = src.get("constants") or []
    if not isinstance(constants_src, list) or len(constants_src) > MAX_PARAMETERS:
        raise DynamicSystemError("constants must be a bounded array.")
    constants: list[dict[str, Any]] = []
    constant_seen: set[str] = set()
    for index, row in enumerate(constants_src):
        if not isinstance(row, dict):
            raise DynamicSystemError("constants must contain objects.")
        symbol = _symbol(row.get("symbol") or row.get("name"), f"constants[{index}].symbol")
        if symbol in state_seen or symbol in param_seen or symbol == time_symbol or symbol in constant_seen:
            raise DynamicSystemError(f"Duplicate or reserved constant symbol: {symbol}.")
        constant_seen.add(symbol)
        constants.append({
            "symbol": symbol,
            "label": _text(row.get("label") or symbol, f"constants[{index}].label", 120, True),
            "unit": _text(row.get("unit"), f"constants[{index}].unit", 80),
            "value": _finite(row.get("value"), f"constants[{index}].value", True),
        })

    equations_src = src.get("equations") or []
    if isinstance(equations_src, dict):
        equations_src = [{"state": key, "rhs": value} for key, value in equations_src.items()]
    if not isinstance(equations_src, list) or len(equations_src) != len(states):
        raise DynamicSystemError("Exactly one derivative equation is required for each state variable.")
    by_state: dict[str, dict[str, Any]] = {}
    declared = [time_symbol, *sorted(state_seen), *sorted(param_seen), *sorted(constant_seen)]
    for index, row in enumerate(equations_src):
        if not isinstance(row, dict):
            raise DynamicSystemError("equations must contain objects.")
        state = _symbol(row.get("state"), f"equations[{index}].state")
        if state not in state_seen:
            raise DynamicSystemError(f"Equation references unknown state: {state}.")
        if state in by_state:
            raise DynamicSystemError(f"Duplicate derivative equation for state: {state}.")
        rhs = _text(row.get("rhs") or row.get("equation"), f"equations[{index}].rhs", 2000, True)
        derivative_symbol = f"d{state}_dt"
        try:
            compiled = compile_equation(rhs, declared, derivative_symbol)
        except EquationBuilderError as exc:
            raise DynamicSystemError(f"Derivative for {state}: {exc}") from exc
        if compiled.lhs != derivative_symbol:
            raise DynamicSystemError(f"Derivative equation for {state} must target {derivative_symbol} when an '=' marker is used.")
        by_state[state] = {
            "state": state,
            "derivativeSymbol": derivative_symbol,
            "rhs": compiled.rhs,
            "equation": compiled.normalized,
            "referencedSymbols": list(compiled.symbols),
            "functions": list(compiled.functions),
        }
    equations = [by_state[state["symbol"]] for state in states]

    normalized = {
        "schema": SYSTEM_SCHEMA,
        "version": VERSION,
        "recordType": "dynamic-system",
        "id": _text(src.get("id") or f"dynamic-{_digest(src)[:16]}", "id", 120, True),
        "title": _text(src.get("title") or "Untitled dynamic system", "title", 180, True),
        "independentVariable": independent,
        "states": states,
        "parameters": parameters,
        "constants": constants,
        "equations": equations,
        "timeSpan": _normalize_time_span(src),
        "solver": _normalize_solver(src),
        "assumptions": [_text(v, "assumption", 500, True) for v in (src.get("assumptions") or [])][:50],
        "limitations": [_text(v, "limitation", 500, True) for v in (src.get("limitations") or [])][:50],
        "provenance": deepcopy(src.get("provenance") or {}),
        "createdAt": _text(src.get("createdAt") or _now(), "createdAt", 80, True),
        "boundaries": {
            "arbitraryCode": False,
            "safeDeclarativeDerivativeExpressions": True,
            "events": False,
            "delays": False,
        },
    }
    hashable = deepcopy(normalized)
    hashable.pop("systemHash", None)
    normalized["systemHash"] = _digest(hashable)
    return normalized


def _compile_system(definition: dict[str, Any]) -> CompiledSystem:
    normalized = normalize_definition(definition)
    states = tuple(row["symbol"] for row in normalized["states"])
    params = tuple(row["symbol"] for row in normalized["parameters"])
    constants = {row["symbol"]: float(row["value"]) for row in normalized["constants"]}
    declared = [normalized["independentVariable"]["symbol"], *states, *params, *constants.keys()]
    compiled = []
    for row in normalized["equations"]:
        try:
            compiled.append(compile_equation(row["equation"], declared, row["derivativeSymbol"]))
        except EquationBuilderError as exc:
            raise DynamicSystemError(str(exc)) from exc
    return CompiledSystem(normalized, states, params, constants, tuple(compiled))


def _parameter_values(system: CompiledSystem, overrides: dict[str, Any] | None = None) -> dict[str, float]:
    values = {row["symbol"]: float(row["value"]) for row in system.definition["parameters"]}
    if overrides:
        for symbol, raw in overrides.items():
            if symbol not in values:
                raise DynamicSystemError(f"Unknown parameter override: {symbol}.")
            values[symbol] = float(_finite(raw, f"parameter override {symbol}", True))
    return values


def _rhs_function(system: CompiledSystem, params: dict[str, float]):
    time_symbol = system.definition["independentVariable"]["symbol"]

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        env = {time_symbol: float(t), **system.constant_values, **params}
        env.update({symbol: float(y[index]) for index, symbol in enumerate(system.state_symbols)})
        try:
            values = [evaluate(eq, env) for eq in system.equations]
        except EquationBuilderError as exc:
            raise DynamicSystemError(str(exc)) from exc
        if not np.all(np.isfinite(values)):
            raise DynamicSystemError("Dynamic-system derivative produced a non-finite value.")
        return np.asarray(values, dtype=float)

    return rhs


def _solve(system: CompiledSystem, params: dict[str, float], t_eval: np.ndarray, start: float | None = None, y0: np.ndarray | None = None) -> Any:
    definition = system.definition
    span = definition["timeSpan"]
    t0 = float(span["start"] if start is None else start)
    if t_eval.ndim != 1 or len(t_eval) < 1:
        raise DynamicSystemError("At least one simulation time is required.")
    if np.any(~np.isfinite(t_eval)) or np.any(np.diff(t_eval) < 0):
        raise DynamicSystemError("Simulation times must be finite and sorted.")
    if float(t_eval[0]) < t0 - 1e-12:
        raise DynamicSystemError("Observation/simulation times cannot precede the initial-condition time.")
    t_end = float(t_eval[-1])
    initial = np.asarray(y0 if y0 is not None else [row["initial"] for row in definition["states"]], dtype=float)
    solver = definition["solver"]
    kwargs: dict[str, Any] = {
        "method": solver["method"],
        "rtol": solver["rtol"],
        "atol": solver["atol"],
        "t_eval": t_eval,
    }
    if solver.get("maxStep") is not None:
        kwargs["max_step"] = solver["maxStep"]
    if t_end == t0:
        class Result:
            success = True
            message = "Initial condition only"
            t = np.asarray([t0], dtype=float)
            y = initial.reshape((-1, 1))
            nfev = 0
            njev = 0
            nlu = 0
        return Result()
    try:
        result = solve_ivp(_rhs_function(system, params), (t0, t_end), initial, **kwargs)
    except (DynamicSystemError, ArithmeticError, ValueError, OverflowError) as exc:
        raise DynamicSystemError(f"ODE integration failed: {exc}") from exc
    if not result.success:
        raise DynamicSystemError(f"ODE integration failed: {result.message}")
    if result.y.shape[1] != len(t_eval) or not np.all(np.isfinite(result.y)):
        raise DynamicSystemError("ODE solver returned an incomplete or non-finite trajectory.")
    return result


def _trajectory_rows(system: CompiledSystem, result: Any) -> list[dict[str, float]]:
    time_symbol = system.definition["independentVariable"]["symbol"]
    rows = []
    for col, t in enumerate(result.t):
        row: dict[str, float] = {time_symbol: float(t)}
        for index, state in enumerate(system.state_symbols):
            row[state] = float(result.y[index, col])
        rows.append(row)
    return rows


def _graph(title: str, x_label: str, y_label: str, series: list[dict[str, Any]], description: str, annotations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    graph = {
        "schema": GRAPH_SCHEMA,
        "version": VERSION,
        "kind": "line-scatter",
        "title": title,
        "description": description,
        "xLabel": x_label,
        "yLabel": y_label,
        "series": series,
        "annotations": annotations or [],
        "interaction": {"tooltip": True, "focusablePoints": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": True},
        "publication": {"subtitle": "", "caption": "", "source": "", "method": "", "notes": "", "aspectRatio": "16:9", "showGrid": True, "showLegend": True, "background": "white"},
        "exports": ["svg", "png", "csv", "json"],
        "accessibility": {"role": "img", "tabularFallback": True, "keyboardNavigation": True},
    }
    graph["graphHash"] = _digest(graph)
    return graph


def simulate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DynamicSystemError("Simulation request must be an object.")
    system = _compile_system(payload.get("system") or payload.get("definition") or payload)
    span_override = payload.get("timeSpan")
    if isinstance(span_override, dict):
        merged = deepcopy(system.definition)
        merged["timeSpan"] = {**merged["timeSpan"], **span_override}
        system = _compile_system(merged)
    span = system.definition["timeSpan"]
    t_eval = np.linspace(float(span["start"]), float(span["end"]), int(span["points"]), dtype=float)
    params = _parameter_values(system, payload.get("parameterValues") if isinstance(payload.get("parameterValues"), dict) else None)
    result = _solve(system, params, t_eval)
    rows = _trajectory_rows(system, result)
    iv = system.definition["independentVariable"]
    trajectory_series = []
    for state in system.definition["states"]:
        trajectory_series.append({
            "id": f"state-{state['symbol']}",
            "label": state["label"],
            "mode": "line",
            "points": [{"x": row[iv["symbol"]], "y": row[state["symbol"]]} for row in rows],
        })
    x_label = iv["label"] + (f" ({iv['unit']})" if iv.get("unit") else "")
    trajectory = _graph(f"{system.definition['title']} — state trajectories", x_label, "State value", trajectory_series, "Numerically integrated dynamic-system state trajectories.")
    phase = None
    if len(system.definition["states"]) >= 2:
        sx, sy = system.definition["states"][0], system.definition["states"][1]
        phase = _graph(
            f"{system.definition['title']} — phase portrait",
            sx["label"] + (f" ({sx['unit']})" if sx.get("unit") else ""),
            sy["label"] + (f" ({sy['unit']})" if sy.get("unit") else ""),
            [{"id": "phase-trajectory", "label": f"{sy['symbol']} vs {sx['symbol']}", "mode": "line-scatter", "points": [{"x": row[sx["symbol"]], "y": row[sy["symbol"]]} for row in rows]}],
            "Phase-space trajectory for the first two state variables.",
        )
    simulation = {
        "schema": SIMULATION_SCHEMA,
        "version": VERSION,
        "recordType": "dynamic-system-simulation",
        "createdAt": _now(),
        "system": system.definition,
        "parameterValues": params,
        "rows": rows,
        "rowCount": len(rows),
        "solver": {
            "method": system.definition["solver"]["method"],
            "success": True,
            "message": str(result.message),
            "nfev": int(getattr(result, "nfev", 0) or 0),
            "njev": int(getattr(result, "njev", 0) or 0),
            "nlu": int(getattr(result, "nlu", 0) or 0),
        },
        "graphs": {"trajectory": trajectory, "phasePortrait": phase},
        "boundaries": {"arbitraryCode": False, "safeDeclarativeDerivativeExpressions": True},
    }
    hashable = deepcopy(simulation)
    hashable.pop("simulationHash", None)
    simulation["simulationHash"] = _digest(hashable)
    return {"ok": True, "simulation": simulation}


def _observations(payload: dict[str, Any], system: CompiledSystem) -> tuple[list[dict[str, Any]], list[str]]:
    rows = payload.get("observations") or payload.get("rows") or []
    if not isinstance(rows, list) or len(rows) < 3:
        raise DynamicSystemError("Parameter estimation requires at least three observation rows.")
    if len(rows) > MAX_OBSERVATIONS:
        raise DynamicSystemError(f"Parameter estimation is limited to {MAX_OBSERVATIONS} observation rows.")
    time_symbol = system.definition["independentVariable"]["symbol"]
    requested_states = payload.get("observedStates") or list(system.state_symbols)
    if not isinstance(requested_states, list) or not requested_states:
        raise DynamicSystemError("observedStates must identify at least one state.")
    observed_states = [_symbol(v, "observed state") for v in requested_states]
    if any(v not in system.state_symbols for v in observed_states):
        raise DynamicSystemError("observedStates contains a state not defined by the dynamic system.")
    clean: list[dict[str, Any]] = []
    measured = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DynamicSystemError(f"observations[{index}] must be an object.")
        if time_symbol not in row:
            raise DynamicSystemError(f"Observation row {index} is missing time symbol {time_symbol}.")
        t = _finite(row.get(time_symbol), f"observations[{index}].{time_symbol}", True)
        item: dict[str, Any] = {time_symbol: t}
        for state in observed_states:
            if row.get(state) is not None and row.get(state) != "":
                item[state] = _finite(row.get(state), f"observations[{index}].{state}", True)
                measured += 1
        clean.append(item)
    if measured < 3:
        raise DynamicSystemError("Parameter estimation requires at least three finite state measurements.")
    clean.sort(key=lambda r: r[time_symbol])
    start = float(system.definition["timeSpan"]["start"])
    if clean[0][time_symbol] < start - 1e-12:
        raise DynamicSystemError("Observations cannot precede the initial-condition time.")
    return clean, observed_states


def _prediction_map(system: CompiledSystem, params: dict[str, float], times: list[float]) -> dict[float, dict[str, float]]:
    unique = np.asarray(sorted(set(float(t) for t in times)), dtype=float)
    start = float(system.definition["timeSpan"]["start"])
    if unique[0] > start:
        t_eval = np.concatenate(([start], unique))
        result = _solve(system, params, t_eval)
        result_times = result.t[1:]
        values = result.y[:, 1:]
    else:
        result = _solve(system, params, unique)
        result_times = result.t
        values = result.y
    out: dict[float, dict[str, float]] = {}
    for col, t in enumerate(result_times):
        out[float(t)] = {state: float(values[i, col]) for i, state in enumerate(system.state_symbols)}
    return out


def estimate_parameters(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DynamicSystemError("Parameter-estimation request must be an object.")
    system = _compile_system(payload.get("system") or payload.get("definition") or {})
    observations, observed_states = _observations(payload, system)
    estimated = [row for row in system.definition["parameters"] if row.get("role") == "estimated"]
    if not estimated:
        raise DynamicSystemError("At least one parameter must have role 'estimated'.")
    if len(estimated) > 12:
        raise DynamicSystemError("A single estimation run is limited to 12 estimated parameters.")
    time_symbol = system.definition["independentVariable"]["symbol"]
    times = [float(row[time_symbol]) for row in observations]
    fixed = {row["symbol"]: float(row["value"]) for row in system.definition["parameters"] if row.get("role") == "fixed"}
    symbols = [row["symbol"] for row in estimated]
    x0 = np.asarray([float(row["value"]) for row in estimated], dtype=float)
    lower = np.asarray([float(row["bounds"]["lower"]) if row["bounds"]["lower"] is not None else -np.inf for row in estimated], dtype=float)
    upper = np.asarray([float(row["bounds"]["upper"]) if row["bounds"]["upper"] is not None else np.inf for row in estimated], dtype=float)
    loss = _text(payload.get("loss") or "linear", "loss", 20, True)
    if loss not in LOSSES:
        raise DynamicSystemError("Unsupported least-squares loss.")
    f_scale = _finite(payload.get("fScale", 1.0), "fScale", True)
    if f_scale <= 0:
        raise DynamicSystemError("fScale must be positive.")
    max_nfev = int(payload.get("maxEvaluations") or 1000)
    if max_nfev < 10 or max_nfev > MAX_NFEV:
        raise DynamicSystemError(f"maxEvaluations must be between 10 and {MAX_NFEV}.")

    weights_raw = payload.get("stateWeights") if isinstance(payload.get("stateWeights"), dict) else {}
    state_weights = {state: float(_finite(weights_raw.get(state, 1.0), f"weight for {state}", True)) for state in observed_states}
    if any(v <= 0 for v in state_weights.values()):
        raise DynamicSystemError("State weights must be positive.")

    def vector_to_params(vector: np.ndarray) -> dict[str, float]:
        return {**fixed, **{symbol: float(vector[i]) for i, symbol in enumerate(symbols)}}

    def residual_vector(vector: np.ndarray) -> np.ndarray:
        try:
            predictions = _prediction_map(system, vector_to_params(vector), times)
        except DynamicSystemError as exc:
            raise ValueError(str(exc)) from exc
        residuals: list[float] = []
        for row in observations:
            pred = predictions[float(row[time_symbol])]
            for state in observed_states:
                if state in row:
                    residuals.append((pred[state] - float(row[state])) * state_weights[state])
        arr = np.asarray(residuals, dtype=float)
        if not np.all(np.isfinite(arr)):
            raise ValueError("Non-finite residual encountered during estimation.")
        return arr

    try:
        result = least_squares(residual_vector, x0, bounds=(lower, upper), loss=loss, f_scale=f_scale, max_nfev=max_nfev, x_scale="jac")
    except (ValueError, DynamicSystemError, ArithmeticError, OverflowError) as exc:
        raise DynamicSystemError(f"Parameter estimation failed: {exc}") from exc
    if not result.success:
        raise DynamicSystemError(f"Parameter estimation did not converge: {result.message}")

    params = vector_to_params(result.x)
    predictions = _prediction_map(system, params, times)
    residual_records: list[dict[str, Any]] = []
    y_obs: list[float] = []
    y_pred: list[float] = []
    for index, row in enumerate(observations):
        pred = predictions[float(row[time_symbol])]
        for state in observed_states:
            if state in row:
                obs = float(row[state])
                pv = float(pred[state])
                residual_records.append({"row": index, time_symbol: float(row[time_symbol]), "state": state, "observed": obs, "predicted": pv, "residual": obs - pv})
                y_obs.append(obs)
                y_pred.append(pv)
    obs_arr, pred_arr = np.asarray(y_obs), np.asarray(y_pred)
    residual_arr = obs_arr - pred_arr
    sse = float(np.sum(residual_arr ** 2))
    rmse = float(np.sqrt(np.mean(residual_arr ** 2)))
    mae = float(np.mean(np.abs(residual_arr)))
    bias = float(np.mean(residual_arr))
    sst = float(np.sum((obs_arr - float(np.mean(obs_arr))) ** 2))
    r2 = float(1.0 - sse / sst) if sst > 0 else None

    n = len(residual_arr)
    p = len(symbols)
    dof = max(0, n - p)
    rank = int(np.linalg.matrix_rank(result.jac)) if result.jac.size else 0
    jt_j = result.jac.T @ result.jac if result.jac.size else np.zeros((p, p))
    try:
        condition = float(np.linalg.cond(jt_j)) if jt_j.size else math.inf
    except np.linalg.LinAlgError:
        condition = math.inf
    covariance = None
    standard_errors: dict[str, float | None] = {symbol: None for symbol in symbols}
    if dof > 0 and rank == p:
        try:
            covariance_matrix = np.linalg.inv(jt_j) * (sse / dof)
            covariance = covariance_matrix.tolist()
            se = np.sqrt(np.maximum(np.diag(covariance_matrix), 0.0))
            standard_errors = {symbol: float(se[i]) for i, symbol in enumerate(symbols)}
        except np.linalg.LinAlgError:
            covariance = None

    estimates = []
    for i, row in enumerate(estimated):
        value = float(result.x[i])
        se = standard_errors[row["symbol"]]
        lo_bound, hi_bound = row["bounds"]["lower"], row["bounds"]["upper"]
        at_bound = bool((lo_bound is not None and abs(value - lo_bound) <= 1e-7 * max(1.0, abs(value))) or (hi_bound is not None and abs(value - hi_bound) <= 1e-7 * max(1.0, abs(value))))
        estimates.append({
            "symbol": row["symbol"],
            "value": value,
            "standardError": se,
            "confidence95": {"lower": value - 1.96 * se, "upper": value + 1.96 * se} if se is not None else None,
            "bounds": deepcopy(row["bounds"]),
            "atBound": at_bound,
        })

    fitted_definition = deepcopy(system.definition)
    for row in fitted_definition["parameters"]:
        if row["symbol"] in params:
            row["value"] = params[row["symbol"]]
    fitted_system = _compile_system(fitted_definition)
    full_times = np.linspace(float(fitted_definition["timeSpan"]["start"]), max(float(fitted_definition["timeSpan"]["end"]), max(times)), int(fitted_definition["timeSpan"]["points"]), dtype=float)
    fit_result = _solve(fitted_system, params, full_times)
    fit_rows = _trajectory_rows(fitted_system, fit_result)

    trajectory_series: list[dict[str, Any]] = []
    for state in observed_states:
        label = next(row["label"] for row in fitted_definition["states"] if row["symbol"] == state)
        trajectory_series.append({"id": f"fit-{state}", "label": f"Fitted {label}", "mode": "line", "points": [{"x": row[time_symbol], "y": row[state]} for row in fit_rows]})
        trajectory_series.append({"id": f"observed-{state}", "label": f"Observed {label}", "mode": "scatter", "points": [{"x": row[time_symbol], "y": row[state], "label": "Observed"} for row in observations if state in row]})
    iv = fitted_definition["independentVariable"]
    fit_graph = _graph(
        f"{fitted_definition['title']} — parameter fit",
        iv["label"] + (f" ({iv['unit']})" if iv.get("unit") else ""),
        "State value",
        trajectory_series,
        "Observed state measurements overlaid on the fitted dynamic-system trajectories.",
    )
    residual_graph = _graph(
        f"{fitted_definition['title']} — estimation residuals",
        "Predicted value",
        "Observed − predicted",
        [{"id": "residuals", "label": "Residuals", "mode": "scatter", "points": [{"x": row["predicted"], "y": row["residual"], "label": f"{row['state']} @ {row[time_symbol]:g}"} for row in residual_records]}],
        "Residuals from bounded dynamic-system parameter estimation.",
        annotations=[{"type": "horizontal-line", "value": 0.0, "label": "Zero residual"}],
    )

    identifiability_status = "adequate"
    warnings: list[str] = []
    if rank < p:
        identifiability_status = "rank-deficient"
        warnings.append("The parameter Jacobian is rank-deficient; one or more parameters are not locally identifiable from these observations.")
    elif not math.isfinite(condition) or condition > 1e10:
        identifiability_status = "ill-conditioned"
        warnings.append("The parameter information matrix is ill-conditioned; parameter uncertainty may be unstable.")
    if any(row["atBound"] for row in estimates):
        warnings.append("At least one estimated parameter lies on a configured bound; review bounds and model identifiability.")

    estimation = {
        "schema": ESTIMATION_SCHEMA,
        "version": VERSION,
        "recordType": "dynamic-parameter-estimation",
        "createdAt": _now(),
        "system": fitted_definition,
        "optimizer": {"method": "scipy-least_squares", "loss": loss, "fScale": f_scale, "success": True, "message": str(result.message), "nfev": int(result.nfev), "cost": float(result.cost), "optimality": float(result.optimality)},
        "estimatedParameters": estimates,
        "fixedParameters": fixed,
        "metrics": {"n": n, "parameterCount": p, "degreesOfFreedom": dof, "sse": sse, "rmse": rmse, "mae": mae, "bias": bias, "rSquared": r2},
        "identifiability": {"status": identifiability_status, "jacobianRank": rank, "parameterCount": p, "conditionNumber": condition, "covariance": covariance, "warnings": warnings},
        "residuals": residual_records,
        "graphs": {"fit": fit_graph, "residuals": residual_graph},
        "boundaries": {"arbitraryCode": False, "safeDeclarativeDerivativeExpressions": True},
    }
    hashable = deepcopy(estimation)
    hashable.pop("estimationHash", None)
    estimation["estimationHash"] = _digest(hashable)
    return {"ok": True, "estimation": estimation}


def templates() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "templates": {
            "exponential-decay": {
                "title": "Exponential decay ODE",
                "independentVariable": {"symbol": "t", "label": "Time", "unit": "s"},
                "states": [{"symbol": "X", "label": "Quantity", "unit": "", "initial": 10.0}],
                "parameters": [{"symbol": "k", "label": "Decay rate", "unit": "1/s", "role": "estimated", "value": 0.35, "bounds": {"lower": 0.0, "upper": 5.0}}],
                "equations": [{"state": "X", "rhs": "-k*X"}],
                "timeSpan": {"start": 0.0, "end": 10.0, "points": 201},
            },
            "logistic-growth": {
                "title": "Logistic growth ODE",
                "independentVariable": {"symbol": "t", "label": "Time", "unit": "day"},
                "states": [{"symbol": "N", "label": "Population", "unit": "", "initial": 10.0}],
                "parameters": [{"symbol": "r", "label": "Growth rate", "unit": "1/day", "role": "estimated", "value": 0.5, "bounds": {"lower": 0.0, "upper": 5.0}}, {"symbol": "K", "label": "Carrying capacity", "unit": "", "role": "estimated", "value": 100.0, "bounds": {"lower": 10.0, "upper": 10000.0}}],
                "equations": [{"state": "N", "rhs": "r*N*(1-N/K)"}],
                "timeSpan": {"start": 0.0, "end": 20.0, "points": 301},
            },
            "sir": {
                "title": "SIR compartment model",
                "independentVariable": {"symbol": "t", "label": "Time", "unit": "day"},
                "states": [{"symbol": "S", "label": "Susceptible", "unit": "people", "initial": 990.0}, {"symbol": "I", "label": "Infectious", "unit": "people", "initial": 10.0}, {"symbol": "R", "label": "Recovered", "unit": "people", "initial": 0.0}],
                "parameters": [{"symbol": "beta", "label": "Transmission rate", "unit": "1/day", "role": "estimated", "value": 0.35, "bounds": {"lower": 0.0, "upper": 3.0}}, {"symbol": "gamma", "label": "Recovery rate", "unit": "1/day", "role": "estimated", "value": 0.1, "bounds": {"lower": 0.0, "upper": 2.0}}],
                "constants": [{"symbol": "Pop", "label": "Population", "unit": "people", "value": 1000.0}],
                "equations": [{"state": "S", "rhs": "-beta*S*I/Pop"}, {"state": "I", "rhs": "beta*S*I/Pop-gamma*I"}, {"state": "R", "rhs": "gamma*I"}],
                "timeSpan": {"start": 0.0, "end": 120.0, "points": 481},
            },
            "predator-prey": {
                "title": "Lotka-Volterra predator-prey model",
                "independentVariable": {"symbol": "t", "label": "Time", "unit": ""},
                "states": [{"symbol": "Prey", "label": "Prey", "unit": "", "initial": 40.0}, {"symbol": "Pred", "label": "Predator", "unit": "", "initial": 9.0}],
                "parameters": [{"symbol": "alpha", "label": "Prey growth", "unit": "", "role": "estimated", "value": 0.1, "bounds": {"lower": 0.0, "upper": 2.0}}, {"symbol": "beta", "label": "Predation", "unit": "", "role": "estimated", "value": 0.02, "bounds": {"lower": 0.0, "upper": 1.0}}, {"symbol": "delta", "label": "Predator reproduction", "unit": "", "role": "estimated", "value": 0.01, "bounds": {"lower": 0.0, "upper": 1.0}}, {"symbol": "gamma", "label": "Predator loss", "unit": "", "role": "estimated", "value": 0.1, "bounds": {"lower": 0.0, "upper": 2.0}}],
                "equations": [{"state": "Prey", "rhs": "alpha*Prey-beta*Prey*Pred"}, {"state": "Pred", "rhs": "delta*Prey*Pred-gamma*Pred"}],
                "timeSpan": {"start": 0.0, "end": 80.0, "points": 401},
            },
        },
    }
