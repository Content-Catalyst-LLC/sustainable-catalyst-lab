import numpy as np
import pytest

from app.correlated_uncertainty import CorrelatedUncertaintyError, analyze, estimate_dependency, normalize_study, policies


def model():
    return {
        "family":"declarative-expression","title":"Dependent linear model","definition":{"equation":"y = a + 2*b"},
        "variables":[{"symbol":"y","role":"response","unit":"u"}],
        "parameters":[
            {"symbol":"a","role":"estimated","value":10,"bounds":{"lower":0,"upper":20}},
            {"symbol":"b","role":"estimated","value":5,"bounds":{"lower":0,"upper":10}},
        ],"constants":[],"initialConditions":[],"dataset":{"datasetId":"","bindings":[]},"datasetBindings":[],"assumptions":[],"limitations":[],"provenance":{}
    }


def study(matrix=None, matrix_type="correlation", method="latin-hypercube"):
    payload={"title":"dependency study","model":model(),"uncertainInputs":[
        {"symbol":"a","distribution":"normal","mean":10,"stdDev":2},
        {"symbol":"b","distribution":"normal","mean":5,"stdDev":1},
    ],"design":{"method":method,"samples":4096,"seed":7},"analysis":{"confidence":.95}}
    if matrix is not None:
        payload["dependency"]={"method":"gaussian-copula","matrixType":matrix_type,"symbols":["a","b"],"matrix":matrix,"source":"test"}
    return payload


def test_policy_declares_dependency_boundaries():
    p=policies(); assert p["version"]=="0.53.0"; assert p["dependentSaltelliSobol"] is False; assert p["automaticDependencyInference"] is False


def test_correlation_matrix_normalizes_and_hashes():
    s=normalize_study(study([[1,.7],[.7,1]])); assert s["dependency"]["method"]=="gaussian-copula"; assert s["governance"]["dependentInputs"] is True; assert len(s["studyHash"])==64


def test_covariance_converts_to_correlation():
    s=normalize_study(study([[4,1],[1,1]],"covariance")); c=np.array(s["dependency"]["latentCorrelation"]); assert c[0,1]==pytest.approx(.5)


def test_non_psd_matrix_is_rejected():
    with pytest.raises(CorrelatedUncertaintyError, match="positive semidefinite"):
        normalize_study({**study([[1,.2],[.2,1]]),"uncertainInputs":[
            {"symbol":"a","distribution":"normal","mean":10,"stdDev":2},
            {"symbol":"b","distribution":"normal","mean":5,"stdDev":1},
            {"symbol":"c","distribution":"normal","mean":1,"stdDev":1}],
            "model":{**model(),"parameters":model()["parameters"]+[{"symbol":"c","role":"estimated","value":1,"bounds":{"lower":-2,"upper":3}}]},
            "dependency":{"method":"gaussian-copula","matrixType":"correlation","symbols":["a","b","c"],"matrix":[[1,.9,.9],[.9,1,-.9],[.9,-.9,1]]}})


def test_dependent_saltelli_is_rejected():
    with pytest.raises(CorrelatedUncertaintyError, match="Saltelli"):
        normalize_study(study([[1,.5],[.5,1]],method="saltelli-sobol"))


def test_gaussian_copula_produces_requested_dependence_and_graph():
    r=analyze(study([[1,.75],[.75,1]]))["result"]
    assert r["version"]=="0.53.0"; assert "dependency" in r["graphs"]
    assert r["dependencyDiagnostics"]["empiricalSpearman"][0][1] > .65
    assert r["governance"]["automaticCausalInterpretation"] is False


def test_dependence_changes_output_variance():
    independent=analyze(study())["result"]["summary"]["variance"]
    dependent=analyze(study([[1,.8],[.8,1]]))["result"]["summary"]["variance"]
    assert dependent > independent


def test_empirical_gaussian_rank_estimator_returns_review_only_dependency():
    rng=np.random.default_rng(3); x=rng.normal(size=300); z=rng.normal(size=300); y=.8*x+.6*z
    rows=[{"x":float(a),"y":float(b)} for a,b in zip(x,y)]
    out=estimate_dependency({"symbols":["x","y"],"rows":rows,"method":"gaussian-rank-correlation"})
    assert out["dependency"]["matrix"][0][1]>.65; assert out["estimation"]["governance"]["automaticUse"] is False


def test_dependency_symbol_order_must_match_uncertain_inputs():
    p=study([[1,.4],[.4,1]]); p["dependency"]["symbols"]=["b","a"]
    with pytest.raises(CorrelatedUncertaintyError, match="exactly match"):
        normalize_study(p)
