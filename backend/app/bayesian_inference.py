from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, gammaln

from .advanced_statistical_modeling import _basis, _clean_prediction_rows, _clean_rows, normalize_study as normalize_statistical_study
from .model_studio import normalize_graph

VERSION = "0.52.0"
STUDY_SCHEMA = "sc-lab-bayesian-study/0.52.0"
RESULT_SCHEMA = "sc-lab-bayesian-result/0.52.0"
PREDICTIVE_SCHEMA = "sc-lab-posterior-predictive/0.52.0"
MAX_CHAINS = 8
MAX_DRAWS = 4000
MAX_WARMUP = 3000
MAX_PREDICTIVE_DRAWS = 1200
MAX_RETAINED_DRAWS = 1200
FAMILIES = {"gaussian", "binomial-logit", "poisson-log"}
MODEL_TYPES = {"linear", "cubic-spline"}


class BayesianInferenceError(ValueError):
    pass


FORBIDDEN_EXECUTABLE_KEYS = {"code", "python", "javascript", "script", "command", "shell", "callback", "executable", "exec"}


def _reject_executable_fields(value: Any, path: str = "study") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).strip().lower() in FORBIDDEN_EXECUTABLE_KEYS:
                raise BayesianInferenceError(f"Executable field is not allowed in Bayesian studies: {path}.{key}")
            _reject_executable_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_executable_fields(child, f"{path}[{index}]")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BayesianInferenceError(f"{label} must be numeric.") from exc
    if not math.isfinite(number):
        raise BayesianInferenceError(f"{label} must be finite.")
    return number


def _positive(value: Any, label: str, minimum: float = 1e-12) -> float:
    number = _finite(value, label)
    if number < minimum:
        raise BayesianInferenceError(f"{label} must be at least {minimum:g}.")
    return number


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schemas": {"study": STUDY_SCHEMA, "result": RESULT_SCHEMA, "posteriorPredictive": PREDICTIVE_SCHEMA},
        "families": sorted(FAMILIES),
        "modelTypes": sorted(MODEL_TYPES),
        "priors": {
            "coefficients": "independent-normal",
            "gaussianVariance": "inverse-gamma",
            "termSpecificNormalPriors": True,
        },
        "samplers": {
            "gaussian": "Gibbs: normal coefficients + inverse-gamma residual variance",
            "binomial-logit": "adaptive random-walk Metropolis",
            "poisson-log": "adaptive random-walk Metropolis",
            "maximumChains": MAX_CHAINS,
            "maximumDrawsPerChain": MAX_DRAWS,
            "maximumWarmupPerChain": MAX_WARMUP,
        },
        "diagnostics": ["split-rhat", "autocorrelation-ess", "mcse", "acceptance-rate", "trace"],
        "posteriorPredictive": True,
        "boundaries": {
            "arbitraryCode": False,
            "automaticConvergenceCertification": False,
            "automaticCausalClaims": False,
            "automaticPriorSelection": False,
            "automaticPublication": False,
            "hierarchicalModels": False,
            "bayesFactors": False,
        },
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "bayesian-inference-ready",
        "version": VERSION,
        "gaussianBayesianRegression": True,
        "bayesianLogisticRegression": True,
        "bayesianPoissonRegression": True,
        "cubicSplines": True,
        "posteriorDiagnostics": True,
        "posteriorPredictiveModeling": True,
        "sharedVisualizationContract": True,
        "reproduciblePackageCompatible": True,
        "arbitraryCode": False,
        "automaticConvergenceCertification": False,
    }


def normalize_study(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise BayesianInferenceError("Bayesian study must be an object.")
    _reject_executable_fields(payload)
    family = str(payload.get("family") or "gaussian").strip()
    if family not in FAMILIES:
        raise BayesianInferenceError("Unsupported Bayesian response family.")
    model_type = str(payload.get("modelType") or "linear").strip()
    if model_type not in MODEL_TYPES:
        raise BayesianInferenceError("Unsupported Bayesian model type.")
    if family != "gaussian" and model_type != "linear":
        raise BayesianInferenceError("Cubic splines are limited to Gaussian Bayesian regression in v0.52.0.")

    statistical_payload = {
        "id": payload.get("id") or "bayesian-study",
        "title": payload.get("title") or "Bayesian model",
        "family": family,
        "estimator": "ols" if family == "gaussian" else "glm",
        "modelType": model_type,
        "features": payload.get("features") or [],
        "response": payload.get("response"),
        "standardize": bool(payload.get("standardize", True)),
        "splineFeature": payload.get("splineFeature"),
        "knots": payload.get("knots", 3),
        "confidenceLevel": payload.get("credibleLevel", 0.95),
        "provenance": payload.get("provenance") or {},
    }
    try:
        base = normalize_statistical_study(statistical_payload)
    except Exception as exc:
        raise BayesianInferenceError(str(exc)) from exc

    chains = min(max(int(_finite(payload.get("chains", 4), "chains")), 2), MAX_CHAINS)
    draws = min(max(int(_finite(payload.get("draws", 800), "draws")), 50), MAX_DRAWS)
    warmup = min(max(int(_finite(payload.get("warmup", 500), "warmup")), 0), MAX_WARMUP)
    predictive_draws = min(max(int(_finite(payload.get("posteriorPredictiveDraws", 300), "posteriorPredictiveDraws")), 20), MAX_PREDICTIVE_DRAWS)
    credible = min(max(_finite(payload.get("credibleLevel", 0.95), "credibleLevel"), 0.5), 0.999)
    target_acceptance = min(max(_finite(payload.get("targetAcceptance", 0.28), "targetAcceptance"), 0.1), 0.7)
    proposal_scale = min(max(_positive(payload.get("proposalScale", 1.0), "proposalScale"), 0.02), 20.0)

    term_priors: dict[str, dict[str, float]] = {}
    raw_term_priors = payload.get("termPriors") or {}
    if raw_term_priors and not isinstance(raw_term_priors, dict):
        raise BayesianInferenceError("termPriors must be an object keyed by design-term label.")
    for term, spec in raw_term_priors.items():
        if not isinstance(spec, dict):
            raise BayesianInferenceError("Each term prior must be an object with mean and sd.")
        label = str(term).strip()
        if not label or len(label) > 160:
            raise BayesianInferenceError("Term prior labels must be non-empty and at most 160 characters.")
        term_priors[label] = {"mean": _finite(spec.get("mean", 0), f"{label} prior mean"), "sd": _positive(spec.get("sd", 2.5), f"{label} prior sd")}

    study = {
        "schema": STUDY_SCHEMA,
        "version": VERSION,
        "recordType": "bayesian-inference-study",
        "id": str(payload.get("id") or f"bayes-{_digest({'family': family, 'features': base['features'], 'response': base['response']})[:12]}")[:180],
        "title": str(payload.get("title") or "Bayesian model")[:240],
        "family": family,
        "modelType": model_type,
        "features": list(base["features"]),
        "response": base["response"],
        "standardize": bool(base["standardize"]),
        "splineFeature": base["splineFeature"],
        "knots": deepcopy(base["knots"]),
        "credibleLevel": credible,
        "priors": {
            "intercept": {"distribution": "normal", "mean": _finite(payload.get("interceptPriorMean", 0.0), "interceptPriorMean"), "sd": _positive(payload.get("interceptPriorSD", 10.0), "interceptPriorSD")},
            "coefficient": {"distribution": "normal", "mean": _finite(payload.get("coefficientPriorMean", 0.0), "coefficientPriorMean"), "sd": _positive(payload.get("coefficientPriorSD", 2.5), "coefficientPriorSD")},
            "termSpecific": term_priors,
            "residualVariance": {"distribution": "inverse-gamma", "shape": _positive(payload.get("sigmaPriorShape", 2.0), "sigmaPriorShape"), "scale": _positive(payload.get("sigmaPriorScale", 2.0), "sigmaPriorScale")},
        },
        "sampler": {
            "chains": chains,
            "draws": draws,
            "warmup": warmup,
            "seed": int(_finite(payload.get("seed", 42), "seed")),
            "targetAcceptance": target_acceptance,
            "proposalScale": proposal_scale,
        },
        "posteriorPredictiveDraws": predictive_draws,
        "provenance": deepcopy(payload.get("provenance") or {}) if isinstance(payload.get("provenance"), dict) else {},
        "boundaries": {
            "arbitraryCode": False,
            "automaticConvergenceCertification": False,
            "automaticCausalClaims": False,
            "automaticPriorSelection": False,
        },
    }
    study["studyHash"] = _digest({k: v for k, v in study.items() if k != "studyHash"})
    return study


def _statistical_study(study: dict[str, Any]) -> dict[str, Any]:
    return normalize_statistical_study({
        "id": study["id"],
        "title": study["title"],
        "family": study["family"],
        "estimator": "ols" if study["family"] == "gaussian" else "glm",
        "modelType": study["modelType"],
        "features": study["features"],
        "response": study["response"],
        "standardize": study["standardize"],
        "splineFeature": study["splineFeature"],
        "knots": study["knots"],
        "confidenceLevel": study["credibleLevel"],
        "provenance": study["provenance"],
    })


def _prior_vectors(study: dict[str, Any], labels: list[str]) -> tuple[np.ndarray, np.ndarray]:
    means = []
    sds = []
    specific = study["priors"]["termSpecific"]
    for label in labels:
        if label in specific:
            means.append(float(specific[label]["mean"]))
            sds.append(float(specific[label]["sd"]))
        elif label == "Intercept":
            means.append(float(study["priors"]["intercept"]["mean"]))
            sds.append(float(study["priors"]["intercept"]["sd"]))
        else:
            means.append(float(study["priors"]["coefficient"]["mean"]))
            sds.append(float(study["priors"]["coefficient"]["sd"]))
    return np.asarray(means, dtype=float), np.asarray(sds, dtype=float)


def _log_likelihood(family: str, X: np.ndarray, y: np.ndarray, beta: np.ndarray) -> float:
    eta = X @ beta
    if family == "binomial-logit":
        return float(np.sum(y * (-np.logaddexp(0.0, -eta)) + (1.0 - y) * (-np.logaddexp(0.0, eta))))
    eta = np.clip(eta, -30.0, 30.0)
    mu = np.exp(eta)
    return float(np.sum(y * eta - mu - gammaln(y + 1.0)))


def _log_posterior(family: str, X: np.ndarray, y: np.ndarray, beta: np.ndarray, prior_mean: np.ndarray, prior_sd: np.ndarray) -> float:
    z = (beta - prior_mean) / prior_sd
    prior = -0.5 * float(np.dot(z, z)) - float(np.sum(np.log(prior_sd)))
    value = _log_likelihood(family, X, y, beta) + prior
    return value if math.isfinite(value) else -math.inf


def _laplace_start(family: str, X: np.ndarray, y: np.ndarray, prior_mean: np.ndarray, prior_sd: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    precision = 1.0 / np.maximum(prior_sd ** 2, 1e-12)
    def objective(beta: np.ndarray) -> tuple[float, np.ndarray]:
        eta = X @ beta
        if family == "binomial-logit":
            p = expit(eta)
            nll = float(np.sum(np.logaddexp(0.0, eta) - y * eta))
            grad = X.T @ (p - y)
        else:
            eta = np.clip(eta, -30.0, 30.0)
            mu = np.exp(eta)
            nll = float(np.sum(mu - y * eta + gammaln(y + 1.0)))
            grad = X.T @ (mu - y)
        delta = beta - prior_mean
        nll += 0.5 * float(np.sum(precision * delta * delta))
        grad = grad + precision * delta
        return nll, grad
    result = minimize(lambda b: objective(b)[0], prior_mean.copy(), jac=lambda b: objective(b)[1], method="L-BFGS-B", options={"maxiter": 3000, "ftol": 1e-10})
    mode = np.asarray(result.x if np.all(np.isfinite(result.x)) else prior_mean, dtype=float)
    eta = X @ mode
    if family == "binomial-logit":
        p = expit(eta); weights = np.clip(p * (1.0 - p), 1e-6, None)
    else:
        weights = np.clip(np.exp(np.clip(eta, -30.0, 30.0)), 1e-6, 1e6)
    hessian = X.T @ (X * weights[:, None]) + np.diag(precision)
    covariance = np.linalg.pinv(hessian)
    covariance = (covariance + covariance.T) / 2.0
    return mode, covariance


def _sample_gaussian(study: dict[str, Any], X: np.ndarray, y: np.ndarray, labels: list[str]) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    chains = study["sampler"]["chains"]; draws = study["sampler"]["draws"]; warmup = study["sampler"]["warmup"]
    prior_mean, prior_sd = _prior_vectors(study, labels)
    prior_precision = np.diag(1.0 / np.maximum(prior_sd ** 2, 1e-12))
    a0 = float(study["priors"]["residualVariance"]["shape"]); b0 = float(study["priors"]["residualVariance"]["scale"])
    p = X.shape[1]
    beta_chains = np.zeros((chains, draws, p), dtype=float)
    sigma_chains = np.zeros((chains, draws), dtype=float)
    chain_info = []
    ridge = np.eye(p) * 1e-12
    for chain in range(chains):
        rng = np.random.default_rng(study["sampler"]["seed"] + 1009 * chain)
        beta = prior_mean + rng.normal(0, prior_sd * 0.05)
        sigma2 = max(float(np.var(y)), 1e-6)
        total = warmup + draws
        kept = 0
        for step in range(total):
            precision = prior_precision + (X.T @ X) / sigma2 + ridge
            covariance = np.linalg.pinv(precision)
            mean = covariance @ (prior_precision @ prior_mean + (X.T @ y) / sigma2)
            covariance = (covariance + covariance.T) / 2.0
            beta = rng.multivariate_normal(mean, covariance, check_valid="ignore")
            residual = y - X @ beta
            shape = a0 + len(y) / 2.0
            scale = b0 + 0.5 * float(np.dot(residual, residual))
            sigma2 = 1.0 / rng.gamma(shape, 1.0 / max(scale, 1e-12))
            if step >= warmup:
                beta_chains[chain, kept, :] = beta
                sigma_chains[chain, kept] = math.sqrt(max(sigma2, 1e-15))
                kept += 1
        chain_info.append({"chain": chain + 1, "algorithm": "gibbs-normal-inverse-gamma", "acceptanceRate": None, "draws": draws, "warmup": warmup})
    return beta_chains, sigma_chains, chain_info


def _sample_glm(study: dict[str, Any], X: np.ndarray, y: np.ndarray, labels: list[str]) -> tuple[np.ndarray, None, list[dict[str, Any]]]:
    chains = study["sampler"]["chains"]; draws = study["sampler"]["draws"]; warmup = study["sampler"]["warmup"]
    prior_mean, prior_sd = _prior_vectors(study, labels)
    mode, covariance = _laplace_start(study["family"], X, y, prior_mean, prior_sd)
    eigvals, eigvecs = np.linalg.eigh(covariance)
    eigvals = np.clip(eigvals, 1e-8, 1e6)
    base_chol = eigvecs @ np.diag(np.sqrt(eigvals))
    p = X.shape[1]
    beta_chains = np.zeros((chains, draws, p), dtype=float)
    chain_info = []
    target = study["sampler"]["targetAcceptance"]
    for chain in range(chains):
        rng = np.random.default_rng(study["sampler"]["seed"] + 2003 * chain)
        beta = mode + base_chol @ rng.normal(size=p) * 0.05
        logp = _log_posterior(study["family"], X, y, beta, prior_mean, prior_sd)
        multiplier = study["sampler"]["proposalScale"] * 2.38 / math.sqrt(max(p, 1))
        accepted_total = 0; accepted_window = 0; kept = 0
        total = warmup + draws
        for step in range(total):
            proposal = beta + multiplier * (base_chol @ rng.normal(size=p))
            prop_logp = _log_posterior(study["family"], X, y, proposal, prior_mean, prior_sd)
            accepted = math.log(max(rng.random(), 1e-300)) < (prop_logp - logp)
            if accepted:
                beta = proposal; logp = prop_logp; accepted_total += 1; accepted_window += 1
            if step < warmup and (step + 1) % 50 == 0:
                rate = accepted_window / 50.0
                multiplier *= math.exp(max(min(rate - target, 0.25), -0.25))
                multiplier = min(max(multiplier, 0.01), 10.0)
                accepted_window = 0
            if step >= warmup:
                beta_chains[chain, kept, :] = beta
                kept += 1
        chain_info.append({"chain": chain + 1, "algorithm": "adaptive-random-walk-metropolis", "acceptanceRate": accepted_total / max(total, 1), "proposalMultiplierFinal": multiplier, "draws": draws, "warmup": warmup})
    return beta_chains, None, chain_info


def _split_chains(values: np.ndarray) -> np.ndarray:
    m, n = values.shape[:2]
    half = n // 2
    if half < 2:
        return values
    return np.concatenate([values[:, :half, ...], values[:, n-half:, ...]], axis=0)


def _rhat(values: np.ndarray) -> float:
    x = _split_chains(np.asarray(values, dtype=float))
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 2:
        return float("nan")
    m, n = x.shape
    chain_means = np.mean(x, axis=1)
    chain_vars = np.var(x, axis=1, ddof=1)
    W = float(np.mean(chain_vars))
    if W <= 1e-20:
        return 1.0
    B = n * float(np.var(chain_means, ddof=1))
    var_hat = ((n - 1.0) / n) * W + B / n
    return math.sqrt(max(var_hat / W, 0.0))


def _ess(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    m, n = x.shape
    if n < 4:
        return float(m * n)
    centered = x - np.mean(x, axis=1, keepdims=True)
    var = float(np.mean(np.var(centered, axis=1, ddof=1)))
    if var <= 1e-20:
        return float(m * n)
    max_lag = min(n - 1, 500)
    rho_sum = 0.0
    lag = 1
    while lag <= max_lag:
        pair = 0.0
        for current_lag in (lag, lag + 1):
            if current_lag > max_lag:
                continue
            vals = []
            for c in range(m):
                a = centered[c, :-current_lag]; b = centered[c, current_lag:]
                vals.append(float(np.dot(a, b) / max(len(a), 1) / var))
            pair += float(np.mean(vals))
        if pair < 0:
            break
        rho_sum += pair
        lag += 2
    return float(min(max(m * n / max(1.0 + 2.0 * rho_sum, 1e-9), 1.0), m * n))


def _summary_rows(study: dict[str, Any], labels: list[str], beta_chains: np.ndarray, sigma_chains: np.ndarray | None) -> list[dict[str, Any]]:
    alpha = (1.0 - study["credibleLevel"]) / 2.0
    rows = []
    arrays = [(labels[i], beta_chains[:, :, i]) for i in range(len(labels))]
    if sigma_chains is not None:
        arrays.append(("Residual σ", sigma_chains))
    for label, chain_values in arrays:
        flat = chain_values.reshape(-1)
        ess = _ess(chain_values)
        sd = float(np.std(flat, ddof=1)) if flat.size > 1 else 0.0
        rows.append({
            "term": label,
            "mean": float(np.mean(flat)),
            "sd": sd,
            "median": float(np.median(flat)),
            "credibleLow": float(np.quantile(flat, alpha)),
            "credibleHigh": float(np.quantile(flat, 1.0 - alpha)),
            "rhat": _rhat(chain_values),
            "ess": ess,
            "mcseMean": sd / math.sqrt(max(ess, 1.0)),
        })
    return rows


def _diagnostics(study: dict[str, Any], summaries: list[dict[str, Any]], chain_info: list[dict[str, Any]]) -> dict[str, Any]:
    rhats = [row["rhat"] for row in summaries if math.isfinite(row["rhat"])]
    esses = [row["ess"] for row in summaries if math.isfinite(row["ess"])]
    acceptance = [row["acceptanceRate"] for row in chain_info if row.get("acceptanceRate") is not None]
    warnings = []
    max_rhat = max(rhats) if rhats else None
    min_ess = min(esses) if esses else None
    if max_rhat is not None and max_rhat > 1.01:
        warnings.append("At least one split-Rhat exceeds 1.01; inspect traces and run longer chains before relying on posterior summaries.")
    if min_ess is not None and min_ess < 400:
        warnings.append("At least one effective sample size is below 400; Monte Carlo uncertainty may be material.")
    if acceptance and (min(acceptance) < 0.12 or max(acceptance) > 0.65):
        warnings.append("Metropolis acceptance is outside the broad 0.12–0.65 review range for at least one chain.")
    return {
        "method": "split-Rhat plus initial-positive-sequence autocorrelation ESS",
        "rankNormalized": False,
        "maxRhat": max_rhat,
        "minEss": min_ess,
        "chainInfo": chain_info,
        "warnings": warnings,
        "reviewRequired": bool(warnings),
        "automaticConvergenceCertification": False,
        "note": "Diagnostics are screening evidence, not an automatic convergence certificate.",
    }


def _thin_retained(beta_chains: np.ndarray, sigma_chains: np.ndarray | None) -> dict[str, Any]:
    combined = beta_chains.reshape(-1, beta_chains.shape[2])
    total = len(combined)
    take = min(total, MAX_RETAINED_DRAWS)
    idx = np.linspace(0, total - 1, take, dtype=int)
    out = {"coefficientDraws": combined[idx].tolist(), "retained": int(take), "totalPosteriorDraws": int(total)}
    if sigma_chains is not None:
        sig = sigma_chains.reshape(-1)
        out["sigmaDraws"] = sig[idx].tolist()
    return out


def _predictive_from_draws(study: dict[str, Any], rows: list[dict[str, Any]], basis_state: dict[str, Any], retained: dict[str, Any], seed: int, draws_requested: int, observed: np.ndarray | None = None) -> dict[str, Any]:
    statistical = _statistical_study(study)
    X, _, _ = _basis(statistical, rows, basis_state)
    beta = np.asarray(retained["coefficientDraws"], dtype=float)
    total = len(beta)
    draws = min(max(int(draws_requested), 20), total)
    idx = np.linspace(0, total - 1, draws, dtype=int)
    beta = beta[idx]
    rng = np.random.default_rng(seed)
    eta = beta @ X.T
    if study["family"] == "gaussian":
        sigma = np.asarray(retained.get("sigmaDraws") or [], dtype=float)[idx]
        latent = eta
        replicated = latent + rng.normal(size=latent.shape) * sigma[:, None]
    elif study["family"] == "binomial-logit":
        latent = expit(eta)
        replicated = rng.binomial(1, np.clip(latent, 1e-9, 1 - 1e-9))
    else:
        latent = np.exp(np.clip(eta, -30.0, 13.8))
        replicated = rng.poisson(np.clip(latent, 1e-12, 1e6))
    alpha = (1.0 - study["credibleLevel"]) / 2.0
    predictions = []
    for i in range(len(rows)):
        predictions.append({
            "index": i,
            "posteriorMean": float(np.mean(latent[:, i])),
            "posteriorLow": float(np.quantile(latent[:, i], alpha)),
            "posteriorHigh": float(np.quantile(latent[:, i], 1 - alpha)),
            "predictiveMean": float(np.mean(replicated[:, i])),
            "predictiveLow": float(np.quantile(replicated[:, i], alpha)),
            "predictiveHigh": float(np.quantile(replicated[:, i], 1 - alpha)),
        })
    checks: dict[str, Any] = {"draws": draws}
    if observed is not None and len(observed) == len(rows):
        stats: dict[str, tuple[float, np.ndarray]] = {"mean": (float(np.mean(observed)), np.mean(replicated, axis=1))}
        if len(observed) > 1:
            stats["sd"] = (float(np.std(observed, ddof=1)), np.std(replicated, axis=1, ddof=1))
        if study["family"] == "poisson-log":
            stats["zeroRate"] = (float(np.mean(observed == 0)), np.mean(replicated == 0, axis=1))
        rows_out = []
        for name, (obs, rep) in stats.items():
            p = float(np.mean(rep >= obs))
            rows_out.append({"statistic": name, "observed": obs, "replicatedMean": float(np.mean(rep)), "replicatedLow": float(np.quantile(rep, alpha)), "replicatedHigh": float(np.quantile(rep, 1-alpha)), "bayesianPValue": p, "tailWarning": bool(p < 0.05 or p > 0.95)})
        checks["statistics"] = rows_out
        checks["tailWarnings"] = sum(1 for row in rows_out if row["tailWarning"])
    return {"predictions": predictions, "checks": checks, "replicatedShape": [int(v) for v in replicated.shape]}


def _graphs(study: dict[str, Any], labels: list[str], summaries: list[dict[str, Any]], beta_chains: np.ndarray, predictive: dict[str, Any], observed: np.ndarray) -> dict[str, Any]:
    coeff_rows = summaries[:len(labels)]
    coeff = normalize_graph({
        "kind": "line-scatter",
        "title": f"{study['title']} — posterior coefficient intervals",
        "xLabel": "Parameter index",
        "yLabel": "Posterior estimate",
        "description": "Posterior means with central credible intervals. Parameter labels are preserved on each point.",
        "series": [{"id": "posterior-coefficients", "label": "Posterior coefficient", "mode": "scatter", "points": [{"x": i+1, "y": row["mean"], "yLow": row["credibleLow"], "yHigh": row["credibleHigh"], "label": row["term"]} for i, row in enumerate(coeff_rows)]}],
    })
    pred_rows = predictive["predictions"]
    posterior_predictive = normalize_graph({
        "kind": "line-scatter",
        "title": f"{study['title']} — posterior predictive check",
        "xLabel": "Observation index",
        "yLabel": study["response"],
        "description": "Observed values compared with posterior predictive means and central predictive intervals.",
        "series": [
            {"id": "observed", "label": "Observed", "mode": "scatter", "points": [{"x": i+1, "y": float(observed[i])} for i in range(len(observed))]},
            {"id": "posterior-predictive", "label": "Posterior predictive", "mode": "line", "points": [{"x": i+1, "y": row["predictiveMean"], "yLow": row["predictiveLow"], "yHigh": row["predictiveHigh"]} for i, row in enumerate(pred_rows)]},
        ],
    })
    trace_series = []
    max_params = min(len(labels), 6)
    for j in range(max_params):
        flat = beta_chains[:, :, j].reshape(-1)
        stride = max(1, len(flat) // 600)
        trace_series.append({"id": f"trace-{j+1}", "label": labels[j], "mode": "line", "points": [{"x": int(i), "y": float(flat[i])} for i in range(0, len(flat), stride)]})
    trace = normalize_graph({"kind": "line-scatter", "title": f"{study['title']} — posterior traces", "xLabel": "Retained draw", "yLabel": "Parameter value", "description": "Trace screening for the first six coefficient parameters across retained chain draws.", "series": trace_series})
    ppc_bars = []
    for row in predictive.get("checks", {}).get("statistics", []):
        ppc_bars.extend([{"label": f"Observed {row['statistic']}", "value": row["observed"]}, {"label": f"Predictive {row['statistic']}", "value": row["replicatedMean"]}])
    ppc_summary = normalize_graph({"kind": "horizontal-bars", "title": f"{study['title']} — predictive summary", "xLabel": "Statistic value", "yLabel": "Check", "description": "Observed summary statistics compared with posterior-predictive replicated means.", "bars": ppc_bars})
    return {"coefficientIntervals": coeff, "posteriorPredictive": posterior_predictive, "trace": trace, "predictiveSummary": ppc_summary}


def fit(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise BayesianInferenceError("Bayesian fit request must be an object.")
    study = normalize_study(payload.get("study") if isinstance(payload.get("study"), dict) else payload)
    statistical = _statistical_study(study)
    try:
        rows, dropped = _clean_rows(statistical, payload.get("rows") or (payload.get("study") or {}).get("rows"))
    except Exception as exc:
        raise BayesianInferenceError(str(exc)) from exc
    X, labels, basis_state = _basis(statistical, rows)
    y = np.asarray([float(row[study["response"]]) for row in rows], dtype=float)
    if study["family"] == "gaussian":
        beta_chains, sigma_chains, chain_info = _sample_gaussian(study, X, y, labels)
    else:
        beta_chains, sigma_chains, chain_info = _sample_glm(study, X, y, labels)
    summaries = _summary_rows(study, labels, beta_chains, sigma_chains)
    diagnostics = _diagnostics(study, summaries, chain_info)
    retained = _thin_retained(beta_chains, sigma_chains)
    predictive = _predictive_from_draws(study, rows, basis_state, retained, study["sampler"]["seed"] + 9001, study["posteriorPredictiveDraws"], y)
    result = {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "recordType": "bayesian-inference-result",
        "study": study,
        "n": len(rows),
        "droppedRows": dropped,
        "design": {"columns": X.shape[1], "rank": int(np.linalg.matrix_rank(X)), "conditionNumber": float(np.linalg.cond(X)), "labels": labels, "state": basis_state},
        "posterior": {"summaries": summaries, "retainedDraws": retained, "totalDraws": int(beta_chains.shape[0] * beta_chains.shape[1])},
        "diagnostics": diagnostics,
        "posteriorPredictive": {"schema": PREDICTIVE_SCHEMA, "version": VERSION, **predictive},
        "graphs": _graphs(study, labels, summaries, beta_chains, predictive, y),
        "governance": {
            "posteriorIsConditionalOnModelAndPriors": True,
            "diagnosticsRequireReview": True,
            "automaticConvergenceCertification": False,
            "automaticCausalClaims": False,
            "arbitraryCode": False,
            "hierarchicalModels": False,
        },
        "createdAt": _now(),
    }
    result["resultHash"] = _digest({k: v for k, v in result.items() if k not in {"createdAt", "resultHash"}})
    return {"ok": True, "result": result}


def posterior_predictive(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("result"), dict):
        raise BayesianInferenceError("Posterior prediction requires a v0.52.0 Bayesian result.")
    result = payload["result"]
    if result.get("schema") != RESULT_SCHEMA:
        raise BayesianInferenceError("Unsupported Bayesian result contract.")
    study = normalize_study(result.get("study") or {})
    statistical = _statistical_study(study)
    try:
        rows, dropped = _clean_prediction_rows(statistical, payload.get("rows"))
    except Exception as exc:
        raise BayesianInferenceError(str(exc)) from exc
    retained = ((result.get("posterior") or {}).get("retainedDraws") or {})
    if not retained.get("coefficientDraws"):
        raise BayesianInferenceError("Bayesian result does not contain retained posterior coefficient draws.")
    basis_state = ((result.get("design") or {}).get("state") or {})
    prediction = _predictive_from_draws(study, rows, basis_state, retained, int(payload.get("seed", study["sampler"]["seed"] + 12001)), int(payload.get("draws", study["posteriorPredictiveDraws"])), None)
    record = {"schema": PREDICTIVE_SCHEMA, "version": VERSION, "recordType": "posterior-predictive-result", "studyId": study["id"], "rows": len(rows), "droppedRows": dropped, **prediction, "createdAt": _now()}
    record["predictiveHash"] = _digest({k: v for k, v in record.items() if k not in {"createdAt", "predictiveHash"}})
    return {"ok": True, "posteriorPredictive": record}
