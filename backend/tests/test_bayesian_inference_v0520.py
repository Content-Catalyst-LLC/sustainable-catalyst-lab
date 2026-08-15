import math
import pytest

from app.bayesian_inference import (
    BayesianInferenceError,
    fit,
    health,
    normalize_study,
    policies,
    posterior_predictive,
)


def gaussian_rows(n=36):
    return [
        {"x": i / 6.0, "z": (i % 5) - 2.0, "y": 2.0 + 1.35 * (i / 6.0) - 0.45 * ((i % 5) - 2.0) + 0.08 * ((i % 3) - 1)}
        for i in range(n)
    ]


def logistic_rows(n=48):
    rows = []
    for i in range(n):
        x = (i - n / 2) / 7.0
        z = (i % 4) - 1.5
        y = 1 if (1.15 * x - 0.35 * z + (0.4 if i % 5 else -0.3)) > 0 else 0
        rows.append({"x": x, "z": z, "y": y})
    return rows


def poisson_rows(n=42):
    rows = []
    for i in range(n):
        x = i / 18.0
        z = (i % 3) - 1.0
        mean = math.exp(0.45 + 0.35 * x - 0.2 * z)
        # deterministic count pattern around the mean for stable tests
        y = max(0, int(round(mean + ((i % 4) - 1.5) * 0.35)))
        rows.append({"x": x, "z": z, "y": y})
    return rows


def base_study(family="gaussian"):
    return {
        "title": f"Bayesian {family} test",
        "family": family,
        "modelType": "linear",
        "features": ["x", "z"],
        "response": "y",
        "standardize": True,
        "chains": 2,
        "draws": 90,
        "warmup": 50,
        "seed": 17,
        "posteriorPredictiveDraws": 50,
    }


def test_health_and_policy_contract():
    assert health()["version"] == "0.52.0"
    assert health()["posteriorPredictiveModeling"] is True
    policy = policies()
    assert policy["boundaries"]["arbitraryCode"] is False
    assert policy["boundaries"]["automaticConvergenceCertification"] is False
    assert "split-rhat" in policy["diagnostics"]


def test_normalize_study_declares_priors_and_sampler():
    study = normalize_study({**base_study(), "coefficientPriorSD": 3.0, "termPriors": {"z(x)": {"mean": 0.5, "sd": 1.2}}})
    assert study["schema"] == "sc-lab-bayesian-study/0.52.0"
    assert study["priors"]["coefficient"]["sd"] == 3.0
    assert study["priors"]["termSpecific"]["z(x)"]["mean"] == 0.5
    assert study["sampler"]["chains"] == 2


def test_executable_fields_are_rejected():
    with pytest.raises(BayesianInferenceError):
        normalize_study({**base_study(), "script": "import os"})
    with pytest.raises(BayesianInferenceError):
        normalize_study({**base_study(), "provenance": {"callback": "https://example.test"}})


def test_gaussian_bayesian_fit_and_predictive_checks():
    result = fit({"study": base_study(), "rows": gaussian_rows()})["result"]
    assert result["schema"] == "sc-lab-bayesian-result/0.52.0"
    assert result["n"] == 36
    assert len(result["posterior"]["summaries"]) == 4  # intercept + 2 coefficients + sigma
    assert result["posterior"]["summaries"][1]["term"] == "z(x)"
    assert result["posterior"]["summaries"][1]["mean"] > 0
    assert result["posterior"]["summaries"][2]["mean"] < 0
    assert result["diagnostics"]["automaticConvergenceCertification"] is False
    assert result["posteriorPredictive"]["checks"]["statistics"]
    assert set(result["graphs"]) >= {"coefficientIntervals", "posteriorPredictive", "trace", "predictiveSummary"}


def test_logistic_metropolis_fit_is_finite_and_reports_acceptance():
    study = {**base_study("binomial-logit"), "draws": 70, "warmup": 45, "proposalScale": 0.8}
    result = fit({"study": study, "rows": logistic_rows()})["result"]
    summaries = result["posterior"]["summaries"]
    assert len(summaries) == 3
    assert all(math.isfinite(row["mean"]) for row in summaries)
    rates = [row["acceptanceRate"] for row in result["diagnostics"]["chainInfo"]]
    assert all(rate is not None and 0 <= rate <= 1 for rate in rates)
    preds = result["posteriorPredictive"]["predictions"]
    assert all(0 <= row["posteriorMean"] <= 1 for row in preds)


def test_poisson_metropolis_fit_outputs_nonnegative_predictive_counts():
    study = {**base_study("poisson-log"), "draws": 70, "warmup": 45, "proposalScale": 0.8}
    result = fit({"study": study, "rows": poisson_rows()})["result"]
    assert result["study"]["family"] == "poisson-log"
    assert all(row["predictiveLow"] >= 0 for row in result["posteriorPredictive"]["predictions"])
    assert any(row["statistic"] == "zeroRate" for row in result["posteriorPredictive"]["checks"]["statistics"])


def test_posterior_predictive_new_rows_reuse_design_state():
    result = fit({"study": base_study(), "rows": gaussian_rows()})["result"]
    out = posterior_predictive({"result": result, "rows": [{"x": 1.0, "z": 0.0}, {"x": 2.0, "z": 1.0}], "draws": 30, "seed": 88})["posteriorPredictive"]
    assert out["schema"] == "sc-lab-posterior-predictive/0.52.0"
    assert out["rows"] == 2
    assert len(out["predictions"]) == 2
    assert out["predictions"][0]["predictiveLow"] <= out["predictions"][0]["predictiveHigh"]


def test_binomial_requires_both_classes():
    rows = [{"x": i, "z": 0, "y": 1} for i in range(12)]
    with pytest.raises(BayesianInferenceError):
        fit({"study": base_study("binomial-logit"), "rows": rows})


def test_non_gaussian_spline_is_out_of_scope():
    with pytest.raises(BayesianInferenceError):
        normalize_study({**base_study("poisson-log"), "modelType": "cubic-spline"})
