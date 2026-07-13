from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .biotechnology_bioprocess_engineering import (
    BioprocessEngineeringError,
    VERSION,
    catalog,
    run_batch,
    run_method,
    simulate,
)

router = APIRouter(tags=["biotechnology-bioprocess-engineering"])


@router.get("/v1/bioprocess/methods")
def bioprocess_methods() -> dict[str, Any]:
    return catalog()


@router.get("/v1/bioprocess/health")
def bioprocess_health() -> dict[str, Any]:
    contract = catalog()
    return {
        "ok": True,
        "status": "ready",
        "release": VERSION,
        "methodCount": len(contract["methods"]),
        "benchmarkCount": len(contract["benchmarks"]),
        "categoryCount": len(contract["categories"]),
    }


@router.post("/v1/bioprocess/run")
def bioprocess_run(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return run_method(
            str(payload.get("methodId") or ""),
            payload.get("inputs") or {},
        )
    except BioprocessEngineeringError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/bioprocess/batch")
def bioprocess_batch(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows") or []
    if not isinstance(rows, list):
        raise HTTPException(status_code=422, detail="rows must be an array.")
    try:
        return run_batch(str(payload.get("methodId") or ""), rows)
    except BioprocessEngineeringError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/bioprocess/simulate")
def bioprocess_simulate(payload: dict[str, Any]) -> dict[str, Any]:
    parameters = payload.get("parameters") or {}
    if not isinstance(parameters, dict):
        raise HTTPException(status_code=422, detail="parameters must be an object.")
    try:
        return simulate(str(payload.get("mode") or ""), parameters)
    except BioprocessEngineeringError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
