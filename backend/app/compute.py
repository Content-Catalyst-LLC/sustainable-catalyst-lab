from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any

from .methods.core import MethodInputError
from .provenance import build_provenance
from .registry import resolve
from .schemas import ComputeRequest, ComputeResponse


@dataclass
class ComputeExecutionError(Exception):
    status_code: int
    detail: str
    retryable: bool = False
    code: str = "compute_execution_error"

    def __str__(self) -> str:
        return self.detail


def finite_tree(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_tree(v) for v in value.values())
    if isinstance(value, list):
        return all(finite_tree(v) for v in value)
    return True


def run_compute(payload: ComputeRequest, auth: dict[str, str]) -> ComputeResponse:
    try:
        method = resolve(payload.method)
    except KeyError as exc:
        raise ComputeExecutionError(404, str(exc), False, "method_not_found") from exc

    if payload.version and payload.version != method.version:
        raise ComputeExecutionError(
            409,
            f"Requested {payload.method} version {payload.version}; available version is {method.version}.",
            False,
            "method_version_conflict",
        )

    start = time.perf_counter()
    try:
        outputs = method.handler(payload.inputs, payload.parameters, payload.random_seed)
    except MethodInputError as exc:
        raise ComputeExecutionError(422, str(exc), False, "method_input_error") from exc
    except Exception as exc:
        raise ComputeExecutionError(500, str(exc), True, "method_runtime_error") from exc

    duration = (time.perf_counter() - start) * 1000
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
        summary=f"{method.title} completed with {len(outputs)} output fields.",
        validation={"registeredMethod": True, "finiteOutputs": finite_tree(outputs)},
        provenance=provenance,
    )
