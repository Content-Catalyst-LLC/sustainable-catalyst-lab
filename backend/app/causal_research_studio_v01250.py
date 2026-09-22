from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from .causal_inference_v0670 import (
    CausalInferenceError,
    evaluate as governance_evaluate,
    normalize_design as governance_normalize_design,
    policies as governance_policies,
)

VERSION = "0.125.0"
ENGINE_VERSION = "6.0.0"
SCHEMA = "sc-lab-causal-research-studio/0.125.0"
SNAPSHOT_SCHEMA = "sc-lab-causal-research-snapshot/0.125.0"
MAX_ROWS = 20_000
MAX_COVARIATES = 64
MAX_DAG_NODES = 128
MAX_DAG_EDGES = 512
MAX_DONORS = 128
MAX_PLACEBO_TESTS = 64

METHOD_FAMILIES = {
    "propensity-score",
    "nearest-neighbor-matching",
    "inverse-probability-weighting",
    "difference-in-differences",
    "interrupted-time-series",
    "regression-discontinuity",
    "synthetic-control",
    "dag-adjustment",
}

FIGURE_FAMILIES = {
    "dag",
    "propensity-overlap",
    "covariate-balance-love-plot",
    "matched-outcome",
    "weighted-outcome",
    "did-event-study",
    "its-segmented-trend",
    "rd-cutoff",
    "synthetic-control-gap",
    "placebo-distribution",
    "counterfactual-trajectory",
    "robustness-grid",
}


class CausalResearchStudioError(ValueError):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _finite(value: Any, label: str) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise CausalResearchStudioError(f"{label} must be numeric.") from exc
    if not math.isfinite(x):
        raise CausalResearchStudioError(f"{label} must be finite.")
    return x


def _string(value: Any, label: str, limit: int = 160) -> str:
    s = str(value or "").strip()
    if not s:
        raise CausalResearchStudioError(f"{label} is required.")
    return s[:limit]


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise CausalResearchStudioError("rows must be a non-empty array of row objects.")
    if len(rows) > MAX_ROWS:
        raise CausalResearchStudioError(f"rows cannot exceed {MAX_ROWS} records.")
    if not all(isinstance(row, dict) for row in rows):
        raise CausalResearchStudioError("Each row must be an object.")
    return copy.deepcopy(rows)


def _column(rows: list[dict[str, Any]], name: str) -> np.ndarray:
    values=[]
    for i,row in enumerate(rows):
        if name not in row:
            raise CausalResearchStudioError(f"Missing column {name!r} at row {i}.")
        values.append(_finite(row[name], f"{name}[{i}]"))
    return np.asarray(values,dtype=float)


def _binary(values: np.ndarray, label: str) -> np.ndarray:
    unique=set(np.unique(values).tolist())
    if not unique <= {0.0,1.0} or len(unique)<2:
        raise CausalResearchStudioError(f"{label} must contain both binary values 0 and 1.")
    return values.astype(float)


def _design_matrix(rows: list[dict[str, Any]], covariates: list[str]) -> tuple[np.ndarray,list[str]]:
    if len(covariates)>MAX_COVARIATES:
        raise CausalResearchStudioError(f"covariates cannot exceed {MAX_COVARIATES}.")
    columns=[np.ones(len(rows),dtype=float)]
    names=["intercept"]
    for cov in covariates:
        columns.append(_column(rows,cov)); names.append(cov)
    return np.column_stack(columns),names


def _ols(X: np.ndarray, y: np.ndarray) -> dict[str,Any]:
    if X.ndim!=2 or len(y)!=X.shape[0]:
        raise CausalResearchStudioError("OLS matrix dimensions are inconsistent.")
    if X.shape[0] <= X.shape[1]:
        raise CausalResearchStudioError("Not enough rows for the requested regression specification.")
    beta=np.linalg.pinv(X.T@X)@(X.T@y)
    fitted=X@beta
    resid=y-fitted
    dof=max(1,X.shape[0]-X.shape[1])
    sigma2=float(np.sum(resid**2)/dof)
    vcov=sigma2*np.linalg.pinv(X.T@X)
    se=np.sqrt(np.maximum(0,np.diag(vcov)))
    return {"beta":beta,"se":se,"fitted":fitted,"residuals":resid,"sigma2":sigma2,"dof":dof}


def _effect_row(estimate: float, se: float | None, metric: str="difference") -> dict[str,Any]:
    out={"estimate":float(estimate),"standard_error":None if se is None else float(se),"effect_metric":metric,"confidence_level":0.95}
    if se is not None and math.isfinite(se):
        out["ci_lower"]=float(estimate-1.959963984540054*se)
        out["ci_upper"]=float(estimate+1.959963984540054*se)
    else:
        out["ci_lower"]=None; out["ci_upper"]=None
    return out


def schema_info() -> dict[str,Any]:
    return {"ok":True,"schema":SCHEMA,"version":VERSION,"engine_version":ENGINE_VERSION,"snapshot_schema":SNAPSHOT_SCHEMA,
            "limits":{"rows":MAX_ROWS,"covariates":MAX_COVARIATES,"dag_nodes":MAX_DAG_NODES,"dag_edges":MAX_DAG_EDGES,"donors":MAX_DONORS,"placebo_tests":MAX_PLACEBO_TESTS}}


def catalog() -> dict[str,Any]:
    return {"ok":True,"version":VERSION,"method_families":sorted(METHOD_FAMILIES),"figure_families":sorted(FIGURE_FAMILIES),
            "governance_engine":"causal-inference-v0.67.0","human_review_required":True}


def manifest() -> dict[str,Any]:
    return {"ok":True,"status":"causal-research-studio-ready","version":VERSION,"engine_version":ENGINE_VERSION,
            "dag_workflows":True,"propensity_scores":True,"matching":True,"weighting":True,"difference_in_differences":True,
            "interrupted_time_series":True,"regression_discontinuity":True,"synthetic_control":True,"balance_diagnostics":True,
            "overlap_diagnostics":True,"robustness_planning":True,"placebo_planning":True,"counterfactual_reporting":True,
            "explicit_identification_assumptions_required":True,"human_causal_review_required":True,
            "automatic_causal_proof":False,"automatic_assumption_satisfaction":False,"automatic_method_selection":False,
            "automatic_covariate_selection":False,"automatic_model_selection":False,"automatic_publication":False,
            "automatic_core_submission":False,"scientific_validity_certified":False,"determine_truth":False}


def health() -> dict[str,Any]:
    return {**manifest(),"schema":SCHEMA,"method_family_count":len(METHOD_FAMILIES),"figure_family_count":len(FIGURE_FAMILIES)}


def normalize_study(payload: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(payload,dict): raise CausalResearchStudioError("study payload must be an object.")
    rows=_rows(payload)
    treatment=_string(payload.get("treatment"),"treatment")
    outcome=_string(payload.get("outcome"),"outcome")
    covariates=[str(x).strip() for x in (payload.get("covariates") or []) if str(x).strip()]
    if len(set(covariates))!=len(covariates): raise CausalResearchStudioError("covariates must be unique.")
    if treatment in covariates or outcome in covariates: raise CausalResearchStudioError("treatment/outcome cannot also be covariates.")
    _binary(_column(rows,treatment),"treatment")
    _column(rows,outcome)
    for c in covariates: _column(rows,c)
    study={"schema":SCHEMA,"version":VERSION,"id":str(payload.get("id") or "causal-study")[:160],"title":str(payload.get("title") or "Causal research study")[:400],
           "treatment":treatment,"outcome":outcome,"covariates":covariates,"row_count":len(rows),"rows":rows,
           "estimand":str(payload.get("estimand") or "researcher-declared")[:1000],"identification_assumptions":copy.deepcopy(payload.get("identification_assumptions") or []),
           "data_semantics":str(payload.get("data_semantics") or "researcher-provided-study-data")[:120],"automatic_causal_proof":False}
    study["study_hash"]=_hash({k:v for k,v in study.items() if k!="study_hash"})
    return {"ok":True,"version":VERSION,"study":study}


def normalize_dag(payload: dict[str,Any]) -> dict[str,Any]:
    nodes=payload.get("nodes") or [] ; edges=payload.get("edges") or []
    if not isinstance(nodes,list) or not isinstance(edges,list): raise CausalResearchStudioError("nodes and edges must be arrays.")
    if len(nodes)>MAX_DAG_NODES or len(edges)>MAX_DAG_EDGES: raise CausalResearchStudioError("DAG exceeds configured size limits.")
    out_nodes=[]; ids=set()
    for raw in nodes:
        if not isinstance(raw,dict): raise CausalResearchStudioError("Each DAG node must be an object.")
        node_id=_string(raw.get("id"),"node.id",120)
        if node_id in ids: raise CausalResearchStudioError("DAG node ids must be unique.")
        ids.add(node_id); out_nodes.append({"id":node_id,"label":str(raw.get("label") or node_id)[:240],"role":str(raw.get("role") or "variable")[:80]})
    out_edges=[]; graph={x:set() for x in ids}
    for raw in edges:
        if not isinstance(raw,dict): raise CausalResearchStudioError("Each DAG edge must be an object.")
        source=_string(raw.get("source"),"edge.source",120); target=_string(raw.get("target"),"edge.target",120)
        if source not in ids or target not in ids: raise CausalResearchStudioError("DAG edges must reference registered nodes.")
        if source==target: raise CausalResearchStudioError("DAG self-edges are not allowed.")
        graph[source].add(target); out_edges.append({"source":source,"target":target})
    visiting=set(); visited=set()
    def dfs(n):
        if n in visiting: raise CausalResearchStudioError("DAG contains a directed cycle.")
        if n in visited:return
        visiting.add(n)
        for nxt in graph[n]: dfs(nxt)
        visiting.remove(n); visited.add(n)
    for n in ids: dfs(n)
    dag={"schema":f"{SCHEMA}/dag","version":VERSION,"nodes":out_nodes,"edges":out_edges,"acyclic":True,"automatic_edge_inference":False,"automatic_causal_direction_inference":False}
    dag["dag_hash"]=_hash(dag)
    return {"ok":True,"dag":dag}


def dag_adjustment_plan(payload: dict[str,Any]) -> dict[str,Any]:
    dag=normalize_dag(payload.get("dag") if isinstance(payload.get("dag"),dict) else payload)["dag"]
    treatment=_string(payload.get("treatment"),"treatment"); outcome=_string(payload.get("outcome"),"outcome")
    node_ids={x["id"] for x in dag["nodes"]}
    if treatment not in node_ids or outcome not in node_ids: raise CausalResearchStudioError("treatment and outcome must be DAG nodes.")
    declared=[str(x) for x in (payload.get("adjustment_set") or [])]
    if any(x not in node_ids for x in declared): raise CausalResearchStudioError("adjustment_set contains an unknown DAG node.")
    return {"ok":True,"schema":f"{SCHEMA}/dag-adjustment-plan","version":VERSION,"dag_hash":dag["dag_hash"],"treatment":treatment,"outcome":outcome,
            "declared_adjustment_set":declared,"backdoor_sufficiency_certified":False,"automatic_adjustment_set_discovery":False,
            "review_required":True,"interpretation":"The Studio records and visualizes the researcher-declared adjustment set; it does not certify identification from the DAG."}


def fit_propensity(payload: dict[str,Any]) -> dict[str,Any]:
    study=normalize_study(payload)["study"]
    covariates=study["covariates"]
    if not covariates: raise CausalResearchStudioError("Propensity fitting requires at least one covariate.")
    X,names=_design_matrix(study["rows"],covariates); t=_binary(_column(study["rows"],study["treatment"]),"treatment")
    beta=np.zeros(X.shape[1],dtype=float)
    for _ in range(100):
        p=np.clip(expit(X@beta),1e-6,1-1e-6); w=p*(1-p)
        z=X@beta+(t-p)/w
        new=np.linalg.pinv(X.T@(w[:,None]*X))@(X.T@(w*z))
        if float(np.max(np.abs(new-beta)))<1e-9: beta=new; break
        beta=new
    scores=np.clip(expit(X@beta),1e-6,1-1e-6)
    return {"ok":True,"schema":f"{SCHEMA}/propensity","version":VERSION,"study_hash":study["study_hash"],"covariates":covariates,
            "coefficients":[{"term":n,"coefficient":float(b)} for n,b in zip(names,beta)],"scores":[float(x) for x in scores],
            "score_summary":{"min":float(scores.min()),"max":float(scores.max()),"treated_mean":float(scores[t==1].mean()),"comparison_mean":float(scores[t==0].mean())},
            "automatic_covariate_selection":False,"propensity_model_correctness_certified":False}


def _weighted_mean(y: np.ndarray,w: np.ndarray)->float:
    total=float(np.sum(w));
    if total<=0: raise CausalResearchStudioError("Weights must sum to a positive value.")
    return float(np.sum(w*y)/total)


def estimate_weighting(payload: dict[str,Any]) -> dict[str,Any]:
    study=normalize_study(payload)["study"]
    prop=fit_propensity(payload); p=np.asarray(prop["scores"],dtype=float)
    t=_binary(_column(study["rows"],study["treatment"]),"treatment"); y=_column(study["rows"],study["outcome"])
    estimand=str(payload.get("weighting_estimand") or "ATE").upper()
    if estimand=="ATE": weights=t/p+(1-t)/(1-p)
    elif estimand=="ATT": weights=t+(1-t)*p/(1-p)
    else: raise CausalResearchStudioError("weighting_estimand must be ATE or ATT.")
    wt=weights*t; wc=weights*(1-t)
    effect=_weighted_mean(y,wt)-_weighted_mean(y,wc)
    # conservative design-based approximation, reported as descriptive
    se=float(np.sqrt(np.var(y[t==1],ddof=1)/max(1,np.sum(t)) + np.var(y[t==0],ddof=1)/max(1,np.sum(1-t)))) if np.sum(t)>1 and np.sum(1-t)>1 else None
    return {"ok":True,"schema":f"{SCHEMA}/weighting-estimate","version":VERSION,"method":"inverse-probability-weighting","estimand":estimand,"effect":_effect_row(effect,se),
            "weights":[float(x) for x in weights],"effective_sample_size":float((weights.sum()**2)/np.sum(weights**2)),
            "identification_conditional_on_declared_assumptions":True,"causal_proof":False}


def estimate_matching(payload: dict[str,Any]) -> dict[str,Any]:
    study=normalize_study(payload)["study"]; prop=fit_propensity(payload); scores=np.asarray(prop["scores"])
    t=_binary(_column(study["rows"],study["treatment"]),"treatment"); y=_column(study["rows"],study["outcome"])
    treated=np.where(t==1)[0]; controls=list(np.where(t==0)[0]); replacement=bool(payload.get("replacement",False)); caliper=payload.get("caliper")
    caliper=None if caliper in (None,"") else float(caliper)
    pairs=[]; effects=[]
    for i in treated:
        if not controls: break
        j=min(controls,key=lambda k:(abs(scores[i]-scores[k]),k)); distance=float(abs(scores[i]-scores[j]))
        if caliper is not None and distance>caliper: continue
        pairs.append({"treated_index":int(i),"comparison_index":int(j),"propensity_distance":distance}); effects.append(float(y[i]-y[j]))
        if not replacement: controls.remove(j)
    if not effects: raise CausalResearchStudioError("No matched pairs were produced under the declared matching settings.")
    arr=np.asarray(effects); se=float(np.std(arr,ddof=1)/math.sqrt(len(arr))) if len(arr)>1 else None
    return {"ok":True,"schema":f"{SCHEMA}/matching-estimate","version":VERSION,"method":"nearest-neighbor-propensity-matching","effect":_effect_row(float(arr.mean()),se),
            "pair_count":len(pairs),"pairs":pairs,"replacement":replacement,"caliper":caliper,"automatic_match_quality_certification":False,"causal_proof":False}


def balance_report(payload: dict[str,Any]) -> dict[str,Any]:
    study=normalize_study(payload)["study"]; t=_binary(_column(study["rows"],study["treatment"]),"treatment")
    weights=np.asarray(payload.get("weights") or np.ones(len(t)),dtype=float)
    if len(weights)!=len(t): raise CausalResearchStudioError("weights length must equal row count.")
    rows=[]
    for cov in study["covariates"]:
        x=_column(study["rows"],cov); xt=x[t==1]; xc=x[t==0]; wt=weights[t==1]; wc=weights[t==0]
        mt=_weighted_mean(xt,wt); mc=_weighted_mean(xc,wc); pooled=math.sqrt(max(1e-15,(float(np.var(xt,ddof=1))+float(np.var(xc,ddof=1)))/2)) if len(xt)>1 and len(xc)>1 else 1.0
        rows.append({"covariate":cov,"treated_mean":mt,"comparison_mean":mc,"standardized_mean_difference":float((mt-mc)/pooled)})
    return {"ok":True,"schema":f"{SCHEMA}/balance","version":VERSION,"covariates":rows,"automatic_balance_pass_fail":False,"causal_identification_certified":False}


def overlap_report(payload: dict[str,Any]) -> dict[str,Any]:
    study=normalize_study(payload)["study"]; prop=fit_propensity(payload); p=np.asarray(prop["scores"]); t=_binary(_column(study["rows"],study["treatment"]),"treatment")
    pt=p[t==1]; pc=p[t==0]; lo=max(float(pt.min()),float(pc.min())); hi=min(float(pt.max()),float(pc.max()))
    in_overlap=(p>=lo)&(p<=hi)
    return {"ok":True,"schema":f"{SCHEMA}/overlap","version":VERSION,"common_support":{"lower":lo,"upper":hi,"row_fraction":float(np.mean(in_overlap))},
            "treated_range":[float(pt.min()),float(pt.max())],"comparison_range":[float(pc.min()),float(pc.max())],"overlap_sufficient_certified":False}


def estimate_did(payload: dict[str,Any]) -> dict[str,Any]:
    rows=_rows(payload); outcome=_string(payload.get("outcome"),"outcome"); treated_name=_string(payload.get("treated"),"treated"); post_name=_string(payload.get("post"),"post")
    y=_column(rows,outcome); treated=_binary(_column(rows,treated_name),"treated"); post=_binary(_column(rows,post_name),"post")
    X=np.column_stack([np.ones(len(rows)),treated,post,treated*post]); fit=_ols(X,y)
    return {"ok":True,"schema":f"{SCHEMA}/did-estimate","version":VERSION,"method":"difference-in-differences","effect":_effect_row(float(fit['beta'][3]),float(fit['se'][3])),
            "parallel_trends_assumption_required":True,"parallel_trends_certified":False,"no_anticipation_certified":False,"causal_proof":False}


def estimate_its(payload: dict[str,Any]) -> dict[str,Any]:
    rows=_rows(payload); outcome=_string(payload.get("outcome"),"outcome"); time_name=_string(payload.get("time"),"time"); post_name=_string(payload.get("post"),"post")
    y=_column(rows,outcome); time=_column(rows,time_name); post=_binary(_column(rows,post_name),"post")
    first_post=float(np.min(time[post==1])); time_after=np.maximum(0,time-first_post)*post
    X=np.column_stack([np.ones(len(rows)),time,post,time_after]); fit=_ols(X,y)
    return {"ok":True,"schema":f"{SCHEMA}/its-estimate","version":VERSION,"method":"interrupted-time-series","level_change":_effect_row(float(fit['beta'][2]),float(fit['se'][2]),"level-change"),
            "slope_change":_effect_row(float(fit['beta'][3]),float(fit['se'][3]),"slope-change"),"stable_pretrend_certified":False,"no_concurrent_intervention_certified":False,"causal_proof":False}


def estimate_rd(payload: dict[str,Any]) -> dict[str,Any]:
    rows=_rows(payload); outcome=_string(payload.get("outcome"),"outcome"); running_name=_string(payload.get("running"),"running"); cutoff=_finite(payload.get("cutoff"),"cutoff"); bandwidth=float(payload.get("bandwidth") or 1.0)
    if bandwidth<=0: raise CausalResearchStudioError("bandwidth must be positive.")
    y=_column(rows,outcome); running=_column(rows,running_name); centered=running-cutoff; mask=np.abs(centered)<=bandwidth
    if int(mask.sum())<8: raise CausalResearchStudioError("Regression discontinuity requires at least 8 rows inside the bandwidth.")
    c=centered[mask]; yy=y[mask]; treated=(c>=0).astype(float); X=np.column_stack([np.ones(len(c)),c,treated,c*treated]); fit=_ols(X,yy)
    return {"ok":True,"schema":f"{SCHEMA}/rd-estimate","version":VERSION,"method":"local-linear-regression-discontinuity","cutoff":cutoff,"bandwidth":bandwidth,"rows_in_bandwidth":int(mask.sum()),
            "effect":_effect_row(float(fit['beta'][2]),float(fit['se'][2])),"continuity_at_cutoff_certified":False,"no_precise_manipulation_certified":False,"causal_proof":False}


def estimate_synthetic_control(payload: dict[str,Any]) -> dict[str,Any]:
    treated_pre=np.asarray(payload.get("treated_pre") or [],dtype=float); treated_post=np.asarray(payload.get("treated_post") or [],dtype=float)
    donors_pre=np.asarray(payload.get("donors_pre") or [],dtype=float); donors_post=np.asarray(payload.get("donors_post") or [],dtype=float)
    if treated_pre.ndim!=1 or treated_post.ndim!=1 or donors_pre.ndim!=2 or donors_post.ndim!=2: raise CausalResearchStudioError("Synthetic control inputs have invalid dimensions.")
    if donors_pre.shape[0]!=len(treated_pre) or donors_post.shape[0]!=len(treated_post) or donors_pre.shape[1]!=donors_post.shape[1]: raise CausalResearchStudioError("Synthetic control input dimensions do not align.")
    if donors_pre.shape[1]<2 or donors_pre.shape[1]>MAX_DONORS: raise CausalResearchStudioError("Synthetic control requires 2 to 128 donor units.")
    n=donors_pre.shape[1]; objective=lambda w: float(np.sum((treated_pre-donors_pre@w)**2))
    res=minimize(objective,np.ones(n)/n,bounds=[(0,1)]*n,constraints={"type":"eq","fun":lambda w:float(np.sum(w)-1)},method="SLSQP")
    if not res.success: raise CausalResearchStudioError("Synthetic control weight optimization did not converge.")
    w=np.asarray(res.x); synth_pre=donors_pre@w; synth_post=donors_post@w; gaps=treated_post-synth_post
    return {"ok":True,"schema":f"{SCHEMA}/synthetic-control-estimate","version":VERSION,"method":"synthetic-control","donor_weights":[float(x) for x in w],
            "pre_rmse":float(np.sqrt(np.mean((treated_pre-synth_pre)**2))),"post_gaps":[float(x) for x in gaps],"average_post_gap":float(np.mean(gaps)),
            "donor_pool_exchangeability_certified":False,"intervention_isolation_certified":False,"causal_proof":False}


def robustness_plan(payload: dict[str,Any]) -> dict[str,Any]:
    analyses=payload.get("analyses") or ["alternative-adjustment-set","trim-overlap","caliper-variation","bandwidth-variation","placebo-outcome","placebo-time","negative-control"]
    if not isinstance(analyses,list): raise CausalResearchStudioError("analyses must be an array.")
    out={"ok":True,"schema":f"{SCHEMA}/robustness-plan","version":VERSION,"analyses":[str(x)[:120] for x in analyses[:64]],"automatic_execution":False,"robustness_certified":False}
    out["plan_hash"]=_hash(out); return out


def placebo_plan(payload: dict[str,Any]) -> dict[str,Any]:
    tests=payload.get("tests") or [{"type":"pre-period-placebo"},{"type":"placebo-outcome"},{"type":"placebo-exposure"}]
    if not isinstance(tests,list) or len(tests)>MAX_PLACEBO_TESTS: raise CausalResearchStudioError("tests must be an array within the configured limit.")
    out={"ok":True,"schema":f"{SCHEMA}/placebo-plan","version":VERSION,"tests":copy.deepcopy(tests),"automatic_execution":False,"placebo_pass_fail_certified":False}
    out["plan_hash"]=_hash(out); return out


def counterfactual_report(payload: dict[str,Any]) -> dict[str,Any]:
    observed=[float(x) for x in (payload.get("observed") or [])]; counterfactual=[float(x) for x in (payload.get("counterfactual") or [])]
    if not observed or len(observed)!=len(counterfactual): raise CausalResearchStudioError("observed and counterfactual must be equal-length non-empty arrays.")
    gaps=[a-b for a,b in zip(observed,counterfactual)]
    return {"ok":True,"schema":f"{SCHEMA}/counterfactual-report","version":VERSION,"observed":observed,"counterfactual":counterfactual,"gaps":gaps,"average_gap":float(np.mean(gaps)),
            "counterfactual_is_model_based":True,"counterfactual_observed":False,"causal_proof":False}


def build_visualization_plan(payload: dict[str,Any]) -> dict[str,Any]:
    figures=[{"family":x,"role":"causal-diagnostic-or-estimate","automatic_causal_interpretation":False} for x in sorted(FIGURE_FAMILIES)]
    out={"ok":True,"schema":f"{SCHEMA}/visualization-plan","version":VERSION,"figures":figures,"automatic_render":False,"causal_proof":False}; out["plan_hash"]=_hash(out); return out


def build_studio(payload: dict[str,Any]) -> dict[str,Any]:
    design=payload.get("governance_design")
    governance=None
    if isinstance(design,dict):
        try: governance=governance_normalize_design(design)
        except CausalInferenceError as exc: raise CausalResearchStudioError(str(exc)) from exc
    out={"ok":True,"schema":f"{SCHEMA}/studio","version":VERSION,"study_id":str(payload.get("study_id") or "causal-study")[:160],"governance_design":governance,
         "dag":copy.deepcopy(payload.get("dag")),"declared_method":str(payload.get("method") or "researcher-selected")[:120],"human_causal_review_required":True,
         "automatic_method_selection":False,"automatic_causal_proof":False,"visualization_plan":build_visualization_plan({})}
    out["studio_hash"]=_hash(out); return out


def build_snapshot(payload: dict[str,Any]) -> dict[str,Any]:
    studio=payload.get("studio") if isinstance(payload.get("studio"),dict) else payload
    out={"ok":True,"schema":SNAPSHOT_SCHEMA,"version":VERSION,"studio":copy.deepcopy(studio),"automatic_persistence":False,"scientific_validity_certified":False}
    out["snapshot_hash"]=_hash(out); return out


def build_reproduction_plan(payload: dict[str,Any]) -> dict[str,Any]:
    out={"ok":True,"schema":f"{SCHEMA}/reproduction-plan","version":VERSION,"required_refs":copy.deepcopy(payload.get("required_refs") or []),"environment_ref":payload.get("environment_ref"),
         "study_hash":payload.get("study_hash"),"dag_hash":payload.get("dag_hash"),"method":payload.get("method"),"automatic_execution":False}; out["plan_hash"]=_hash(out); return out


def build_export_plan(payload: dict[str,Any]) -> dict[str,Any]:
    formats=[str(x).lower() for x in (payload.get("formats") or ["json","csv","svg","pdf"])]
    out={"ok":True,"schema":f"{SCHEMA}/export-plan","version":VERSION,"formats":formats,"include_assumptions":True,"include_diagnostics":True,"include_provenance":True,
         "include_counterfactual_semantics":True,"automatic_file_write":False,"automatic_publication":False}; out["plan_hash"]=_hash(out); return out


def build_core_object_plan(payload: dict[str,Any]) -> dict[str,Any]:
    session_id=_string(payload.get("session_id"),"session_id")
    analysis_id=_string(payload.get("analysis_id") or payload.get("study_id") or "causal-analysis","analysis_id")
    out={"ok":True,"schema":f"{SCHEMA}/core-object-plan","version":VERSION,"session_id":session_id,"analysis_id":analysis_id,
         "objects":[{"object_type":"research-analysis","ref":analysis_id},{"object_type":"causal-design","ref":str(payload.get("design_ref") or f"{analysis_id}:design")},{"object_type":"validation","ref":str(payload.get("validation_ref") or f"{analysis_id}:diagnostics")}],
         "automatic_core_submission":False,"automatic_claim_promotion":False,"causal_proof":False}; out["plan_hash"]=_hash(out); return out


def build_execution_lineage_plan(payload: dict[str,Any]) -> dict[str,Any]:
    session_id=_string(payload.get("session_id"),"session_id"); analysis_id=_string(payload.get("analysis_id") or "causal-analysis","analysis_id")
    out={"ok":True,"schema":f"{SCHEMA}/execution-lineage-plan","version":VERSION,"session_id":session_id,"analysis_id":analysis_id,"method":str(payload.get("method") or "researcher-selected")[:120],
         "input_refs":copy.deepcopy(payload.get("input_refs") or []),"output_refs":copy.deepcopy(payload.get("output_refs") or []),"environment_ref":payload.get("environment_ref"),"automatic_execution":False,"automatic_core_submission":False}; out["plan_hash"]=_hash(out); return out


def governance_review_report(payload: dict[str,Any]) -> dict[str,Any]:
    try:
        result=governance_evaluate(payload)
    except CausalInferenceError as exc:
        raise CausalResearchStudioError(str(exc)) from exc
    return {"ok":True,"schema":f"{SCHEMA}/governance-review","version":VERSION,"governance":result,"automatic_causal_proof":False,"human_review_required":True}


def interpretation_boundaries_report(payload: dict[str,Any] | None=None) -> dict[str,Any]:
    p=governance_policies()
    return {"ok":True,"schema":f"{SCHEMA}/interpretation-boundaries","version":VERSION,"boundaries":[
        "Causal estimates are conditional on a declared design and identification assumptions.",
        "DAG edges and adjustment sets are researcher-declared; the Studio does not prove causal direction or identification.",
        "Balance and overlap diagnostics are descriptive checks, not proof that exchangeability holds.",
        "Parallel trends, continuity, stable pretrend, and no-concurrent-intervention assumptions are not automatically certified.",
        "Counterfactuals and synthetic controls are modeled constructs, not observed alternate histories.",
        "Sensitivity and placebo analyses can reveal fragility but do not prove absence of bias or confounding.",
        "Human causal review remains required before bounded causal language is used.",
    ],"governance_policies":p,"automatic_causal_proof":False,"automatic_assumption_satisfaction":False,"scientific_validity_certified":False,"determine_truth":False}
