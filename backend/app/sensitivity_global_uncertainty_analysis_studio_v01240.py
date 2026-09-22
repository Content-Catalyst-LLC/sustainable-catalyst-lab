from __future__ import annotations

import copy
import itertools
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np
from scipy.stats import qmc

from .probabilistic_analysis import (
    ProbabilisticAnalysisError,
    _evaluate_matrix,
    _transform,
    _unit_design,
    normalize_study as probabilistic_normalize,
)
from .simulation_monte_carlo_research_studio_v01230 import (
    SimulationStudioError,
    build_core_object_plan as simulation_core_object_plan,
    parameter_sweep_plan,
    run_parameter_sweep,
    run_simulation,
)

VERSION = "0.124.0"
ENGINE_VERSION = "5.0.0"
SCHEMA = "sc-lab-sensitivity-global-uncertainty-analysis-studio/0.124.0"
SNAPSHOT_SCHEMA = "sc-lab-sensitivity-global-uncertainty-snapshot/0.124.0"
MAX_SOBOL_BASE_SAMPLES = 16_384
MAX_MORRIS_TRAJECTORIES = 128
MAX_RESPONSE_SURFACE_EVALUATIONS = 20_000
MAX_REPLICATIONS = 12
MAX_CONVERGENCE_CHECKPOINTS = 8

METHOD_FAMILIES = {
    "saltelli-sobol",
    "morris-elementary-effects",
    "correlation-src-screening",
    "quadratic-response-surface",
    "seed-replication",
    "sensitivity-convergence",
}
FIGURE_FAMILIES = {
    "sobol-first-total",
    "morris-mu-star-sigma",
    "correlation-screening",
    "variance-decomposition",
    "interaction-heatmap",
    "response-surface",
    "sensitivity-convergence",
    "seed-replication",
    "parameter-distributions",
    "output-uncertainty",
    "index-intervals",
    "tornado-summary",
}


class SensitivityStudioError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _copy_study(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("study") if isinstance(payload.get("study"), dict) else payload
    if not isinstance(source, dict):
        raise SensitivityStudioError("study must be an object.")
    return copy.deepcopy(source)


def _integer(value: Any, label: str, default: int, minimum: int, maximum: int) -> int:
    try:
        result = int(default if value is None else value)
    except (TypeError, ValueError) as exc:
        raise SensitivityStudioError(f"{label} must be an integer.") from exc
    if result < minimum or result > maximum:
        raise SensitivityStudioError(f"{label} must be between {minimum} and {maximum}.")
    return result


def schema_info() -> dict[str, Any]:
    return {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "snapshot_schema": SNAPSHOT_SCHEMA,
        "limits": {
            "sobol_base_samples": MAX_SOBOL_BASE_SAMPLES,
            "morris_trajectories": MAX_MORRIS_TRAJECTORIES,
            "response_surface_evaluations": MAX_RESPONSE_SURFACE_EVALUATIONS,
            "replications": MAX_REPLICATIONS,
            "convergence_checkpoints": MAX_CONVERGENCE_CHECKPOINTS,
        },
    }


def catalog() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "method_families": sorted(METHOD_FAMILIES),
        "figure_families": sorted(FIGURE_FAMILIES),
        "sobol_indices": ["first-order", "total-order"],
        "morris_statistics": ["mu", "mu-star", "sigma"],
        "interaction_method": "standardized-quadratic-screening",
        "response_surface_family": "second-order-polynomial",
        "underlying_engines": ["probabilistic-analysis-v0.48.0", "simulation-studio-v0.123.0"],
    }


def manifest() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "sensitivity-global-uncertainty-analysis-studio-ready",
        "version": VERSION,
        "engine_version": ENGINE_VERSION,
        "sobol_first_total": True,
        "morris_elementary_effects": True,
        "variance_decomposition": True,
        "interaction_screening": True,
        "response_surfaces": True,
        "sensitivity_convergence": True,
        "seed_replication": True,
        "publication_visualization": True,
        "source_models_immutable": True,
        "simulation_outputs_are_modeled_not_observed": True,
        "automatic_parameter_ranking": False,
        "automatic_significance_inference": False,
        "automatic_causal_inference": False,
        "automatic_model_selection": False,
        "automatic_scientific_validity_certification": False,
        "automatic_core_submission": False,
        "determine_truth": False,
    }


def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA, "method_family_count": len(METHOD_FAMILIES), "figure_family_count": len(FIGURE_FAMILIES)}


def normalize_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    source = _copy_study(payload)
    try:
        study = probabilistic_normalize(source)
    except ProbabilisticAnalysisError as exc:
        raise SensitivityStudioError(str(exc), getattr(exc, "status_code", 400)) from exc
    study = copy.deepcopy(study)
    study["sensitivity_studio_schema"] = SCHEMA
    study["sensitivity_studio_version"] = VERSION
    study["simulation_output_semantics"] = "modeled-not-observed"
    study["automatic_parameter_ranking"] = False
    study["automatic_significance_inference"] = False
    study["automatic_causal_inference"] = False
    study["sensitivity_study_hash"] = _hash({k: v for k, v in study.items() if k != "sensitivity_study_hash"})
    return {"ok": True, "version": VERSION, "study": study}


def sobol_report(payload: dict[str, Any]) -> dict[str, Any]:
    source = _copy_study(payload)
    design = source.setdefault("design", {})
    design["method"] = "saltelli-sobol"
    design["samples"] = _integer(payload.get("base_samples", design.get("samples", 256)), "base_samples", 256, 16, MAX_SOBOL_BASE_SAMPLES)
    try:
        result = run_simulation(source)["result"]
    except SimulationStudioError as exc:
        raise SensitivityStudioError(str(exc), getattr(exc, "status_code", 400)) from exc
    sensitivity = copy.deepcopy(result.get("sensitivity") or {})
    rows=[]
    for row in sensitivity.get("variables") or []:
        rows.append({
            "symbol": row.get("symbol"),
            "label": row.get("label") or row.get("symbol"),
            "first_order": float(row.get("firstOrder") or 0.0),
            "total_order": float(row.get("totalOrder") or 0.0),
        })
    out={
        "ok":True,"schema":f"{SCHEMA}/sobol-report","version":VERSION,
        "method":"saltelli-sobol","base_samples":design["samples"],
        "evaluation_count":int((result.get("study") or {}).get("design",{}).get("evaluationCount") or 0),
        "output_variance":float(sensitivity.get("outputVariance") or 0.0),"indices":rows,
        "simulation_output_semantics":"modeled-not-observed","automatic_parameter_ranking":False,
        "automatic_significance_inference":False,"automatic_causal_inference":False,
        "interpretation":"First- and total-order Sobol indices describe variance attribution under the declared model, distributions, independence assumption, sampling design, and seed."
    }
    out["sobol_report_hash"]=_hash(out)
    return out


def _morris_unit_trajectories(dimensions: int, trajectories: int, seed: int, delta: float) -> list[tuple[np.ndarray,np.ndarray,int]]:
    rng=np.random.default_rng(seed)
    records=[]
    for _ in range(trajectories):
        base=rng.uniform(0.05, max(0.051,0.95-delta), size=dimensions)
        order=rng.permutation(dimensions)
        current=base.copy()
        for j in order:
            nxt=current.copy(); nxt[j]=min(0.999999, current[j]+delta)
            records.append((current.copy(),nxt.copy(),int(j))); current=nxt
    return records


def morris_report(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_analysis(payload)["study"]
    specs=normalized["uncertainInputs"]
    trajectories=_integer(payload.get("trajectories"),"trajectories",16,4,MAX_MORRIS_TRAJECTORIES)
    seed=_integer(payload.get("seed",(normalized.get("design") or {}).get("seed",42)),"seed",42,-2_147_483_648,2_147_483_647)
    delta=float(payload.get("delta",0.1))
    if not 0.02 <= delta <= 0.5: raise SensitivityStudioError("delta must be between 0.02 and 0.5.")
    effects={spec["symbol"]:[] for spec in specs}
    for u0,u1,j in _morris_unit_trajectories(len(specs),trajectories,seed,delta):
        x0=np.array([_transform(np.asarray([u0[i]]),specs[i])[0] for i in range(len(specs))],dtype=float)
        x1=np.array([_transform(np.asarray([u1[i]]),specs[i])[0] for i in range(len(specs))],dtype=float)
        y=_evaluate_matrix(normalized,np.vstack([x0,x1]))
        denom=float(x1[j]-x0[j])
        ee=float((y[1]-y[0])/denom) if abs(denom)>1e-15 else 0.0
        effects[specs[j]["symbol"]].append(ee)
    rows=[]
    for spec in specs:
        vals=np.asarray(effects[spec["symbol"]],dtype=float)
        rows.append({"symbol":spec["symbol"],"label":spec.get("label") or spec["symbol"],"unit":spec.get("unit") or "","mu":float(np.mean(vals)),"mu_star":float(np.mean(np.abs(vals))),"sigma":float(np.std(vals,ddof=1)) if len(vals)>1 else 0.0,"elementary_effect_count":int(len(vals))})
    out={"ok":True,"schema":f"{SCHEMA}/morris-report","version":VERSION,"method":"morris-elementary-effects","trajectories":trajectories,"delta_unit_space":delta,"seed":seed,"effects":rows,"simulation_output_semantics":"modeled-not-observed","automatic_parameter_ranking":False,"automatic_significance_inference":False,"automatic_causal_inference":False,"interpretation":"Morris mu, mu-star, and sigma are screening diagnostics under the declared trajectories and distribution transforms; they are not significance tests."}
    out["morris_report_hash"]=_hash(out); return out


def correlation_screening_report(payload: dict[str, Any]) -> dict[str, Any]:
    source=_copy_study(payload); source.setdefault("design",{})["method"]="latin-hypercube"
    source["design"]["samples"]=_integer(payload.get("samples",source["design"].get("samples",512)),"samples",512,32,16_384)
    try: result=run_simulation(source)["result"]
    except SimulationStudioError as exc: raise SensitivityStudioError(str(exc),getattr(exc,"status_code",400)) from exc
    s=copy.deepcopy(result.get("sensitivity") or {})
    rows=[]
    for row in s.get("variables") or []:
        rows.append({"symbol":row.get("symbol"),"label":row.get("label") or row.get("symbol"),"pearson":float(row.get("pearson") or 0),"spearman":float(row.get("spearman") or 0),"standardized_regression":float(row.get("standardizedRegression") or 0)})
    out={"ok":True,"schema":f"{SCHEMA}/correlation-screening","version":VERSION,"samples":source["design"]["samples"],"variables":rows,"automatic_parameter_ranking":False,"automatic_significance_inference":False,"automatic_causal_inference":False,"interpretation":"Correlation and standardized-regression coefficients are descriptive screening measures, not causal effects or significance tests."}; out["screening_hash"]=_hash(out); return out


def variance_decomposition_report(payload: dict[str, Any]) -> dict[str, Any]:
    sob=sobol_report(payload); first=sum(r["first_order"] for r in sob["indices"]); total=sum(r["total_order"] for r in sob["indices"])
    out={"ok":True,"schema":f"{SCHEMA}/variance-decomposition","version":VERSION,"output_variance":sob["output_variance"],"first_order_sum":float(first),"total_order_sum":float(total),"unattributed_or_interaction_component":float(1.0-first),"indices":copy.deepcopy(sob["indices"]),"automatic_interaction_proof":False,"automatic_parameter_ranking":False,"interpretation":"The residual 1 - sum(first-order) can reflect interactions and finite-sample estimation error; it is not treated as a certified interaction variance share."}; out["variance_decomposition_hash"]=_hash(out); return out


def interaction_screening_report(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_analysis(payload)["study"]; specs=normalized["uncertainInputs"]; d=len(specs)
    samples=_integer(payload.get("samples"),"samples",512,max(32,4*d),4096); seed=_integer(payload.get("seed",(normalized.get("design") or {}).get("seed",42)),"seed",42,-2_147_483_648,2_147_483_647)
    unit=_unit_design("latin-hypercube",samples,d,seed); x=np.column_stack([_transform(unit[:,i],spec) for i,spec in enumerate(specs)]); y=_evaluate_matrix(normalized,x)
    xstd=np.std(x,axis=0,ddof=1); z=(x-np.mean(x,axis=0))/np.where(xstd>0,xstd,1.0); ysd=float(np.std(y,ddof=1)); yz=(y-np.mean(y))/(ysd if ysd>0 else 1.0)
    cols=[np.ones(samples)]; names=[("intercept",None,None)]
    for i,spec in enumerate(specs): cols.append(z[:,i]); names.append(("main",spec["symbol"],None))
    for i,j in itertools.combinations(range(d),2): cols.append(z[:,i]*z[:,j]); names.append(("interaction",specs[i]["symbol"],specs[j]["symbol"]))
    beta=np.linalg.lstsq(np.column_stack(cols),yz,rcond=None)[0]
    pairs=[]
    for idx,name in enumerate(names):
        if name[0]=="interaction": pairs.append({"left":name[1],"right":name[2],"standardized_interaction_coefficient":float(beta[idx]),"absolute_screening_score":abs(float(beta[idx]))})
    pred=np.column_stack(cols)@beta; ss_res=float(np.sum((yz-pred)**2)); ss_tot=float(np.sum((yz-np.mean(yz))**2)); r2=1-ss_res/ss_tot if ss_tot>0 else 0.0
    out={"ok":True,"schema":f"{SCHEMA}/interaction-screening","version":VERSION,"method":"standardized-quadratic-screening","samples":samples,"seed":seed,"pairs":pairs,"screening_model_r_squared":float(r2),"formal_second_order_sobol":False,"automatic_causal_inference":False,"automatic_significance_inference":False,"interpretation":"Pairwise coefficients screen for nonlinear interaction structure in a standardized quadratic approximation; they are not formal Sobol S2 indices or causal effects."}; out["interaction_screening_hash"]=_hash(out); return out


def response_surface_plan(payload: dict[str, Any]) -> dict[str, Any]:
    try: plan=parameter_sweep_plan(payload)
    except SimulationStudioError as exc: raise SensitivityStudioError(str(exc),getattr(exc,"status_code",400)) from exc
    if plan["evaluation_count"]>MAX_RESPONSE_SURFACE_EVALUATIONS: raise SensitivityStudioError("Response-surface sweep exceeds evaluation limit.",413)
    out={"ok":True,"schema":f"{SCHEMA}/response-surface-plan","version":VERSION,"sweep_plan":plan,"surface_family":"second-order-polynomial","includes_pairwise_interactions":True,"automatic_optimum_selection":False,"automatic_model_selection":False}; out["response_surface_plan_hash"]=_hash(out); return out


def response_surface_run(payload: dict[str, Any]) -> dict[str, Any]:
    plan=response_surface_plan(payload)
    try: sweep=run_parameter_sweep(payload)
    except SimulationStudioError as exc: raise SensitivityStudioError(str(exc),getattr(exc,"status_code",400)) from exc
    axes=[a["symbol"] for a in sweep["plan"]["axes"]]; rows=sweep["records"]
    x=np.asarray([[r["coordinates"][a] for a in axes] for r in rows],dtype=float); y=np.asarray([r["output"] for r in rows],dtype=float)
    means=np.mean(x,axis=0); scales=np.std(x,axis=0,ddof=1); z=(x-means)/np.where(scales>0,scales,1.0)
    cols=[np.ones(len(z))]; terms=[{"type":"intercept","symbols":[]}]
    for i,a in enumerate(axes): cols.append(z[:,i]); terms.append({"type":"main","symbols":[a]})
    for i,a in enumerate(axes): cols.append(z[:,i]**2); terms.append({"type":"quadratic","symbols":[a]})
    for i,j in itertools.combinations(range(len(axes)),2): cols.append(z[:,i]*z[:,j]); terms.append({"type":"interaction","symbols":[axes[i],axes[j]]})
    mat=np.column_stack(cols); beta=np.linalg.lstsq(mat,y,rcond=None)[0]; pred=mat@beta; resid=y-pred; ss_res=float(np.sum(resid**2)); ss_tot=float(np.sum((y-np.mean(y))**2)); r2=1-ss_res/ss_tot if ss_tot>0 else 0.0
    coefs=[]
    for t,b in zip(terms,beta): coefs.append({**t,"coefficient":float(b)})
    out={"ok":True,"schema":f"{SCHEMA}/response-surface-result","version":VERSION,"surface_family":"second-order-polynomial","axes":axes,"standardization":{"means":{a:float(means[i]) for i,a in enumerate(axes)},"scales":{a:float(scales[i]) for i,a in enumerate(axes)}},"coefficients":coefs,"diagnostics":{"r_squared":float(r2),"rmse":float(math.sqrt(np.mean(resid**2))),"record_count":len(rows)},"simulation_output_semantics":"modeled-not-observed","automatic_optimum_selection":False,"automatic_model_selection":False,"automatic_causal_inference":False}; out["response_surface_hash"]=_hash(out); return out


def sensitivity_convergence_report(payload: dict[str, Any]) -> dict[str, Any]:
    requested=payload.get("checkpoints") or [64,128,256]
    if not isinstance(requested,list) or not requested: raise SensitivityStudioError("checkpoints must be a non-empty array.")
    checkpoints=sorted(set(_integer(x,"checkpoint",64,16,MAX_SOBOL_BASE_SAMPLES) for x in requested))[-MAX_CONVERGENCE_CHECKPOINTS:]
    rows=[]; previous=None
    for n in checkpoints:
        rep=sobol_report({**payload,"base_samples":n})
        current={r["symbol"]:r["total_order"] for r in rep["indices"]}; delta=None
        if previous is not None: delta={k:float(current[k]-previous.get(k,0.0)) for k in current}
        rows.append({"base_samples":n,"evaluation_count":rep["evaluation_count"],"indices":copy.deepcopy(rep["indices"]),"delta_total_order_from_previous":delta}); previous=current
    out={"ok":True,"schema":f"{SCHEMA}/sensitivity-convergence","version":VERSION,"checkpoints":rows,"convergence_certified":False,"automatic_convergence_certification":False,"interpretation":"Index stability across sample sizes is descriptive convergence evidence only."}; out["sensitivity_convergence_hash"]=_hash(out); return out


def sensitivity_replication_report(payload: dict[str, Any]) -> dict[str, Any]:
    source=_copy_study(payload); base_seed=int((source.get("design") or {}).get("seed",42)); seeds=payload.get("seeds")
    if seeds is None: seeds=[base_seed+i*104729 for i in range(_integer(payload.get("replications"),"replications",4,2,MAX_REPLICATIONS))]
    if not isinstance(seeds,list) or not 2<=len(seeds)<=MAX_REPLICATIONS: raise SensitivityStudioError(f"seeds must contain 2 to {MAX_REPLICATIONS} integers.")
    reports=[]
    for seed in seeds:
        st=_copy_study(payload); st.setdefault("design",{})["seed"]=int(seed); reports.append({"seed":int(seed),"report":sobol_report({"study":st,"base_samples":payload.get("base_samples",64)})})
    symbols=[r["symbol"] for r in reports[0]["report"]["indices"]]; summary=[]
    for sym in symbols:
        first=np.asarray([next(r for r in x["report"]["indices"] if r["symbol"]==sym)["first_order"] for x in reports],dtype=float); total=np.asarray([next(r for r in x["report"]["indices"] if r["symbol"]==sym)["total_order"] for x in reports],dtype=float)
        summary.append({"symbol":sym,"first_order_mean":float(np.mean(first)),"first_order_sd":float(np.std(first,ddof=1)),"total_order_mean":float(np.mean(total)),"total_order_sd":float(np.std(total,ddof=1))})
    out={"ok":True,"schema":f"{SCHEMA}/replication-report","version":VERSION,"runs":[{"seed":r["seed"],"indices":r["report"]["indices"]} for r in reports],"summary":summary,"stability_certified":False,"automatic_parameter_ranking":False}; out["replication_report_hash"]=_hash(out); return out


def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    requested=payload.get("figure_families") or ["sobol-first-total","morris-mu-star-sigma","variance-decomposition","interaction-heatmap","response-surface","sensitivity-convergence","seed-replication","tornado-summary"]
    if not isinstance(requested,list): raise SensitivityStudioError("figure_families must be an array.")
    invalid=[x for x in requested if x not in FIGURE_FAMILIES]
    if invalid: raise SensitivityStudioError("Unsupported sensitivity figure families: "+", ".join(map(str,invalid)))
    out={"ok":True,"schema":f"{SCHEMA}/visualization-plan","version":VERSION,"figures":[{"figure_family":x,"publication_profile":"research-paper","semantic_role":"sensitivity","automatic_render":False} for x in requested],"uses_v01140_publication_design_system":True,"uses_v01150_statistical_uncertainty_graphics":True,"uses_v01160_interactive_dashboards":True,"uses_v01190_figure_intelligence":True,"automatic_render":False,"automatic_scientific_interpretation":False}; out["visualization_plan_hash"]=_hash(out); return out


def build_studio(payload: dict[str, Any]) -> dict[str, Any]:
    normalized=normalize_analysis(payload)["study"]; sob=sobol_report(payload); var=variance_decomposition_report(payload); vis=build_visualization_plan({})
    out={"ok":True,"schema":f"{SCHEMA}/studio","version":VERSION,"study":normalized,"sobol":sob,"variance_decomposition":var,"visualization_plan":vis,"simulation_output_semantics":"modeled-not-observed","automatic_parameter_ranking":False,"automatic_significance_inference":False,"automatic_causal_inference":False}; out["studio_hash"]=_hash(out); return out


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    studio=copy.deepcopy(payload.get("studio")) if isinstance(payload.get("studio"),dict) else build_studio(payload)
    out={"ok":True,"schema":SNAPSHOT_SCHEMA,"version":VERSION,"studio_hash":studio.get("studio_hash"),"content_hash":_hash(studio),"reproducible":True,"automatic_persistence":False}; out["snapshot_hash"]=_hash(out); return out


def build_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    study=normalize_analysis(payload)["study"]
    out={"ok":True,"schema":f"{SCHEMA}/reproduction-plan","version":VERSION,"required":["model-specification","uncertain-input-distributions","independence-assumption","sampling-method","base-sample-count","random-seed","software-version"],"study_hash":study.get("sensitivity_study_hash"),"seed":(study.get("design") or {}).get("seed"),"automatic_execution":False,"automatic_environment_mutation":False}; out["reproduction_plan_hash"]=_hash(out); return out


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    formats=payload.get("formats") or ["json","csv","svg","pdf"]
    if not isinstance(formats,list) or any(str(x).lower() not in {"json","csv","svg","pdf","png"} for x in formats): raise SensitivityStudioError("Unsupported export format.")
    out={"ok":True,"schema":f"{SCHEMA}/export-plan","version":VERSION,"formats":[str(x).lower() for x in formats],"include":["study","sobol-indices","morris-effects","variance-decomposition","interaction-screening","response-surface","convergence","replication","visualization-plan","provenance"],"automatic_file_write":False,"publication_grade_figures":True}; out["export_plan_hash"]=_hash(out); return out


def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        plan=simulation_core_object_plan({"session_id":payload.get("session_id"),"simulation_id":payload.get("analysis_id") or payload.get("sensitivity_id") or "sensitivity-analysis"})
    except SimulationStudioError as exc: raise SensitivityStudioError(str(exc),getattr(exc,"status_code",400)) from exc
    plan=copy.deepcopy(plan); plan["schema"]=f"{SCHEMA}/core-object-plan"; plan["version"]=VERSION; plan["analysis_kind"]="sensitivity-global-uncertainty-analysis"; plan["automatic_core_submission"]=False; plan["core_certifies_scientific_validity"]=False; return plan


def build_execution_lineage_plan(payload: dict[str, Any]) -> dict[str, Any]:
    session_id=str(payload.get("session_id") or "").strip()
    if not session_id: raise SensitivityStudioError("session_id is required.")
    analysis_id=str(payload.get("analysis_id") or payload.get("sensitivity_id") or "sensitivity-analysis").strip()
    seed=payload.get("seed")
    if seed is None and isinstance(payload.get("study"),dict): seed=(payload["study"].get("design") or {}).get("seed")
    out={"ok":True,"schema":f"{SCHEMA}/execution-lineage-plan","version":VERSION,"target_contract":"sc-lab-scientific-execution-lineage/0.107.0","session_id":session_id,"execution":{"id":analysis_id,"runtime":"python/sc-lab-sensitivity-global-uncertainty","environment_ref":"lab:environment:production","method_ref":f"lab:method:sensitivity-global-uncertainty-analysis:{VERSION}","seed_ref":f"seed:{seed}" if seed is not None else None,"metadata":{"simulation_output_semantics":"modeled-not-observed","lab_release_version":VERSION}},"automatic_core_submission":False,"automatic_execution":False,"underlying_execution_remains_authoritative_in_lab":True}; out["execution_lineage_plan_hash"]=_hash(out); return out


def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    out={"ok":True,"schema":f"{SCHEMA}/interpretation-boundaries","version":VERSION,"boundaries":["Sensitivity indices depend on the declared model, distributions, parameter ranges, independence assumptions, sample size, and random seed.","Large sensitivity measures do not by themselves establish causality, practical importance, or statistical significance.","Morris elementary effects are screening diagnostics, not significance tests.","Quadratic interaction coefficients are screening approximations, not formal second-order Sobol indices.","Simulated outputs are modeled-not-observed and are not automatically promoted to evidence."],"automatic_parameter_ranking":False,"automatic_significance_inference":False,"automatic_causal_inference":False,"scientific_validity_certified":False}; out["boundaries_hash"]=_hash(out); return out
