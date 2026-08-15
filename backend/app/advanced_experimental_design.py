from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
import math
import random
from typing import Any

import numpy as np

from .design_studies import DesignStudyError, normalize_factors

VERSION = "0.56.0"
DESIGN_SCHEMA = "sc-lab-advanced-experimental-design/0.56.0"
SEQUENTIAL_SCHEMA = "sc-lab-sequential-experiment-plan/0.56.0"
DIAGNOSTIC_SCHEMA = "sc-lab-design-optimality-diagnostics/0.56.0"
MAX_FACTORS = 10
MAX_RUNS = 500
MAX_CANDIDATES = 1500
MAX_BATCH = 50


class AdvancedExperimentalDesignError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _text(value: Any, limit: int = 4000) -> str:
    return " ".join(str(value or "").split())[:limit]


def _finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise AdvancedExperimentalDesignError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise AdvancedExperimentalDesignError(f"{label} must be finite.")
    return out


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "ready",
        "version": VERSION,
        "designSchema": DESIGN_SCHEMA,
        "sequentialSchema": SEQUENTIAL_SCHEMA,
        "diagnosticSchema": DIAGNOSTIC_SCHEMA,
        "capabilities": {
            "dOptimalDesign": True,
            "maximinSpaceFilling": True,
            "blocking": True,
            "centerReplication": True,
            "sequentialInformationGain": True,
            "responseGuidedProposal": True,
            "stoppingEvidence": True,
            "automaticExperimentExecution": False,
            "automaticStopping": False,
            "arbitraryCode": False,
        },
        "limits": {"factors": MAX_FACTORS, "runs": MAX_RUNS, "candidatePool": MAX_CANDIDATES, "sequentialBatch": MAX_BATCH},
    }


def policies() -> dict[str, Any]:
    return {
        "version": VERSION,
        "criteria": ["d-optimal", "maximin"],
        "modelOrders": ["linear", "interaction", "quadratic"],
        "sequentialStrategies": ["information-gain", "response-guided"],
        "objectives": ["explore", "maximize", "minimize", "target"],
        "execution": "proposal-only",
        "automaticExperimentExecution": False,
        "automaticStopping": False,
        "formalOptimalityProof": False,
        "arbitraryCode": False,
    }


def _normalize_factors(payload: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        factors = normalize_factors(payload)
    except DesignStudyError as exc:
        raise AdvancedExperimentalDesignError(str(exc)) from exc
    if len(factors) > MAX_FACTORS:
        raise AdvancedExperimentalDesignError(f"No more than {MAX_FACTORS} factors are supported by v0.56.0 advanced design.")
    return factors


def normalize_spec(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedExperimentalDesignError("Advanced design specification must be an object.")
    source = payload.get("spec") if isinstance(payload.get("spec"), dict) else payload
    factors = _normalize_factors(source)
    criterion = _text(source.get("criterion"), 40).lower() or "d-optimal"
    if criterion not in {"d-optimal", "maximin"}:
        raise AdvancedExperimentalDesignError("criterion must be d-optimal or maximin.")
    model_order = _text(source.get("modelOrder"), 40).lower() or "quadratic"
    if model_order not in {"linear", "interaction", "quadratic"}:
        raise AdvancedExperimentalDesignError("modelOrder must be linear, interaction, or quadratic.")
    run_budget = int(source.get("runBudget") or max(8, 2 * len(factors) + 1))
    run_budget = max(2, min(MAX_RUNS, run_budget))
    candidate_size = int(source.get("candidatePoolSize") or max(120, run_budget * 12))
    candidate_size = max(run_budget, min(MAX_CANDIDATES, candidate_size))
    block_count = max(1, min(20, int(source.get("blockCount") or 1)))
    center_replicates = max(0, min(20, int(source.get("centerReplicates") or 0)))
    seed = int(source.get("seed") or 42)
    spec = {
        "schema": DESIGN_SCHEMA,
        "version": VERSION,
        "recordType": "advanced-experimental-design-spec",
        "id": _text(source.get("id"), 180) or f"advanced-design-{_hash(source)[:16]}",
        "title": _text(source.get("title"), 500) or "Advanced experimental design",
        "criterion": criterion,
        "modelOrder": model_order,
        "runBudget": run_budget,
        "candidatePoolSize": candidate_size,
        "blockCount": block_count,
        "centerReplicates": center_replicates,
        "randomizeRunOrder": bool(source.get("randomizeRunOrder", True)),
        "seed": seed,
        "responseName": _text(source.get("responseName"), 200) or "response",
        "responseUnit": _text(source.get("responseUnit"), 80),
        "objective": _text(source.get("objective"), 40).lower() or "explore",
        "targetValue": source.get("targetValue"),
        "factors": factors,
        "protocolId": _text(source.get("protocolId"), 180),
        "evidenceNote": _text(source.get("evidenceNote"), 8000),
        "createdAt": source.get("createdAt") or _now(),
    }
    if spec["objective"] not in {"explore", "maximize", "minimize", "target"}:
        raise AdvancedExperimentalDesignError("Unsupported objective.")
    if spec["objective"] == "target":
        spec["targetValue"] = _finite(spec.get("targetValue"), "targetValue")
    else:
        spec["targetValue"] = None
    spec["specHash"] = _hash({k: v for k, v in spec.items() if k not in {"specHash", "createdAt"}})
    return spec


def _scale_factor(factor: dict[str, Any], coded: float) -> Any:
    coded = max(-1.0, min(1.0, float(coded)))
    if factor["type"] == "categorical":
        levels = factor["levels"]
        idx = int(round((coded + 1.0) * (len(levels) - 1) / 2.0))
        return levels[max(0, min(len(levels) - 1, idx))]
    low, high = float(factor["low"]), float(factor["high"])
    value = low + (coded + 1.0) * (high - low) / 2.0
    return int(round(value)) if factor["type"] == "integer" else float(value)


def _candidate_pool(factors: list[dict[str, Any]], size: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    k = len(factors)
    columns: list[list[float]] = []
    for factor in factors:
        if factor["type"] == "categorical":
            levels = factor["levels"]
            vals = [-1.0 + 2.0 * (i % len(levels)) / max(1, len(levels) - 1) for i in range(size)]
            rng.shuffle(vals)
            columns.append(vals)
        else:
            bins = list(range(size))
            rng.shuffle(bins)
            columns.append([-1.0 + 2.0 * ((b + rng.random()) / size) for b in bins])
    candidates = []
    for i in range(size):
        coded = [float(columns[j][i]) for j in range(k)]
        candidates.append({
            "candidate": i + 1,
            "codedVector": coded,
            "coded": {factors[j]["name"]: coded[j] for j in range(k)},
            "values": {factors[j]["name"]: _scale_factor(factors[j], coded[j]) for j in range(k)},
        })
    # Ensure a center candidate for continuous spaces and deterministic extreme anchors.
    center = [0.0] * k
    candidates.append({"candidate": len(candidates) + 1, "codedVector": center, "coded": {factors[j]["name"]: 0.0 for j in range(k)}, "values": {factors[j]["name"]: _scale_factor(factors[j], 0.0) for j in range(k)}})
    return candidates[: MAX_CANDIDATES]


def _term_names(names: list[str], order: str) -> list[str]:
    terms = ["intercept"] + list(names)
    if order in {"interaction", "quadratic"}:
        terms += [f"{names[i]}:{names[j]}" for i, j in combinations(range(len(names)), 2)]
    if order == "quadratic":
        terms += [f"{name}^2" for name in names]
    return terms


def _features(vector: list[float], order: str) -> np.ndarray:
    values = [1.0] + [float(x) for x in vector]
    if order in {"interaction", "quadratic"}:
        values += [float(vector[i]) * float(vector[j]) for i, j in combinations(range(len(vector)), 2)]
    if order == "quadratic":
        values += [float(x) ** 2 for x in vector]
    return np.asarray(values, dtype=float)


def _logdet(info: np.ndarray) -> float:
    sign, value = np.linalg.slogdet(info)
    return float(value) if sign > 0 and math.isfinite(float(value)) else -1e300


def _min_distance(vector: np.ndarray, chosen: list[np.ndarray]) -> float:
    if not chosen:
        return float(np.linalg.norm(vector))
    return min(float(np.linalg.norm(vector - other)) for other in chosen)


def _select_d_optimal(candidates: list[dict[str, Any]], budget: int, order: str) -> list[int]:
    features = [_features(row["codedVector"], order) for row in candidates]
    p = len(features[0])
    chosen: list[int] = []
    info = np.eye(p, dtype=float) * 1e-9
    chosen_vectors: list[np.ndarray] = []
    remaining = set(range(len(candidates)))
    while remaining and len(chosen) < budget:
        best_idx = None
        best_score = -1e300
        for idx in remaining:
            x = features[idx]
            score = _logdet(info + np.outer(x, x))
            # Tiny distance tie-breaker improves spread when determinants tie early.
            score += 1e-9 * _min_distance(np.asarray(candidates[idx]["codedVector"]), chosen_vectors)
            if score > best_score:
                best_idx, best_score = idx, score
        if best_idx is None:
            break
        chosen.append(best_idx)
        x = features[best_idx]
        info = info + np.outer(x, x)
        chosen_vectors.append(np.asarray(candidates[best_idx]["codedVector"], dtype=float))
        remaining.remove(best_idx)
    return chosen


def _select_maximin(candidates: list[dict[str, Any]], budget: int) -> list[int]:
    if not candidates:
        return []
    arrays = [np.asarray(row["codedVector"], dtype=float) for row in candidates]
    start = max(range(len(arrays)), key=lambda i: float(np.linalg.norm(arrays[i])))
    chosen = [start]
    remaining = set(range(len(arrays))) - {start}
    while remaining and len(chosen) < budget:
        idx = max(remaining, key=lambda i: min(float(np.linalg.norm(arrays[i] - arrays[j])) for j in chosen))
        chosen.append(idx)
        remaining.remove(idx)
    return chosen


def design_diagnostics(rows: list[dict[str, Any]], model_order: str) -> dict[str, Any]:
    if not rows:
        raise AdvancedExperimentalDesignError("At least one design row is required for diagnostics.")
    vectors = [list(map(float, row.get("codedVector") or list((row.get("coded") or {}).values()))) for row in rows]
    X = np.vstack([_features(v, model_order) for v in vectors])
    info = X.T @ X
    rank = int(np.linalg.matrix_rank(X))
    p = int(X.shape[1])
    condition = float(np.linalg.cond(info)) if info.size else float("inf")
    pinv = np.linalg.pinv(info)
    leverages = np.einsum("ij,jk,ik->i", X, pinv, X)
    distances = []
    for i, j in combinations(range(len(vectors)), 2):
        distances.append(float(np.linalg.norm(np.asarray(vectors[i]) - np.asarray(vectors[j]))))
    logdet = _logdet(info + np.eye(p) * 1e-12)
    d_eff = math.exp(logdet / max(1, p)) / max(1, len(rows)) if logdet > -1e200 else 0.0
    return {
        "schema": DIAGNOSTIC_SCHEMA,
        "version": VERSION,
        "modelOrder": model_order,
        "runCount": len(rows),
        "modelTermCount": p,
        "rank": rank,
        "fullRank": rank == p,
        "conditionNumber": condition if math.isfinite(condition) else None,
        "logDetInformation": logdet if logdet > -1e200 else None,
        "dEfficiencyIndex": float(d_eff),
        "meanLeverage": float(np.mean(leverages)),
        "maxLeverage": float(np.max(leverages)),
        "minPairwiseDistance": min(distances) if distances else None,
        "warnings": ([] if rank == p else ["The selected design is rank deficient for the requested model order."]) + (["The information matrix is poorly conditioned; coefficient estimates may be unstable."] if math.isfinite(condition) and condition > 1e10 else []),
    }


def generate_optimal_design(payload: dict[str, Any]) -> dict[str, Any]:
    spec = normalize_spec(payload)
    factors = spec["factors"]
    pool = _candidate_pool(factors, spec["candidatePoolSize"], spec["seed"])
    center_reps = min(spec["centerReplicates"], max(0, spec["runBudget"] - 2))
    selection_budget = max(2, spec["runBudget"] - center_reps)
    if spec["criterion"] == "d-optimal":
        selected = _select_d_optimal(pool, selection_budget, spec["modelOrder"])
    else:
        selected = _select_maximin(pool, selection_budget)
    rows = []
    for idx in selected:
        row = dict(pool[idx])
        rows.append(row)
    if center_reps:
        center = min(pool, key=lambda r: sum(abs(float(x)) for x in r["codedVector"]))
        for _ in range(center_reps):
            rows.append(dict(center))
    rng = random.Random(spec["seed"] + 1)
    if spec["randomizeRunOrder"]:
        rng.shuffle(rows)
    for i, row in enumerate(rows):
        row["run"] = i + 1
        row["designPointId"] = f"design-point-{_hash([spec['specHash'], row['codedVector'], i])[:16]}"
        row["block"] = (i % spec["blockCount"]) + 1
        row["response"] = None
        row.pop("candidate", None)
    diagnostics = design_diagnostics(rows, spec["modelOrder"])
    result = {
        "schema": DESIGN_SCHEMA,
        "version": VERSION,
        "recordType": "advanced-experimental-design",
        "id": f"advanced-design-{_hash([spec['specHash'], [r['codedVector'] for r in rows]])[:16]}",
        "title": spec["title"],
        "criterion": spec["criterion"],
        "modelOrder": spec["modelOrder"],
        "factorNames": [f["name"] for f in factors],
        "factors": factors,
        "runCount": len(rows),
        "candidatePoolSize": len(pool),
        "blockCount": spec["blockCount"],
        "centerReplicates": center_reps,
        "randomized": spec["randomizeRunOrder"],
        "seed": spec["seed"],
        "responseName": spec["responseName"],
        "responseUnit": spec["responseUnit"],
        "objective": spec["objective"],
        "targetValue": spec["targetValue"],
        "protocolId": spec["protocolId"],
        "evidenceNote": spec["evidenceNote"],
        "rows": rows,
        "diagnostics": diagnostics,
        "execution": "proposal-only",
        "createdAt": _now(),
    }
    result["designHash"] = _hash({k: v for k, v in result.items() if k not in {"designHash", "createdAt"}})
    return {"ok": True, "version": VERSION, "spec": spec, "design": result}


def _normalize_existing(rows: Any, factor_names: list[str]) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise AdvancedExperimentalDesignError("existingRows must be an array.")
    if len(rows) > MAX_RUNS:
        raise AdvancedExperimentalDesignError(f"existingRows exceeds the {MAX_RUNS}-run limit.")
    out = []
    for i, raw in enumerate(rows):
        if not isinstance(raw, dict):
            raise AdvancedExperimentalDesignError(f"existingRows[{i}] must be an object.")
        coded = raw.get("coded") if isinstance(raw.get("coded"), dict) else {}
        vector = raw.get("codedVector") if isinstance(raw.get("codedVector"), list) else [coded.get(n) for n in factor_names]
        if len(vector) != len(factor_names) or any(v is None for v in vector):
            raise AdvancedExperimentalDesignError("Every existing row must include coded coordinates for each factor.")
        vector = [_finite(v, "coded factor") for v in vector]
        response = raw.get("response")
        if response is not None and response != "":
            response = _finite(response, "response")
        else:
            response = None
        out.append({**raw, "codedVector": vector, "coded": {factor_names[j]: vector[j] for j in range(len(factor_names))}, "response": response})
    return out


def _fit_response_model(rows: list[dict[str, Any]], order: str) -> dict[str, Any] | None:
    completed = [r for r in rows if r.get("response") is not None]
    if not completed:
        return None
    X = np.vstack([_features(r["codedVector"], order) for r in completed])
    y = np.asarray([float(r["response"]) for r in completed], dtype=float)
    p = X.shape[1]
    if len(completed) < max(3, min(p, 6)):
        return None
    coef, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    residual = y - pred
    dof = max(1, len(y) - int(rank))
    variance = float(np.sum(residual**2) / dof)
    return {"coef": coef, "variance": variance, "infoInv": np.linalg.pinv(X.T @ X), "rank": int(rank), "n": len(y), "y": y}


def _response_score(model: dict[str, Any], x: np.ndarray, objective: str, target: float | None, exploration_weight: float) -> tuple[float, float, float]:
    mean = float(x @ model["coef"])
    var = max(0.0, float(model["variance"] * (1.0 + x @ model["infoInv"] @ x)))
    se = math.sqrt(var)
    if objective == "maximize":
        exploitation = mean
    elif objective == "minimize":
        exploitation = -mean
    elif objective == "target" and target is not None:
        exploitation = -abs(mean - target)
    else:
        exploitation = 0.0
    return exploitation + exploration_weight * se, mean, se


def sequential_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AdvancedExperimentalDesignError("Sequential experiment request must be an object.")
    spec = normalize_spec(payload.get("spec") if isinstance(payload.get("spec"), dict) else payload)
    factor_names = [f["name"] for f in spec["factors"]]
    existing = _normalize_existing(payload.get("existingRows") or [], factor_names)
    if not existing:
        raise AdvancedExperimentalDesignError("Sequential planning requires at least one existing design row.")
    strategy = _text(payload.get("strategy"), 50).lower() or "information-gain"
    if strategy not in {"information-gain", "response-guided"}:
        raise AdvancedExperimentalDesignError("strategy must be information-gain or response-guided.")
    batch_size = max(1, min(MAX_BATCH, int(payload.get("batchSize") or 3)))
    max_total = max(len(existing), min(MAX_RUNS, int(payload.get("maxTotalRuns") or spec["runBudget"])))
    batch_size = min(batch_size, max(0, max_total - len(existing)))
    min_gain = max(0.0, _finite(payload.get("minRelativeInformationGain", 0.0), "minRelativeInformationGain"))
    exploration_weight = max(0.0, _finite(payload.get("explorationWeight", 1.0), "explorationWeight"))
    source_note = _text(payload.get("evidenceNote") or spec.get("evidenceNote"), 8000)
    if batch_size <= 0:
        plan = {
            "schema": SEQUENTIAL_SCHEMA, "version": VERSION, "recordType": "sequential-experiment-plan",
            "id": f"sequential-plan-{_hash([spec['specHash'], [r['codedVector'] for r in existing], 'budget-reached'])[:16]}",
            "title": f"{spec['title']} — sequential augmentation", "strategy": strategy, "objective": spec["objective"],
            "targetValue": spec["targetValue"], "modelOrder": spec["modelOrder"], "existingRunCount": len(existing),
            "completedResponseCount": sum(1 for r in existing if r.get("response") is not None), "proposedRunCount": 0,
            "maxTotalRuns": max_total, "candidatePoolSize": 0, "relativeInformationGain": 0.0,
            "minRelativeInformationGain": float(min_gain), "recommendation": "stop",
            "stopReasons": ["The declared maximum total run budget has been reached."], "proposedRows": [],
            "evidenceNote": source_note, "execution": "proposal-only", "automaticExecutionAuthorized": False,
            "automaticStoppingAuthorized": False, "warnings": [], "createdAt": _now(),
        }
        plan["planHash"] = _hash({k: v for k, v in plan.items() if k not in {"planHash", "createdAt"}})
        return {"ok": True, "version": VERSION, "spec": spec, "plan": plan}

    pool = _candidate_pool(spec["factors"], spec["candidatePoolSize"], spec["seed"] + len(existing) + 17)
    existing_vectors = [np.asarray(r["codedVector"], dtype=float) for r in existing]
    def duplicate(candidate: dict[str, Any]) -> bool:
        v = np.asarray(candidate["codedVector"], dtype=float)
        return any(float(np.linalg.norm(v - e)) < 1e-8 for e in existing_vectors)
    candidates = [c for c in pool if not duplicate(c)]
    if not candidates:
        raise AdvancedExperimentalDesignError("No unused candidate points remain within the bounded candidate pool.")

    X_existing = np.vstack([_features(r["codedVector"], spec["modelOrder"]) for r in existing])
    info = X_existing.T @ X_existing + np.eye(X_existing.shape[1]) * 1e-9
    base_logdet = _logdet(info)
    response_model = _fit_response_model(existing, spec["modelOrder"]) if strategy == "response-guided" else None
    if strategy == "response-guided" and response_model is None:
        raise AdvancedExperimentalDesignError("Response-guided sequential planning requires more completed responses for the requested model order.")

    proposed: list[dict[str, Any]] = []
    remaining = set(range(len(candidates)))
    for step in range(batch_size):
        best_idx = None
        best_score = -1e300
        best_meta: dict[str, Any] = {}
        current_logdet = _logdet(info)
        for idx in remaining:
            x = _features(candidates[idx]["codedVector"], spec["modelOrder"])
            new_logdet = _logdet(info + np.outer(x, x))
            gain = max(0.0, new_logdet - current_logdet)
            if strategy == "response-guided" and response_model is not None:
                rs, pred, se = _response_score(response_model, x, spec["objective"], spec["targetValue"], exploration_weight)
                score = rs + 0.05 * gain
                meta = {"predictedResponse": pred, "predictionStdError": se, "informationGain": gain, "acquisitionScore": score}
            else:
                score = gain
                meta = {"informationGain": gain, "acquisitionScore": score}
            if score > best_score:
                best_idx, best_score, best_meta = idx, score, meta
        if best_idx is None:
            break
        c = dict(candidates[best_idx])
        x = _features(c["codedVector"], spec["modelOrder"])
        info = info + np.outer(x, x)
        c.update(best_meta)
        c["proposedRun"] = len(existing) + step + 1
        c["block"] = ((len(existing) + step) % spec["blockCount"]) + 1
        c["response"] = None
        c["proposalId"] = f"sequential-proposal-{_hash([spec['specHash'], c['codedVector'], c['proposedRun']])[:16]}"
        c.pop("candidate", None)
        proposed.append(c)
        remaining.remove(best_idx)

    final_logdet = _logdet(info)
    relative_gain = 0.0
    if math.isfinite(base_logdet) and math.isfinite(final_logdet):
        relative_gain = max(0.0, math.exp((final_logdet - base_logdet) / max(1, info.shape[0])) - 1.0)
    stop_reasons = []
    recommendation = "continue"
    if len(existing) + len(proposed) >= max_total:
        stop_reasons.append("The proposed batch reaches the declared maximum total run budget.")
    if proposed and relative_gain < min_gain:
        stop_reasons.append("The proposed batch falls below the declared minimum relative information-gain threshold.")
    if not proposed:
        stop_reasons.append("No additional bounded candidate points were selected.")
    if stop_reasons:
        recommendation = "review" if proposed else "stop"
    plan = {
        "schema": SEQUENTIAL_SCHEMA,
        "version": VERSION,
        "recordType": "sequential-experiment-plan",
        "id": f"sequential-plan-{_hash([spec['specHash'], [r['codedVector'] for r in existing], [r['codedVector'] for r in proposed]])[:16]}",
        "title": f"{spec['title']} — sequential augmentation",
        "strategy": strategy,
        "objective": spec["objective"],
        "targetValue": spec["targetValue"],
        "modelOrder": spec["modelOrder"],
        "existingRunCount": len(existing),
        "completedResponseCount": sum(1 for r in existing if r.get("response") is not None),
        "proposedRunCount": len(proposed),
        "maxTotalRuns": max_total,
        "candidatePoolSize": len(candidates),
        "relativeInformationGain": float(relative_gain),
        "minRelativeInformationGain": float(min_gain),
        "recommendation": recommendation,
        "stopReasons": stop_reasons,
        "proposedRows": proposed,
        "evidenceNote": source_note,
        "execution": "proposal-only",
        "automaticExecutionAuthorized": False,
        "automaticStoppingAuthorized": False,
        "warnings": ["Response-guided acquisition is a local model-based heuristic and does not guarantee a global optimum."] if strategy == "response-guided" else [],
        "createdAt": _now(),
    }
    plan["planHash"] = _hash({k: v for k, v in plan.items() if k not in {"planHash", "createdAt"}})
    return {"ok": True, "version": VERSION, "spec": spec, "plan": plan}


def verify_record(payload: dict[str, Any]) -> dict[str, Any]:
    record = payload.get("record") if isinstance(payload.get("record"), dict) else payload
    if not isinstance(record, dict):
        raise AdvancedExperimentalDesignError("A design or sequential-plan record is required.")
    key = "designHash" if record.get("designHash") else "planHash" if record.get("planHash") else None
    if not key:
        raise AdvancedExperimentalDesignError("Record requires designHash or planHash.")
    actual = _hash({k: v for k, v in record.items() if k not in {key, "createdAt"}})
    return {"ok": actual == record[key], "version": VERSION, "expectedHash": record[key], "actualHash": actual, "verifiedAt": _now()}
