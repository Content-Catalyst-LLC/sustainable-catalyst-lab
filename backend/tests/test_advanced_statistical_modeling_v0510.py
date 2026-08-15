import math
import pytest
from app.advanced_statistical_modeling import AdvancedStatisticalModelingError, compare, cross_validate, fit, health, normalize_study, policies, predict


def linear_rows(n=40):
    return [{"x": float(i), "z": float(i % 5), "y": 3.0 + 2.0*i - 0.5*(i%5), "w": 1.0 + (i % 3)} for i in range(n)]


def test_health_and_policy_boundaries():
    assert health()["version"] == "0.51.0"
    p = policies()
    assert p["boundaries"]["arbitraryCode"] is False
    assert "binomial-logit" in p["families"]
    assert p["regularization"]["elasticNet"] is True


def test_ols_recovers_linear_coefficients_and_inference():
    r = fit({"title":"linear","family":"gaussian","estimator":"ols","features":["x","z"],"response":"y","rows":linear_rows()})["result"]
    coeff = {row["term"]: row["estimate"] for row in r["coefficients"]}
    assert coeff["Intercept"] == pytest.approx(3.0, abs=1e-8)
    assert coeff["x"] == pytest.approx(2.0, abs=1e-8)
    assert coeff["z"] == pytest.approx(-0.5, abs=1e-8)
    assert r["metrics"]["rSquared"] > 0.999999
    assert r["inference"]["available"] is True


def test_weighted_huber_and_regularized_models_fit():
    rows = linear_rows(); rows[-1]["y"] += 250
    wls = fit({"family":"gaussian","estimator":"weighted-least-squares","features":["x","z"],"response":"y","weightColumn":"w","rows":rows})["result"]
    huber = fit({"family":"gaussian","estimator":"huber","features":["x","z"],"response":"y","rows":rows})["result"]
    ridge = fit({"family":"gaussian","estimator":"ridge","alpha":0.2,"standardize":True,"features":["x","z"],"response":"y","rows":rows})["result"]
    lasso = fit({"family":"gaussian","estimator":"lasso","alpha":0.01,"standardize":True,"features":["x","z"],"response":"y","rows":rows})["result"]
    elastic = fit({"family":"gaussian","estimator":"elastic-net","alpha":0.01,"l1Ratio":0.5,"standardize":True,"features":["x","z"],"response":"y","rows":rows})["result"]
    assert all(r["n"] == 40 for r in [wls,huber,ridge,lasso,elastic])
    assert huber["inference"]["available"] is False
    assert ridge["coefficients"][1]["penalized"] is True


def test_binomial_logit_glm_and_prediction():
    rows=[]
    for i in range(-30,31):
        x=i/6
        y=1.0 if x>0 else 0.0
        rows.append({"x":x,"y":y})
    fitted=fit({"family":"binomial-logit","estimator":"glm","features":["x"],"response":"y","rows":rows})["result"]
    assert fitted["metrics"]["accuracy"] > 0.9
    pred=predict({"result":fitted,"rows":[{"x":-2,"y":0},{"x":2,"y":1}]})["predictions"]
    assert pred[0] < 0.5 < pred[1]
    assert fitted["inference"]["available"] is True


def test_poisson_log_glm():
    rows=[]
    for i in range(1,50):
        x=i/15
        mu=math.exp(0.3+0.35*x)
        rows.append({"x":x,"count":round(mu)})
    fitted=fit({"family":"poisson-log","estimator":"glm","features":["x"],"response":"count","rows":rows})["result"]
    assert fitted["metrics"]["poissonDevianceMean"] >= 0
    assert fitted["coefficients"][1]["estimate"] > 0


def test_cubic_spline_produces_knots_and_curve_graph():
    rows=[{"x":i/10,"y":math.sin(i/10)} for i in range(60)]
    fitted=fit({"family":"gaussian","estimator":"ols","modelType":"cubic-spline","features":["x"],"response":"y","knots":4,"rows":rows})["result"]
    assert len(fitted["design"]["state"]["knots"]) == 4
    assert "splineCurve" in fitted["graphs"]
    assert fitted["metrics"]["rSquared"] > 0.95


def test_repeated_cross_validation_is_deterministic():
    payload={"study":{"family":"gaussian","estimator":"ridge","alpha":0.1,"standardize":True,"features":["x","z"],"response":"y"},"rows":linear_rows(),"folds":5,"repeats":2,"seed":9}
    a=cross_validate(payload)["validation"]
    b=cross_validate(payload)["validation"]
    assert a["mean"] == pytest.approx(b["mean"])
    assert len(a["foldResults"]) == 10


def test_model_comparison_ranks_candidates():
    rows=linear_rows()
    c=compare({"rows":rows,"folds":4,"candidates":[
        {"id":"ols","title":"OLS","family":"gaussian","estimator":"ols","features":["x","z"],"response":"y"},
        {"id":"ridge","title":"Ridge","family":"gaussian","estimator":"ridge","alpha":10,"standardize":True,"features":["x","z"],"response":"y"},
    ]})["comparison"]
    assert len(c["ranking"]) == 2
    assert c["ranking"][0]["rank"] == 1
    assert c["winner"]["title"] in {"OLS","Ridge"}


def test_invalid_family_combinations_and_bad_binomial_rejected():
    with pytest.raises(AdvancedStatisticalModelingError):
        normalize_study({"family":"binomial-logit","estimator":"lasso","features":["x"],"response":"y"})
    with pytest.raises(AdvancedStatisticalModelingError):
        fit({"family":"binomial-logit","estimator":"glm","features":["x"],"response":"y","rows":[{"x":i,"y":2} for i in range(10)]})
