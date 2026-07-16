from fastapi.testclient import TestClient
from app.main import app
from app.reproducibility import build_manifest, compare_manifests, verify_manifest

client = TestClient(app)

def fixture():
    request={"method":"mechanics.kinetic_energy","inputs":{"mass":10,"velocity":5},"parameters":{},"units":{"mass":"kg","velocity":"m/s"},"random_seed":42}
    response=client.post('/v1/compute/run',json=request).json()
    return request,response

def test_manifest_build_and_verify():
    request,response=fixture()
    manifest=build_manifest({"title":"KE fixture","request":request,"response":response})["manifest"]
    assert manifest["version"] == "0.28.2"
    assert len(manifest["checksums"]["requestSha256"]) == 64
    assert verify_manifest({"manifest":manifest})["ok"] is True

def test_tamper_detection():
    request,response=fixture(); manifest=build_manifest({"request":request,"response":response})["manifest"]
    manifest["response"]["outputs"]["kineticEnergyJ"] = 126
    assert verify_manifest({"manifest":manifest})["ok"] is False

def test_compare_reproduced_and_changed():
    request,response=fixture(); left=build_manifest({"request":request,"response":response})["manifest"]
    right=build_manifest({"request":request,"response":response,"parentRunId":left["id"]})["manifest"]
    assert compare_manifests({"left":left,"right":right})["comparison"]["status"] == "reproduced"
    right["response"]["outputs"]["kineticEnergyJ"] = 130
    assert compare_manifests({"left":left,"right":right})["comparison"]["status"] == "changed"

def test_reproducibility_api():
    request,response=fixture()
    health=client.get('/v1/reproducibility/health').json()
    assert health["version"] == "0.28.2"
    built=client.post('/v1/reproducibility/manifest',json={"request":request,"response":response}).json()
    assert built["ok"] is True
    verified=client.post('/v1/reproducibility/verify',json={"manifest":built["manifest"]}).json()
    assert verified["ok"] is True
