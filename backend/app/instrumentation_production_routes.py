from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from .instrumentation_production_health import instrumentation_production_health

router = APIRouter(tags=["instrumentation-production-reliability"])


@router.get("/v1/instrumentation/production-health")
def production_health_route() -> dict[str, Any]:
    return instrumentation_production_health()
