from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .bioprocess_validation_provenance import (
    BioprocessValidationError,
    contract,
    create_dossier,
    create_record,
    evaluate,
    verify_ledger,
)

router = APIRouter(
    tags=["bioprocess-validation-provenance"]
)


@router.get("/v1/bioprocess/validation/profiles")
def profiles() -> dict[str, Any]:
    return contract()


@router.post("/v1/bioprocess/validation/evaluate")
def evaluate_route(
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        return evaluate(
            str(payload.get("profileId") or ""),
            payload.get("rows") or [],
            payload.get("thresholds") or {},
        )
    except BioprocessValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.post("/v1/bioprocess/provenance/record")
def record_route(
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        return create_record(
            payload.get("payload"),
            payload.get("metadata") or {},
            payload.get("previousHash"),
        )
    except BioprocessValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.post("/v1/bioprocess/provenance/verify")
def verify_route(
    payload: dict[str, Any],
) -> dict[str, Any]:
    return verify_ledger(
        payload.get("records") or []
    )


@router.post("/v1/bioprocess/validation/dossier")
def dossier_route(
    payload: dict[str, Any],
) -> dict[str, Any]:
    return create_dossier(
        payload.get("validationResults") or [],
        payload.get("batch") or {},
        payload.get("records") or [],
        payload.get("disposition"),
    )
