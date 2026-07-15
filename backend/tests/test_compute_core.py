from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)


def test_health():
    response=client.get('/health')
    assert response.status_code==200
    assert response.json()['version']=='0.28.0'
    assert response.json()['architecture']=='python-compute-core'


def test_capabilities_and_registry():
    caps=client.get('/v1/capabilities')
    assert caps.status_code==200
    assert caps.json()['security']['registeredMethodsOnly'] is True
    methods=client.get('/v1/methods').json()['methods']
    assert len(methods)>=10
    assert any(row['id']=='statistics.linear_regression' for row in methods)


def test_kinetic_with_provenance():
    response=client.post('/v1/compute/run',json={'method':'mechanics.kinetic_energy','inputs':{'mass':10,'velocity':5}})
    assert response.status_code==200, response.text
    body=response.json()
    assert body['outputs']['kineticEnergyJ']==125
    assert body['outputs']['momentumKgMs']==50
    assert len(body['provenance']['input_sha256'])==64
    assert body['validation']['registeredMethod'] is True


def test_linear_regression():
    response=client.post('/v1/compute/run',json={'method':'statistics.linear_regression','inputs':{'x':[1,2,3,4],'y':[2,4,6,8]}})
    assert response.status_code==200
    assert abs(response.json()['outputs']['slope']-2)<1e-12
    assert response.json()['outputs']['rSquared']>0.999999


def test_seeded_monte_carlo_is_reproducible():
    payload={'method':'simulation.monte_carlo_pi','inputs':{'samples':10000},'random_seed':42}
    left=client.post('/v1/compute/run',json=payload).json()['outputs']
    right=client.post('/v1/compute/run',json=payload).json()['outputs']
    assert left==right


def test_unknown_method_rejected():
    response=client.post('/v1/compute/run',json={'method':'unknown.method','inputs':{}})
    assert response.status_code==404


def test_legacy_execute_alias():
    response=client.post('/v1/execute',json={'methodId':'kinetic','language':'python','inputs':{'mass':2,'velocity':3}})
    assert response.status_code==200
    assert response.json()['outputs']['kineticEnergyJ']==9


def test_report_pdf():
    response=client.post('/v1/reports/pdf',json={'title':'Test report','analyses':[{'title':'Run 1'}]})
    assert response.status_code==200
    assert response.json()['sizeBytes']>500
