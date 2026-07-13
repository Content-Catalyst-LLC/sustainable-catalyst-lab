from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException

from .architecture_building import (
    ArchitectureBuildingError,
    public_catalog,
    run_method,
)

router = APIRouter(tags=["architecture-building"])


def require_architecture_key(
    x_sc_lab_key: str | None = Header(default=None),
) -> None:
    expected = os.getenv("SC_LAB_API_KEY", "").strip()

    if expected and x_sc_lab_key != expected:
        raise HTTPException(
            status_code=401,
            detail="A valid X-SC-Lab-Key header is required.",
        )


@router.get("/v1/architecture/methods")
def architecture_methods(
    x_sc_lab_key: str | None = Header(default=None),
) -> dict[str, Any]:
    require_architecture_key(x_sc_lab_key)
    return public_catalog()


@router.post("/v1/architecture/run")
def architecture_run(
    payload: dict[str, Any],
    x_sc_lab_key: str | None = Header(default=None),
) -> dict[str, Any]:
    require_architecture_key(x_sc_lab_key)

    method_id = str(payload.get("methodId") or "")
    inputs = payload.get("inputs") or {}

    if not method_id or not isinstance(inputs, dict):
        raise HTTPException(
            status_code=422,
            detail="methodId and numerical inputs are required.",
        )

    try:
        return run_method(method_id, inputs)
    except ArchitectureBuildingError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
