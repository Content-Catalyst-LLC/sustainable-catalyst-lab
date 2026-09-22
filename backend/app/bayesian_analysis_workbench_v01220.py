from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np
from scipy import stats

from .bayesian_inference import BayesianInferenceError, fit as bayes_fit, normalize_study as bayes_normalize, posterior_predictive as bayes_posterior_predictive
from .platform_core_v3_object_mapping_v01050 import build_core_object_binding

VERSION = "0.122.0"
ENGINE_VERSION = "4.2.0"
SCHEMA = "sc-lab-bayesian-analysis-workbench-ii/0.122.0"
SNAPSHOT_SCHEMA = "sc-lab-bayesian-analysis-workbench-snapshot/0.122.0"
MAX_ROWS = 5_000
MAX_MODELS = 10
MAX_HIERARCHICAL_UNITS = 500
MAX_PROBABILITY_QUERIES = 100
MAX_HIERARCHICAL_DRAWS = 4_000

FAMILIES = {"gaussian", "binomial-logit", "poisson-log"}
DIAGNOSTICS = {"split-rhat", "ess", "mcse", "acceptance-rate", "posterior-predictive", "prior-posterior", "trace"}
FIGURE_FAMILIES = {
    "prior-posterior", "trace", "rank", "autocorrelation", "posterior-interval", "posterior-density",
    "posterior-predictive", "ppc-discrepancy", "calibration-reliability", "hierarchical-forest",
    "shrinkage", "model-comparison"
}

class BayesianWorkbenchError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail); self.detail = detail; self.status_code = status_code


def _stable(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)

def _hash(v: Any) -> str:
    return sha256(_stable(v).encode()).hexdigest()

def _dict(v: Any, label: str) -> dict[str, Any]:
    if v is None: return {}
    if not isinstance(v, dict): raise BayesianWorkbenchError(f"{label} must be an object.")
    return copy.deepcopy(v)

def _list(v: Any, label: str, maximum: int = 1000) -> list[Any]:
    if v is None: return []
    if not isinstance(v, list): raise BayesianWorkbenchError(f"{label} must be an array.")
    if len(v) > maximum: raise BayesianWorkbenchError(f"{label} exceeds {maximum} entries.", 413)
    return copy.deepcopy(v)

def _text(v: Any, label: str, maximum: int = 500, required: bool = False) -> str:
    s = str(v or "").strip()
    if required and not s: raise BayesianWorkbenchError(f"{label} is required.")
    if len(s) > maximum: raise BayesianWorkbenchError(f"{label} exceeds {maximum} characters.")
    return s

def _finite(v: Any, label: str, default: float | None = None) -> float:
    if v is None and default is not None: return default
    try: x = float(v)
    except (TypeError, ValueError) as exc: raise BayesianWorkbenchError(f"{label} must be numeric.") from exc
    if not math.isfinite(x): raise BayesianWorkbenchError(f"{label} must be finite.")
    return x

def _clean(v: Any) -> Any:
    if isinstance(v, (np.floating, float)):
        x = float(v); return x if math.isfinite(x) else None
    if isinstance(v, np.integer): return int(v)
    if isinstance(v, np.bool_): return bool(v)
    if isinstance(v, dict): return {str(k): _clean(x) for k, x in v.items()}
    if isinstance(v, list): return [_clean(x) for x in v]
    return v

def _dataset(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    src = payload.get("dataset") if isinstance(payload.get("dataset"), dict) else payload
    dataset_id = _text(src.get("id") or src.get("dataset_id") or "dataset", "dataset id", 180, True)
    rows = src.get("rows")
    if not isinstance(rows, list) or not rows: raise BayesianWorkbenchError("dataset.rows must be a non-empty array.")
    if len(rows) > MAX_ROWS: raise BayesianWorkbenchError(f"dataset exceeds {MAX_ROWS} rows.", 413)
    if any(not isinstance(r, dict) for r in rows): raise BayesianWorkbenchError("Every dataset row must be an object.")
    return dataset_id, copy.deepcopy(rows)

def _study_and_rows(payload: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    dataset_id, rows = _dataset(payload)
    study_payload = _dict(payload.get("study") or payload.get("model"), "study")
    if not study_payload:
        keys = {"id","title","family","modelType","features","response","standardize","splineFeature","knots","credibleLevel","chains","draws","warmup","seed","targetAcceptance","proposalScale","posteriorPredictiveDraws","interceptPriorMean","interceptPriorSD","coefficientPriorMean","coefficientPriorSD","termPriors","sigmaPriorShape","sigmaPriorScale","provenance"}
        study_payload = {k: copy.deepcopy(payload[k]) for k in keys if k in payload}
    if not study_payload: raise BayesianWorkbenchError("study specification is required.")
    study_payload.setdefault("id", _text(payload.get("model_id") or "bayesian-model", "model id", 180, True))
    try: study = bayes_normalize(study_payload)
    except BayesianInferenceError as exc: raise BayesianWorkbenchError(str(exc)) from exc
    return dataset_id, study, rows

def schema_info() -> dict[str, Any]:
    return {"ok": True, "schema": SCHEMA, "version": VERSION, "engine_version": ENGINE_VERSION, "snapshot_schema": SNAPSHOT_SCHEMA,
            "max_rows": MAX_ROWS, "max_models": MAX_MODELS, "max_hierarchical_units": MAX_HIERARCHICAL_UNITS,
            "max_probability_queries": MAX_PROBABILITY_QUERIES}

def catalog() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "families": sorted(FAMILIES), "diagnostics": sorted(DIAGNOSTICS),
            "figure_families": sorted(FIGURE_FAMILIES),
            "analysis_families": ["posterior-fit","prior-posterior","sampler-diagnostics","convergence-audit","posterior-predictive","probability-statements","hierarchical-normal","model-comparison","visualization","snapshot"],
            "hierarchical_models": ["normal-normal-random-effects"],
            "comparison_metrics": ["posterior-predictive-rmse","posterior-predictive-mae","max-rhat","min-ess"]}

def manifest() -> dict[str, Any]:
    return {"ok": True, "status": "bayesian-analysis-workbench-ii-ready", "version": VERSION, "engine_version": ENGINE_VERSION,
            "gaussian_regression": True, "binomial_logit": True, "poisson_log": True, "prior_posterior_comparison": True,
            "posterior_diagnostics": True, "posterior_predictive_checks": True, "probability_statements": True,
            "hierarchical_normal_random_effects": True, "model_comparison": True, "publication_visualization": True,
            "source_rows_immutable": True, "automatic_prior_selection": False, "automatic_convergence_certification": False,
            "automatic_model_selection": False, "automatic_significance_labels": False, "automatic_causal_inference": False,
            "automatic_scientific_validity_certification": False, "automatic_core_submission": False, "determine_truth": False}

def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA, "family_count": len(FAMILIES), "diagnostic_count": len(DIAGNOSTICS),
            "figure_family_count": len(FIGURE_FAMILIES)}

def normalize_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, study, _ = _study_and_rows(payload)
    return {"ok": True, "schema": f"{SCHEMA}/analysis-spec", "version": VERSION, "dataset_id": dataset_id, "study": study,
            "source_rows_immutable": True, "automatic_prior_selection": False,
            "analysis_spec_hash": _hash({"dataset_id": dataset_id, "study": study})}

def fit_posterior(payload: dict[str, Any]) -> dict[str, Any]:
    dataset_id, study, rows = _study_and_rows(payload)
    try: result = bayes_fit({"study": study, "rows": rows})["result"]
    except BayesianInferenceError as exc: raise BayesianWorkbenchError(str(exc)) from exc
    result = copy.deepcopy(result)
    result["lab_release_version"] = VERSION
    result["workbench_schema"] = SCHEMA
    result["dataset_id"] = dataset_id
    result["source_rows_immutable"] = True
    result["automatic_prior_selection"] = False
    result["automatic_convergence_certification"] = False
    result["automatic_model_selection"] = False
    result["automatic_significance_labels"] = False
    result["automatic_causal_inference"] = False
    result["scientific_validity_certified"] = False
    result["workbench_result_hash"] = _hash({k:v for k,v in result.items() if k != "workbench_result_hash"})
    return {"ok": True, "version": VERSION, "result": _clean(result)}

def _result(payload: dict[str, Any]) -> dict[str, Any]:
    r = _dict(payload.get("result"), "result")
    return r or fit_posterior(payload)["result"]

def prior_posterior_report(payload: dict[str, Any]) -> dict[str, Any]:
    r = _result(payload); study = _dict(r.get("study"), "result.study")
    summaries = (r.get("posterior") or {}).get("summaries") or []
    term_specific = ((study.get("priors") or {}).get("termSpecific") or {})
    rows=[]
    for s in summaries:
        term = s.get("term")
        if term == "Residual σ":
            prior = copy.deepcopy((study.get("priors") or {}).get("residualVariance") or {})
            prior_scale = "variance-prior"
        elif term == "Intercept":
            prior = copy.deepcopy((study.get("priors") or {}).get("intercept") or {})
            prior_scale = "coefficient"
        else:
            prior = copy.deepcopy(term_specific.get(term) or (study.get("priors") or {}).get("coefficient") or {})
            prior_scale = "coefficient"
        row={"term":term,"prior":prior,"prior_scale":prior_scale,"posterior":{"mean":s.get("mean"),"sd":s.get("sd"),"median":s.get("median"),"credibleLow":s.get("credibleLow"),"credibleHigh":s.get("credibleHigh")},"automatic_prior_adequacy_judgment":False}
        if prior.get("distribution") == "normal" and isinstance(prior.get("mean"),(int,float)) and isinstance(prior.get("sd"),(int,float)) and prior["sd"]>0 and isinstance(s.get("mean"),(int,float)):
            row["posterior_shift_in_prior_sd"]=(float(s["mean"])-float(prior["mean"]))/float(prior["sd"])
        rows.append(_clean(row))
    out={"ok":True,"schema":f"{SCHEMA}/prior-posterior-report","version":VERSION,"model_id":study.get("id"),"terms":rows,"automatic_prior_selection":False,"automatic_prior_adequacy_judgment":False}; out["report_hash"]=_hash(out); return out

def sampler_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    r=_result(payload); d=copy.deepcopy(r.get("diagnostics") or {}); summaries=(r.get("posterior") or {}).get("summaries") or []
    rows=[{"term":s.get("term"),"rhat":s.get("rhat"),"ess":s.get("ess"),"mcse_mean":s.get("mcseMean"),"automatic_pass_fail":False} for s in summaries]
    return {"ok":True,"schema":f"{SCHEMA}/sampler-diagnostics","version":VERSION,"diagnostics":_clean(d),"terms":_clean(rows),"automatic_convergence_certification":False,"review_required":bool(d.get("reviewRequired"))}

def convergence_audit(payload: dict[str, Any]) -> dict[str, Any]:
    report=sampler_diagnostics(payload); thresholds=_dict(payload.get("thresholds"),"thresholds")
    rhat_max=_finite(thresholds.get("rhat_max"),"rhat_max",1.01); ess_min=_finite(thresholds.get("ess_min"),"ess_min",400.0)
    findings=[]
    for row in report["terms"]:
        if isinstance(row.get("rhat"),(int,float)) and row["rhat"]>rhat_max: findings.append({"term":row["term"],"kind":"rhat-above-declared-threshold","value":row["rhat"],"threshold":rhat_max})
        if isinstance(row.get("ess"),(int,float)) and row["ess"]<ess_min: findings.append({"term":row["term"],"kind":"ess-below-declared-threshold","value":row["ess"],"threshold":ess_min})
    return {"ok":True,"schema":f"{SCHEMA}/convergence-audit","version":VERSION,"declared_thresholds":{"rhat_max":rhat_max,"ess_min":ess_min},"findings":findings,"review_required":bool(findings) or report["review_required"],"convergence_certified":False,"automatic_convergence_certification":False}

def posterior_predictive_report(payload: dict[str, Any]) -> dict[str, Any]:
    r=_result(payload)
    pp=copy.deepcopy(r.get("posteriorPredictive") or {})
    if not pp and payload.get("prediction_rows"):
        try: pp=bayes_posterior_predictive({"result":r,"rows":payload["prediction_rows"],"draws":payload.get("draws",300),"seed":payload.get("seed",42)})["posteriorPredictive"]
        except BayesianInferenceError as exc: raise BayesianWorkbenchError(str(exc)) from exc
    return {"ok":True,"schema":f"{SCHEMA}/posterior-predictive-report","version":VERSION,"posterior_predictive":_clean(pp),"tail_warning_count":((pp.get("checks") or {}).get("tailWarnings")),"automatic_model_approval":False,"automatic_scientific_interpretation":False}

def probability_report(payload: dict[str, Any]) -> dict[str, Any]:
    r=_result(payload); queries=_list(payload.get("queries"),"queries",MAX_PROBABILITY_QUERIES)
    labels=((r.get("design") or {}).get("labels") or []); retained=((r.get("posterior") or {}).get("retainedDraws") or {})
    coeff=np.asarray(retained.get("coefficientDraws") or [],dtype=float)
    sigma=np.asarray(retained.get("sigmaDraws") or [],dtype=float)
    lookup={str(label):coeff[:,i] for i,label in enumerate(labels)} if coeff.ndim==2 and coeff.shape[1]==len(labels) else {}
    if sigma.size: lookup["Residual σ"]=sigma
    out=[]
    for q in queries:
        if not isinstance(q,dict): raise BayesianWorkbenchError("Each probability query must be an object.")
        term=_text(q.get("term"),"query.term",180,True); threshold=_finite(q.get("threshold"),"query.threshold",0.0); direction=str(q.get("direction") or "greater-than")
        draws=lookup.get(term)
        if draws is None or not len(draws): raise BayesianWorkbenchError(f"No retained posterior draws found for term: {term}")
        if direction=="greater-than": prob=float(np.mean(draws>threshold))
        elif direction=="less-than": prob=float(np.mean(draws<threshold))
        else: raise BayesianWorkbenchError("query.direction must be greater-than or less-than.")
        out.append({"term":term,"direction":direction,"threshold":threshold,"posterior_probability":prob,"draw_count":int(len(draws)),"automatic_decision":False})
    result={"ok":True,"schema":f"{SCHEMA}/probability-report","version":VERSION,"queries":_clean(out),"automatic_decision":False,"automatic_significance_label":False}; result["report_hash"]=_hash(result); return result

def _weighted_quantile(values: np.ndarray, weights: np.ndarray, probs: list[float]) -> list[float]:
    idx=np.argsort(values); v=values[idx]; w=weights[idx]; c=np.cumsum(w); c=c/c[-1]
    return [float(np.interp(p,c,v)) for p in probs]

def fit_hierarchical_normal(payload: dict[str, Any]) -> dict[str, Any]:
    spec=_dict(payload.get("hierarchical") or payload.get("model"),"hierarchical")
    units=_list(payload.get("units") or spec.get("units"),"units",MAX_HIERARCHICAL_UNITS)
    if len(units)<2: raise BayesianWorkbenchError("At least two hierarchical units are required.")
    ids=[]; y=[]; se=[]
    for i,u in enumerate(units):
        if not isinstance(u,dict): raise BayesianWorkbenchError("Each hierarchical unit must be an object.")
        ids.append(_text(u.get("id") or f"unit-{i+1}","unit id",180,True)); y.append(_finite(u.get("estimate"),"unit estimate")); s=_finite(u.get("standard_error") or u.get("standardError"),"unit standard_error");
        if s<=0: raise BayesianWorkbenchError("unit standard_error must be positive.")
        se.append(s)
    y=np.asarray(y); se=np.asarray(se); m0=_finite(spec.get("mu_prior_mean"),"mu_prior_mean",0.0); s0=_finite(spec.get("mu_prior_sd"),"mu_prior_sd",10.0); tau_scale=_finite(spec.get("tau_prior_scale"),"tau_prior_scale",1.0)
    if s0<=0 or tau_scale<=0: raise BayesianWorkbenchError("Prior scales must be positive.")
    draws=int(min(max(_finite(spec.get("draws"),"draws",2000),200),MAX_HIERARCHICAL_DRAWS)); seed=int(_finite(spec.get("seed"),"seed",42)); level=min(max(_finite(spec.get("credible_level"),"credible_level",0.95),0.5),0.999)
    upper=max(tau_scale*5,float(np.std(y))*3,float(np.max(se))*4,1e-6); grid=np.linspace(0,upper,600)
    logw=[]; mu_mean=[]; mu_sd=[]
    for tau in grid:
        var=se**2+tau**2; prec=1/(s0**2)+np.sum(1/var); b=m0/(s0**2)+np.sum(y/var); c=m0*m0/(s0**2)+np.sum(y*y/var)
        lm=-0.5*(np.sum(np.log(var))+math.log(s0**2)+math.log(prec)+(c-b*b/prec))-0.5*(tau/tau_scale)**2
        logw.append(lm); mu_mean.append(b/prec); mu_sd.append(math.sqrt(1/prec))
    logw=np.asarray(logw); weights=np.exp(logw-np.max(logw)); weights=weights/weights.sum(); rng=np.random.default_rng(seed); idx=rng.choice(len(grid),size=draws,p=weights)
    tau_draws=grid[idx]; mu_draws=np.asarray([rng.normal(mu_mean[j],mu_sd[j]) for j in idx]); alpha=(1-level)/2
    theta=np.empty((draws,len(y)))
    for d,(mu,tau) in enumerate(zip(mu_draws,tau_draws)):
        if tau<1e-12: theta[d,:]=mu
        else:
            prec=1/(se**2)+1/(tau**2); mean=(y/(se**2)+mu/(tau**2))/prec; sd=np.sqrt(1/prec); theta[d,:]=rng.normal(mean,sd)
    def summ(a):
        return {"mean":float(np.mean(a)),"sd":float(np.std(a,ddof=1)),"median":float(np.median(a)),"credibleLow":float(np.quantile(a,alpha)),"credibleHigh":float(np.quantile(a,1-alpha))}
    group=[]
    for j,name in enumerate(ids): group.append({"unit_id":name,"observed_estimate":float(y[j]),"standard_error":float(se[j]),"posterior":summ(theta[:,j]),"shrinkage_from_observed":float(np.mean(theta[:,j])-y[j])})
    res={"ok":True,"schema":f"{SCHEMA}/hierarchical-normal","version":VERSION,"model_id":_text(spec.get("id") or "hierarchical-bayesian-model","model id",180,True),"unit_count":len(ids),"prior":{"mu":{"distribution":"normal","mean":m0,"sd":s0},"tau":{"distribution":"half-normal","scale":tau_scale}},"posterior":{"mu":summ(mu_draws),"tau":summ(tau_draws),"groups":group},"credible_level":level,"draw_count":draws,"automatic_generalization":False,"automatic_heterogeneity_judgment":False,"automatic_scientific_validity_certification":False}; res["result_hash"]=_hash(res); return _clean(res)

def hierarchical_summary(payload: dict[str, Any]) -> dict[str, Any]:
    r=_dict(payload.get("hierarchical_result"),"hierarchical_result") or fit_hierarchical_normal(payload)
    return {"ok":True,"schema":f"{SCHEMA}/hierarchical-summary","version":VERSION,"model_id":r.get("model_id"),"unit_count":r.get("unit_count"),"population_posterior":(r.get("posterior") or {}).get("mu"),"heterogeneity_posterior":(r.get("posterior") or {}).get("tau"),"group_posteriors":(r.get("posterior") or {}).get("groups"),"automatic_generalization":False,"automatic_heterogeneity_judgment":False}

def compare_models(payload: dict[str, Any]) -> dict[str, Any]:
    models=_list(payload.get("results"),"results",MAX_MODELS)
    if len(models)<2: raise BayesianWorkbenchError("At least two fitted Bayesian results are required.")
    rows=[]
    for r in models:
        if not isinstance(r,dict): raise BayesianWorkbenchError("Each result must be an object.")
        study=r.get("study") or {}; pp=r.get("posteriorPredictive") or {}; preds=pp.get("predictions") or []; observed=_list(r.get("observed") or [],"observed",MAX_ROWS)
        rmse=mae=None
        if observed and len(observed)==len(preds):
            y=np.asarray([_finite(x,"observed") for x in observed]); p=np.asarray([_finite(x.get("predictiveMean"),"predictiveMean") for x in preds]); rmse=float(np.sqrt(np.mean((y-p)**2))); mae=float(np.mean(np.abs(y-p)))
        d=r.get("diagnostics") or {}
        rows.append({"model_id":study.get("id"),"family":study.get("family"),"posterior_predictive_rmse":rmse,"posterior_predictive_mae":mae,"max_rhat":d.get("maxRhat"),"min_ess":d.get("minEss"),"review_required":d.get("reviewRequired")})
    out={"ok":True,"schema":f"{SCHEMA}/model-comparison","version":VERSION,"models":_clean(rows),"selected_model_id":None,"automatic_model_selection":False,"comparison_note":"Metrics are reported side-by-side; no model is automatically ranked or selected."}; out["comparison_hash"]=_hash(out); return out

def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    r=_dict(payload.get("result"),"result"); figures=["prior-posterior","posterior-interval","posterior-density","trace","autocorrelation","posterior-predictive","ppc-discrepancy"]
    if r and ((r.get("study") or {}).get("family") == "binomial-logit"): figures.append("calibration-reliability")
    if payload.get("hierarchical_result"): figures += ["hierarchical-forest","shrinkage"]
    if payload.get("comparison"): figures.append("model-comparison")
    out={"ok":True,"schema":f"{SCHEMA}/visualization-plan","version":VERSION,"figures":[{"figure_family":x,"publication_profile":"research-paper","automatic_render":False} for x in figures],"uses_v01140_publication_design_system":True,"uses_v01150_statistical_graphics":True,"uses_v01160_dashboards":True,"automatic_render":False,"automatic_scientific_interpretation":False}; out["visualization_plan_hash"]=_hash(out); return out

def build_workbench(payload: dict[str, Any]) -> dict[str, Any]:
    fit=fit_posterior(payload)["result"]; prior=prior_posterior_report({"result":fit}); diagnostics=sampler_diagnostics({"result":fit}); audit=convergence_audit({"result":fit,"thresholds":payload.get("thresholds")}); ppc=posterior_predictive_report({"result":fit}); vis=build_visualization_plan({"result":fit})
    out={"ok":True,"schema":f"{SCHEMA}/workbench","version":VERSION,"result":fit,"prior_posterior":prior,"sampler_diagnostics":diagnostics,"convergence_audit":audit,"posterior_predictive":ppc,"visualization_plan":vis,"source_rows_immutable":True,"automatic_prior_selection":False,"automatic_convergence_certification":False,"automatic_model_selection":False,"automatic_causal_inference":False}; out["workbench_hash"]=_hash(out); return out

def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    wb=_dict(payload.get("workbench"),"workbench") or build_workbench(payload); out={"ok":True,"schema":SNAPSHOT_SCHEMA,"version":VERSION,"workbench_hash":wb.get("workbench_hash"),"model_id":((wb.get("result") or {}).get("study") or {}).get("id"),"content_hash":_hash(wb),"automatic_persistence":False,"reproducible":True}; out["snapshot_hash"]=_hash(out); return out

def build_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    r=_dict(payload.get("result"),"result"); study=(r.get("study") or {}) if r else _dict(payload.get("study"),"study")
    out={"ok":True,"schema":f"{SCHEMA}/reproduction-plan","version":VERSION,"model_id":study.get("id"),"required":["study-specification","priors","sampler-settings","random-seed","dataset-reference","software-version"],"sampler":copy.deepcopy(study.get("sampler") or {}),"automatic_execution":False,"automatic_data_fetch":False}; out["reproduction_plan_hash"]=_hash(out); return out

def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    formats=[str(x).lower() for x in _list(payload.get("formats") or ["json","csv","svg","pdf"],"formats",20)]; allowed={"json","csv","svg","pdf","png"}
    if any(x not in allowed for x in formats): raise BayesianWorkbenchError("Unsupported export format.")
    out={"ok":True,"schema":f"{SCHEMA}/export-plan","version":VERSION,"formats":formats,"include":["study","priors","posterior-summaries","diagnostics","posterior-predictive","probability-statements","visualization-plan","provenance"],"automatic_file_write":False,"publication_grade_figures":True}; out["export_plan_hash"]=_hash(out); return out

def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    session_id=_text(payload.get("session_id"),"session_id",240,True); model_id=_text(payload.get("model_id") or ((_dict(payload.get("result"),"result").get("study") or {}).get("id")) or "bayesian-model","model_id",180,True)
    object_payload={"session_id":session_id,"object":{"object_type":"model","id":model_id,"metadata":{"lab_release_version":VERSION,"workbench_schema":SCHEMA,"analysis_kind":"bayesian-analysis-workbench-ii","underlying_object_remains_authoritative_in_lab":True}}}
    try: binding=build_core_object_binding(object_payload)
    except Exception as exc: raise BayesianWorkbenchError(str(exc)) from exc
    return {"ok":True,"schema":f"{SCHEMA}/core-object-plan","version":VERSION,"binding":binding,"automatic_core_submission":False,"core_executes_model":False,"core_selects_priors":False,"core_certifies_scientific_validity":False}
