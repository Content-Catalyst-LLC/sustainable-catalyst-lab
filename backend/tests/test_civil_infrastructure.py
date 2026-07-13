import math
from app.civil_infrastructure import VERSION,METHODS,public_catalog,run_method
def test_catalog_has_48_methods():
    assert VERSION=="0.12.0" and public_catalog()["methodCount"]==48 and len(METHODS)==48
def test_structural_and_geotechnical():
    assert run_method("ci.uniform_beam_moment",{"loadNPerM":10,"spanM":4})["outputs"]["maxMomentNm"]==20
    assert run_method("ci.vertical_effective_stress",{"unitWeightNPerM3":20,"depthM":5,"porePressurePa":30})["outputs"]["effectiveStressPa"]==70
    assert math.isclose(run_method("ci.rankine_active_coefficient",{"frictionAngleDeg":0})["outputs"]["activeCoefficient"],1)
def test_other_domains():
    assert run_method("ci.rational_peak_runoff",{"runoffCoefficient":.5,"intensityMps":.001,"areaM2":1000})["outputs"]["peakFlowM3S"]==.5
    assert run_method("ci.traffic_flow",{"densityVehPerKm":20,"speedKmH":60})["outputs"]["flowVehPerH"]==1200
    assert run_method("ci.chlorine_dose",{"doseMgL":2,"volumeM3":1000})["outputs"]["massKg"]==2
    assert run_method("ci.risk_score",{"annualProbability":.1,"consequenceCost":1000})["outputs"]["annualizedRisk"]==100
