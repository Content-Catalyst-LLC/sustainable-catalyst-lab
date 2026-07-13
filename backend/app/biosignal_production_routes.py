from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from .biosignal_production_health import (
    biosignal_production_health,
)

router = APIRouter(
    tags=["biosignal-production-reliability"]
)


@router.get("/v1/biomedical/biosignals/production-health")
def production_health_route() -> dict[str, Any]:
    return biosignal_production_health()
