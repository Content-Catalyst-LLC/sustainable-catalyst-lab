from __future__ import annotations

import os

from fastapi.testclient import TestClient

from app.main import app


def test_api_key_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("SC_LAB_COMPUTE_API_KEY", "test-secret")
    client = TestClient(app)
    denied = client.get("/v1/methods")
    assert denied.status_code == 401
    allowed = client.get("/v1/methods", headers={"X-SC-Lab-Key": "test-secret"})
    assert allowed.status_code == 200
    monkeypatch.delenv("SC_LAB_COMPUTE_API_KEY", raising=False)
