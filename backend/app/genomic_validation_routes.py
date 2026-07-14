from fastapi import APIRouter,HTTPException
from .genomic_validation_sequence_provenance import GenomicValidationError,contract,create_dossier,create_manifest,create_record,evaluate,verify_ledger
router=APIRouter(tags=["genomic-validation-provenance"])
@router.get("/v1/genomics/validation/profiles")
def profiles():return contract()
@router.post("/v1/genomics/validation/evaluate")
def evaluate_route(payload):
 try:return evaluate(str(payload.get("profileId") or ""),payload.get("rows") or [],payload.get("thresholds") or {})
 except GenomicValidationError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
@router.post("/v1/genomics/provenance/manifest")
def manifest_route(payload):return create_manifest(payload.get("sequences"),payload.get("metadata"),payload.get("reference"),payload.get("pipeline"),payload.get("variants"),payload.get("annotations"))
@router.post("/v1/genomics/provenance/record")
def record_route(payload):
 try:return create_record(payload.get("payload"),payload.get("metadata") or {},payload.get("previousHash"))
 except GenomicValidationError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
@router.post("/v1/genomics/provenance/verify")
def verify_route(payload):return verify_ledger(payload.get("records") or [])
@router.post("/v1/genomics/validation/dossier")
def dossier_route(payload):return create_dossier(payload.get("validationResults") or [],payload.get("manifest") or {},payload.get("records") or [],payload.get("disposition"))
