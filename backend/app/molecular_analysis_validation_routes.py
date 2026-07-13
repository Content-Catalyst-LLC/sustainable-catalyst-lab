from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .molecular_analysis_validation import (
    MolecularValidationError,
    create_provenance_record,
    profiles_contract,
    validate_profile,
    verify_ledger,
)

router = APIRouter(
    tags=["molecular-analysis-validation-provenance"]
)


@router.get("/v1/biochemistry/validation/profiles")
def molecular_validation_profiles() -> dict[str, Any]:
    return profiles_contract()


@router.post("/v1/biochemistry/validation/run")
def molecular_validation_run(
    payload: dict[str, Any],
) -> dict[str, Any]:
    profile_id = str(payload.get("profileId") or "")
    rows = payload.get("rows") or []
    thresholds = payload.get("thresholds") or {}

    if not isinstance(rows, list):
        raise HTTPException(
            status_code=422,
            detail="rows must be an array.",
        )

    if not isinstance(thresholds, dict):
        raise HTTPException(
            status_code=422,
            detail="thresholds must be an object.",
        )

    try:
        validation = validate_profile(
            profile_id,
            rows,
            thresholds,
        )
    except MolecularValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "schema": (
            "sc-lab-molecular-analysis-validation-dossier/1.0"
        ),
        "version": "0.21.3",
        "methodId": payload.get("methodId"),
        "profileId": profile_id,
        "decision": validation["decision"],
        "validation": validation,
        "dataset": {
            "rowCount": len(rows),
            "rows": rows,
        },
        "audit": {
            "engine": (
                "sc-lab-molecular-validation-python"
            ),
            "release": "0.21.3",
            "analysisEngineVersion": "0.21.0",
        },
    }


@router.post("/v1/biochemistry/provenance/record")
def molecular_provenance_record(
    payload: dict[str, Any],
) -> dict[str, Any]:
    if "payload" not in payload:
        raise HTTPException(
            status_code=422,
            detail="payload is required.",
        )

    metadata = payload.get("metadata") or {}

    if not isinstance(metadata, dict):
        raise HTTPException(
            status_code=422,
            detail="metadata must be an object.",
        )

    return create_provenance_record(
        payload["payload"],
        metadata,
        payload.get("previousHash"),
    )


@router.post("/v1/biochemistry/provenance/verify")
def molecular_provenance_verify(
    payload: dict[str, Any],
) -> dict[str, Any]:
    records = payload.get("records") or []

    if not isinstance(records, list):
        raise HTTPException(
            status_code=422,
            detail="records must be an array.",
        )

    return verify_ledger(records)
