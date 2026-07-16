import math
from fastapi.testclient import TestClient
from app.main import app
from app.model_calibration import calibrate, compare_models, normalize_study, verify

def rows():
    return [{"x":float(i),"z":float(i%3),"y":2.0+3.0*i-0.5*(i%3)} for i in range(1,31)]

def study(model="linear-multivariate"):
    return {"title":"Calibration fixture","modelType":model,"features":["x","z"] if model=="linear-multivariate" else ["x"],"response":"y","objective":"least-squares","holdoutFraction":0.2,"seed":7}

def test_normalize_and_hash():
    s=normalize_study(study()); assert s["version"]=="0.30.2"; assert verify(s)["ok"]

def test_linear_calibration_and_holdout():
    out=calibrate({"study":study(),"rows":rows()}); r=out["result"]
    assert r["success"] and r["holdoutMetrics"]["rmse"] < 1e-8
    assert abs(r["parameters"]["beta:x"]-3.0) < 1e-8
    assert verify(r)["ok"] and out["validation"]["passed"]

def test_polynomial_calibration():
    data=[{"x":float(i),"y":1+2*i+0.5*i*i} for i in range(-10,11)]
    out=calibrate({"study":{**study("polynomial-univariate"),"degree":2},"rows":data})
    p=out["result"]["parameters"]; assert abs(p["c0"]-1)<1e-7 and abs(p["c2"]-.5)<1e-7

def test_robust_calibration_reduces_outlier_effect():
    data=rows(); data[-1]={"x":30.0,"z":0.0,"y":1000.0}
    a=calibrate({"study":{**study(),"objective":"least-squares"},"rows":data})["result"]
    b=calibrate({"study":{**study(),"objective":"robust-huber"},"rows":data})["result"]
    assert abs(b["parameters"]["beta:x"]-3.0) < abs(a["parameters"]["beta:x"]-3.0)

def test_model_comparison():
    a=calibrate({"study":study(),"rows":rows()})["result"]
    noisy=[dict(r,y=r["y"]+(0.1 if int(r["x"])%2 else -0.1)) for r in rows()]
    b=calibrate({"study":study(),"rows":noisy})["result"]
    c=compare_models({"results":[b,a]}); assert c["recommendedResultId"]==a["id"] and verify(c)["ok"]

def test_fastapi_routes():
    with TestClient(app) as client:
        assert client.get('/v1/model-calibration/health').json()["version"]=="0.30.2"
        response=client.post('/v1/model-calibration/calibrate',json={"study":study(),"rows":rows()})
        assert response.status_code==200 and response.json()["result"]["success"]
