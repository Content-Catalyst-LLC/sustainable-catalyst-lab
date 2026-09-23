from __future__ import annotations

import copy
import json
import math
from hashlib import sha256
from typing import Any

import numpy as np
from scipy.optimize import brentq
from scipy.stats import f as f_dist
from scipy.stats import ncf, norm

VERSION = "0.128.0"
ENGINE_VERSION = "9.0.0"
SCHEMA = "sc-lab-experimental-design-power-analysis/0.128.0"
SNAPSHOT_SCHEMA = "sc-lab-experimental-design-snapshot/0.128.0"
MAX_GROUPS = 64
MAX_FACTORS = 12
MAX_LEVELS_PER_FACTOR = 32
MAX_SIMULATIONS = 200_000
MAX_TOTAL_SAMPLE = 10_000_000

METHOD_FAMILIES = {
    "one-sample-mean-power", "two-sample-mean-power", "paired-mean-power",
    "one-proportion-power", "two-proportion-power", "one-way-anova-power",
    "factorial-design", "blocked-randomization", "cluster-design-effect",
    "precision-based-sample-size", "simulation-based-power", "sequential-design-plan",
    "adaptive-reestimation-plan", "multiple-testing-plan", "randomization-schedule",
}

FIGURE_FAMILIES = {
    "power-curve", "sample-size-curve", "effect-size-power", "precision-width-curve",
    "anova-power", "factorial-cell-map", "randomization-allocation", "block-balance",
    "cluster-design-effect", "simulation-power-convergence", "sequential-boundary-plan",
    "adaptive-reestimation-flow", "multiplicity-alpha-allocation", "design-assumption-panel",
    "operating-characteristics-table", "sensitivity-to-assumptions",
}


class ExperimentalDesignError(ValueError):
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
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ExperimentalDesignError(f"{label} must be numeric.") from exc
    if not math.isfinite(out):
        raise ExperimentalDesignError(f"{label} must be finite.")
    return out


def _integer(value: Any, label: str, minimum: int = 1, maximum: int | None = None) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ExperimentalDesignError(f"{label} must be an integer.") from exc
    if out < minimum or (maximum is not None and out > maximum):
        suffix = f" and <= {maximum}" if maximum is not None else ""
        raise ExperimentalDesignError(f"{label} must be >= {minimum}{suffix}.")
    return out


def _prob(value: Any, label: str, open_interval: bool = True) -> float:
    out = _finite(value, label)
    lo_ok = out > 0 if open_interval else out >= 0
    hi_ok = out < 1 if open_interval else out <= 1
    if not (lo_ok and hi_ok):
        b = "between 0 and 1 exclusive" if open_interval else "between 0 and 1 inclusive"
        raise ExperimentalDesignError(f"{label} must be {b}.")
    return out


def _alternative(payload: dict[str, Any]) -> str:
    alt = str(payload.get("alternative") or "two-sided").strip().lower()
    aliases = {"two_sided": "two-sided", "two sided": "two-sided", "greater": "one-sided", "less": "one-sided", "one_sided": "one-sided"}
    alt = aliases.get(alt, alt)
    if alt not in {"two-sided", "one-sided"}:
        raise ExperimentalDesignError("alternative must be 'two-sided' or 'one-sided'.")
    return alt


def _zcrit(alpha: float, alt: str) -> float:
    return float(norm.ppf(1 - alpha / 2)) if alt == "two-sided" else float(norm.ppf(1 - alpha))


def _normal_power(noncentrality: float, alpha: float, alt: str) -> float:
    z = _zcrit(alpha, alt)
    mu = abs(float(noncentrality))
    if alt == "one-sided":
        return float(norm.cdf(mu - z))
    return float(norm.cdf(mu - z) + norm.cdf(-mu - z))


def _solve_integer(target_power: float, power_fn, minimum: int = 2, maximum: int = MAX_TOTAL_SAMPLE) -> int:
    if power_fn(maximum) < target_power:
        raise ExperimentalDesignError("target power is not reached within the configured maximum sample size.", 422)
    lo, hi = minimum, maximum
    while lo < hi:
        mid = (lo + hi) // 2
        if power_fn(mid) >= target_power:
            hi = mid
        else:
            lo = mid + 1
    return lo


def schema_info() -> dict[str, Any]:
    return {"ok": True, "schema": SCHEMA, "version": VERSION, "engine_version": ENGINE_VERSION,
            "snapshot_schema": SNAPSHOT_SCHEMA,
            "limits": {"groups": MAX_GROUPS, "factors": MAX_FACTORS, "levels_per_factor": MAX_LEVELS_PER_FACTOR,
                       "simulations": MAX_SIMULATIONS, "total_sample": MAX_TOTAL_SAMPLE}}


def catalog() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "method_families": sorted(METHOD_FAMILIES),
            "figure_families": sorted(FIGURE_FAMILIES), "automatic_effect_size_selection": False,
            "automatic_design_selection": False, "automatic_significance_claims": False,
            "automatic_power_guarantee": False}


def manifest() -> dict[str, Any]:
    return {"ok": True, "status": "experimental-design-power-analysis-ready", "version": VERSION,
            "engine_version": ENGINE_VERSION, "analytical_power": True, "simulation_power": True,
            "factorial_design": True, "blocked_randomization": True, "cluster_design": True,
            "sequential_planning": True, "adaptive_planning": True, "precision_planning": True,
            "automatic_effect_size_selection": False, "automatic_design_selection": False,
            "automatic_sample_size_guarantee": False, "automatic_significance_claims": False,
            "automatic_scientific_validity_certification": False, "automatic_core_submission": False,
            "determine_truth": False}


def health() -> dict[str, Any]:
    return {**manifest(), "schema": SCHEMA, "method_family_count": len(METHOD_FAMILIES),
            "figure_family_count": len(FIGURE_FAMILIES)}


def normalize_design(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ExperimentalDesignError("payload must be an object.")
    alpha = _prob(payload.get("alpha", 0.05), "alpha")
    target = _prob(payload.get("target_power", 0.8), "target_power")
    alt = _alternative(payload)
    design = {
        "schema": SCHEMA, "version": VERSION, "id": str(payload.get("id") or "experimental-design")[:180],
        "title": str(payload.get("title") or "Experimental design")[:400], "alpha": alpha,
        "target_power": target, "alternative": alt,
        "effect_size_source": str(payload.get("effect_size_source") or "researcher-declared")[:180],
        "variance_source": str(payload.get("variance_source") or "researcher-declared")[:180],
        "assumptions": copy.deepcopy(payload.get("assumptions") or {}),
        "provenance": copy.deepcopy(payload.get("provenance") or {}),
        "boundaries": {"effect_size_inferred": False, "variance_inferred": False, "power_guaranteed": False,
                       "automatic_significance_claim": False, "automatic_design_selection": False},
    }
    design["design_hash"] = _hash(design)
    return {"ok": True, "version": VERSION, "design": design}


def standardized_effect_report(payload: dict[str, Any]) -> dict[str, Any]:
    kind = str(payload.get("kind") or "mean-difference").lower()
    if kind == "mean-difference":
        diff = _finite(payload.get("difference"), "difference")
        sd = _finite(payload.get("sd"), "sd")
        if sd <= 0: raise ExperimentalDesignError("sd must be > 0.")
        effect = diff / sd; label = "cohen_d"
    elif kind == "proportion-difference":
        p0 = _prob(payload.get("p0"), "p0", False); p1 = _prob(payload.get("p1"), "p1", False)
        effect = 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p0))); label = "cohen_h"
    elif kind == "anova":
        means = payload.get("means"); weights = payload.get("weights")
        if not isinstance(means, list) or len(means) < 2: raise ExperimentalDesignError("means must contain at least two group means.")
        m = np.asarray([_finite(x, "mean") for x in means], dtype=float)
        if weights is None: w = np.repeat(1 / len(m), len(m))
        else:
            if not isinstance(weights, list) or len(weights) != len(m): raise ExperimentalDesignError("weights must match means.")
            w = np.asarray([_finite(x, "weight") for x in weights], dtype=float)
            if np.any(w < 0) or w.sum() <= 0: raise ExperimentalDesignError("weights must be non-negative with positive sum.")
            w = w / w.sum()
        sd = _finite(payload.get("sd"), "sd")
        if sd <= 0: raise ExperimentalDesignError("sd must be > 0.")
        grand = float(np.sum(w * m)); effect = math.sqrt(float(np.sum(w * (m - grand) ** 2))) / sd; label = "cohen_f"
    else:
        raise ExperimentalDesignError("kind must be mean-difference, proportion-difference, or anova.")
    return {"ok": True, "version": VERSION, "kind": kind, "metric": label, "effect_size": float(effect),
            "automatic_magnitude_label": False, "interpretation": "Effect size is standardized from declared inputs; practical importance remains domain-specific."}


def _mean_plan(payload: dict[str, Any], groups: int) -> dict[str, Any]:
    alpha = _prob(payload.get("alpha", 0.05), "alpha"); target = _prob(payload.get("target_power", 0.8), "target_power"); alt = _alternative(payload)
    d = abs(_finite(payload.get("effect_size"), "effect_size"))
    if d <= 0: raise ExperimentalDesignError("effect_size must be non-zero.")
    n = payload.get("n") or payload.get("n_per_group")
    factor = 1.0 if groups == 1 else 1 / math.sqrt(2)
    def power_fn(nn: int) -> float:
        ncp = d * math.sqrt(nn) if groups == 1 else d * math.sqrt(nn / 2)
        return _normal_power(ncp, alpha, alt)
    if n is None:
        n_int = _solve_integer(target, power_fn, minimum=2)
        achieved = power_fn(n_int)
    else:
        n_int = _integer(n, "n" if groups == 1 else "n_per_group", 2, MAX_TOTAL_SAMPLE)
        achieved = power_fn(n_int)
    return {"ok": True, "version": VERSION, "effect_size": d, "alpha": alpha, "alternative": alt,
            "n": n_int if groups == 1 else None, "n_per_group": n_int if groups == 2 else None,
            "total_n": n_int if groups == 1 else 2 * n_int, "achieved_power": achieved,
            "target_power": target, "method": "normal-approximation-standardized-mean",
            "power_is_guaranteed": False, "automatic_effect_size_selection": False}


def one_sample_mean_power(payload: dict[str, Any]) -> dict[str, Any]: return _mean_plan(payload, 1)
def two_sample_mean_power(payload: dict[str, Any]) -> dict[str, Any]: return _mean_plan(payload, 2)
def paired_mean_power(payload: dict[str, Any]) -> dict[str, Any]:
    out = _mean_plan(payload, 1); out["method"] = "normal-approximation-standardized-paired-difference"; out["pairs"] = out.pop("n"); out["total_measurements"] = 2 * out["pairs"]; return out


def one_proportion_power(payload: dict[str, Any]) -> dict[str, Any]:
    p0 = _prob(payload.get("p0"), "p0", False); p1 = _prob(payload.get("p1"), "p1", False)
    h = abs(2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p0))))
    return {**_mean_plan({**payload, "effect_size": h}, 1), "p0": p0, "p1": p1, "cohen_h": h, "method": "normal-approximation-one-proportion"}


def two_proportion_power(payload: dict[str, Any]) -> dict[str, Any]:
    p1 = _prob(payload.get("p1"), "p1", False); p2 = _prob(payload.get("p2"), "p2", False)
    h = abs(2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2))))
    return {**_mean_plan({**payload, "effect_size": h}, 2), "p1": p1, "p2": p2, "cohen_h": h, "method": "normal-approximation-two-proportion"}


def one_way_anova_power(payload: dict[str, Any]) -> dict[str, Any]:
    k = _integer(payload.get("groups"), "groups", 2, MAX_GROUPS)
    f = abs(_finite(payload.get("effect_size"), "effect_size")); alpha = _prob(payload.get("alpha", 0.05), "alpha"); target = _prob(payload.get("target_power", 0.8), "target_power")
    if f <= 0: raise ExperimentalDesignError("effect_size must be > 0.")
    def power_total(n_total: int) -> float:
        if n_total <= k: return 0.0
        df1, df2 = k - 1, n_total - k; critical = f_dist.ppf(1 - alpha, df1, df2); lam = n_total * f * f
        return float(1 - ncf.cdf(critical, df1, df2, lam))
    n_total_in = payload.get("total_n")
    if n_total_in is None:
        total = _solve_integer(target, power_total, minimum=k + 2)
        total = int(math.ceil(total / k) * k)
    else: total = _integer(n_total_in, "total_n", k + 2, MAX_TOTAL_SAMPLE)
    return {"ok": True, "version": VERSION, "groups": k, "effect_size": f, "alpha": alpha, "target_power": target,
            "total_n": total, "n_per_group_balanced": int(math.ceil(total / k)), "achieved_power": power_total(total),
            "method": "noncentral-f-one-way-anova", "balanced_design_assumed": True, "automatic_group_selection": False,
            "power_is_guaranteed": False}


def factorial_design_plan(payload: dict[str, Any]) -> dict[str, Any]:
    factors = payload.get("factors")
    if not isinstance(factors, list) or not factors or len(factors) > MAX_FACTORS: raise ExperimentalDesignError(f"factors must contain 1..{MAX_FACTORS} factor definitions.")
    normed=[]; cells=1
    for i,f in enumerate(factors):
        if not isinstance(f,dict): raise ExperimentalDesignError("each factor must be an object.")
        levels=f.get("levels");
        if not isinstance(levels,list) or len(levels)<2 or len(levels)>MAX_LEVELS_PER_FACTOR: raise ExperimentalDesignError(f"factor {i} levels must contain 2..{MAX_LEVELS_PER_FACTOR} entries.")
        name=str(f.get("name") or f"factor_{i+1}"); normed.append({"name":name,"levels":[str(x) for x in levels]}); cells*=len(levels)
    reps=_integer(payload.get("replicates_per_cell",1),"replicates_per_cell",1,MAX_TOTAL_SAMPLE)
    total=cells*reps
    if total>MAX_TOTAL_SAMPLE: raise ExperimentalDesignError("factorial design exceeds maximum total sample size.",413)
    return {"ok":True,"version":VERSION,"factors":normed,"cell_count":cells,"replicates_per_cell":reps,"total_n":total,
            "full_factorial":True,"automatic_aliasing_resolution":False,"automatic_effect_hierarchy_claim":False,
            "interpretation":"A full-factorial allocation plan; estimability depends on the declared model and replication structure."}


def blocked_randomization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    groups=payload.get("groups") or ["control","treatment"]
    if not isinstance(groups,list) or len(groups)<2 or len(groups)>MAX_GROUPS: raise ExperimentalDesignError("groups must contain 2..64 labels.")
    block_size=_integer(payload.get("block_size",len(groups)),"block_size",len(groups),4096)
    if block_size % len(groups): raise ExperimentalDesignError("block_size must be divisible by the number of groups for equal blocked allocation.")
    blocks=_integer(payload.get("blocks",1),"blocks",1,MAX_TOTAL_SAMPLE)
    per=block_size//len(groups)
    return {"ok":True,"version":VERSION,"groups":[str(x) for x in groups],"block_size":block_size,"blocks":blocks,
            "allocation_per_group_per_block":per,"total_n":block_size*blocks,"automatic_randomization_execution":False,
            "concealment_guaranteed":False,"balance_guaranteed_only_within_completed_blocks":True}


def cluster_design_effect(payload: dict[str, Any]) -> dict[str, Any]:
    m=_finite(payload.get("mean_cluster_size"),"mean_cluster_size"); icc=_prob(payload.get("icc"),"icc",False)
    if m < 1: raise ExperimentalDesignError("mean_cluster_size must be >= 1.")
    cv=_finite(payload.get("cluster_size_cv",0.0),"cluster_size_cv")
    if cv<0: raise ExperimentalDesignError("cluster_size_cv must be >= 0.")
    de=1 + ((1+cv*cv)*m - 1)*icc
    base=_integer(payload.get("individual_level_n",2),"individual_level_n",2,MAX_TOTAL_SAMPLE)
    adjusted=int(math.ceil(base*de)); clusters=int(math.ceil(adjusted/m))
    return {"ok":True,"version":VERSION,"mean_cluster_size":m,"icc":icc,"cluster_size_cv":cv,"design_effect":de,
            "individual_level_n":base,"adjusted_individual_n":adjusted,"approximate_cluster_count":clusters,
            "method":"unequal-cluster-size-design-effect-approximation","automatic_icc_estimation":False,"power_is_guaranteed":False}


def precision_sample_size(payload: dict[str, Any]) -> dict[str, Any]:
    confidence=_prob(payload.get("confidence",0.95),"confidence"); half=_finite(payload.get("half_width"),"half_width")
    if half<=0: raise ExperimentalDesignError("half_width must be > 0.")
    z=float(norm.ppf((1+confidence)/2)); kind=str(payload.get("kind") or "mean").lower()
    if kind=="mean":
        sd=_finite(payload.get("sd"),"sd");
        if sd<=0: raise ExperimentalDesignError("sd must be > 0.")
        n=int(math.ceil((z*sd/half)**2)); assumption={"sd":sd}
    elif kind=="proportion":
        p=_prob(payload.get("p",0.5),"p",False); n=int(math.ceil(z*z*p*(1-p)/(half*half))); assumption={"p":p}
    else: raise ExperimentalDesignError("kind must be mean or proportion.")
    n=max(2,n)
    return {"ok":True,"version":VERSION,"kind":kind,"confidence":confidence,"half_width":half,"sample_size":n,
            "assumptions":assumption,"finite_population_correction_applied":False,"precision_guaranteed":False}


def simulation_power(payload: dict[str, Any]) -> dict[str, Any]:
    n_sim=_integer(payload.get("simulations",10000),"simulations",100,MAX_SIMULATIONS); seed=_integer(payload.get("seed",1729),"seed",0,2**32-1)
    alpha=_prob(payload.get("alpha",0.05),"alpha"); effect=_finite(payload.get("effect_size"),"effect_size"); n=_integer(payload.get("n",30),"n",2,MAX_TOTAL_SAMPLE)
    noise_sd=_finite(payload.get("noise_sd",1.0),"noise_sd")
    if noise_sd<=0: raise ExperimentalDesignError("noise_sd must be > 0.")
    rng=np.random.default_rng(seed); zcrit=_zcrit(alpha,_alternative(payload)); stats=effect*math.sqrt(n)/noise_sd + rng.normal(size=n_sim)
    if _alternative(payload)=="two-sided": rejected=np.abs(stats)>zcrit
    else: rejected=stats>zcrit
    phat=float(np.mean(rejected)); se=math.sqrt(max(phat*(1-phat),0)/n_sim)
    return {"ok":True,"version":VERSION,"simulations":n_sim,"seed":seed,"sample_size":n,"effect_size":effect,"noise_sd":noise_sd,
            "estimated_power":phat,"monte_carlo_se":se,"mc_interval_95":[max(0.0,phat-1.96*se),min(1.0,phat+1.96*se)],
            "method":"seeded-normal-test-operating-characteristic","power_is_estimated_not_guaranteed":True,"automatic_design_selection":False}


def sequential_design_plan(payload: dict[str, Any]) -> dict[str, Any]:
    looks=_integer(payload.get("looks",4),"looks",2,100); alpha=_prob(payload.get("alpha",0.05),"alpha"); spending=str(payload.get("spending") or "obrien-fleming").lower()
    info=np.asarray(payload.get("information_fractions") or np.linspace(1/looks,1,looks),dtype=float)
    if len(info)!=looks or np.any(info<=0) or np.any(info>1) or np.any(np.diff(info)<=0): raise ExperimentalDesignError("information_fractions must be strictly increasing values in (0,1].")
    if abs(info[-1]-1)>1e-9: raise ExperimentalDesignError("final information fraction must equal 1.")
    if spending in {"obrien-fleming","o'brien-fleming","obf"}:
        z_final=norm.ppf(1-alpha/2); cumulative=[float(2*(1-norm.cdf(z_final/math.sqrt(t)))) for t in info]
    elif spending in {"pocock","equal"}:
        cumulative=[float(alpha*t) for t in info]
    else: raise ExperimentalDesignError("spending must be obrien-fleming or pocock/equal.")
    cumulative=np.maximum.accumulate(np.minimum(cumulative,alpha)).tolist(); incremental=[cumulative[0]]+[cumulative[i]-cumulative[i-1] for i in range(1,looks)]
    return {"ok":True,"version":VERSION,"looks":looks,"alpha":alpha,"spending":spending,"information_fractions":info.tolist(),
            "cumulative_alpha":cumulative,"incremental_alpha":incremental,"automatic_stopping":False,"boundary_crossing_is_not_scientific_truth":True}


def adaptive_reestimation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    initial=_integer(payload.get("initial_n"),"initial_n",2,MAX_TOTAL_SAMPLE); review=_integer(payload.get("review_n",max(2,initial//2)),"review_n",2,initial)
    max_n=_integer(payload.get("max_n",initial*2),"max_n",initial,MAX_TOTAL_SAMPLE); target=_prob(payload.get("target_power",0.8),"target_power")
    rule=str(payload.get("rule") or "variance-only-blinded")
    return {"ok":True,"version":VERSION,"initial_n":initial,"review_n":review,"max_n":max_n,"target_power":target,"rule":rule,
            "automatic_reestimation":False,"automatic_sample_size_change":False,"type_i_error_preservation_not_certified":True,
            "required_review":["pre-specify adaptation rule","record observed nuisance estimate","recompute under declared method","human approval before changing target N"]}


def multiple_testing_plan(payload: dict[str, Any]) -> dict[str, Any]:
    hypotheses=payload.get("hypotheses")
    if not isinstance(hypotheses,list) or not hypotheses: raise ExperimentalDesignError("hypotheses must be a non-empty array.")
    alpha=_prob(payload.get("alpha",0.05),"alpha"); method=str(payload.get("method") or "bonferroni").lower(); m=len(hypotheses)
    if method=="bonferroni": alloc=[alpha/m]*m
    elif method=="holm": alloc=[alpha/(m-i) for i in range(m)]
    elif method in {"equal","fixed"}: alloc=[alpha/m]*m
    else: raise ExperimentalDesignError("method must be bonferroni, holm, or equal.")
    return {"ok":True,"version":VERSION,"method":method,"family_alpha":alpha,"hypotheses":[str(x) for x in hypotheses],
            "nominal_alpha_sequence":alloc,"automatic_hypothesis_ordering":False,"automatic_significance_claims":False,
            "interpretation":"Holm values are step-down critical levels and require a declared p-value ordering at analysis time." if method=="holm" else "Declared per-hypothesis alpha allocation."}


def randomization_schedule(payload: dict[str, Any]) -> dict[str, Any]:
    groups=payload.get("groups") or ["control","treatment"]
    if not isinstance(groups,list) or len(groups)<2 or len(groups)>MAX_GROUPS: raise ExperimentalDesignError("groups must contain 2..64 labels.")
    n=_integer(payload.get("n"),"n",len(groups),MAX_TOTAL_SAMPLE); seed=_integer(payload.get("seed",1729),"seed",0,2**32-1)
    rng=np.random.default_rng(seed); base=[str(groups[i%len(groups)]) for i in range(n)]; rng.shuffle(base)
    counts={g:base.count(str(g)) for g in groups}
    return {"ok":True,"version":VERSION,"seed":seed,"n":n,"assignments":base,"counts":counts,
            "allocation_concealment_not_guaranteed":True,"automatic_enrollment_assignment":False,"schedule_hash":_hash({"seed":seed,"assignments":base})}


def design_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    issues=[]; warnings=[]
    alpha=_prob(payload.get("alpha",0.05),"alpha"); power=_prob(payload.get("target_power",0.8),"target_power")
    if alpha>0.1: warnings.append("alpha exceeds 0.10; verify this is intentional.")
    if power<0.8: warnings.append("target_power is below 0.80; adequacy is domain-specific.")
    if payload.get("effect_size_source") in {None,""}: issues.append("effect_size_source is not declared.")
    if payload.get("variance_source") in {None,""}: issues.append("variance_source is not declared.")
    if payload.get("multiple_primary_outcomes") and not payload.get("multiplicity_plan"): issues.append("multiple primary outcomes declared without multiplicity_plan.")
    if payload.get("clustered") and payload.get("icc") is None: issues.append("clustered design requires a declared ICC or design-effect assumption.")
    return {"ok":True,"version":VERSION,"issues":issues,"warnings":warnings,"ready_for_review":len(issues)==0,
            "scientific_validity_certified":False,"ethics_approval_certified":False,"power_guaranteed":False}


def build_visualization_plan(payload: dict[str, Any]) -> dict[str, Any]:
    figures=[{"figure_type":x,"semantic_role":"design-diagnostic","publication_profile":"scientific"} for x in sorted(FIGURE_FAMILIES)]
    return {"ok":True,"version":VERSION,"figures":figures,"figure_count":len(figures),"automatic_claim_generation":False,
            "automatic_significance_highlighting":False,"renderer_authority":"Lab visualization stack v0.114–v0.119"}


def build_studio(payload: dict[str, Any]) -> dict[str, Any]:
    design_ref=str(payload.get("design_ref") or "design:unbound"); methods=payload.get("methods") or []
    studio={"schema":SCHEMA,"version":VERSION,"design_ref":design_ref,"methods":[str(x) for x in methods],
            "power_assumptions":copy.deepcopy(payload.get("power_assumptions") or {}),"randomization":copy.deepcopy(payload.get("randomization") or {}),
            "adaptive_plan":copy.deepcopy(payload.get("adaptive_plan") or {}),"boundaries":{"automatic_design_selection":False,"power_guaranteed":False,"automatic_core_submission":False}}
    studio["studio_hash"]=_hash(studio)
    return {"ok":True,"version":VERSION,"studio":studio}


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    obj={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"studio":copy.deepcopy(payload.get("studio") or {}),"design_ref":str(payload.get("design_ref") or "design:unbound"),
         "results":copy.deepcopy(payload.get("results") or {}),"assumptions":copy.deepcopy(payload.get("assumptions") or {}),"seed_refs":copy.deepcopy(payload.get("seed_refs") or [])}
    obj["snapshot_hash"]=_hash(obj)
    return {"ok":True,"version":VERSION,"snapshot":obj,"snapshot_hash":obj["snapshot_hash"],"automatic_persistence":False}


def build_reproduction_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"snapshot_ref":str(payload.get("snapshot_ref") or "snapshot:unbound"),
            "required_inputs":["design specification","effect-size assumptions","variance/proportion assumptions","alpha/power targets","randomization seed when applicable","software/version metadata"],
            "automatic_execution":False,"reproduction_certified":False}


def build_export_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"formats":payload.get("formats") or ["json","csv","svg","pdf"],
            "include_assumptions":True,"include_power_method":True,"include_randomization_metadata":True,"include_boundaries":True,
            "automatic_publication":False,"scientific_validity_certified":False}


def build_core_object_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"session_id":str(payload.get("session_id") or "session:unbound"),
            "object_type":"experimental-design-analysis","analysis_id":str(payload.get("analysis_id") or "design-analysis"),
            "source_refs":copy.deepcopy(payload.get("source_refs") or []),"snapshot_ref":payload.get("snapshot_ref"),
            "submission_mode":"reference-first","automatic_core_submission":False,"automatic_evidence_promotion":False,
            "scientific_validity_certified":False}


def build_execution_lineage_plan(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok":True,"version":VERSION,"session_id":str(payload.get("session_id") or "session:unbound"),
            "execution_type":"experimental-design-power-analysis","method_refs":copy.deepcopy(payload.get("method_refs") or []),
            "input_refs":copy.deepcopy(payload.get("input_refs") or []),"output_refs":copy.deepcopy(payload.get("output_refs") or []),
            "seed":payload.get("seed"),"automatic_execution":False,"automatic_core_submission":False}


def interpretation_boundaries_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    boundaries=[
        "Power is conditional on declared effect-size, variance, allocation, attrition, and model assumptions.",
        "A planned power level is not a guarantee that a study will detect an effect.",
        "Low observed power after a study is not a substitute for interval estimation or design review.",
        "Effect sizes are not inferred automatically from domain expectations or prior literature.",
        "Simulation-estimated power carries Monte Carlo uncertainty.",
        "Randomization schedules do not guarantee concealment, compliance, or unbiased execution.",
        "Sequential and adaptive plans require pre-specification and method-appropriate type-I-error control.",
        "Multiplicity plans do not automatically define scientific importance or confirmatory status.",
        "Cluster design effects depend strongly on the declared ICC and cluster-size assumptions.",
        "Precision calculations are conditional planning approximations, not guaranteed interval widths.",
        "No design calculation certifies ethical acceptability or scientific validity.",
        "No result is automatically promoted to a Platform Core finding, claim, or evidence object.",
    ]
    return {"ok":True,"version":VERSION,"boundaries":boundaries,"power_guaranteed":False,"scientific_validity_certified":False,
            "ethics_approval_certified":False,"automatic_significance_claims":False,"automatic_core_submission":False,"determine_truth":False}
