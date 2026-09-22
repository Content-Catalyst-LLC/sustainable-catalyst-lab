from __future__ import annotations

import copy
import itertools
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np

from .equation_builder import EquationBuilderError, compile_equation, evaluate
from .model_studio import ModelStudioError, normalize_model
from .probabilistic_analysis import ProbabilisticAnalysisError, analyze as probabilistic_analyze, normalize_study as probabilistic_normalize
from .platform_core_v3_object_mapping_v01050 import build_core_object_binding

VERSION = "0.123.0"
ENGINE_VERSION = "4.3.0"
SCHEMA = "sc-lab-simulation-monte-carlo-research-studio/0.123.0"
SNAPSHOT_SCHEMA = "sc-lab-simulation-monte-carlo-snapshot/0.123.0"
MAX_BASE_SAMPLES = 65_536
MAX_EVALUATIONS = 250_000
MAX_SWEEP_EVALUATIONS = 20_000
MAX_SCENARIOS = 32
MAX_REPLICATIONS = 12
MAX_CHECKPOINTS = 12
MAX_SWEEP_AXES = 6
MAX_AXIS_VALUES = 100

SAMPLING_DESIGNS = {"monte-carlo", "latin-hypercube", "sobol", "saltelli-sobol"}
FIGURE_FAMILIES = {
    "output-distribution", "empirical-cdf", "threshold-probability", "sample-scatter",
    "convergence-trace", "quantile-stability", "seed-replication", "sensitivity-bars",
    "parameter-sweep", "response-surface", "scenario-ensemble", "uncertainty-band",
}


class SimulationStudioError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _dict(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise SimulationStudioError(f"{label} must be an object.")
    return copy.deepcopy(value)


def _list(value: Any, label: str, maximum: int = 1000) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SimulationStudioError(f"{label} must be an array.")
    if len(value) > maximum:
        raise SimulationStudioError(f"{label} exceeds {maximum} entries.", 413)
    return copy.deepcopy(value)


def _text(value: Any, label: str, maximum: int = 500, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise SimulationStudioError(f"{label} is required.")
    if len(text) > maximum:
        raise SimulationStudioError(f"{label} exceeds {maximum} characters.")
    return text


def _finite(value: Any, label: str, default: float | None = None) -> float:
    if value is None and default is not None:
        return default
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise SimulationStudioError(f"{label} must be numeric.") from exc
    if not math.isfinite(number):
        raise SimulationStudioError(f"{label} must be finite.")
    return number


def _int(value: Any, label: str, default: int | None = None, minimum: int | None = None, maximum: int | None = None) -> int:
    if value is None and default is not None:
        result = int(default)
    else:
        try:
            result = int(value)
        except (TypeError, ValueError) as exc:
            raise SimulationStudioError(f"{label} must be an integer.") from exc
    if minimum is not None and result < minimum:
        raise SimulationStudioError(f"{label} must be at least {minimum}.")
    if maximum is not None and result > maximum:
        raise SimulationStudioError(f"{label} must be no more than {maximum}.")
    return result


def schema_info() -> dict[str, Any]:
    return {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "snapshot_schema": SNAPSHOT_SCHEMA,
        "limits": {
            "base_samples": MAX_BASE_SAMPLES,
            "evaluations": MAX_EVALUATIONS,
            "sweep_evaluations": MAX_SWEEP_EVALUATIONS,
            "scenarios": MAX_SCENARIOS,
            "replications": MAX_REPLICATIONS,
            "convergence_checkpoints": MAX_CHECKPOINTS,
            "sweep_axes": MAX_SWEEP_AXES,
        },
    }


def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "sampling_designs": sorted(SAMPLING_DESIGNS),
        "study_families": ["uncertainty-propagation", "parameter-sweep", "scenario-ensemble", "seed-replication", "convergence-study"],
        "figure_families": sorted(FIGURE_FAMILIES),
        "summary_metrics": ["mean", "standard-deviation", "variance", "median", "quantiles", "central-interval", "threshold-probability"],
        "execution_modes": ["direct", "long-running-job-plan"],
        "underlying_engines": ["probabilistic-analysis-v0.48.0", "safe-declarative-model-studio"],
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "simulation-monte-carlo-research-studio-ready",
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "monte_carlo": True,
        "latin_hypercube": True,
        "sobol_sampling": True,
        "saltelli_sobol": True,
        "parameter_sweeps": True,
        "scenario_ensembles": True,
        "convergence_diagnostics": True,
        "seed_replication": True,
        "uncertainty_propagation": True,
        "publication_visualization": True,
        "reproducible_seeded_execution": True,
        "source_models_immutable": True,
        "simulated_outputs_marked_as_modeled": True,
        "automatic_convergence_certification": False,
        "automatic_scenario_selection": False,
        "automatic_evidence_promotion": False,
        "automatic_causal_inference": False,
        "automatic_scientific_validity_certification": False,
        "automatic_core_submission": False,
        "determine_truth": False,
    }


def health() -> dict[str, Any]:
    return {
        **manifest(),
        "schema": SCHEMA,
        "sampling_design_count": len(SAMPLING_DESIGNS),
        "figure_family_count": len(FIGURE_FAMILIES),
    }


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("study") if isinstance(payload.get("study"), dict) else payload
    try:
        study = probabilistic_normalize(copy.deepcopy(raw))
    except ProbabilisticAnalysisError as exc:
        raise SimulationStudioError(str(exc), getattr(exc, "status_code", 400)) from exc
    out = copy.deepcopy(study)
    out["studio_schema"] = SCHEMA
    out["studio_version"] = VERSION
    out["simulation_output_semantics"] = "modeled-not-observed"
    out["automatic_evidence_promotion"] = False
    out["automatic_convergence_certification"] = False
    out["automatic_scenario_selection"] = False
    out["studio_study_hash"] = _hash({k: v for k, v in out.items() if k != "studio_study_hash"})
    return {"ok": True, "version": VERSION, "study": out}


def build_sampling_plan(payload: dict[str, Any]) -> dict[str, Any]:
    study = normalize_study(payload)["study"]
    design = copy.deepcopy(study.get("design") or {})
    plan = {
        "ok": True,
        "schema": f"{SCHEMA}/sampling-plan",
        "version": VERSION,
        "design": design,
        "uncertain_inputs": copy.deepcopy(study.get("uncertainInputs") or []),
        "seed": design.get("seed"),
        "base_samples": design.get("samples"),
        "evaluation_count": design.get("evaluationCount"),
        "independent_inputs": bool((study.get("governance") or {}).get("independentInputs")),
        "reproducible_seeded_execution": True,
        "automatic_execution": False,
        "automatic_distribution_selection": False,
    }
    plan["sampling_plan_hash"] = _hash(plan)
    return plan


def build_compute_budget_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan = build_sampling_plan(payload)
    count = int(plan.get("evaluation_count") or 0)
    mode = "direct" if count <= 10_000 else "long-running-job-plan"
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/compute-budget-plan",
        "version": VERSION,
        "evaluation_count": count,
        "maximum_evaluations": MAX_EVALUATIONS,
        "execution_mode": mode,
        "checkpointable": True,
        "automatic_queue_submission": False,
        "automatic_resource_escalation": False,
    }
    out["compute_budget_hash"] = _hash(out)
    return out


def run_simulation(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("study") if isinstance(payload.get("study"), dict) else payload
    try:
        result = probabilistic_analyze(copy.deepcopy(raw))["result"]
    except ProbabilisticAnalysisError as exc:
        raise SimulationStudioError(str(exc), getattr(exc, "status_code", 400)) from exc
    result = copy.deepcopy(result)
    result["lab_release_version"] = VERSION
    result["studio_schema"] = SCHEMA
    result["simulation_output_semantics"] = "modeled-not-observed"
    result["observational_evidence"] = False
    result["automatic_evidence_promotion"] = False
    result["automatic_convergence_certification"] = False
    result["automatic_scenario_selection"] = False
    result["scientific_validity_certified"] = False
    result["simulation_result_hash"] = _hash({k: v for k, v in result.items() if k != "simulation_result_hash"})
    return {"ok": True, "version": VERSION, "result": result}


def _checkpoints(requested: int, supplied: Any) -> list[int]:
    if supplied is not None:
        values = sorted(set(_int(x, "checkpoint", minimum=16, maximum=requested) for x in _list(supplied, "checkpoints", MAX_CHECKPOINTS)))
        if not values:
            raise SimulationStudioError("At least one convergence checkpoint is required.")
        if values[-1] != requested:
            values.append(requested)
        return values[-MAX_CHECKPOINTS:]
    candidates = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, requested]
    return sorted({x for x in candidates if x <= requested})[-MAX_CHECKPOINTS:]


def convergence_report(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_study(payload)["study"]
    requested = int((normalized.get("design") or {}).get("samples") or 0)
    checkpoints = _checkpoints(requested, payload.get("checkpoints"))
    rows: list[dict[str, Any]] = []
    previous: dict[str, float] | None = None
    for n in checkpoints:
        study = copy.deepcopy(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
        study.setdefault("design", {})["samples"] = n
        result = run_simulation(study)["result"]
        summary = result["summary"]
        row = {
            "samples": n,
            "evaluation_count": int((result.get("study") or {}).get("design", {}).get("evaluationCount") or summary.get("count") or 0),
            "mean": summary.get("mean"),
            "standard_deviation": summary.get("standardDeviation"),
            "p05": (summary.get("quantiles") or {}).get("p05"),
            "p50": (summary.get("quantiles") or {}).get("p50"),
            "p95": (summary.get("quantiles") or {}).get("p95"),
        }
        if previous is not None:
            row["delta_from_previous"] = {
                "mean": row["mean"] - previous["mean"],
                "standard_deviation": row["standard_deviation"] - previous["standard_deviation"],
                "p50": row["p50"] - previous["p50"],
            }
        else:
            row["delta_from_previous"] = None
        previous = {"mean": float(row["mean"]), "standard_deviation": float(row["standard_deviation"]), "p50": float(row["p50"])}
        rows.append(row)
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/convergence-report",
        "version": VERSION,
        "checkpoints": rows,
        "declared_final_sample_count": requested,
        "convergence_certified": False,
        "automatic_convergence_certification": False,
        "interpretation": "Checkpoint stability is descriptive evidence only; the Studio does not certify Monte Carlo convergence.",
    }
    out["convergence_report_hash"] = _hash(out)
    return out


def replication_report(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_study(payload)["study"]
    base_seed = int((normalized.get("design") or {}).get("seed") or 42)
    seeds_raw = payload.get("seeds")
    if seeds_raw is None:
        count = _int(payload.get("replications"), "replications", 4, 2, MAX_REPLICATIONS)
        seeds = [base_seed + i * 104729 for i in range(count)]
    else:
        seeds = [_int(x, "seed") for x in _list(seeds_raw, "seeds", MAX_REPLICATIONS)]
        if len(seeds) < 2:
            raise SimulationStudioError("At least two replication seeds are required.")
    runs = []
    for seed in seeds:
        study = copy.deepcopy(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
        study.setdefault("design", {})["seed"] = seed
        result = run_simulation(study)["result"]
        s = result["summary"]
        runs.append({"seed": seed, "mean": s["mean"], "standard_deviation": s["standardDeviation"], "median": s["median"], "p05": s["quantiles"]["p05"], "p95": s["quantiles"]["p95"]})
    means = np.asarray([r["mean"] for r in runs], dtype=float)
    medians = np.asarray([r["median"] for r in runs], dtype=float)
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/replication-report",
        "version": VERSION,
        "runs": runs,
        "between_seed": {
            "mean_of_means": float(np.mean(means)),
            "sd_of_means": float(np.std(means, ddof=1)) if len(means) > 1 else 0.0,
            "range_of_means": [float(np.min(means)), float(np.max(means))],
            "sd_of_medians": float(np.std(medians, ddof=1)) if len(medians) > 1 else 0.0,
        },
        "replication_stability_certified": False,
        "automatic_convergence_certification": False,
    }
    out["replication_report_hash"] = _hash(out)
    return out


def _normalized_model(payload: dict[str, Any]) -> dict[str, Any]:
    model_payload = payload.get("model") if isinstance(payload.get("model"), dict) else ((payload.get("study") or {}).get("model") if isinstance(payload.get("study"), dict) else {})
    if not model_payload:
        raise SimulationStudioError("model is required for parameter sweeps.")
    try:
        model = normalize_model(copy.deepcopy(model_payload))
    except ModelStudioError as exc:
        raise SimulationStudioError(str(exc)) from exc
    if model.get("family") != "declarative-expression" or model.get("definition", {}).get("safeExecution") is not True:
        raise SimulationStudioError("Parameter sweeps require a safe declarative-expression Model Studio model.")
    return model


def _axis_values(axis: dict[str, Any]) -> tuple[str, list[float]]:
    symbol = _text(axis.get("symbol") or axis.get("name"), "sweep axis symbol", 64, True)
    if isinstance(axis.get("values"), list):
        values = [_finite(v, f"{symbol}.values") for v in _list(axis["values"], f"{symbol}.values", MAX_AXIS_VALUES)]
        if not values:
            raise SimulationStudioError(f"{symbol}.values cannot be empty.")
        return symbol, values
    start = _finite(axis.get("start"), f"{symbol}.start")
    stop = _finite(axis.get("stop"), f"{symbol}.stop")
    points = _int(axis.get("points"), f"{symbol}.points", 11, 2, MAX_AXIS_VALUES)
    return symbol, [float(x) for x in np.linspace(start, stop, points)]


def parameter_sweep_plan(payload: dict[str, Any]) -> dict[str, Any]:
    model = _normalized_model(payload)
    axes_raw = _list(payload.get("axes") or ((payload.get("sweep") or {}).get("axes") if isinstance(payload.get("sweep"), dict) else None), "axes", MAX_SWEEP_AXES)
    if not axes_raw:
        raise SimulationStudioError("At least one sweep axis is required.")
    axes = []
    product = 1
    for raw in axes_raw:
        if not isinstance(raw, dict):
            raise SimulationStudioError("Each sweep axis must be an object.")
        symbol, values = _axis_values(raw)
        axes.append({"symbol": symbol, "values": values, "count": len(values)})
        product *= len(values)
    if product > MAX_SWEEP_EVALUATIONS:
        raise SimulationStudioError(f"Parameter sweep requires {product} evaluations; maximum is {MAX_SWEEP_EVALUATIONS}.", 413)
    declared = {row.get("symbol") for row in model.get("variables", []) + model.get("parameters", []) + model.get("constants", [])}
    unknown = [axis["symbol"] for axis in axes if axis["symbol"] not in declared]
    if unknown:
        raise SimulationStudioError("Unknown sweep symbols: " + ", ".join(unknown))
    plan = {
        "ok": True,
        "schema": f"{SCHEMA}/parameter-sweep-plan",
        "version": VERSION,
        "model_id": model.get("id"),
        "axes": axes,
        "evaluation_count": product,
        "source_model_immutable": True,
        "automatic_execution": False,
        "automatic_optimum_selection": False,
    }
    plan["sweep_plan_hash"] = _hash(plan)
    return plan


def run_parameter_sweep(payload: dict[str, Any]) -> dict[str, Any]:
    model = _normalized_model(payload)
    plan = parameter_sweep_plan(payload)
    axes = plan["axes"]
    values = _dict(payload.get("values") or ((payload.get("study") or {}).get("values") if isinstance(payload.get("study"), dict) else None), "values")
    for row in model.get("parameters", []):
        if row.get("value") is not None:
            values.setdefault(row["symbol"], float(row["value"]))
    for row in model.get("constants", []):
        values.setdefault(row["symbol"], float(row["value"]))
    declared = [row["symbol"] for row in model.get("variables", []) + model.get("parameters", []) + model.get("constants", [])]
    try:
        compiled = compile_equation(model["definition"]["equation"], declared, model["definition"].get("outputSymbol"))
    except EquationBuilderError as exc:
        raise SimulationStudioError(str(exc)) from exc
    axis_symbols = {axis["symbol"] for axis in axes}
    missing = [symbol for symbol in compiled.symbols if symbol not in values and symbol not in axis_symbols]
    if missing:
        raise SimulationStudioError("Missing deterministic values for model symbols: " + ", ".join(sorted(missing)) + ".")
    records = []
    for index, combo in enumerate(itertools.product(*[axis["values"] for axis in axes])):
        env = {k: _finite(v, f"values.{k}") for k, v in values.items()}
        env.update({axes[i]["symbol"]: float(combo[i]) for i in range(len(axes))})
        try:
            y = float(evaluate(compiled, env))
        except EquationBuilderError as exc:
            raise SimulationStudioError(f"Model evaluation failed at sweep index {index}: {exc}") from exc
        records.append({"index": index, "coordinates": {axes[i]["symbol"]: float(combo[i]) for i in range(len(axes))}, "output": y})
    out_values = np.asarray([r["output"] for r in records], dtype=float)
    result = {
        "ok": True,
        "schema": f"{SCHEMA}/parameter-sweep-result",
        "version": VERSION,
        "model_id": model.get("id"),
        "plan": plan,
        "records": records,
        "summary": {"count": len(records), "minimum": float(np.min(out_values)), "maximum": float(np.max(out_values)), "mean": float(np.mean(out_values)), "median": float(np.median(out_values))},
        "simulation_output_semantics": "modeled-not-observed",
        "automatic_optimum_selection": False,
        "automatic_causal_inference": False,
    }
    result["sweep_result_hash"] = _hash(result)
    return result


def run_scenario_ensemble(payload: dict[str, Any]) -> dict[str, Any]:
    base = _dict(payload.get("study"), "study")
    if not base:
        raise SimulationStudioError("study is required for scenario ensembles.")
    scenarios = _list(payload.get("scenarios"), "scenarios", MAX_SCENARIOS)
    if not scenarios:
        raise SimulationStudioError("At least one scenario is required.")
    rows = []
    seen: set[str] = set()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise SimulationStudioError("Each scenario must be an object.")
        scenario_id = _text(scenario.get("id") or f"scenario-{index+1}", "scenario id", 180, True)
        if scenario_id in seen:
            raise SimulationStudioError("Scenario IDs must be unique.")
        seen.add(scenario_id)
        study = copy.deepcopy(base)
        if isinstance(scenario.get("values"), dict):
            study.setdefault("values", {}).update(copy.deepcopy(scenario["values"]))
        if isinstance(scenario.get("design"), dict):
            study.setdefault("design", {}).update(copy.deepcopy(scenario["design"]))
        if isinstance(scenario.get("analysis"), dict):
            study.setdefault("analysis", {}).update(copy.deepcopy(scenario["analysis"]))
        if isinstance(scenario.get("uncertainInputs"), list):
            study["uncertainInputs"] = copy.deepcopy(scenario["uncertainInputs"])
        result = run_simulation(study)["result"]
        rows.append({"scenario_id": scenario_id, "label": _text(scenario.get("label") or scenario_id, "scenario label", 240, True), "summary": copy.deepcopy(result["summary"]), "simulation_result_hash": result["simulation_result_hash"], "assumptions": copy.deepcopy(scenario.get("assumptions") or {})})
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/scenario-ensemble",
        "version": VERSION,
        "scenarios": rows,
        "selected_scenario_id": None,
        "automatic_scenario_selection": False,
        "automatic_scenario_ranking": False,
        "scenario_outputs_are_modeled_not_observed": True,
    }
    out["scenario_ensemble_hash"] = _hash(out)
    return out


def run_uncertainty_propagation(payload: dict[str, Any]) -> dict[str, Any]:
    result = run_simulation(payload)["result"]
    return {
        "ok": True,
        "schema": f"{SCHEMA}/uncertainty-propagation",
        "version": VERSION,
        "study_hash": (result.get("study") or {}).get("studyHash"),
        "simulation_result_hash": result.get("simulation_result_hash"),
        "summary": copy.deepcopy(result.get("summary") or {}),
        "sensitivity": copy.deepcopy(result.get("sensitivity") or {}),
        "graphs": copy.deepcopy(result.get("graphs") or {}),
        "simulation_output_semantics": "modeled-not-observed",
        "automatic_evidence_promotion": False,
    }


def threshold_report(payload: dict[str, Any]) -> dict[str, Any]:
    result = _dict(payload.get("result"), "result") or run_simulation(payload)["result"]
    probabilities = copy.deepcopy((result.get("summary") or {}).get("thresholdProbabilities") or [])
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/threshold-report",
        "version": VERSION,
        "threshold_probabilities": probabilities,
        "automatic_decision": False,
        "automatic_risk_classification": False,
        "interpretation": "Probabilities describe the declared simulation model and assumptions; they are not empirical frequencies unless the study design supports that interpretation.",
    }
    out["threshold_report_hash"] = _hash(out)
    return out


def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    requested = _list(payload.get("figure_families"), "figure_families", len(FIGURE_FAMILIES)) if payload.get("figure_families") is not None else []
    figures = [str(x) for x in requested] if requested else ["output-distribution", "empirical-cdf", "sample-scatter", "convergence-trace", "quantile-stability", "seed-replication", "sensitivity-bars", "parameter-sweep", "scenario-ensemble", "uncertainty-band"]
    invalid = [x for x in figures if x not in FIGURE_FAMILIES]
    if invalid:
        raise SimulationStudioError("Unsupported simulation figure families: " + ", ".join(invalid))
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/visualization-plan",
        "version": VERSION,
        "figures": [{"figure_family": x, "publication_profile": "research-paper", "semantic_role": "simulation", "automatic_render": False} for x in figures],
        "uses_v01140_publication_design_system": True,
        "uses_v01150_statistical_uncertainty_graphics": True,
        "uses_v01160_interactive_dashboards": True,
        "uses_v01190_figure_intelligence": True,
        "automatic_render": False,
        "automatic_scientific_interpretation": False,
    }
    out["visualization_plan_hash"] = _hash(out)
    return out


def build_studio(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_study(payload)["study"]
    sampling = build_sampling_plan(payload)
    budget = build_compute_budget_plan(payload)
    simulation = run_simulation(payload)["result"]
    visualization = build_visualization_plan({})
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/studio",
        "version": VERSION,
        "study": normalized,
        "sampling_plan": sampling,
        "compute_budget": budget,
        "simulation_result": simulation,
        "visualization_plan": visualization,
        "simulation_output_semantics": "modeled-not-observed",
        "automatic_evidence_promotion": False,
        "automatic_convergence_certification": False,
        "automatic_scenario_selection": False,
        "automatic_causal_inference": False,
    }
    out["studio_hash"] = _hash(out)
    return out


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    studio = _dict(payload.get("studio"), "studio") or build_studio(payload)
    out = {
        "ok": True,
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "studio_hash": studio.get("studio_hash"),
        "study_hash": ((studio.get("study") or {}).get("studio_study_hash")),
        "simulation_result_hash": ((studio.get("simulation_result") or {}).get("simulation_result_hash")),
        "content_hash": _hash(studio),
        "reproducible": True,
        "automatic_persistence": False,
    }
    out["snapshot_hash"] = _hash(out)
    return out


def build_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    study = normalize_study(payload)["study"]
    design = copy.deepcopy(study.get("design") or {})
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/reproduction-plan",
        "version": VERSION,
        "required": ["model-specification", "fixed-values", "uncertainty-distributions", "sampling-design", "sample-count", "random-seed", "software-version"],
        "study_hash": study.get("studio_study_hash"),
        "design": design,
        "seed": design.get("seed"),
        "automatic_execution": False,
        "automatic_data_fetch": False,
        "automatic_environment_mutation": False,
    }
    out["reproduction_plan_hash"] = _hash(out)
    return out


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    formats = [str(x).lower() for x in _list(payload.get("formats") or ["json", "csv", "svg", "pdf"], "formats", 20)]
    allowed = {"json", "csv", "svg", "pdf", "png"}
    if any(x not in allowed for x in formats):
        raise SimulationStudioError("Unsupported export format.")
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/export-plan",
        "version": VERSION,
        "formats": formats,
        "include": ["study", "sampling-design", "seed", "simulation-summary", "convergence", "replication", "scenarios", "sweeps", "visualization-plan", "provenance"],
        "automatic_file_write": False,
        "publication_grade_figures": True,
    }
    out["export_plan_hash"] = _hash(out)
    return out


def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    session_id = _text(payload.get("session_id"), "session_id", 240, True)
    simulation_id = _text(payload.get("simulation_id") or payload.get("study_id") or "simulation-study", "simulation_id", 180, True)
    object_payload = {
        "session_id": session_id,
        "object": {
            "object_type": "experiment",
            "id": simulation_id,
            "metadata": {
                "lab_release_version": VERSION,
                "studio_schema": SCHEMA,
                "analysis_kind": "simulation-monte-carlo-research-studio",
                "simulation_output_semantics": "modeled-not-observed",
                "underlying_object_remains_authoritative_in_lab": True,
            },
        },
    }
    try:
        binding = build_core_object_binding(object_payload)
    except Exception as exc:
        raise SimulationStudioError(str(exc)) from exc
    return {
        "ok": True,
        "schema": f"{SCHEMA}/core-object-plan",
        "version": VERSION,
        "binding": binding,
        "automatic_core_submission": False,
        "core_executes_simulation": False,
        "core_promotes_simulation_to_evidence": False,
        "core_certifies_scientific_validity": False,
    }


def build_execution_lineage_plan(payload: dict[str, Any]) -> dict[str, Any]:
    session_id = _text(payload.get("session_id"), "session_id", 240, True)
    simulation_id = _text(payload.get("simulation_id") or "simulation-study", "simulation_id", 180, True)
    seed = payload.get("seed")
    if seed is None and isinstance(payload.get("study"), dict):
        seed = (payload["study"].get("design") or {}).get("seed")
    out = {
        "ok": True,
        "schema": f"{SCHEMA}/execution-lineage-plan",
        "version": VERSION,
        "target_contract": "sc-lab-scientific-execution-lineage/0.107.0",
        "session_id": session_id,
        "execution": {
            "id": simulation_id,
            "runtime": "python/sc-lab-simulation-monte-carlo",
            "environment_ref": "lab:environment:production",
            "method_ref": f"lab:method:simulation-monte-carlo-research-studio:{VERSION}",
            "seed_ref": f"seed:{seed}" if seed is not None else None,
            "parameters": copy.deepcopy(payload.get("parameters") or {}),
            "assumptions": copy.deepcopy(payload.get("assumptions") or {}),
            "metadata": {"simulation_output_semantics": "modeled-not-observed", "lab_release_version": VERSION},
        },
        "automatic_core_submission": False,
        "automatic_execution": False,
        "underlying_execution_remains_authoritative_in_lab": True,
    }
    out["execution_lineage_plan_hash"] = _hash(out)
    return out
