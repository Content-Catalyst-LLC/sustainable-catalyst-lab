from app.datasets import DatasetProfileError, health, profile_dataset

def test_dataset_profile_numeric_and_missing_values():
    result = profile_dataset({"rows": [{"time": 0, "value": 1.0}, {"time": 1, "value": 3.0}, {"time": 2, "value": None}], "dataDictionary": [{"name": "time", "unit": "s", "role": "time"}, {"name": "value", "unit": "m", "role": "measure"}]})
    assert result["ok"] is True
    profile = result["profile"]
    assert profile["rowCount"] == 3
    assert profile["columnCount"] == 2
    assert profile["missingCellCount"] == 1
    value = next(row for row in profile["variables"] if row["name"] == "value")
    assert value["numeric"]["mean"] == 2.0
    assert value["unit"] == "m"

def test_dataset_profile_strict_missing_policy():
    result = profile_dataset({"rows": [{"id": "a"}, {"id": ""}], "dataDictionary": [{"name": "id", "missingPolicy": "not-allowed"}]})
    assert result["validation"]["status"] == "invalid"
    assert result["validation"]["issues"][0]["code"] == "missing_not_allowed"

def test_dataset_profile_limits():
    try:
        profile_dataset({"rows": [{str(i): i for i in range(201)}]})
    except DatasetProfileError as exc:
        assert "variable" in str(exc)
    else:
        raise AssertionError("expected DatasetProfileError")

def test_dataset_health():
    body = health()
    assert body["version"] == "0.28.1"
    assert body["arbitraryCode"] is False

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dataset_profile_api():
    health_response = client.get('/v1/datasets/health')
    assert health_response.status_code == 200
    assert health_response.json()['version'] == '0.28.1'
    response = client.post('/v1/datasets/profile', json={'title':'Fixture','rows':[{'x':1,'y':2},{'x':2,'y':4}]})
    assert response.status_code == 200, response.text
    assert response.json()['profile']['rowCount'] == 2
    assert response.json()['profile']['columnCount'] == 2
