from __future__ import annotations

from app.instrumentation_production_health import VERSION, instrumentation_production_health


def test_instrumentation_production_health_is_ready() -> None:
    health = instrumentation_production_health()
    assert VERSION == "0.25.1"
    assert health["ok"] is True
    assert health["status"] == "ready"
    assert health["release"] == "0.25.1"
    assert health["engineRelease"] == "0.25.0"
    assert health["methodCount"] == 48
    assert health["benchmarkCount"] == 48
    assert health["categoryCount"] == 8
    assert health["recordTypeCount"] == 9
    assert health["connectionProfileCount"] == 8
    assert health["qualityFlagCount"] == 8
    assert all(health["assets"].values())
    assert health["boundaries"]["automaticLocalDeviceAccess"] is False
    assert health["boundaries"]["localFirstManualOperation"] is True
