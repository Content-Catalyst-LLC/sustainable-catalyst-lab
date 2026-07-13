from __future__ import annotations

from app.biosignal_production_health import (
    VERSION,
    biosignal_production_health,
)


def test_biosignal_production_health_is_ready() -> None:
    health = biosignal_production_health()

    assert VERSION == "0.23.1"
    assert health["ok"] is True
    assert health["status"] == "ready"
    assert health["release"] == "0.23.1"
    assert health["engineRelease"] == "0.23.0"
    assert health["methodCount"] == 48
    assert health["benchmarkCount"] == 48
    assert health["categoryCount"] == 8
    assert health["assets"]["contract"] is True
    assert health["assets"]["engine"] is True
    assert health["assets"]["engineRoutes"] is True
    assert health["assets"]["productionHealth"] is True
    assert health["assets"]["productionRoutes"] is True
    assert health["responsibleUse"]["clinicalUse"] is False
