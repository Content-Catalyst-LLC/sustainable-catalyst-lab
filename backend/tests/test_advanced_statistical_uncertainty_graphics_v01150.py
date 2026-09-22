import math
import pytest
from app.advanced_statistical_uncertainty_graphics_v01150 import *

PUB={"caption":"Statistical fixture.","source":"Fixture source.","method":"Declared fixture method."}

def test_catalog_and_manifest():
    assert len(catalog()["graphic_types"])==16
    assert manifest()["boundaries"]["automatic_kde_bandwidth"] is False

def test_distribution_histogram_and_ecdf():
    h=build_distribution_figure({"mode":"histogram","samples":[1,2,2,3,4],"bins":4,"title":"Distribution","publication":PUB})
    assert h["graphic_type"]=="histogram" and len(h["spec"]["bins"])==4
    e=build_distribution_figure({"mode":"ecdf","samples":[1,2,3],"title":"ECDF","publication":PUB})
    assert e["spec"]["series"][0]["points"][-1]["y"]==1

def test_density_requires_explicit_bandwidth():
    with pytest.raises(AdvancedStatisticalGraphicsError):
        build_distribution_figure({"mode":"violin","samples":[1,2,3],"publication":PUB})
    v=build_distribution_figure({"mode":"violin","samples":[1,2,3],"density":{"bandwidth":0.4},"publication":PUB})
    assert v["graphic_type"]=="violin" and v["spec"]["violins"]

def test_interval_semantics_and_fan_chart():
    i=build_interval_figure({"semantics":"confidence","level":.95,"records":[{"x":0,"center":1,"lower":.8,"upper":1.2},{"x":1,"center":2,"lower":1.7,"upper":2.3}],"publication":PUB})
    assert i["statistical_metadata"]["level"]==.95
    f=build_fan_chart({"quantile_levels":[.1,.25,.5,.75,.9],"records":[{"x":0,"values":[1,2,3,4,5]},{"x":1,"values":[2,3,4,5,6]}],"publication":PUB})
    assert len(f["statistical_metadata"]["bands"])==2

def test_posterior_and_forest():
    p=build_posterior_figure({"parameters":[{"name":"beta","samples":[.1,.2,.3,.4,.5]}],"publication":PUB})
    assert p["statistical_metadata"]["posterior_intervals"][0]["name"]=="beta"
    c=build_coefficient_forest({"coefficients":[{"label":"x1","estimate":1,"lower":.5,"upper":1.5}],"publication":PUB})
    assert c["spec"]["series"][0]["points"][0]["y"]==1

def test_calibration_and_residuals():
    c=build_calibration_figure({"bins":[{"predicted":.2,"observed":.1,"count":10},{"predicted":.8,"observed":.9,"count":10}],"publication":PUB})
    assert math.isclose(c["statistical_metadata"]["expected_calibration_error"],.1)
    r=build_residual_diagnostics({"observed":[1,2,3],"predicted":[1.1,1.8,3.2],"publication":PUB})
    assert r["statistical_metadata"]["n"]==3 and r["statistical_metadata"]["automatic_diagnostic_pass_fail"] is False

def test_qq_requires_declared_reference():
    with pytest.raises(AdvancedStatisticalGraphicsError): build_qq_figure({"samples":[1,2,3]})
    q=build_qq_figure({"samples":[1,2,3],"reference_distribution":"normal","publication":PUB})
    assert len(q["spec"]["series"][0]["points"])==3

def test_sensitivity_and_decomposition():
    s=build_sensitivity_figure({"method":"sobol","indices":[{"parameter":"a","st":.7,"s1":.5},{"parameter":"b","st":.2,"s1":.1}],"publication":PUB})
    assert s["statistical_metadata"]["ranked_effects"][0]["name"]=="a"
    d=build_uncertainty_decomposition({"components":[{"name":"measurement","variance":2},{"name":"model","variance":1}],"publication":PUB})
    assert math.isclose(d["statistical_metadata"]["components"][0]["share"],2/3)

def test_coverage_and_small_multiples():
    c=build_coverage_figure({"records":[{"lower":0,"upper":2,"truth":1},{"lower":0,"upper":1,"truth":2}],"publication":PUB})
    assert c["statistical_metadata"]["coverage_rate"]==.5
    sm=compose_statistical_small_multiples({"panels":[{"id":"a"},{"id":"b"}],"columns":2})
    assert sm["responsive"]["mobile_columns"]==1

def test_publication_bridge():
    p=build_publication_figure({"builder":"calibration","bins":[{"predicted":.2,"observed":.2,"count":10},{"predicted":.8,"observed":.8,"count":10}],"title":"Calibration","publication":PUB,"alt_text":"Reliability diagram comparing predicted probabilities and observed frequencies."})
    assert p["publication_ready"] is True and p["scientific_validity_certified"] is False
