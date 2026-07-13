from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException

from .comparative_economics_development_systems import (
    ComparativeEconomicsDevelopmentSystemsError,
    public_catalog,
    run_method,
)

router = APIRouter(tags=["comparative-economics-development-systems"])


def require_development_economics_key(
    x_sc_lab_key: str | None = Header(default=None),
) -> None:
    expected = os.getenv("SC_LAB_API_KEY", "").strip()

    if expected and x_sc_lab_key != expected:
        raise HTTPException(
            status_code=401,
            detail="A valid X-SC-Lab-Key header is required.",
        )


@router.get(
    "/v1/development-economics/methods",
    dependencies=[Depends(require_development_economics_key)],
)
def development_economics_methods() -> dict[str, Any]:
    return public_catalog()


@router.post(
    "/v1/development-economics/run",
    dependencies=[Depends(require_development_economics_key)],
)
def development_economics_run(
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
    except ComparativeEconomicsDevelopmentSystemsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
