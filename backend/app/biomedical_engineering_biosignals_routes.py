from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .biomedical_engineering_biosignals import (
    BiosignalError,
    analyze_signal,
    batch_execute,
    catalog,
    execute,
)

router = APIRouter(
    tags=["biomedical-engineering-biosignals"]
)


@router.get("/v1/biomedical/biosignals/methods")
def methods() -> dict[str, Any]:
    return catalog()


@router.get("/v1/biomedical/biosignals/health")
def health() -> dict[str, Any]:
    data = catalog()
    ready = (
        data.get("version") == "0.23.0"
        and len(data.get("methods", [])) == 48
        and len(data.get("benchmarks", [])) == 48
        and len(data.get("categories", [])) == 8
    )

    return {
        "ok": ready,
        "status": "ready" if ready else "contract-incomplete",
        "release": "0.23.0",
        "methodCount": len(data.get("methods", [])),
        "benchmarkCount": len(data.get("benchmarks", [])),
        "categoryCount": len(data.get("categories", [])),
    }


@router.post("/v1/biomedical/biosignals/run")
def run(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return execute(
            str(payload.get("methodId") or ""),
            payload.get("inputs") or {},
        )
    except BiosignalError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.post("/v1/biomedical/biosignals/analyze")
def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return analyze_signal(
            payload.get("samples") or [],
            payload.get("sampleRateHz"),
        )
    except BiosignalError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.post("/v1/biomedical/biosignals/batch")
def batch(payload: dict[str, Any]) -> dict[str, Any]:
    return batch_execute(
        payload.get("rows") or []
    )
