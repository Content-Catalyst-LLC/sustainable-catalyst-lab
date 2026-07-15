from __future__ import annotations

import math
import time
from typing import Any, Callable

import numpy as np

from .compute import finite_tree
from .methods.core import MethodInputError
from .provenance import build_provenance
from .registry import resolve
from .schemas import ComputeRequest, ComputeResponse

CheckpointEmitter = Callable[[float, str, dict[str, Any], dict[str, Any] | None], None]

CHECKPOINTABLE_METHODS = {
    "simulation.parameter_sweep",
    "uncertainty.bootstrap_mean_interval",
}


def is_checkpointable(method_id: str) -> bool:
    try:
        return resolve(method_id).id in CHECKPOINTABLE_METHODS
    except KeyError:
        return False


def _response(payload: ComputeRequest, auth: dict[str, str], outputs: dict[str, Any], started: float) -> ComputeResponse:
    method = resolve(payload.method)
    duration = (time.perf_counter() - started) * 1000
    provenance = build_provenance(
        method=method.id,
        method_version=method.version,
        inputs={
            "inputs": payload.inputs,
            "units": payload.units,
            "parameters": payload.parameters,
            "projectId": payload.project_id,
        },
        result=outputs,
        duration_ms=duration,
        packages=method.packages,
        random_seed=payload.random_seed,
        auth=auth,
    )
    return ComputeResponse(
        method=method.id,
        method_version=method.version,
        outputs=outputs,
        summary=f"{method.title} completed with resumable checkpoints and {len(outputs)} output fields.",
        validation={
            "registeredMethod": True,
            "finiteOutputs": finite_tree(outputs),
            "checkpointedExecution": True,
        },
        provenance=provenance,
    )


def _parameter_sweep_value(model: str, parameter_name: str, value: float, fixed: dict[str, Any]) -> float:
    local = {str(key): float(item) for key, item in fixed.items() if isinstance(item, (int, float))}
    local[parameter_name] = float(value)
    if model == "logistic_growth":
        initial = float(local.get("initial", 10.0))
        rate = float(local.get("rate", 0.5))
        capacity = float(local.get("carryingCapacity", 100.0))
        duration = float(local.get("time", 10.0))
        if initial <= 0 or capacity <= 0:
            raise MethodInputError("logistic_growth requires positive initial and carryingCapacity.")
        return capacity / (1 + ((capacity - initial) / initial) * math.exp(-rate * duration))
    if model == "projectile_range":
        speed = float(local.get("speed", 20.0))
        angle = math.radians(float(local.get("angleDeg", 45.0)))
        gravity = float(local.get("gravity", 9.80665))
        if speed < 0 or gravity <= 0:
            raise MethodInputError("projectile_range requires non-negative speed and positive gravity.")
        return speed * speed * math.sin(2 * angle) / gravity
    if model == "photovoltaic_output":
        return (
            float(local.get("irradiance", 1000))
            * float(local.get("area", 10))
            * float(local.get("efficiency", 0.2))
            * float(local.get("systemFactor", 0.85))
        )
    if model == "michaelis_menten":
        vmax = float(local.get("vmax", 10))
        substrate = float(local.get("substrate", 5))
        km = float(local.get("km", 2))
        if substrate < 0 or vmax < 0 or km <= 0:
            raise MethodInputError("michaelis_menten requires non-negative vmax/substrate and positive km.")
        return vmax * substrate / (km + substrate)
    raise MethodInputError("model must be logistic_growth, projectile_range, photovoltaic_output, or michaelis_menten.")


def _run_parameter_sweep(
    payload: ComputeRequest,
    checkpoint: dict[str, Any],
    emit: CheckpointEmitter,
) -> dict[str, Any]:
    inputs = payload.inputs
    model = str(inputs.get("model") or "logistic_growth").lower()
    parameter_name = str(inputs.get("parameter") or "rate")[:64]
    raw_values = inputs.get("values")
    fixed = inputs.get("fixed") or {}
    if not isinstance(raw_values, list) or not 1 <= len(raw_values) <= 10000:
        raise MethodInputError("values must contain between 1 and 10,000 numeric values.")
    if not isinstance(fixed, dict):
        raise MethodInputError("fixed must be an object.")
    values = [float(value) for value in raw_values]
    if not all(math.isfinite(value) for value in values):
        raise MethodInputError("values must be finite numbers.")

    rows = list(checkpoint.get("rows") or [])
    next_index = max(0, min(len(values), int(checkpoint.get("nextIndex") or len(rows))))
    chunk_size = max(1, min(250, int(payload.parameters.get("checkpointChunkSize", 50))))
    checkpoint_delay = max(0.0, min(0.1, float(payload.parameters.get("checkpointDelayMs", 0)) / 1000.0))

    for start in range(next_index, len(values), chunk_size):
        end = min(len(values), start + chunk_size)
        for index in range(start, end):
            result = _parameter_sweep_value(model, parameter_name, values[index], fixed)
            if not math.isfinite(result):
                raise MethodInputError("The parameter sweep produced a non-finite result.")
            rows.append({"parameterValue": values[index], "output": float(result)})
        progress = 5 + (90 * end / len(values))
        partial_outputs = {
            "completedRows": end,
            "totalRows": len(values),
            "latestRows": rows[max(0, len(rows) - 25):],
        }
        emit(
            progress,
            f"Completed {end} of {len(values)} parameter values",
            {"nextIndex": end, "rows": rows, "model": model, "parameter": parameter_name},
            partial_outputs,
        )
        if checkpoint_delay:
            time.sleep(checkpoint_delay)

    outputs = np.asarray([row["output"] for row in rows], dtype=float)
    return {
        "model": model,
        "parameter": parameter_name,
        "rows": rows,
        "minimumOutput": float(outputs.min()),
        "maximumOutput": float(outputs.max()),
        "monotonicIncreasing": bool(np.all(np.diff(outputs) >= 0)),
        "monotonicDecreasing": bool(np.all(np.diff(outputs) <= 0)),
        "checkpointed": True,
        "resumedFromRow": next_index,
    }


def _run_bootstrap(
    payload: ComputeRequest,
    checkpoint: dict[str, Any],
    emit: CheckpointEmitter,
) -> dict[str, Any]:
    inputs = payload.inputs
    raw_values = inputs.get("values")
    if not isinstance(raw_values, list) or not 2 <= len(raw_values) <= 100000:
        raise MethodInputError("values must contain between 2 and 100,000 numeric observations.")
    values = np.asarray([float(value) for value in raw_values], dtype=float)
    if not np.isfinite(values).all():
        raise MethodInputError("values must be finite numbers.")
    resamples = int(inputs.get("resamples") or 0)
    if not 100 <= resamples <= 50000:
        raise MethodInputError("resamples must be between 100 and 50,000.")
    confidence = float(payload.parameters.get("confidence", 0.95))
    if not 0.5 < confidence < 1:
        raise MethodInputError("confidence must be between 0.5 and 1.")

    seed = 0 if payload.random_seed is None else int(payload.random_seed)
    means = [float(value) for value in (checkpoint.get("means") or [])]
    completed = max(0, min(resamples, int(checkpoint.get("completed") or len(means))))
    means = means[:completed]
    chunk_size = max(10, min(1000, int(payload.parameters.get("checkpointChunkSize", 250))))
    checkpoint_delay = max(0.0, min(0.1, float(payload.parameters.get("checkpointDelayMs", 0)) / 1000.0))

    for start in range(completed, resamples, chunk_size):
        count = min(chunk_size, resamples - start)
        # Each chunk has a stable independent seed, so restart order cannot change the final result.
        rng = np.random.default_rng(np.random.SeedSequence([seed, start]))
        indexes = rng.integers(0, values.size, size=(count, values.size))
        chunk_means = np.mean(values[indexes], axis=1)
        means.extend(float(item) for item in chunk_means)
        done = start + count
        progress = 5 + (90 * done / resamples)
        partial_outputs = {
            "completedResamples": done,
            "totalResamples": resamples,
            "runningBootstrapMean": float(np.mean(means)),
            "runningStandardError": float(np.std(means, ddof=1)) if len(means) > 1 else 0.0,
        }
        emit(
            progress,
            f"Completed {done} of {resamples} bootstrap resamples",
            {"completed": done, "means": means, "seed": seed},
            partial_outputs,
        )
        if checkpoint_delay:
            time.sleep(checkpoint_delay)

    bootstrap = np.asarray(means, dtype=float)
    tail = (1 - confidence) / 2
    lower, upper = np.quantile(bootstrap, [tail, 1 - tail])
    return {
        "sampleMean": float(np.mean(values)),
        "sampleStandardDeviation": float(np.std(values, ddof=1)),
        "bootstrapMean": float(np.mean(bootstrap)),
        "bootstrapStandardError": float(np.std(bootstrap, ddof=1)),
        "confidence": confidence,
        "confidenceInterval": [float(lower), float(upper)],
        "resamples": resamples,
        "seed": seed,
        "checkpointed": True,
        "resumedFromResample": completed,
    }


def run_checkpointed(
    payload: ComputeRequest,
    auth: dict[str, str],
    checkpoint: dict[str, Any] | None,
    emit: CheckpointEmitter,
) -> ComputeResponse:
    method = resolve(payload.method)
    if method.id not in CHECKPOINTABLE_METHODS:
        raise KeyError(method.id)
    started = time.perf_counter()
    state = checkpoint if isinstance(checkpoint, dict) else {}
    if method.id == "simulation.parameter_sweep":
        outputs = _run_parameter_sweep(payload, state, emit)
    elif method.id == "uncertainty.bootstrap_mean_interval":
        outputs = _run_bootstrap(payload, state, emit)
    else:  # pragma: no cover - guarded by set above
        raise KeyError(method.id)
    emit(99, "Finalizing reproducibility provenance", state, None)
    return _response(payload, auth, outputs, started)
