from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from .bioprocess_production_health import (
    production_health,
)

router = APIRouter(
    tags=["bioprocess-production-reliability"]
)


@router.get("/v1/bioprocess/production-health")
def bioprocess_production_health() -> dict[str, Any]:
    return production_health()
