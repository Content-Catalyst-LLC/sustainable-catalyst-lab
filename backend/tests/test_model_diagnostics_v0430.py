import math
import pytest

from app.model_diagnostics import ModelDiagnosticsError, compare, cross_validate, diagnose, health, policies


def rows(n=30):
    noise = [0.12, -0.08, 0.18, -0.14, 0.03]
    return [{"x": float(i), "y": 1.5 + 2.25 * i + noise[i % len(noise)]} for i in range(n)]


def study(model_type="linear-multivariate"):
    return {
        "title": "Linear evidence model",
        "modelType": model_type,
        "features": ["x"],
        "response": "y",
        "objective": "least-squares",
        "degree": 2,
        "seed": 42,
    }


def test_health_and_policy_contract():
    assert health()["status"] == "model-diagnostics-ready"
    p = policies()
    assert p["version"] == "0.43.0"
    assert p["validation"]["methods"] == ["k-fold", "repeated-k-fold"]
    assert p["boundaries"]["arbitraryCode"] is False
    assert p["boundaries"]["declarativeParameterFitting"] is False


def test_diagnostics_produce_fit_residual_and_information_criteria():
    result = diagnose({"study": study(), "rows": rows()})
    d = result["diagnostics"]
    assert d["schema"] == "sc-lab-model-diagnostics/0.43.0"
    assert d["metrics"]["rmse"] < 0.3
    assert d["metrics"]["rSquared"] > 0.999
    assert math.isfinite(d["informationCriteria"]["aic"])
    assert math.isfinite(d["informationCriteria"]["aicc"])
    assert math.isfinite(d["informationCriteria"]["bic"])
    assert d["graphs"]["observedPredicted"]["kind"] == "line-scatter"
    assert d["graphs"]["residualVsFitted"]["series"][1]["mode"] == "scatter"
    assert d["graphs"]["qqNormal"]["title"].endswith("normal Q–Q diagnostic")
    assert len(d["diagnosticsHash"]) == 64


def test_cross_validation_is_deterministic_and_reports_fold_dispersion():
    payload = {"study": study(), "rows": rows(), "folds": 5, "repeats": 2, "seed": 77}
    first = cross_validate(payload)["crossValidation"]
    second = cross_validate(payload)["crossValidation"]
    assert first["method"] == "repeated-k-fold"
    assert len(first["foldResults"]) == 10
    fields = ("repeat", "fold", "trainingCount", "validationCount", "rmse", "mae", "bias", "rSquared", "maxAbsoluteError")
    assert [[row.get(f) for f in fields] for row in first["foldResults"]] == [[row.get(f) for f in fields] for row in second["foldResults"]]
    assert first["aggregate"]["rmse"]["mean"] < 0.4
    assert first["aggregate"]["rmse"]["std"] >= 0
    assert first["graphs"]["foldRMSE"]["kind"] == "line-scatter"
    assert len(first["crossValidationHash"]) == 64


def test_cross_validation_rejects_impossible_fold_configuration():
    with pytest.raises(ModelDiagnosticsError, match="too small|folds"):
        cross_validate({"study": study(), "rows": rows(4), "folds": 4, "repeats": 1})


def test_model_comparison_ranks_candidates_on_common_validation_policy():
    result = compare({
        "title": "Linear vs quadratic",
        "rows": rows(),
        "folds": 5,
        "repeats": 1,
        "seed": 42,
        "candidates": [
            {"id": "linear", "title": "Linear", "study": study("linear-multivariate")},
            {"id": "quadratic", "title": "Quadratic", "study": study("polynomial-univariate")},
        ],
    })["comparison"]
    assert result["schema"] == "sc-lab-scientific-model-comparison/0.43.0"
    assert len(result["ranking"]) == 2
    assert result["ranking"][0]["rank"] == 1
    assert result["recommendedCandidateId"] in {"linear", "quadratic"}
    assert result["graph"]["kind"] == "horizontal-bars"
    assert len(result["graph"]["bars"]) == 2
    assert "cross-validation RMSE" in result["selectionPolicy"]
    assert len(result["comparisonHash"]) == 64


def test_comparison_rejects_single_candidate():
    with pytest.raises(ModelDiagnosticsError, match="At least two"):
        compare({"rows": rows(), "candidates": [{"id": "one", "study": study()}]})
