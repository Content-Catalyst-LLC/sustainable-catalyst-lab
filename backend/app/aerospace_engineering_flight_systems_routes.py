from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException

from .aerospace_engineering_flight_systems import (
    AerospaceEngineeringFlightSystemsError,
    public_catalog,
    run_method,
)

router = APIRouter(tags=["aerospace-engineering-flight-systems"])


def require_aerospace_flight_key(
    x_sc_lab_key: str | None = Header(default=None),
) -> None:
    expected = os.getenv("SC_LAB_API_KEY", "").strip()

    if expected and x_sc_lab_key != expected:
        raise HTTPException(
            status_code=401,
            detail="A valid X-SC-Lab-Key header is required.",
        )


@router.get(
    "/v1/aerospace-flight/methods",
    dependencies=[Depends(require_aerospace_flight_key)],
)
def aerospace_flight_methods() -> dict[str, Any]:
    return public_catalog()


@router.post(
    "/v1/aerospace-flight/run",
    dependencies=[Depends(require_aerospace_flight_key)],
)
def aerospace_flight_run(
    payload: dict[str, Any],
) -> dict[str, Any]:
    method_id = str(payload.get("methodId") or "")
    inputs = payload.get("inputs") or {}

    if not method_id or not isinstance(inputs, dict):
        raise HTTPException(
            status_code=422,
            detail="methodId and numerical inputs are required.",
        )

    try:
        return run_method(method_id, inputs)
    except AerospaceEngineeringFlightSystemsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
