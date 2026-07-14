from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .instrumentation_validation_custody import (
    InstrumentationValidationError,
    VERSION,
    contract,
    create_custody_event,
    create_dossier,
    create_manifest,
    execute,
    verify_custody_chain,
)

router = APIRouter(tags=["instrumentation-validation-custody"])


@router.get("/v1/instrumentation/validation/profiles")
def profiles() -> dict[str, Any]:
    return contract()


@router.get("/v1/instrumentation/validation/health")
def health() -> dict[str, Any]:
    data = contract()
    ready = (
        data.get("version") == VERSION
        and len(data.get("validationProfiles", [])) == 8
        and len(data.get("acceptanceStates", [])) == 8
        and len(data.get("provenanceEventTypes", [])) == 8
        and len(data.get("deviationTypes", [])) == 8
        and len(data.get("analysisMethods", [])) == 16
        and len(data.get("benchmarks", [])) == 16
    )
    return {
        "ok": ready,
        "status": "ready" if ready else "contract-incomplete",
        "release": VERSION,
        "validationProfileCount": len(data.get("validationProfiles", [])),
        "acceptanceStateCount": len(data.get("acceptanceStates", [])),
        "eventTypeCount": len(data.get("provenanceEventTypes", [])),
        "deviationTypeCount": len(data.get("deviationTypes", [])),
        "analysisMethodCount": len(data.get("analysisMethods", [])),
        "benchmarkCount": len(data.get("benchmarks", [])),
        "preservedInstrumentation": data.get("preservedInstrumentation", {}),
        "liveLayer": data.get("liveLayer", {}),
        "boundaries": data.get("responsibleUse", {}).get("boundaries", {}),
    }


@router.post("/v1/instrumentation/validation/evaluate")
def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return execute(
            str(payload.get("methodId") or ""),
            payload.get("inputs") or {},
        )
    except InstrumentationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/instrumentation/validation/manifest")
def manifest(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return create_manifest(
            payload.get("components") or {},
            payload.get("metadata") or {},
        )
    except InstrumentationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/instrumentation/custody/event")
def custody_event(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return create_custody_event(
            str(payload.get("sampleId") or ""),
            str(payload.get("action") or ""),
            str(payload.get("actor") or ""),
            str(payload.get("location") or ""),
            payload.get("timestamp"),
            str(payload.get("previousHash") or ""),
            payload.get("metadata") or {},
        )
    except InstrumentationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/instrumentation/custody/verify")
def verify(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return verify_custody_chain(payload.get("events") or [])
    except InstrumentationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/instrumentation/validation/dossier")
def dossier(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return create_dossier(
            payload.get("profileResults") or {},
            payload.get("manifest") or {},
            payload.get("custodyEvents") or [],
            payload.get("deviations") or [],
            payload.get("metadata") or {},
        )
    except InstrumentationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
