from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import copy
import json
import math
import random
from typing import Any, Iterable

import numpy as np
from scipy.special import ndtr

VERSION = "0.33.1"
KERNELS = {"rbf", "matern32", "matern52"}
ACQUISITIONS = {"expected-improvement", "probability-improvement", "confidence-bound", "max-variance"}


class BayesianOptimizationError(ValueError):
    pass


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _finite(value: Any, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if not math.isfinite(number):
        number = default
    return max(low, min(high, number))


def _integer(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def normalize_strategy(raw: dict[str, Any], parameter_count: int) -> dict[str, Any]:
    strategy_type = str(raw.get("type") or "bayesian-optimization").strip()
    acquisition_default = "max-variance" if strategy_type == "active-learning" else "expected-improvement"
    acquisition = str(raw.get("acquisition") or acquisition_default).strip()
    if acquisition not in ACQUISITIONS:
        raise BayesianOptimizationError(f"Unsupported acquisition policy: {acquisition}")
    kernel = str(raw.get("kernel") or "matern52").strip()
    if kernel not in KERNELS:
        raise BayesianOptimizationError(f"Unsupported surrogate kernel: {kernel}")
    return {
        "type": strategy_type,
        "initialRandomTrials": _integer(raw.get("initialRandomTrials"), max(4, min(12, parameter_count * 2)), 2, 1000),
        "randomSeed": _integer(raw.get("randomSeed"), 3310, 0, 2147483647),
        "candidatePoolSize": _integer(raw.get("candidatePoolSize"), 512, 32, 10000),
        "kernel": kernel,
        "lengthScale": _finite(raw.get("lengthScale"), 0.35, 0.01, 10.0),
        "observationNoise": _finite(raw.get("observationNoise"), 1e-6, 1e-12, 1.0),
        "acquisition": acquisition,
        "explorationWeight": _finite(raw.get("explorationWeight"), 2.0, 0.0, 100.0),
        "improvementThreshold": _finite(raw.get("improvementThreshold"), 0.01, 0.0, 1e12),
        "localCandidateFraction": _finite(raw.get("localCandidateFraction"), 0.35, 0.0, 0.9),
        "localScale": _finite(raw.get("localScale"), 0.18, 0.001, 1.0),
        "costExponent": _finite(raw.get("costExponent"), 1.0, 0.0, 10.0),
    }


def normalize_resource_model(raw: Any, parameter_space: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    weights = source.get("parameterWeights") if isinstance(source.get("parameterWeights"), dict) else {}
    categorical = source.get("categoricalCosts") if isinstance(source.get("categoricalCosts"), dict) else {}
    clean_weights: dict[str, float] = {}
    clean_categorical: dict[str, dict[str, float]] = {}
    for name, value in weights.items():
        if name in parameter_space:
            clean_weights[name] = _finite(value, 0.0, 0.0, 1e12)
    for name, mapping in categorical.items():
        if name not in parameter_space or parameter_space[name]["type"] != "categorical" or not isinstance(mapping, dict):
            continue
        clean_categorical[name] = {str(key): _finite(value, 0.0, 0.0, 1e12) for key, value in mapping.items()}
    result = {
        "enabled": source.get("enabled", False) is True or bool(clean_weights) or bool(clean_categorical),
        "baseCost": _finite(source.get("baseCost"), 1.0, 1e-9, 1e12),
        "parameterWeights": clean_weights,
        "categoricalCosts": clean_categorical,
        "resultCostPath": str(source.get("resultCostPath") or "").strip()[:500],
        "maxEstimatedCostPerTrial": _finite(source.get("maxEstimatedCostPerTrial"), 1e12, 1e-9, 1e15),
        "maxTotalCost": _finite(source.get("maxTotalCost"), 1e15, 1e-9, 1e18),
    }
    return result


def feature_names(parameter_space: dict[str, dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for name, spec in parameter_space.items():
        if spec["type"] == "categorical":
            names.extend(f"{name}={value}" for value in spec["values"])
        else:
            names.append(name)
    return names


def encode_parameters(parameter_space: dict[str, dict[str, Any]], parameters: dict[str, Any]) -> np.ndarray:
    encoded: list[float] = []
    for name, spec in parameter_space.items():
        value = parameters[name]
        if spec["type"] == "categorical":
            encoded.extend(1.0 if value == category else 0.0 for category in spec["values"])
        else:
            minimum = float(spec["min"])
            maximum = float(spec["max"])
            encoded.append((float(value) - minimum) / max(1e-15, maximum - minimum))
    return np.asarray(encoded, dtype=float)


def estimate_cost(resource_model: dict[str, Any], parameter_space: dict[str, dict[str, Any]], parameters: dict[str, Any]) -> float:
    cost = float(resource_model.get("baseCost", 1.0))
    for name, weight in resource_model.get("parameterWeights", {}).items():
        spec = parameter_space[name]
        value = parameters[name]
        if spec["type"] == "categorical":
            continue
        normalized = (float(value) - float(spec["min"])) / max(1e-15, float(spec["max"]) - float(spec["min"]))
        cost += float(weight) * max(0.0, normalized)
    for name, mapping in resource_model.get("categoricalCosts", {}).items():
        cost += float(mapping.get(str(parameters[name]), 0.0))
    return max(1e-9, float(cost))


def _random_point(parameter_space: dict[str, dict[str, Any]], rng: random.Random) -> dict[str, Any]:
    point: dict[str, Any] = {}
    for name, spec in parameter_space.items():
        if spec["type"] == "categorical":
            point[name] = copy.deepcopy(rng.choice(spec["values"]))
        elif spec["type"] == "integer":
            values = list(range(int(spec["min"]), int(spec["max"]) + 1, int(spec.get("step", 1))))
            point[name] = int(rng.choice(values))
        else:
            point[name] = round(rng.uniform(float(spec["min"]), float(spec["max"])), int(spec.get("precision", 8)))
    return point


def _local_point(parameter_space: dict[str, dict[str, Any]], center: dict[str, Any], scale: float, rng: random.Random) -> dict[str, Any]:
    point: dict[str, Any] = {}
    for name, spec in parameter_space.items():
        current = center.get(name)
        if spec["type"] == "categorical":
            point[name] = copy.deepcopy(current if current in spec["values"] and rng.random() > scale else rng.choice(spec["values"]))
        elif spec["type"] == "integer":
            span = max(1.0, (float(spec["max"]) - float(spec["min"])) * scale)
            raw = int(round(float(current) + rng.gauss(0.0, span))) if current is not None else int(rng.randint(int(spec["min"]), int(spec["max"])))
            step = int(spec.get("step", 1))
            raw = int(spec["min"]) + round((raw - int(spec["min"])) / step) * step
            point[name] = max(int(spec["min"]), min(int(spec["max"]), raw))
        else:
            span = (float(spec["max"]) - float(spec["min"])) * scale
            raw = float(current) + rng.gauss(0.0, span) if current is not None else rng.uniform(float(spec["min"]), float(spec["max"]))
            point[name] = round(max(float(spec["min"]), min(float(spec["max"]), raw)), int(spec.get("precision", 8)))
    return point


def candidate_pool(parameter_space: dict[str, dict[str, Any]], size: int, seed: int, best: dict[str, Any] | None, local_fraction: float, local_scale: float, excluded_hashes: set[str]) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    points: list[dict[str, Any]] = []
    seen = set(excluded_hashes)
    attempts = max(size * 20, 1000)
    local_count = int(size * local_fraction) if best else 0
    for index in range(attempts):
        use_local = best is not None and len(points) < local_count
        point = _local_point(parameter_space, best, local_scale, rng) if use_local else _random_point(parameter_space, rng)
        digest = stable_hash(point)
        if digest in seen:
            continue
        seen.add(digest)
        points.append(point)
        if len(points) >= size:
            break
    return points


def _kernel(xa: np.ndarray, xb: np.ndarray, kind: str, length_scale: float) -> np.ndarray:
    distances = np.linalg.norm((xa[:, None, :] - xb[None, :, :]) / length_scale, axis=2)
    if kind == "rbf":
        return np.exp(-0.5 * distances * distances)
    if kind == "matern32":
        scaled = math.sqrt(3.0) * distances
        return (1.0 + scaled) * np.exp(-scaled)
    scaled = math.sqrt(5.0) * distances
    return (1.0 + scaled + (scaled * scaled) / 3.0) * np.exp(-scaled)


@dataclass
class GaussianProcess:
    x: np.ndarray
    y_mean: float
    y_scale: float
    alpha: np.ndarray
    chol: np.ndarray
    kernel: str
    length_scale: float
    noise: float
    condition_number: float

    def predict(self, candidates: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        cross = _kernel(self.x, candidates, self.kernel, self.length_scale)
        mean_standard = cross.T @ self.alpha
        v = np.linalg.solve(self.chol, cross)
        variance = np.maximum(1e-12, 1.0 - np.sum(v * v, axis=0))
        return self.y_mean + self.y_scale * mean_standard, self.y_scale * np.sqrt(variance)


def fit_gaussian_process(x: np.ndarray, y: np.ndarray, kernel: str, length_scale: float, noise: float) -> GaussianProcess:
    if x.ndim != 2 or y.ndim != 1 or len(x) != len(y) or len(y) < 2:
        raise BayesianOptimizationError("At least two completed observations are required to fit the surrogate.")
    y_mean = float(np.mean(y))
    y_scale = float(np.std(y))
    if y_scale < 1e-12:
        y_scale = 1.0
    normalized = (y - y_mean) / y_scale
    covariance = _kernel(x, x, kernel, length_scale)
    jitter = max(noise, 1e-12)
    chol = None
    for _ in range(8):
        try:
            chol = np.linalg.cholesky(covariance + np.eye(len(x)) * jitter)
            break
        except np.linalg.LinAlgError:
            jitter *= 10.0
    if chol is None:
        raise BayesianOptimizationError("The surrogate covariance matrix could not be stabilized.")
    alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, normalized))
    condition = float(np.linalg.cond(covariance + np.eye(len(x)) * jitter))
    return GaussianProcess(x=x, y_mean=y_mean, y_scale=y_scale, alpha=alpha, chol=chol, kernel=kernel, length_scale=length_scale, noise=jitter, condition_number=condition)


def acquisition_values(mean: np.ndarray, std: np.ndarray, best: float, goal: str, policy: str, exploration_weight: float, threshold: float) -> np.ndarray:
    std_safe = np.maximum(std, 1e-12)
    direction = -1.0 if goal == "minimize" else 1.0
    improvement = direction * (mean - best) - threshold
    z = improvement / std_safe
    if policy == "expected-improvement":
        density = np.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
        return improvement * ndtr(z) + std_safe * density
    if policy == "probability-improvement":
        return ndtr(z)
    if policy == "confidence-bound":
        return direction * mean + exploration_weight * std_safe
    return std_safe


def propose(
    parameter_space: dict[str, dict[str, Any]],
    observations: Iterable[dict[str, Any]],
    strategy: dict[str, Any],
    resource_model: dict[str, Any],
    goal: str,
    seed: int,
    excluded_hashes: set[str],
    best_parameters: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    rows = [row for row in observations if row.get("objective") is not None]
    if len(rows) < max(2, int(strategy["initialRandomTrials"])):
        pool = candidate_pool(parameter_space, max(64, int(strategy["candidatePoolSize"])), seed, best_parameters, 0.0, float(strategy["localScale"]), excluded_hashes)
        if not pool:
            raise BayesianOptimizationError("The parameter space is exhausted or no unique proposal could be generated.")
        eligible_points = [
            point for point in pool
            if estimate_cost(resource_model, parameter_space, point) <= float(resource_model["maxEstimatedCostPerTrial"])
        ]
        if not eligible_points:
            raise BayesianOptimizationError("No initial-design candidate satisfies the per-trial resource limit.")
        parameters = eligible_points[0]
        cost = estimate_cost(resource_model, parameter_space, parameters)
        return parameters, {
            "source": "initial-random",
            "prediction": None,
            "acquisition": None,
            "estimatedCost": cost,
            "candidatePoolSize": len(pool),
            "modelHash": None,
        }, {"trained": False, "observationCount": len(rows), "reason": "initial-design"}

    x = np.vstack([encode_parameters(parameter_space, row["parameters"]) for row in rows])
    y = np.asarray([float(row["objective"]) for row in rows], dtype=float)
    model = fit_gaussian_process(x, y, strategy["kernel"], float(strategy["lengthScale"]), float(strategy["observationNoise"]))
    pool = candidate_pool(parameter_space, int(strategy["candidatePoolSize"]), seed, best_parameters, float(strategy["localCandidateFraction"]), float(strategy["localScale"]), excluded_hashes)
    if not pool:
        raise BayesianOptimizationError("The parameter space is exhausted or no unique proposal could be generated.")
    candidate_matrix = np.vstack([encode_parameters(parameter_space, point) for point in pool])
    mean, std = model.predict(candidate_matrix)
    best = float(np.min(y) if goal == "minimize" else np.max(y))
    raw_acquisition = acquisition_values(mean, std, best, goal, strategy["acquisition"], float(strategy["explorationWeight"]), float(strategy["improvementThreshold"]))
    costs = np.asarray([estimate_cost(resource_model, parameter_space, point) for point in pool], dtype=float)
    eligible = costs <= float(resource_model["maxEstimatedCostPerTrial"])
    if not np.any(eligible):
        raise BayesianOptimizationError("No proposed candidate satisfies the per-trial resource limit.")
    exponent = float(strategy.get("costExponent", 0.0)) if resource_model.get("enabled") else 0.0
    adjusted = raw_acquisition / np.power(np.maximum(costs, 1e-12), exponent)
    adjusted = np.where(eligible, adjusted, -np.inf)
    index = int(np.argmax(adjusted))
    parameters = pool[index]
    diagnostics = {
        "trained": True,
        "observationCount": len(rows),
        "featureCount": int(x.shape[1]),
        "features": feature_names(parameter_space),
        "kernel": model.kernel,
        "lengthScale": model.length_scale,
        "noise": model.noise,
        "conditionNumber": model.condition_number,
        "objectiveMean": model.y_mean,
        "objectiveScale": model.y_scale,
        "modelHash": stable_hash({"x": x.tolist(), "y": y.tolist(), "strategy": strategy}),
    }
    proposal = {
        "source": "surrogate-acquisition",
        "prediction": {"mean": float(mean[index]), "standardDeviation": float(std[index])},
        "acquisition": {"policy": strategy["acquisition"], "rawValue": float(raw_acquisition[index]), "costAdjustedValue": float(adjusted[index])},
        "estimatedCost": float(costs[index]),
        "candidatePoolSize": len(pool),
        "modelHash": diagnostics["modelHash"],
    }
    return parameters, proposal, diagnostics
