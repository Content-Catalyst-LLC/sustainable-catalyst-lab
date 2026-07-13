from __future__ import annotations

from app.bioprocess_production_health import (
    VERSION,
    production_health,
)


def test_production_health_is_ready() -> None:
    health = production_health()

    assert VERSION == "0.22.1"
    assert health["ok"] is True
    assert health["status"] == "ready"
    assert health["release"] == "0.22.1"
    assert health["engineRelease"] == "0.22.0"
    assert health["methodCount"] == 48
    assert health["benchmarkCount"] == 48
    assert health["categoryCount"] == 8
    assert health["assets"]["contract"] is True
    assert health["assets"]["engine"] is True
    assert health["assets"]["routes"] is True
