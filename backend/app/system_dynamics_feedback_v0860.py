from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any

from .equation_builder import EquationBuilderError, compile_equation, evaluate

VERSION = "0.86.0"
ENGINE_VERSION = "1.0.0"
MODEL_SCHEMA = "sc-lab-system-dynamics-model/0.86.0"
CAUSAL_SCHEMA = "sc-lab-causal-loop-model/0.86.0"
SIMULATION_SCHEMA = "sc-lab-stock-flow-simulation/0.86.0"
LEVERAGE_SCHEMA = "sc-lab-system-leverage-analysis/0.86.0"

MAX_VARIABLES = 256
MAX_LINKS = 1024
MAX_STOCKS = 64
MAX_FLOWS = 256
MAX_AUXILIARIES = 256
MAX_PARAMETERS = 256
MAX_STEPS = 100_000
MAX_LOOPS = 256
MAX_LOOP_LENGTH = 16


class SystemDynamicsV0860Error(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def _id(value: Any, label: str, fallback: str | None = None) -> str:
    text = str(value or fallback or "").strip()
    if not text or len(text) > 80 or not text[0].isalpha() or not all(ch.isalnum() or ch == "_" for ch in text):
        raise SystemDynamicsV0860Error(f"{label} must be a safe identifier beginning with a letter")
    return text


def _text(value: Any, label: str, max_len: int = 500, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise SystemDynamicsV0860Error(f"{label} is required")
    if len(text) > max_len:
        raise SystemDynamicsV0860Error(f"{label} exceeds {max_len} characters")
    return text


def _number(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise SystemDynamicsV0860Error(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise SystemDynamicsV0860Error(f"{label} must be finite")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "capabilities": {
            "causalLoopDiagrams": True,
            "reinforcingBalancingLoops": True,
            "explicitDelays": True,
            "stockFlowModels": True,
            "auxiliaryVariables": True,
            "safeEquationEvaluation": True,
            "eulerIntegration": True,
            "rk4Integration": True,
            "scenarioSimulation": True,
            "structuralLeverageAnalysis": True,
            "graphStudioHandoff": True,
            "provenanceFingerprinting": True,
        },
        "limits": {
            "variables": MAX_VARIABLES,
            "links": MAX_LINKS,
            "stocks": MAX_STOCKS,
            "flows": MAX_FLOWS,
            "auxiliaries": MAX_AUXILIARIES,
            "parameters": MAX_PARAMETERS,
            "simulationSteps": MAX_STEPS,
            "feedbackLoops": MAX_LOOPS,
            "feedbackLoopLength": MAX_LOOP_LENGTH,
        },
        "boundaries": {
            "causalLinkInference": False,
            "automaticEquationGeneration": False,
            "automaticLeveragePointRanking": False,
            "paradigmInference": False,
            "hiddenDelays": False,
            "silentStockClamping": False,
            "automaticUnitConversion": False,
            "arbitraryCode": False,
            "networkAccess": False,
            "filesystemAccess": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "system-dynamics-feedback-stock-flow-ready",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "engine": "system-dynamics",
        "causalLoopDiagrams": True,
        "stockFlowModels": True,
        "reinforcingBalancingLoops": True,
        "scenarioSimulation": True,
        "structuralLeverageAnalysis": True,
        "v0850WebGL2Compatibility": True,
        "v0830ProvenanceCompatibility": True,
        "arbitraryCode": False,
    }


def normalize_causal_loop(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SystemDynamicsV0860Error("causal-loop model must be an object")
    variables = payload.get("variables") or []
    links = payload.get("links") or []
    if not isinstance(variables, list) or not variables or len(variables) > MAX_VARIABLES:
        raise SystemDynamicsV0860Error(f"variables must contain 1..{MAX_VARIABLES} records")
    if not isinstance(links, list) or len(links) > MAX_LINKS:
        raise SystemDynamicsV0860Error(f"links must contain no more than {MAX_LINKS} records")
    normalized_vars = []
    seen = set()
    for i, row in enumerate(variables):
        if not isinstance(row, dict):
            raise SystemDynamicsV0860Error("variables must contain objects")
        vid = _id(row.get("id"), f"variables[{i}].id")
        if vid in seen:
            raise SystemDynamicsV0860Error(f"duplicate variable id: {vid}")
        seen.add(vid)
        normalized_vars.append({
            "id": vid,
            "label": _text(row.get("label") or vid, f"variables[{i}].label", 160, True),
            "unit": _text(row.get("unit"), f"variables[{i}].unit", 80),
            "kind": str(row.get("kind") or "variable").strip().lower(),
            "evidence": _text(row.get("evidence"), f"variables[{i}].evidence", 1000),
        })
    normalized_links = []
    for i, row in enumerate(links):
        if not isinstance(row, dict):
            raise SystemDynamicsV0860Error("links must contain objects")
        source = _id(row.get("source"), f"links[{i}].source")
        target = _id(row.get("target"), f"links[{i}].target")
        if source not in seen or target not in seen:
            raise SystemDynamicsV0860Error(f"links[{i}] references an undeclared variable")
        raw_polarity = row.get("polarity", row.get("sign"))
        polarity = 1 if raw_polarity in {1, "+", "+1", "positive", "same"} else -1 if raw_polarity in {-1, "-", "-1", "negative", "opposite"} else None
        if polarity is None:
            raise SystemDynamicsV0860Error(f"links[{i}].polarity must be explicit positive/+ or negative/-")
        normalized_links.append({
            "id": _id(row.get("id"), f"links[{i}].id", f"link_{i+1}"),
            "source": source,
            "target": target,
            "polarity": polarity,
            "delay": bool(row.get("delay", False)),
            "evidence": _text(row.get("evidence"), f"links[{i}].evidence", 1000),
        })
    out = {
        "schema": CAUSAL_SCHEMA,
        "version": VERSION,
        "title": _text(payload.get("title") or "Causal-loop model", "title", 200, True),
        "variables": normalized_vars,
        "links": normalized_links,
        "assumptions": [_text(x, "assumption", 1000, True) for x in (payload.get("assumptions") or [])][:100],
        "provenance": deepcopy(payload.get("provenance") or {}),
        "boundaries": {"causalLinkInference": False, "hiddenDelays": False},
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def analyze_feedback(payload: dict[str, Any]) -> dict[str, Any]:
    model = normalize_causal_loop(payload.get("model") or payload)
    graph: dict[str, list[tuple[str, int, bool, str]]] = {v["id"]: [] for v in model["variables"]}
    for link in model["links"]:
        graph[link["source"]].append((link["target"], link["polarity"], link["delay"], link["id"]))
    loops: dict[tuple[str, ...], dict[str, Any]] = {}

    def canonical(nodes: list[str]) -> tuple[str, ...]:
        body = nodes[:-1]
        rotations = [tuple(body[i:] + body[:i]) for i in range(len(body))]
        return min(rotations)

    def dfs(start: str, node: str, path: list[str], signs: list[int], delays: list[bool], link_ids: list[str]):
        if len(loops) >= MAX_LOOPS or len(path) > MAX_LOOP_LENGTH:
            return
        for target, sign, delay, lid in graph.get(node, []):
            if target == start and len(path) >= 2:
                nodes = path + [start]
                key = canonical(nodes)
                if key not in loops:
                    product = math.prod(signs + [sign])
                    loops[key] = {
                        "id": f"loop_{len(loops)+1}",
                        "variables": nodes,
                        "linkIds": link_ids + [lid],
                        "polarity": product,
                        "type": "reinforcing" if product > 0 else "balancing",
                        "containsDelay": any(delays + [delay]),
                    }
            elif target not in path:
                dfs(start, target, path + [target], signs + [sign], delays + [delay], link_ids + [lid])

    for start in sorted(graph):
        dfs(start, start, [start], [], [], [])
    rows = sorted(loops.values(), key=lambda x: (x["type"], x["variables"]))
    participation = {vid: 0 for vid in graph}
    for loop in rows:
        for vid in set(loop["variables"][:-1]):
            participation[vid] += 1
    return {
        "ok": True,
        "schema": "sc-lab-feedback-loop-analysis/0.86.0",
        "version": VERSION,
        "modelFingerprint": model["fingerprint"],
        "loopCount": len(rows),
        "reinforcingLoopCount": sum(1 for x in rows if x["type"] == "reinforcing"),
        "balancingLoopCount": sum(1 for x in rows if x["type"] == "balancing"),
        "loops": rows,
        "loopParticipation": participation,
        "truncated": len(rows) >= MAX_LOOPS,
        "boundaries": {"loopClassificationUsesDeclaredPolarityOnly": True, "causalStrengthInference": False},
    }


def _topological_auxiliaries(auxiliaries: list[dict[str, Any]], declared: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ids = [x["id"] for x in auxiliaries]
    auxset = set(ids)
    compiled: dict[str, Any] = {}
    deps: dict[str, set[str]] = {}
    for row in auxiliaries:
        try:
            ce = compile_equation(row["equation"], declared | auxset, row["id"])
        except EquationBuilderError as exc:
            raise SystemDynamicsV0860Error(f"auxiliary {row['id']}: {exc}") from exc
        compiled[row["id"]] = ce
        deps[row["id"]] = {s for s in ce.symbols if s in auxset and s != row["id"]}
    ordered = []
    pending = set(ids)
    while pending:
        ready = sorted(x for x in pending if not (deps[x] & pending))
        if not ready:
            raise SystemDynamicsV0860Error("auxiliary equations contain an algebraic dependency cycle; explicit algebraic-loop solving is not enabled")
        for x in ready:
            ordered.append(next(r for r in auxiliaries if r["id"] == x))
            pending.remove(x)
    return ordered, compiled


def normalize_stock_flow(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SystemDynamicsV0860Error("stock-flow model must be an object")
    stocks = payload.get("stocks") or []
    flows = payload.get("flows") or []
    auxiliaries = payload.get("auxiliaries") or []
    parameters = payload.get("parameters") or []
    if not isinstance(stocks, list) or not stocks or len(stocks) > MAX_STOCKS:
        raise SystemDynamicsV0860Error(f"stocks must contain 1..{MAX_STOCKS} records")
    if not isinstance(flows, list) or len(flows) > MAX_FLOWS:
        raise SystemDynamicsV0860Error(f"flows must contain no more than {MAX_FLOWS} records")
    if not isinstance(auxiliaries, list) or len(auxiliaries) > MAX_AUXILIARIES:
        raise SystemDynamicsV0860Error(f"auxiliaries must contain no more than {MAX_AUXILIARIES} records")
    if not isinstance(parameters, list) or len(parameters) > MAX_PARAMETERS:
        raise SystemDynamicsV0860Error(f"parameters must contain no more than {MAX_PARAMETERS} records")

    all_ids: set[str] = set()
    norm_stocks = []
    for i, row in enumerate(stocks):
        sid = _id(row.get("id"), f"stocks[{i}].id")
        if sid in all_ids: raise SystemDynamicsV0860Error(f"duplicate symbol: {sid}")
        all_ids.add(sid)
        norm_stocks.append({"id": sid, "label": _text(row.get("label") or sid, f"stocks[{i}].label", 160, True), "initial": _number(row.get("initial", 0), f"stocks[{i}].initial"), "unit": _text(row.get("unit"), f"stocks[{i}].unit", 80)})
    norm_params = []
    for i, row in enumerate(parameters):
        pid = _id(row.get("id"), f"parameters[{i}].id")
        if pid in all_ids: raise SystemDynamicsV0860Error(f"duplicate symbol: {pid}")
        all_ids.add(pid)
        norm_params.append({"id": pid, "value": _number(row.get("value"), f"parameters[{i}].value"), "unit": _text(row.get("unit"), f"parameters[{i}].unit", 80)})
    norm_aux = []
    for i, row in enumerate(auxiliaries):
        aid = _id(row.get("id"), f"auxiliaries[{i}].id")
        if aid in all_ids: raise SystemDynamicsV0860Error(f"duplicate symbol: {aid}")
        all_ids.add(aid)
        norm_aux.append({"id": aid, "label": _text(row.get("label") or aid, f"auxiliaries[{i}].label", 160, True), "equation": _text(row.get("equation"), f"auxiliaries[{i}].equation", 2000, True), "unit": _text(row.get("unit"), f"auxiliaries[{i}].unit", 80)})
    norm_flows = []
    stock_ids = {x["id"] for x in norm_stocks}
    for i, row in enumerate(flows):
        fid = _id(row.get("id"), f"flows[{i}].id")
        if fid in all_ids: raise SystemDynamicsV0860Error(f"duplicate symbol: {fid}")
        all_ids.add(fid)
        source = row.get("sourceStock")
        target = row.get("targetStock")
        source = _id(source, f"flows[{i}].sourceStock") if source else None
        target = _id(target, f"flows[{i}].targetStock") if target else None
        if source and source not in stock_ids: raise SystemDynamicsV0860Error(f"flows[{i}].sourceStock is undeclared")
        if target and target not in stock_ids: raise SystemDynamicsV0860Error(f"flows[{i}].targetStock is undeclared")
        if source is None and target is None: raise SystemDynamicsV0860Error(f"flows[{i}] must connect to at least one stock")
        norm_flows.append({"id": fid, "label": _text(row.get("label") or fid, f"flows[{i}].label", 160, True), "equation": _text(row.get("equation"), f"flows[{i}].equation", 2000, True), "sourceStock": source, "targetStock": target, "unit": _text(row.get("unit"), f"flows[{i}].unit", 80)})

    declared = {"t"} | stock_ids | {x["id"] for x in norm_params}
    ordered_aux, compiled_aux = _topological_auxiliaries(norm_aux, declared)
    declared_with_aux = declared | {x["id"] for x in norm_aux}
    compiled_flows = {}
    for row in norm_flows:
        try:
            compiled_flows[row["id"]] = compile_equation(row["equation"], declared_with_aux, row["id"])
        except EquationBuilderError as exc:
            raise SystemDynamicsV0860Error(f"flow {row['id']}: {exc}") from exc

    out = {
        "schema": MODEL_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "title": _text(payload.get("title") or "Stock-flow model", "title", 200, True),
        "stocks": norm_stocks,
        "flows": norm_flows,
        "auxiliaries": norm_aux,
        "parameters": norm_params,
        "auxiliaryEvaluationOrder": [x["id"] for x in ordered_aux],
        "time": {
            "start": _number((payload.get("time") or {}).get("start", 0), "time.start"),
            "end": _number((payload.get("time") or {}).get("end", 100), "time.end"),
            "dt": _number((payload.get("time") or {}).get("dt", 1), "time.dt"),
            "method": str((payload.get("time") or {}).get("method") or "rk4").strip().lower(),
        },
        "assumptions": [_text(x, "assumption", 1000, True) for x in (payload.get("assumptions") or [])][:100],
        "provenance": deepcopy(payload.get("provenance") or {}),
        "boundaries": {"automaticEquationGeneration": False, "silentStockClamping": False, "automaticUnitConversion": False},
    }
    if out["time"]["end"] <= out["time"]["start"]: raise SystemDynamicsV0860Error("time.end must be greater than time.start")
    if out["time"]["dt"] <= 0: raise SystemDynamicsV0860Error("time.dt must be positive")
    if out["time"]["method"] not in {"euler", "rk4"}: raise SystemDynamicsV0860Error("time.method must be euler or rk4")
    steps = math.ceil((out["time"]["end"] - out["time"]["start"]) / out["time"]["dt"])
    if steps > MAX_STEPS: raise SystemDynamicsV0860Error(f"simulation exceeds {MAX_STEPS} steps")
    # Compile once during normalization to prove all equations are safe.
    _ = compiled_aux, compiled_flows
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return out


def _compile_model(model: dict[str, Any]):
    stock_ids = {x["id"] for x in model["stocks"]}
    param_ids = {x["id"] for x in model["parameters"]}
    aux_ids = {x["id"] for x in model["auxiliaries"]}
    declared = {"t"} | stock_ids | param_ids | aux_ids
    aux = {row["id"]: compile_equation(row["equation"], declared, row["id"]) for row in model["auxiliaries"]}
    flows = {row["id"]: compile_equation(row["equation"], declared, row["id"]) for row in model["flows"]}
    return aux, flows


def simulate_stock_flow(payload: dict[str, Any]) -> dict[str, Any]:
    model = normalize_stock_flow(payload.get("model") or payload)
    parameter_overrides = payload.get("parameterValues") or {}
    if not isinstance(parameter_overrides, dict): raise SystemDynamicsV0860Error("parameterValues must be an object")
    params = {x["id"]: x["value"] for x in model["parameters"]}
    for key, value in parameter_overrides.items():
        if key not in params: raise SystemDynamicsV0860Error(f"unknown parameter override: {key}")
        params[key] = _number(value, f"parameterValues.{key}")
    aux_compiled, flow_compiled = _compile_model(model)
    aux_order = model["auxiliaryEvaluationOrder"]
    stocks = [x["id"] for x in model["stocks"]]
    state = {x["id"]: x["initial"] for x in model["stocks"]}

    def rates(t: float, s: dict[str, float]):
        values = {"t": t, **params, **s}
        aux_values: dict[str, float] = {}
        for aid in aux_order:
            aux_values[aid] = evaluate(aux_compiled[aid], {**values, **aux_values})
        full = {**values, **aux_values}
        flow_values = {fid: evaluate(compiled, full) for fid, compiled in flow_compiled.items()}
        deriv = {sid: 0.0 for sid in stocks}
        for row in model["flows"]:
            value = flow_values[row["id"]]
            if row["sourceStock"]: deriv[row["sourceStock"]] -= value
            if row["targetStock"]: deriv[row["targetStock"]] += value
        return deriv, aux_values, flow_values

    start, end, dt, method = model["time"]["start"], model["time"]["end"], model["time"]["dt"], model["time"]["method"]
    rows = []
    t = start
    step = 0
    while True:
        deriv, aux_values, flow_values = rates(t, state)
        rows.append({"step": step, "t": t, "stocks": deepcopy(state), "auxiliaries": aux_values, "flows": flow_values})
        if t >= end - 1e-12: break
        h = min(dt, end - t)
        if method == "euler":
            state = {sid: state[sid] + h * deriv[sid] for sid in stocks}
        else:
            k1 = deriv
            s2 = {sid: state[sid] + h * k1[sid] / 2 for sid in stocks}; k2, _, _ = rates(t + h/2, s2)
            s3 = {sid: state[sid] + h * k2[sid] / 2 for sid in stocks}; k3, _, _ = rates(t + h/2, s3)
            s4 = {sid: state[sid] + h * k3[sid] for sid in stocks}; k4, _, _ = rates(t + h, s4)
            state = {sid: state[sid] + h * (k1[sid] + 2*k2[sid] + 2*k3[sid] + k4[sid]) / 6 for sid in stocks}
        if not all(math.isfinite(v) for v in state.values()):
            raise SystemDynamicsV0860Error("simulation produced a non-finite stock value")
        t = round(t + h, 12)
        step += 1
        if step > MAX_STEPS: raise SystemDynamicsV0860Error("simulation exceeded the governed step limit")
    result = {
        "ok": True,
        "schema": SIMULATION_SCHEMA,
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "modelFingerprint": model["fingerprint"],
        "method": method,
        "parameterValues": params,
        "rowCount": len(rows),
        "rows": rows,
        "finalStocks": deepcopy(rows[-1]["stocks"]),
        "boundaries": {"silentStockClamping": False, "automaticUnitConversion": False, "forecastClaim": False},
    }
    result["fingerprint"] = _hash({k: v for k, v in result.items() if k not in {"fingerprint", "rows"}})
    return result


def analyze_leverage(payload: dict[str, Any]) -> dict[str, Any]:
    causal = normalize_causal_loop(payload.get("causalModel") or payload.get("model") or payload)
    feedback = analyze_feedback(causal)
    in_degree = {v["id"]: 0 for v in causal["variables"]}
    out_degree = {v["id"]: 0 for v in causal["variables"]}
    delay_touch = {v["id"]: 0 for v in causal["variables"]}
    for link in causal["links"]:
        out_degree[link["source"]] += 1; in_degree[link["target"]] += 1
        if link["delay"]:
            delay_touch[link["source"]] += 1; delay_touch[link["target"]] += 1
    participation = feedback["loopParticipation"]
    indicators = []
    for row in causal["variables"]:
        vid = row["id"]
        indicators.append({
            "variable": vid,
            "inDegree": in_degree[vid],
            "outDegree": out_degree[vid],
            "feedbackLoopParticipation": participation.get(vid, 0),
            "delayConnections": delay_touch[vid],
            "structuralIndicatorOnly": True,
        })
    indicators.sort(key=lambda r: (-r["feedbackLoopParticipation"], -(r["inDegree"] + r["outDegree"]), r["variable"]))
    return {
        "ok": True,
        "schema": LEVERAGE_SCHEMA,
        "version": VERSION,
        "causalModelFingerprint": causal["fingerprint"],
        "indicators": indicators,
        "declaredInterventions": deepcopy(payload.get("interventions") or []),
        "meadowsCategories": ["parameters", "buffers", "stock-flow-structure", "delays", "balancing-feedback", "reinforcing-feedback", "information-flows", "rules", "self-organization", "goals", "paradigms"],
        "boundaries": {"automaticLeveragePointRanking": False, "paradigmInference": False, "policyRecommendation": False},
    }


def build_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    causal = normalize_causal_loop(payload["causalModel"]) if payload.get("causalModel") else None
    stock_flow = normalize_stock_flow(payload["stockFlowModel"]) if payload.get("stockFlowModel") else None
    if causal is None and stock_flow is None:
        raise SystemDynamicsV0860Error("workspace requires causalModel and/or stockFlowModel")
    out = {
        "schema": "sc-lab-system-dynamics-workspace/0.86.0",
        "version": VERSION,
        "engineVersion": ENGINE_VERSION,
        "title": _text(payload.get("title") or "System dynamics workspace", "title", 200, True),
        "causalModel": causal,
        "stockFlowModel": stock_flow,
        "graphStudio": {"compatible": True, "preferredRenderer": "webgl2", "fallbackRenderer": "svg2d"},
        "provenance": deepcopy(payload.get("provenance") or {}),
    }
    out["fingerprint"] = _hash({k: v for k, v in out.items() if k != "fingerprint"})
    return {"ok": True, "workspace": out}
