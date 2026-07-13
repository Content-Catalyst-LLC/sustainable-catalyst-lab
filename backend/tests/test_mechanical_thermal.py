from __future__ import annotations
import math
from app.mechanical_thermal import VERSION, METHODS, public_catalog, run_method
def test_catalog_has_48_methods():
    assert VERSION=="0.11.0"
    assert public_catalog()["methodCount"]==48
    assert len(METHODS)==48
def test_core_mechanical_methods():
    assert run_method("mt.vector_resultant",{"fx":3,"fy":4,"fz":0})["outputs"]["resultantN"]==5
    assert run_method("mt.axial_stress",{"forceN":1000,"areaM2":.001})["outputs"]["stressPa"]==1_000_000
    p=run_method("mt.euler_buckling",{"modulusPa":200e9,"inertiaM4":1e-6,"lengthM":2,"kFactor":1})["outputs"]["criticalLoadN"]
    assert math.isclose(p,math.pi**2*200e9*1e-6/4)
def test_core_thermal_and_fluid_methods():
    assert run_method("mt.reynolds",{"densityKgM3":1000,"velocityMps":1,"diameterM":.1,"viscosityPaS":.001})["outputs"]["reynolds"]==100000
    assert run_method("mt.carnot_efficiency",{"hotK":600,"coldK":300})["outputs"]["efficiency"]==.5
    assert run_method("mt.plane_wall_conduction",{"conductivityWmK":2,"areaM2":3,"deltaTK":10,"thicknessM":.5})["outputs"]["heatRateW"]==120
