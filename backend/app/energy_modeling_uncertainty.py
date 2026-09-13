from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np
from scipy import stats
from fastapi import APIRouter, HTTPException

# Reuse the Lab's certified probabilistic sampling implementation rather than
# introducing a second stochastic engine for Energy Systems.
from .probabilistic_analysis import _transform, _unit_design

LAB_VERSION = "0.102.0"
ENERGY_SYSTEMS_VERSION = "1.4.0"
WORKBENCH_VERSION = "6.2.0"
FRAMEWORK_SCHEMA = "sc-energy-modeling-uncertainty-framework/1.0"
PLAN_SCHEMA = "sc-energy-modeling-uncertainty-plan/1.0"
ANALYSIS_SCHEMA = "sc-energy-modeling-uncertainty-analysis/1.0"
VALIDATION_SCHEMA = "sc-energy-modeling-uncertainty-validation/1.0"
WORKBENCH_HANDOFF_SCHEMA = "sc-energy-runtime-handoff/1.0"
WORKBENCH_CONTRACT = "sc-energy-runtime-workbench-handoff/1.0"
WORKBENCH_RESULT_SCHEMA = "sc-energy-workbench-result-packet/1.0"
DESIGNS = {"monte-carlo", "latin-hypercube"}
DISTRIBUTIONS = {"uniform", "normal", "lognormal", "triangular"}
EXECUTABLE_SECTIONS = {"numeric_registry", "energy_balance", "economics", "bioenergy_and_carbon"}
SUPPORTED_OPERATIONS = {
    "unit-conversion", "conversion-chain", "supply-demand-balance", "capacity-factor-generation",
    "energy-cost-comparison", "simple-payback", "net-present-value", "cost-benefit", "cost-efficiency",
    "levelized-energy-cost", "feedstock-energy", "anaerobic-digestion-energy", "biochar-carbon",
    "biomass-to-oil-energy",
}
MAX_VARIABLES = 24
MAX_SAMPLES = 4096
MIN_SAMPLES = 8
BOUNDARY = (
    "Lab designs and analyzes uncertainty around explicit Energy Systems calculations. It does not reimplement "
    "Workbench formulas, infer missing distributions or parameters, execute Workbench automatically, rank "
    "technologies, recommend a winner, fetch market data, persist studies automatically, or create carbon-credit claims."
)

router = APIRouter(prefix="/v1/energy-modeling", tags=["energy-modeling-uncertainty"])

class EnergyModelingError(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any, prefix: str, size: int = 20) -> str:
    return prefix + sha256(_canonical(value).encode("utf-8")).hexdigest()[:size]


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise EnergyModelingError(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise EnergyModelingError(f"{label} must be finite")
    return number


def _positive_int(value: Any, label: str, low: int, high: int) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise EnergyModelingError(f"{label} must be an integer") from exc
    if result < low or result > high:
        raise EnergyModelingError(f"{label} must be between {low} and {high}")
    return result


def _normalize_distribution(raw: dict[str, Any], baseline_inputs: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise EnergyModelingError("uncertainty.variables must contain objects")
    name = str(raw.get("name") or "").strip()
    if not name:
        raise EnergyModelingError("uncertainty variable name is required")
    if name not in baseline_inputs:
        raise EnergyModelingError(f"uncertainty variable {name} is not present in calculation_request.inputs")
    distribution = str(raw.get("distribution") or "").strip().lower()
    if not distribution:
        raise EnergyModelingError(f"{name}.distribution is required; no implicit distribution is allowed")
    if distribution not in DISTRIBUTIONS:
        raise EnergyModelingError(f"unsupported distribution for {name}: {distribution}")
    record: dict[str, Any] = {
        "symbol": name,
        "label": str(raw.get("label") or name),
        "unit": str(raw.get("unit") or ""),
        "distribution": distribution,
    }
    if distribution == "uniform":
        low, high = _finite(raw.get("low"), f"{name}.low"), _finite(raw.get("high"), f"{name}.high")
        if high <= low:
            raise EnergyModelingError(f"{name}.high must exceed low")
        record.update(low=low, high=high)
    elif distribution == "normal":
        mean = _finite(raw.get("mean"), f"{name}.mean")
        std = _finite(raw.get("stdDev"), f"{name}.stdDev")
        if std <= 0:
            raise EnergyModelingError(f"{name}.stdDev must be positive")
        record.update(mean=mean, stdDev=std)
    elif distribution == "lognormal":
        mean_log = _finite(raw.get("meanLog"), f"{name}.meanLog")
        std_log = _finite(raw.get("stdLog"), f"{name}.stdLog")
        if std_log <= 0:
            raise EnergyModelingError(f"{name}.stdLog must be positive")
        record.update(meanLog=mean_log, stdLog=std_log)
    else:
        low = _finite(raw.get("low"), f"{name}.low")
        mode = _finite(raw.get("mode"), f"{name}.mode")
        high = _finite(raw.get("high"), f"{name}.high")
        if high <= low or not low <= mode <= high:
            raise EnergyModelingError(f"{name} triangular bounds must satisfy low <= mode <= high with high > low")
        record.update(low=low, mode=mode, high=high)
    return record


def _normalize_plan_request(body: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise EnergyModelingError("Energy modeling plan must be a JSON object")
    study_id = str(body.get("study_id") or "").strip()
    if not study_id:
        raise EnergyModelingError("study_id is required")
    calculation = body.get("calculation_request")
    if not isinstance(calculation, dict):
        raise EnergyModelingError("calculation_request is required")
    section = str(calculation.get("section") or "").strip()
    operation = str(calculation.get("operation") or "").strip()
    inputs = calculation.get("inputs")
    if section not in EXECUTABLE_SECTIONS:
        raise EnergyModelingError("calculation_request.section must be a Workbench executable section")
    if operation not in SUPPORTED_OPERATIONS:
        raise EnergyModelingError(f"unsupported Workbench operation: {operation}")
    if not isinstance(inputs, dict) or not inputs:
        raise EnergyModelingError("calculation_request.inputs must be a non-empty object")
    uncertainty = body.get("uncertainty")
    if not isinstance(uncertainty, dict):
        raise EnergyModelingError("uncertainty is required")
    variables_raw = uncertainty.get("variables")
    if not isinstance(variables_raw, list) or not variables_raw:
        raise EnergyModelingError("uncertainty.variables requires at least one variable")
    if len(variables_raw) > MAX_VARIABLES:
        raise EnergyModelingError(f"at most {MAX_VARIABLES} uncertain variables are supported")
    variables = [_normalize_distribution(v, inputs) for v in variables_raw]
    names = [v["symbol"] for v in variables]
    if len(set(names)) != len(names):
        raise EnergyModelingError("uncertainty variable names must be unique")
    design = uncertainty.get("design")
    if not isinstance(design, dict):
        raise EnergyModelingError("uncertainty.design is required")
    method = str(design.get("method") or "").strip().lower()
    if method not in DESIGNS:
        raise EnergyModelingError("uncertainty.design.method must be monte-carlo or latin-hypercube")
    samples = _positive_int(design.get("samples"), "uncertainty.design.samples", MIN_SAMPLES, MAX_SAMPLES)
    if "seed" not in design:
        raise EnergyModelingError("uncertainty.design.seed is required for reproducibility")
    try:
        seed = int(design["seed"])
    except (TypeError, ValueError) as exc:
        raise EnergyModelingError("uncertainty.design.seed must be an integer") from exc
    output = body.get("output")
    if not isinstance(output, dict):
        raise EnergyModelingError("output is required")
    result_path = str(output.get("result_path") or "").strip()
    if not result_path:
        raise EnergyModelingError("output.result_path is required")
    confidence = _finite(output.get("confidence", 0.95), "output.confidence")
    if not 0.5 <= confidence <= 0.999:
        raise EnergyModelingError("output.confidence must be between 0.5 and 0.999")
    thresholds = [_finite(v, "output.thresholds") for v in (output.get("thresholds") or [])]
    if len(thresholds) > 20:
        raise EnergyModelingError("at most 20 output thresholds are supported")
    return {
        "study_id": study_id,
        "question": str(body.get("question") or ""),
        "calculation_request": {
            "section": section,
            "operation": operation,
            "inputs": deepcopy(inputs),
            "source_refs": list(calculation.get("source_refs") or []),
            "assumptions": list(calculation.get("assumptions") or []),
        },
        "uncertainty": {"variables": variables, "design": {"method": method, "samples": samples, "seed": seed}},
        "output": {"result_path": result_path, "unit": str(output.get("unit") or ""), "confidence": confidence, "thresholds": thresholds},
        "provenance": list(body.get("provenance") or []),
        "review": body.get("review") if isinstance(body.get("review"), dict) else {"human_review_required": True},
    }


def framework() -> dict[str, Any]:
    return {
        "ok": True,
        "schema": FRAMEWORK_SCHEMA,
        "version": ENERGY_SYSTEMS_VERSION,
        "lab_version": LAB_VERSION,
        "workbench_runtime": {"required_version": WORKBENCH_VERSION, "execute_route": "/v1/energy-runtime/execute", "automatic_calling": False},
        "designs": sorted(DESIGNS),
        "distributions": sorted(DISTRIBUTIONS),
        "limits": {"minimum_samples": MIN_SAMPLES, "maximum_samples": MAX_SAMPLES, "maximum_uncertain_variables": MAX_VARIABLES},
        "capabilities": {
            "deterministic_seeded_sampling": True,
            "monte_carlo_design": True,
            "latin_hypercube_design": True,
            "workbench_compatible_evaluation_packet": True,
            "empirical_distribution_summary": True,
            "central_uncertainty_interval": True,
            "threshold_probability_analysis": True,
            "pearson_sensitivity": True,
            "spearman_sensitivity": True,
            "standardized_regression_sensitivity": True,
            "provenance_preservation": True,
            "automatic_workbench_execution": False,
            "automatic_persistence": False,
            "technology_ranking": False,
            "automatic_recommendation": False,
        },
        "boundary": BOUNDARY,
    }


def plan(body: dict[str, Any]) -> dict[str, Any]:
    study = _normalize_plan_request(body)
    variables = study["uncertainty"]["variables"]
    design = study["uncertainty"]["design"]
    unit = _unit_design(design["method"], design["samples"], len(variables), design["seed"])
    matrix = np.column_stack([_transform(unit[:, i], spec) for i, spec in enumerate(variables)])
    base = study["calculation_request"]
    requests: list[dict[str, Any]] = []
    evaluation_map: list[dict[str, Any]] = []
    for i, row in enumerate(matrix):
        inputs = deepcopy(base["inputs"])
        sampled = {}
        for j, spec in enumerate(variables):
            value = float(row[j])
            inputs[spec["symbol"]] = value
            sampled[spec["symbol"]] = value
        request_basis = {"study_id": study["study_id"], "index": i, "sampled_inputs": sampled, "operation": base["operation"]}
        request_id = _digest(request_basis, "emu-eval-")
        requests.append({
            "request_id": request_id,
            "operation": base["operation"],
            "inputs": inputs,
            "source_refs": base["source_refs"],
            "assumptions": base["assumptions"],
        })
        evaluation_map.append({"evaluation_index": i, "request_id": request_id, "sampled_inputs": sampled})
    payload = {
        "identity": {"study_id": study["study_id"], "question": study["question"]},
        "numeric_registry": {"calculation_requests": []},
        "energy_balance": {"calculation_requests": []},
        "economics": {"calculation_requests": []},
        "bioenergy_and_carbon": {"calculation_requests": []},
        "provenance": study["provenance"],
        "review": study["review"],
    }
    payload[base["section"]]["calculation_requests"] = requests
    packet_basis = {"study": study, "evaluation_map": evaluation_map}
    plan_id = _digest(packet_basis, "emu-plan-")
    workbench_handoff = {
        "schema": WORKBENCH_HANDOFF_SCHEMA,
        "version": ENERGY_SYSTEMS_VERSION,
        "packet": {
            "handoff_id": f"{plan_id}-workbench",
            "source": {"product": "Lab", "subsystem": "Energy Modeling & Uncertainty", "version": ENERGY_SYSTEMS_VERSION},
            "target": {"key": "workbench", "product": "Workbench", "consumer_contract": WORKBENCH_CONTRACT},
            "contract_refs": ["energy-workbench-runtime/1.0", "energy-modeling-uncertainty/1.0"],
            "payload": payload,
        },
    }
    return {
        "ok": True,
        "schema": PLAN_SCHEMA,
        "version": ENERGY_SYSTEMS_VERSION,
        "lab_version": LAB_VERSION,
        "plan_id": plan_id,
        "study": study,
        "evaluation_count": len(evaluation_map),
        "evaluation_map": evaluation_map,
        "workbench": {"required_version": WORKBENCH_VERSION, "execute_route": "/v1/energy-runtime/execute", "handoff": workbench_handoff, "execution_performed": False},
        "persistence": {"performed": False, "mode": "ephemeral"},
        "boundary": BOUNDARY,
    }


def _extract_path(output: dict[str, Any], path: str) -> float:
    parts = [p for p in path.split(".") if p]
    if parts and parts[0] == "output":
        parts = parts[1:]
    current: Any = output
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise EnergyModelingError(f"result_path not found in Workbench output: {path}")
        current = current[part]
    return _finite(current, f"Workbench result {path}")


def _sensitivity(x: np.ndarray, y: np.ndarray, variables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    y_std = float(np.std(y, ddof=1)) if len(y) > 1 else 0.0
    x_std = np.std(x, axis=0, ddof=1) if len(y) > 1 else np.zeros(x.shape[1])
    if len(y) > x.shape[1] + 1 and y_std > 0 and np.all(x_std > 0):
        xz = (x - np.mean(x, axis=0)) / x_std
        yz = (y - np.mean(y)) / y_std
        coefficients, *_ = np.linalg.lstsq(xz, yz, rcond=None)
    else:
        coefficients = np.zeros(x.shape[1])
    rows = []
    for i, spec in enumerate(variables):
        if x_std[i] > 0 and y_std > 0 and len(y) >= 3:
            pearson = float(stats.pearsonr(x[:, i], y).statistic)
            spearman = float(stats.spearmanr(x[:, i], y).statistic)
        else:
            pearson = spearman = 0.0
        coefficient = float(coefficients[i])
        rows.append({
            "variable": spec["symbol"], "label": spec["label"], "unit": spec["unit"],
            "pearson": pearson, "spearman": spearman,
            "standardized_regression_coefficient": coefficient,
            "influence_magnitude": abs(coefficient),
        })
    rows.sort(key=lambda r: (-r["influence_magnitude"], r["variable"]))
    return rows


def analyze(body: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise EnergyModelingError("analysis request must be an object")
    plan_obj = body.get("plan")
    if not isinstance(plan_obj, dict) or plan_obj.get("schema") != PLAN_SCHEMA:
        raise EnergyModelingError(f"plan must be a {PLAN_SCHEMA} object")
    wb = body.get("workbench_result")
    if not isinstance(wb, dict) or wb.get("schema") != WORKBENCH_RESULT_SCHEMA:
        raise EnergyModelingError(f"workbench_result must be a {WORKBENCH_RESULT_SCHEMA} object")
    if str(wb.get("workbench_version")) != WORKBENCH_VERSION:
        raise EnergyModelingError(f"workbench_result.workbench_version must be {WORKBENCH_VERSION}")
    result_by_id = {str(r.get("request_id")): r for r in wb.get("results", []) if isinstance(r, dict)}
    evaluation_map = plan_obj.get("evaluation_map") or []
    if len(result_by_id) != len(evaluation_map):
        raise EnergyModelingError("Workbench result count does not match the uncertainty evaluation plan")
    result_path = plan_obj["study"]["output"]["result_path"]
    variables = plan_obj["study"]["uncertainty"]["variables"]
    x_rows, y_values = [], []
    evaluation_results = []
    for row in evaluation_map:
        request_id = row["request_id"]
        result = result_by_id.get(request_id)
        if not result:
            raise EnergyModelingError(f"missing Workbench result for {request_id}")
        if result.get("operation") != plan_obj["study"]["calculation_request"]["operation"]:
            raise EnergyModelingError(f"Workbench operation mismatch for {request_id}")
        value = _extract_path(result.get("output") or {}, result_path)
        sampled = row["sampled_inputs"]
        x_rows.append([_finite(sampled[v["symbol"]], v["symbol"]) for v in variables])
        y_values.append(value)
        evaluation_results.append({"request_id": request_id, "output_value": value, "sampled_inputs": sampled})
    x = np.asarray(x_rows, dtype=float)
    y = np.asarray(y_values, dtype=float)
    confidence = plan_obj["study"]["output"]["confidence"]
    alpha = (1.0 - confidence) / 2.0
    summary = {
        "count": int(y.size),
        "mean": float(np.mean(y)),
        "standard_deviation": float(np.std(y, ddof=1)) if y.size > 1 else 0.0,
        "variance": float(np.var(y, ddof=1)) if y.size > 1 else 0.0,
        "minimum": float(np.min(y)),
        "q05": float(np.quantile(y, 0.05)),
        "q25": float(np.quantile(y, 0.25)),
        "median": float(np.quantile(y, 0.50)),
        "q75": float(np.quantile(y, 0.75)),
        "q95": float(np.quantile(y, 0.95)),
        "maximum": float(np.max(y)),
        "central_interval": {"confidence": confidence, "lower": float(np.quantile(y, alpha)), "upper": float(np.quantile(y, 1.0-alpha))},
        "unit": plan_obj["study"]["output"]["unit"],
    }
    thresholds = []
    for threshold in plan_obj["study"]["output"]["thresholds"]:
        thresholds.append({
            "threshold": threshold,
            "probability_at_or_below": float(np.mean(y <= threshold)),
            "probability_at_or_above": float(np.mean(y >= threshold)),
        })
    sensitivity = _sensitivity(x, y, variables)
    analysis_basis = {"plan_id": plan_obj["plan_id"], "result_packet_id": wb.get("result_packet_id"), "summary": summary, "sensitivity": sensitivity, "thresholds": thresholds}
    analysis_id = _digest(analysis_basis, "emu-analysis-")
    return {
        "ok": True,
        "schema": ANALYSIS_SCHEMA,
        "version": ENERGY_SYSTEMS_VERSION,
        "lab_version": LAB_VERSION,
        "analysis_id": analysis_id,
        "plan_id": plan_obj["plan_id"],
        "study_id": plan_obj["study"]["study_id"],
        "workbench_result_packet_id": wb.get("result_packet_id"),
        "summary": summary,
        "threshold_probabilities": thresholds,
        "sensitivity": {"method": "pearson-spearman-standardized-regression", "variables": sensitivity, "ranking_semantics": "input influence only; not technology ranking"},
        "evaluation_results": evaluation_results,
        "provenance": {"study": plan_obj["study"]["provenance"], "workbench": wb.get("provenance") or []},
        "execution": {"performed": True, "mode": "uncertainty-analysis-of-explicit-workbench-results", "workbench_execution_performed_by_lab": False},
        "persistence": {"performed": False, "mode": "ephemeral"},
        "ranking": {"technology_ranking_performed": False},
        "recommendation": {"performed": False},
        "boundary": BOUNDARY,
    }


def validate_result(body: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(body, dict):
        errors.append("result must be an object")
        body = {}
    if body.get("schema") != ANALYSIS_SCHEMA:
        errors.append(f"schema must be {ANALYSIS_SCHEMA}")
    if str(body.get("version")) != ENERGY_SYSTEMS_VERSION:
        errors.append(f"version must be {ENERGY_SYSTEMS_VERSION}")
    if str(body.get("lab_version")) != LAB_VERSION:
        errors.append(f"lab_version must be {LAB_VERSION}")
    if not str(body.get("analysis_id") or "").startswith("emu-analysis-"):
        errors.append("analysis_id is invalid")
    summary = body.get("summary")
    if not isinstance(summary, dict) or int(summary.get("count") or 0) < MIN_SAMPLES:
        errors.append(f"summary.count must be at least {MIN_SAMPLES}")
    sensitivity = body.get("sensitivity")
    if not isinstance(sensitivity, dict) or not isinstance(sensitivity.get("variables"), list):
        errors.append("sensitivity.variables must be an array")
    if (body.get("persistence") or {}).get("performed") is not False:
        errors.append("automatic persistence must remain false")
    if (body.get("recommendation") or {}).get("performed") is not False:
        errors.append("automatic recommendation must remain false")
    return {"ok": not errors, "schema": VALIDATION_SCHEMA, "valid": not errors, "errors": errors, "boundary": "Structural validation does not establish scientific validity or decision suitability."}


@router.get("/framework")
def energy_modeling_framework() -> dict[str, Any]:
    return framework()


@router.post("/plan")
def energy_modeling_plan(body: dict[str, Any]) -> dict[str, Any]:
    try:
        return plan(body)
    except EnergyModelingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/analyze")
def energy_modeling_analyze(body: dict[str, Any]) -> dict[str, Any]:
    try:
        return analyze(body)
    except EnergyModelingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/validate-result")
def energy_modeling_validate(body: dict[str, Any]) -> dict[str, Any]:
    return validate_result(body)
