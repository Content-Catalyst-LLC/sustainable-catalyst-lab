from __future__ import annotations

from copy import deepcopy
import math
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root

from .dynamic_systems import (
    DynamicSystemError,
    _compile_system,
    _digest,
    _graph,
    _now,
    _parameter_values,
    _rhs_function,
    normalize_definition,
)
from .equation_builder import EquationBuilderError, compile_equation, evaluate

VERSION = "0.54.0"
STUDY_SCHEMA = "sc-lab-dynamic-systems-advanced-study/0.54.0"
SIMULATION_SCHEMA = "sc-lab-dynamic-systems-advanced-simulation/0.54.0"
BIFURCATION_SCHEMA = "sc-lab-dynamic-systems-bifurcation/0.54.0"
PHASE_SCHEMA = "sc-lab-dynamic-systems-phase-analysis/0.54.0"
MAX_EVENTS = 12
MAX_REGIMES = 24
MAX_BIFURCATION_POINTS = 121
MAX_PHASE_GRID = 41


class DynamicSystemsV0540Error(ValueError):
    status_code = 422


def _text(value: Any, name: str, max_len: int = 240, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise DynamicSystemsV0540Error(f"{name} is required.")
    if len(text) > max_len:
        raise DynamicSystemsV0540Error(f"{name} exceeds {max_len} characters.")
    return text


def _finite(value: Any, name: str, required: bool = False) -> float | None:
    if value is None or value == "":
        if required:
            raise DynamicSystemsV0540Error(f"{name} is required.")
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DynamicSystemsV0540Error(f"{name} must be numeric.") from exc
    if not math.isfinite(number):
        raise DynamicSystemsV0540Error(f"{name} must be finite.")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "studySchema": STUDY_SCHEMA,
        "simulationSchema": SIMULATION_SCHEMA,
        "bifurcationSchema": BIFURCATION_SCHEMA,
        "phaseSchema": PHASE_SCHEMA,
        "capabilities": {
            "safeStateEvents": True,
            "terminalEvents": True,
            "scheduledRegimeChanges": True,
            "piecewiseConstantParameterProfiles": True,
            "governedStateResetsAtRegimeBoundaries": True,
            "numericalBifurcationScans": True,
            "twoStateAutonomousPhaseAnalysis": True,
            "equilibriumSearch": True,
            "localStabilityClassification": True,
            "nullclineApproximation": True,
            "graphStudioHandoff": True,
        },
        "limits": {
            "events": MAX_EVENTS,
            "regimes": MAX_REGIMES,
            "bifurcationPoints": MAX_BIFURCATION_POINTS,
            "phaseGridPointsPerAxis": MAX_PHASE_GRID,
        },
        "boundaries": {
            "arbitraryCode": False,
            "arbitraryPython": False,
            "delayDifferentialEquations": False,
            "stochasticDifferentialEquations": False,
            "partialDifferentialEquations": False,
            "automaticControlActions": False,
            "formalBifurcationProof": False,
            "automaticRegimeInference": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "dynamic-systems-ii-ready",
        "version": VERSION,
        "events": True,
        "regimeChanges": True,
        "bifurcationScans": True,
        "advancedPhaseAnalysis": True,
        "arbitraryCode": False,
    }


def _compile_event_expression(system, expression: str, index: int):
    declared = [
        system.definition["independentVariable"]["symbol"],
        *system.state_symbols,
        *system.parameter_symbols,
        *system.constant_values.keys(),
    ]
    try:
        return compile_equation(expression, declared, f"event_{index}")
    except EquationBuilderError as exc:
        raise DynamicSystemsV0540Error(f"events[{index}].expression: {exc}") from exc


def _normalize_events(system, raw: Any) -> list[dict[str, Any]]:
    rows = raw or []
    if not isinstance(rows, list):
        raise DynamicSystemsV0540Error("events must be an array.")
    if len(rows) > MAX_EVENTS:
        raise DynamicSystemsV0540Error(f"No more than {MAX_EVENTS} events may be configured.")
    out = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DynamicSystemsV0540Error("events must contain objects.")
        expression = _text(row.get("expression") or row.get("equation"), f"events[{index}].expression", 1200, True)
        compiled = _compile_event_expression(system, expression, index)
        try:
            direction = int(row.get("direction", 0))
        except (TypeError, ValueError) as exc:
            raise DynamicSystemsV0540Error("event direction must be -1, 0, or 1.") from exc
        if direction not in {-1, 0, 1}:
            raise DynamicSystemsV0540Error("event direction must be -1, 0, or 1.")
        out.append({
            "id": _text(row.get("id") or f"event-{index+1}", f"events[{index}].id", 80, True),
            "label": _text(row.get("label") or f"Event {index+1}", f"events[{index}].label", 160, True),
            "expression": compiled.rhs,
            "normalizedExpression": compiled.normalized,
            "direction": direction,
            "terminal": bool(row.get("terminal", False)),
            "note": _text(row.get("note"), f"events[{index}].note", 500),
        })
    return out


def _normalize_regimes(system, raw: Any) -> list[dict[str, Any]]:
    rows = raw or []
    if not isinstance(rows, list):
        raise DynamicSystemsV0540Error("regimes must be an array.")
    if len(rows) > MAX_REGIMES:
        raise DynamicSystemsV0540Error(f"No more than {MAX_REGIMES} regime changes may be configured.")
    start = float(system.definition["timeSpan"]["start"])
    end = float(system.definition["timeSpan"]["end"])
    parameter_rows = {row["symbol"]: row for row in system.definition["parameters"]}
    state_symbols = set(system.state_symbols)
    out = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DynamicSystemsV0540Error("regimes must contain objects.")
        at = float(_finite(row.get("time"), f"regimes[{index}].time", True))
        if not (start < at < end):
            raise DynamicSystemsV0540Error("Regime-change times must fall strictly inside the simulation time span.")
        parameter_values = row.get("parameterValues") or {}
        state_values = row.get("stateValues") or {}
        if not isinstance(parameter_values, dict) or not isinstance(state_values, dict):
            raise DynamicSystemsV0540Error("Regime parameterValues and stateValues must be objects.")
        normalized_params: dict[str, float] = {}
        for symbol, value in parameter_values.items():
            if symbol not in parameter_rows:
                raise DynamicSystemsV0540Error(f"Unknown regime parameter: {symbol}.")
            number = float(_finite(value, f"regime parameter {symbol}", True))
            bounds = parameter_rows[symbol].get("bounds") or {}
            lo, hi = bounds.get("lower"), bounds.get("upper")
            if lo is not None and number < float(lo):
                raise DynamicSystemsV0540Error(f"Regime value for {symbol} is below its declared lower bound.")
            if hi is not None and number > float(hi):
                raise DynamicSystemsV0540Error(f"Regime value for {symbol} is above its declared upper bound.")
            normalized_params[symbol] = number
        normalized_states: dict[str, float] = {}
        for symbol, value in state_values.items():
            if symbol not in state_symbols:
                raise DynamicSystemsV0540Error(f"Unknown regime state: {symbol}.")
            normalized_states[symbol] = float(_finite(value, f"regime state {symbol}", True))
        if not normalized_params and not normalized_states:
            raise DynamicSystemsV0540Error("A regime change must modify at least one parameter or state value.")
        out.append({
            "id": _text(row.get("id") or f"regime-{index+1}", f"regimes[{index}].id", 80, True),
            "label": _text(row.get("label") or f"Regime {index+1}", f"regimes[{index}].label", 160, True),
            "time": at,
            "parameterValues": normalized_params,
            "stateValues": normalized_states,
            "evidence": _text(row.get("evidence") or row.get("source"), f"regimes[{index}].evidence", 500),
        })
    out.sort(key=lambda row: row["time"])
    if any(out[i]["time"] == out[i-1]["time"] for i in range(1, len(out))):
        raise DynamicSystemsV0540Error("Only one regime change may be configured at a given time.")
    return out


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DynamicSystemsV0540Error("Advanced dynamic-system study must be an object.")
    try:
        system_definition = normalize_definition(payload.get("system") or payload.get("definition") or payload)
        system = _compile_system(system_definition)
    except DynamicSystemError as exc:
        raise DynamicSystemsV0540Error(str(exc)) from exc
    events = _normalize_events(system, payload.get("events"))
    regimes = _normalize_regimes(system, payload.get("regimes"))
    study = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "recordType": "dynamic-systems-advanced-study",
        "title": _text(payload.get("title") or f"{system.definition['title']} — Dynamic Systems II", "title", 180, True),
        "system": system.definition,
        "events": events,
        "regimes": regimes,
        "assumptions": [_text(v, "assumption", 500, True) for v in (payload.get("assumptions") or [])][:50],
        "limitations": [_text(v, "limitation", 500, True) for v in (payload.get("limitations") or [])][:50],
        "provenance": deepcopy(payload.get("provenance") or {}),
        "createdAt": _now(),
        "boundaries": policies()["boundaries"],
    }
    hashable = deepcopy(study)
    hashable.pop("studyHash", None)
    study["studyHash"] = _digest(hashable)
    return study


def _event_functions(system, params: dict[str, float], events: list[dict[str, Any]]):
    time_symbol = system.definition["independentVariable"]["symbol"]
    declared = [time_symbol, *system.state_symbols, *system.parameter_symbols, *system.constant_values.keys()]
    functions = []
    for index, event in enumerate(events):
        compiled = compile_equation(event["expression"], declared, f"event_{index}")

        def event_fn(t, y, compiled=compiled):
            env = {time_symbol: float(t), **system.constant_values, **params}
            env.update({symbol: float(y[i]) for i, symbol in enumerate(system.state_symbols)})
            return float(evaluate(compiled, env))

        event_fn.terminal = bool(event["terminal"])
        event_fn.direction = float(event["direction"])
        functions.append(event_fn)
    return functions


def _segment_solve(system, params: dict[str, float], start: float, end: float, y0: np.ndarray, t_eval: np.ndarray, events: list[dict[str, Any]]):
    solver = system.definition["solver"]
    kwargs: dict[str, Any] = {
        "method": solver["method"],
        "rtol": solver["rtol"],
        "atol": solver["atol"],
        "t_eval": t_eval,
        "events": _event_functions(system, params, events) if events else None,
        "dense_output": True,
    }
    if solver.get("maxStep") is not None:
        kwargs["max_step"] = solver["maxStep"]
    try:
        result = solve_ivp(_rhs_function(system, params), (start, end), y0, **kwargs)
    except (DynamicSystemError, EquationBuilderError, ValueError, ArithmeticError, OverflowError) as exc:
        raise DynamicSystemsV0540Error(f"Advanced ODE integration failed: {exc}") from exc
    if not result.success:
        raise DynamicSystemsV0540Error(f"Advanced ODE integration failed: {result.message}")
    return result


def simulate(payload: dict[str, Any]) -> dict[str, Any]:
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
    system = _compile_system(study["system"])
    base_params = _parameter_values(system, payload.get("parameterValues") if isinstance(payload.get("parameterValues"), dict) else None)
    span = system.definition["timeSpan"]
    start, end, points = float(span["start"]), float(span["end"]), int(span["points"])
    requested_times = np.linspace(start, end, points, dtype=float)
    regime_by_time = {float(row["time"]): row for row in study["regimes"]}
    boundaries = sorted({start, end, *regime_by_time.keys()})
    current_params = dict(base_params)
    current_y = np.asarray([row["initial"] for row in system.definition["states"]], dtype=float)
    all_rows: list[dict[str, float]] = []
    event_records: list[dict[str, Any]] = []
    regime_records: list[dict[str, Any]] = []
    nfev = njev = nlu = 0
    terminal_reached = False
    terminal_time = None
    time_symbol = system.definition["independentVariable"]["symbol"]

    for seg_index in range(len(boundaries) - 1):
        seg_start, seg_end = boundaries[seg_index], boundaries[seg_index + 1]
        mask = (requested_times >= seg_start - 1e-12) & (requested_times <= seg_end + 1e-12)
        seg_times = requested_times[mask]
        seg_times = np.unique(np.concatenate(([seg_start], seg_times, [seg_end]))).astype(float)
        result = _segment_solve(system, current_params, seg_start, seg_end, current_y, seg_times, study["events"])
        nfev += int(getattr(result, "nfev", 0) or 0)
        njev += int(getattr(result, "njev", 0) or 0)
        nlu += int(getattr(result, "nlu", 0) or 0)
        for col, t in enumerate(result.t):
            if all_rows and abs(all_rows[-1][time_symbol] - float(t)) < 1e-12:
                continue
            row = {time_symbol: float(t)}
            row.update({symbol: float(result.y[i, col]) for i, symbol in enumerate(system.state_symbols)})
            all_rows.append(row)
        if study["events"]:
            for event_index, times in enumerate(result.t_events or []):
                event = study["events"][event_index]
                y_events = result.y_events[event_index] if result.y_events is not None else []
                for hit_index, t in enumerate(times):
                    states = {symbol: float(y_events[hit_index][i]) for i, symbol in enumerate(system.state_symbols)} if len(y_events) > hit_index else {}
                    event_records.append({
                        "eventId": event["id"], "label": event["label"], "time": float(t),
                        "terminal": bool(event["terminal"]), "direction": event["direction"], "stateValues": states,
                    })
                    if event["terminal"]:
                        terminal_reached, terminal_time = True, float(t)
        if terminal_reached:
            if result.sol is not None and terminal_time is not None:
                y_terminal = np.asarray(result.sol(terminal_time), dtype=float)
                if not all_rows or abs(all_rows[-1][time_symbol] - terminal_time) > 1e-10:
                    row = {time_symbol: terminal_time}
                    row.update({symbol: float(y_terminal[i]) for i, symbol in enumerate(system.state_symbols)})
                    all_rows.append(row)
            break
        current_y = np.asarray(result.y[:, -1], dtype=float)
        regime = regime_by_time.get(seg_end)
        if regime:
            current_params.update(regime["parameterValues"])
            for symbol, value in regime["stateValues"].items():
                current_y[system.state_symbols.index(symbol)] = float(value)
            regime_records.append({
                "regimeId": regime["id"], "label": regime["label"], "time": seg_end,
                "parameterValues": deepcopy(current_params), "stateValues": deepcopy(regime["stateValues"]), "evidence": regime["evidence"],
            })
            if all_rows and abs(all_rows[-1][time_symbol] - seg_end) < 1e-10:
                for i, symbol in enumerate(system.state_symbols):
                    all_rows[-1][symbol] = float(current_y[i])

    iv = system.definition["independentVariable"]
    annotations = [{"type": "vertical-line", "x": r["time"], "label": r["label"]} for r in regime_records]
    annotations += [{"type": "vertical-line", "x": r["time"], "label": r["label"]} for r in event_records]
    series = []
    for state in system.definition["states"]:
        series.append({
            "id": f"state-{state['symbol']}", "label": state["label"], "mode": "line",
            "points": [{"x": row[time_symbol], "y": row[state["symbol"]]} for row in all_rows],
        })
    trajectory = _graph(
        f"{study['title']} — event/regime trajectories",
        iv["label"] + (f" ({iv['unit']})" if iv.get("unit") else ""), "State value", series,
        "Piecewise deterministic ODE trajectories with declared event detections and evidence-backed regime changes.", annotations,
    )
    phase = None
    if len(system.state_symbols) >= 2:
        sx, sy = system.definition["states"][0], system.definition["states"][1]
        phase = _graph(
            f"{study['title']} — phase trajectory", sx["label"], sy["label"],
            [{"id": "phase", "label": f"{sy['symbol']} vs {sx['symbol']}", "mode": "line-scatter", "points": [{"x": r[sx["symbol"]], "y": r[sy["symbol"]]} for r in all_rows]}],
            "Phase-space trajectory under the declared regime schedule.",
        )
    simulation = {
        "schema": SIMULATION_SCHEMA, "version": VERSION, "recordType": "dynamic-systems-advanced-simulation", "createdAt": _now(),
        "study": study, "parameterValuesInitial": base_params, "rows": all_rows, "rowCount": len(all_rows),
        "eventsDetected": event_records, "regimesApplied": regime_records,
        "terminalEventReached": terminal_reached, "terminalTime": terminal_time,
        "solver": {"method": system.definition["solver"]["method"], "nfev": nfev, "njev": njev, "nlu": nlu},
        "graphs": {"trajectory": trajectory, "phasePortrait": phase},
        "boundaries": policies()["boundaries"],
    }
    simulation["simulationHash"] = _digest(simulation)
    return {"ok": True, "simulation": simulation}


def bifurcation_scan(payload: dict[str, Any]) -> dict[str, Any]:
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
    if study["events"] or study["regimes"]:
        raise DynamicSystemsV0540Error("Bifurcation scans require the base autonomous regime; remove events and regime changes for this analysis.")
    system = _compile_system(study["system"])
    sweep = payload.get("sweep") or {}
    if not isinstance(sweep, dict):
        raise DynamicSystemsV0540Error("sweep must be an object.")
    parameter = _text(sweep.get("parameter"), "sweep.parameter", 64, True)
    parameter_rows = {row["symbol"]: row for row in system.definition["parameters"]}
    if parameter not in parameter_rows:
        raise DynamicSystemsV0540Error(f"Unknown sweep parameter: {parameter}.")
    lower = float(_finite(sweep.get("lower"), "sweep.lower", True))
    upper = float(_finite(sweep.get("upper"), "sweep.upper", True))
    if upper <= lower:
        raise DynamicSystemsV0540Error("sweep.upper must be greater than sweep.lower.")
    bounds = parameter_rows[parameter].get("bounds") or {}
    if bounds.get("lower") is not None and lower < float(bounds["lower"]):
        raise DynamicSystemsV0540Error("Sweep lower bound is outside the declared parameter bound.")
    if bounds.get("upper") is not None and upper > float(bounds["upper"]):
        raise DynamicSystemsV0540Error("Sweep upper bound is outside the declared parameter bound.")
    points = int(sweep.get("points", 41))
    if points < 3 or points > MAX_BIFURCATION_POINTS:
        raise DynamicSystemsV0540Error(f"sweep.points must be between 3 and {MAX_BIFURCATION_POINTS}.")
    state_symbol = _text(sweep.get("state") or system.state_symbols[0], "sweep.state", 64, True)
    if state_symbol not in system.state_symbols:
        raise DynamicSystemsV0540Error(f"Unknown sweep state: {state_symbol}.")
    transient = float(_finite(sweep.get("transientFraction", 0.7), "sweep.transientFraction", True))
    if not 0.25 <= transient < 0.98:
        raise DynamicSystemsV0540Error("transientFraction must be between 0.25 and 0.98.")
    span = system.definition["timeSpan"]
    t_eval = np.linspace(float(span["start"]), float(span["end"]), int(span["points"]), dtype=float)
    tail_start = max(1, min(len(t_eval)-1, int(len(t_eval) * transient)))
    base = _parameter_values(system)
    rows = []
    for value in np.linspace(lower, upper, points):
        params = dict(base); params[parameter] = float(value)
        try:
            result = solve_ivp(_rhs_function(system, params), (float(t_eval[0]), float(t_eval[-1])), np.asarray([r["initial"] for r in system.definition["states"]], dtype=float), t_eval=t_eval, method=system.definition["solver"]["method"], rtol=system.definition["solver"]["rtol"], atol=system.definition["solver"]["atol"])
        except Exception as exc:
            raise DynamicSystemsV0540Error(f"Bifurcation scan integration failed at {parameter}={value:g}: {exc}") from exc
        if not result.success or not np.all(np.isfinite(result.y)):
            raise DynamicSystemsV0540Error(f"Bifurcation scan failed at {parameter}={value:g}.")
        values = result.y[system.state_symbols.index(state_symbol), tail_start:]
        rows.append({
            "parameter": float(value), "tailMinimum": float(np.min(values)), "tailMean": float(np.mean(values)),
            "tailMaximum": float(np.max(values)), "tailStdDev": float(np.std(values, ddof=0)), "terminal": float(values[-1]),
        })
    graph = _graph(
        f"{study['title']} — numerical bifurcation scan", parameter, state_symbol,
        [
            {"id":"tail-min","label":"Tail minimum","mode":"line-scatter","points":[{"x":r["parameter"],"y":r["tailMinimum"]} for r in rows]},
            {"id":"tail-mean","label":"Tail mean","mode":"line-scatter","points":[{"x":r["parameter"],"y":r["tailMean"]} for r in rows]},
            {"id":"tail-max","label":"Tail maximum","mode":"line-scatter","points":[{"x":r["parameter"],"y":r["tailMaximum"]} for r in rows]},
        ],
        "Numerical parameter sweep after discarding the declared transient fraction. This is exploratory bifurcation evidence, not a formal bifurcation proof.",
    )
    result = {
        "schema": BIFURCATION_SCHEMA, "version": VERSION, "recordType": "dynamic-system-bifurcation-scan", "createdAt": _now(),
        "study": study, "sweep": {"parameter": parameter, "lower": lower, "upper": upper, "points": points, "state": state_symbol, "transientFraction": transient},
        "rows": rows, "graph": graph,
        "interpretationBoundary": "Numerical tail summaries can reveal candidate transitions or oscillatory regimes; they are not a formal bifurcation proof and do not establish bifurcation type or global stability.",
        "boundaries": policies()["boundaries"],
    }
    result["analysisHash"] = _digest(result)
    return {"ok": True, "analysis": result}


def _classify_eigenvalues(values: np.ndarray) -> str:
    real = np.real(values)
    imag = np.imag(values)
    tol = 1e-7
    if np.any(real > tol) and np.any(real < -tol):
        return "saddle"
    if np.all(real < -tol):
        return "stable-focus" if np.any(np.abs(imag) > tol) else "stable-node"
    if np.all(real > tol):
        return "unstable-focus" if np.any(np.abs(imag) > tol) else "unstable-node"
    if np.all(np.abs(real) <= tol) and np.any(np.abs(imag) > tol):
        return "center-or-neutral"
    return "nonhyperbolic-or-indeterminate"


def phase_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
    if study["events"] or study["regimes"]:
        raise DynamicSystemsV0540Error("Equilibrium phase analysis requires one autonomous regime; remove events and regime changes.")
    system = _compile_system(study["system"])
    if len(system.state_symbols) != 2:
        raise DynamicSystemsV0540Error("Advanced equilibrium phase analysis currently requires exactly two state variables.")
    time_symbol = system.definition["independentVariable"]["symbol"]
    if any(time_symbol in (row.get("referencedSymbols") or []) for row in system.definition["equations"]):
        raise DynamicSystemsV0540Error("Equilibrium phase analysis requires an autonomous system whose derivatives do not explicitly reference time.")
    params = _parameter_values(system)
    sx, sy = system.state_symbols
    states = {row["symbol"]: row for row in system.definition["states"]}
    domain = payload.get("domain") or {}
    if not isinstance(domain, dict):
        raise DynamicSystemsV0540Error("domain must be an object.")

    def axis(symbol: str, key: str):
        initial = float(states[symbol]["initial"])
        default_span = max(1.0, abs(initial) * 0.75)
        spec = domain.get(key) or {}
        lo = float(_finite(spec.get("min", initial-default_span), f"domain.{key}.min", True))
        hi = float(_finite(spec.get("max", initial+default_span), f"domain.{key}.max", True))
        n = int(spec.get("points", 25))
        if hi <= lo:
            raise DynamicSystemsV0540Error(f"domain.{key}.max must exceed min.")
        if n < 7 or n > MAX_PHASE_GRID:
            raise DynamicSystemsV0540Error(f"domain.{key}.points must be between 7 and {MAX_PHASE_GRID}.")
        return lo, hi, n

    xlo, xhi, nx = axis(sx, "x")
    ylo, yhi, ny = axis(sy, "y")
    rhs = _rhs_function(system, params)
    xs, ys = np.linspace(xlo, xhi, nx), np.linspace(ylo, yhi, ny)
    cells = []
    dx_abs, dy_abs = [], []
    raw = []
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            deriv = np.asarray(rhs(float(system.definition["timeSpan"]["start"]), np.asarray([x, y], dtype=float)), dtype=float)
            speed = float(np.linalg.norm(deriv))
            raw.append((i, j, x, y, float(deriv[0]), float(deriv[1]), speed))
            dx_abs.append(abs(float(deriv[0]))); dy_abs.append(abs(float(deriv[1])))
            cells.append({"xIndex": i, "yIndex": j, "x": float(x), "y": float(y), "z": speed})
    dx_tol = max(np.quantile(dx_abs, 0.08), 1e-10)
    dy_tol = max(np.quantile(dy_abs, 0.08), 1e-10)
    xnull = [{"x": float(x), "y": float(y)} for _i,_j,x,y,dx,dy,_s in raw if abs(dx) <= dx_tol]
    ynull = [{"x": float(x), "y": float(y)} for _i,_j,x,y,dx,dy,_s in raw if abs(dy) <= dy_tol]

    equilibria: list[dict[str, Any]] = []
    seeds_x = np.linspace(xlo, xhi, 7); seeds_y = np.linspace(ylo, yhi, 7)
    for x0 in seeds_x:
        for y0 in seeds_y:
            found = root(lambda z: rhs(float(system.definition["timeSpan"]["start"]), np.asarray(z, dtype=float)), np.asarray([x0, y0], dtype=float))
            if not found.success or not np.all(np.isfinite(found.x)):
                continue
            x, y = map(float, found.x)
            if not (xlo - 1e-8 <= x <= xhi + 1e-8 and ylo - 1e-8 <= y <= yhi + 1e-8):
                continue
            if any(math.hypot(x-r["stateValues"][sx], y-r["stateValues"][sy]) < 1e-5 * max(1.0, abs(x), abs(y)) for r in equilibria):
                continue
            z = np.asarray([x, y], dtype=float)
            h = 1e-6 * max(1.0, np.linalg.norm(z))
            jac = np.column_stack([(rhs(0.0, z + np.eye(2)[k]*h) - rhs(0.0, z - np.eye(2)[k]*h))/(2*h) for k in range(2)])
            eig = np.linalg.eigvals(jac)
            equilibria.append({
                "stateValues": {sx: x, sy: y},
                "jacobian": jac.tolist(),
                "eigenvalues": [{"real": float(v.real), "imag": float(v.imag)} for v in eig],
                "classification": _classify_eigenvalues(eig),
            })
    speed_values = [c["z"] for c in cells]
    heatmap = {
        "schema": "sc-lab-scientific-graph/0.44.0", "version": VERSION, "kind": "heatmap",
        "title": f"{study['title']} — phase speed", "description": "Local vector-field speed across the declared two-state phase domain.",
        "xLabel": sx, "yLabel": sy, "xValues": [float(v) for v in xs], "yValues": [float(v) for v in ys], "cells": cells,
        "domain": {"x": [xlo, xhi], "y": [ylo, yhi], "z": [float(min(speed_values)), float(max(speed_values))]},
        "annotations": [{"type":"point","x":r["stateValues"][sx],"y":r["stateValues"][sy]} for r in equilibria],
        "interaction": {"tooltip": True, "zoom": True, "pan": True, "crosshair": True, "seriesToggle": False},
        "publication": {"subtitle":"","caption":"","source":"","method":"","notes":"","aspectRatio":"1:1","showGrid":False,"showLegend":False,"background":"white"},
        "exports": ["svg","png","csv","json"], "accessibility": {"role":"img","tabularFallback":True,"keyboardNavigation":True},
    }
    heatmap["graphHash"] = _digest(heatmap)
    phase_graph = _graph(
        f"{study['title']} — nullclines & equilibria", sx, sy,
        [
            {"id":"dx-nullcline","label":f"d{sx}/dt ≈ 0","mode":"scatter","points":xnull[:800]},
            {"id":"dy-nullcline","label":f"d{sy}/dt ≈ 0","mode":"scatter","points":ynull[:800]},
            {"id":"equilibria","label":"Equilibria","mode":"scatter","points":[{"x":r["stateValues"][sx],"y":r["stateValues"][sy],"label":r["classification"]} for r in equilibria]},
        ],
        "Grid-approximated nullclines and numerically located equilibria. Local stability is classified from finite-difference Jacobian eigenvalues.",
    )
    analysis = {
        "schema": PHASE_SCHEMA, "version": VERSION, "recordType": "dynamic-system-phase-analysis", "createdAt": _now(),
        "study": study, "states": [sx, sy], "domain": {"x":{"min":xlo,"max":xhi,"points":nx},"y":{"min":ylo,"max":yhi,"points":ny}},
        "equilibria": equilibria, "equilibriumCount": len(equilibria),
        "nullclineApproximation": {"dxPointCount": len(xnull), "dyPointCount": len(ynull), "dxTolerance": float(dx_tol), "dyTolerance": float(dy_tol)},
        "graphs": {"speedHeatmap": heatmap, "phasePlane": phase_graph},
        "interpretationBoundary": "Equilibria and stability classifications are local numerical evidence within the declared domain; they are not global stability proofs.",
        "boundaries": policies()["boundaries"],
    }
    analysis["analysisHash"] = _digest(analysis)
    return {"ok": True, "analysis": analysis}
