import math
from app.design_studies import analyze_results, build_batch, generate_design, health, recommend_design, verify

FACTORS=[{"name":"temperature","type":"continuous","low":10,"high":30},{"name":"pressure","type":"continuous","low":1,"high":3}]

def test_health():
    assert health()["ok"] and health()["version"]=="0.30.1"

def test_full_factorial_and_hash():
    out=generate_design({"title":"screen","designType":"full-factorial","factors":FACTORS})
    assert out["matrix"]["runCount"]==4
    assert verify({"record":out["matrix"]})["ok"]

def test_latin_hypercube_is_deterministic():
    a=generate_design({"title":"lhs","designType":"latin-hypercube","runBudget":8,"seed":7,"factors":FACTORS})["matrix"]
    b=generate_design({"title":"lhs","designType":"latin-hypercube","runBudget":8,"seed":7,"factors":FACTORS})["matrix"]
    assert a["rows"]==b["rows"] and a["runCount"]==8

def test_response_surface_analysis():
    matrix=generate_design({"title":"surface","designType":"central-composite","centerPoints":3,"factors":FACTORS})["matrix"]
    responses=[]
    for row in matrix["rows"]:
        x=row["coded"]["temperature"]; y=row["coded"]["pressure"]
        responses.append(5+2*x-3*y+1.5*x*x+0.5*x*y)
    result=analyze_results({"matrix":matrix,"responses":responses,"objective":"maximize","responseName":"yield"})
    assert result["rSquared"]>0.999999 and result["model"]=="quadratic-response-surface"
    assert result["bestObserved"]["response"]==max(responses)

def test_recommendation_and_batch():
    rec=recommend_design({"purpose":"space-filling","runBudget":12,"factors":FACTORS})
    assert rec["recommendedDesign"]=="latin-hypercube"
    matrix=generate_design({"title":"batch","designType":"full-factorial","factors":FACTORS})["matrix"]
    batch=build_batch({"matrix":matrix,"methodId":"simulation.parameter_sweep","projectId":"p1","parameterMappings":{"temperature":"temp"}})
    assert batch["jobCount"]==4 and batch["jobs"][0]["parameters"].get("temp") is not None
    assert verify({"record":batch})["ok"]

def test_api_routes():
    from fastapi.testclient import TestClient
    from app.main import app
    client=TestClient(app)
    health_response=client.get('/v1/design-studies/health')
    assert health_response.status_code==200
    assert health_response.json()['version']=='0.30.1'
    response=client.post('/v1/design-studies/generate',json={"title":"api","designType":"full-factorial","factors":FACTORS})
    assert response.status_code==200, response.text
    assert response.json()['matrix']['runCount']==4
