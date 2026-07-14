from fastapi import APIRouter
from .genomics_production_health import genomics_production_health
router=APIRouter(tags=["genomics-production"])
@router.get("/v1/genomics/production-health")
def health():return genomics_production_health()
