from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .instrumentation_live_visualization import (
    LiveVisualizationError,
    VERSION,
    build_snapshot,
    contract,
    execute,
)

router = APIRouter(tags=["instrumentation-live-visualization"])


@router.get("/v1/instrumentation/live/methods")
def methods() -> dict[str, Any]:
    return contract()


@router.get("/v1/instrumentation/live/health")
def health() -> dict[str, Any]:
    data = contract()
    ready = (
        data.get("version") == VERSION
        and len(data.get("modes", [])) == 8
        and len(data.get("analysisMethods", [])) == 16
        and len(data.get("benchmarks", [])) == 16
        and len(data.get("channelTemplates", [])) == 8
        and len(data.get("connectionStates", [])) == 8
        and len(data.get("eventTypes", [])) == 8
    )
    return {
        "ok": ready,
        "status": "ready" if ready else "contract-incomplete",
        "release": VERSION,
        "modeCount": len(data.get("modes", [])),
        "analysisMethodCount": len(data.get("analysisMethods", [])),
        "benchmarkCount": len(data.get("benchmarks", [])),
        "channelTemplateCount": len(data.get("channelTemplates", [])),
        "connectionStateCount": len(data.get("connectionStates", [])),
        "eventTypeCount": len(data.get("eventTypes", [])),
        "preservedEngine": data.get("preservedEngine", {}),
        "productionLayer": data.get("productionLayer", {}),
        "boundaries": data.get("responsibleUse", {}).get("boundaries", {}),
    }


@router.post("/v1/instrumentation/live/analyze")
def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return execute(
            str(payload.get("methodId") or ""),
            payload.get("inputs") or {},
        )
    except LiveVisualizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/instrumentation/live/snapshot")
def snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return build_snapshot(
            payload.get("records") or [],
            payload.get("thresholds") or {},
            payload.get("maximumGapSeconds", 10),
            payload.get("connectionState", "disconnected"),
        )
    except LiveVisualizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/v1/instrumentation/live/events")
def events(payload: dict[str, Any]) -> dict[str, Any]:
    result = snapshot(payload)
    return {
        "schema": "sc-lab-instrumentation-live-events/1.0",
        "version": VERSION,
        "events": result["events"],
        "eventCount": len(result["events"]),
    }


@router.post("/v1/instrumentation/live/replay")
def replay(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload.get("records") or []
    speed = float(payload.get("speed") or 1)
    if speed <= 0:
        raise HTTPException(status_code=422, detail="speed must be greater than zero.")
    return {
        "schema": "sc-lab-instrumentation-replay-plan/1.0",
        "version": VERSION,
        "recordCount": len(records),
        "speed": speed,
        "records": records,
    }
