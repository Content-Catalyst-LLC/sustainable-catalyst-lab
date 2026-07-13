from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException

from .circular_economy_industrial_ecology import (
    CircularEconomyIndustrialEcologyError,
    public_catalog,
    run_method,
)

router = APIRouter(tags=["circular-economy-industrial-ecology"])


def require_circular_economy_key(
    x_sc_lab_key: str | None = Header(default=None),
) -> None:
    expected = os.getenv("SC_LAB_API_KEY", "").strip()

    if expected and x_sc_lab_key != expected:
        raise HTTPException(
            status_code=401,
            detail="A valid X-SC-Lab-Key header is required.",
        )


@router.get(
    "/v1/circular-economy/methods",
    dependencies=[Depends(require_circular_economy_key)],
)
def circular_economy_methods() -> dict[str, Any]:
    return public_catalog()


@router.post(
    "/v1/circular-economy/run",
    dependencies=[Depends(require_circular_economy_key)],
)
def circular_economy_run(
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
    except CircularEconomyIndustrialEcologyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
