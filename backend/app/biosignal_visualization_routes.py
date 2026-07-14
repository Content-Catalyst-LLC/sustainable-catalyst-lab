from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException
from .biosignal_visualization_comparison import (
    BiosignalVisualizationError,
    VERSION,
    contract,
    execute,
    compare_runs,
    best_lag_correlation,
    annotation_coverage,
)

router = APIRouter(tags=["biosignal-visualization-comparison"])

@router.get("/v1/biomedical/biosignals/visualization/methods")
def methods() -> dict[str, Any]:
    return contract()

@router.get("/v1/biomedical/biosignals/visualization/health")
def health() -> dict[str, Any]:
    data = contract()
    ready = (
        data.get("version") == VERSION
        and len(data.get("modes", [])) == 8
        and len(data.get("analysisMethods", [])) == 16
        and len(data.get("benchmarks", [])) == 16
        and len(data.get("annotationTypes", [])) == 6
    )
    return {
        "ok": ready,
        "status": "ready" if ready else "contract-incomplete",
        "release": VERSION,
        "modeCount": len(data.get("modes", [])),
        "analysisMethodCount": len(data.get("analysisMethods", [])),
        "benchmarkCount": len(data.get("benchmarks", [])),
        "annotationTypeCount": len(data.get("annotationTypes", [])),
        "preservedEngine": data.get("preservedEngine"),
        "productionLayer": data.get("productionLayer"),
    }

@router.post("/v1/biomedical/biosignals/visualization/analyze")
def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return execute(str(payload.get("methodId") or ""), payload.get("inputs") or {})
    except BiosignalVisualizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/v1/biomedical/biosignals/visualization/compare")
def compare(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return {
            "schema":"sc-lab-biosignal-comparison/1.0",
            "version":VERSION,
            "comparison":compare_runs(payload.get("reference"), payload.get("comparison"), payload.get("sampleRateHz", 1)),
            "lag":best_lag_correlation(payload.get("reference"), payload.get("comparison"), payload.get("maxLagSamples", 10)),
        }
    except BiosignalVisualizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/v1/biomedical/biosignals/visualization/annotations")
def annotations(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return annotation_coverage(payload.get("annotations") or [], payload.get("windowStartSeconds"), payload.get("windowEndSeconds"))
    except BiosignalVisualizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
