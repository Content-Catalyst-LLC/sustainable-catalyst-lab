from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any

from .methods.core import MethodInputError
from .precision import diagnostics, prepare, reference_compare
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
    if isinstance(value, float): return math.isfinite(value)
    if isinstance(value, dict): return all(finite_tree(v) for v in value.values())
    if isinstance(value, list): return all(finite_tree(v) for v in value)
    return True


def run_compute(payload: ComputeRequest, auth: dict[str, str]) -> ComputeResponse:
    try:
        method = resolve(payload.method)
    except KeyError as exc:
        raise ComputeExecutionError(404, str(exc), False, "method_not_found") from exc
    if payload.version and payload.version != method.version:
        raise ComputeExecutionError(409, f"Requested {payload.method} version {payload.version}; available version is {method.version}.", False, "method_version_conflict")

    try:
        effective_parameters, governance, warnings = prepare(payload, method)
    except MethodInputError as exc:
        raise ComputeExecutionError(422, str(exc), False, "solver_governance_error") from exc

    start = time.perf_counter()
    try:
        outputs = method.handler(payload.inputs, effective_parameters, payload.random_seed)
    except MethodInputError as exc:
        raise ComputeExecutionError(422, str(exc), False, "method_input_error") from exc
    except Exception as exc:
        raise ComputeExecutionError(500, str(exc), True, "method_runtime_error") from exc

    diagnostic_report, diagnostic_warnings = diagnostics(method.id, outputs, governance)
    warnings.extend(diagnostic_warnings)
    comparison = None
    if governance.get("referenceComparisonRequested"):
        try:
            comparison = reference_compare(method.id, payload.inputs, effective_parameters, outputs)
        except Exception as exc:
            warnings.append(f"Reference comparison could not be completed: {exc}")
    governance["diagnostics"] = diagnostic_report
    governance["referenceComparison"] = comparison
    governance["effectiveParameters"] = {
        key: effective_parameters[key] for key in ("absoluteTolerance", "relativeTolerance", "solver", "conditionThreshold", "illConditionedPolicy") if key in effective_parameters
    }

    duration = (time.perf_counter() - start) * 1000
    provenance = build_provenance(
        method=method.id,
        method_version=method.version,
        inputs={"inputs": payload.inputs, "units": payload.units, "parameters": effective_parameters, "governance": payload.governance.model_dump(by_alias=True), "projectId": payload.project_id},
        result=outputs,
        duration_ms=duration,
        packages=method.packages,
        random_seed=payload.random_seed,
        auth=auth,
        solver_governance=governance,
    )
    return ComputeResponse(
        method=method.id,
        method_version=method.version,
        outputs=outputs,
        summary=f"{method.title} completed under the {governance['precisionProfile']} precision profile.",
        warnings=list(dict.fromkeys(warnings)),
        validation={"registeredMethod": True, "finiteOutputs": finite_tree(outputs), "solverGovernance": True, "unitStatus": governance["units"]["status"], "convergence": diagnostic_report["convergence"]},
        provenance=provenance,
        governance=governance,
    )
