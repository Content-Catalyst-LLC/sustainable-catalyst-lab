from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from .biochemistry_batch_analysis import (
    BiochemistryBatchError,
    run_batch,
)

router = APIRouter(
    tags=["biochemistry-visualization-batch"]
)

PRESETS_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "biochemistry-visualization-presets-v0212.json"
)


@router.get("/v1/biochemistry/visualizations")
def biochemistry_visualizations() -> dict[str, Any]:
    return json.loads(
        PRESETS_PATH.read_text(encoding="utf-8")
    )


@router.post("/v1/biochemistry/batch")
def biochemistry_batch(
    payload: dict[str, Any],
) -> dict[str, Any]:
    method_id = str(payload.get("methodId") or "")
    rows = payload.get("rows") or []

    if not isinstance(rows, list):
        raise HTTPException(
            status_code=422,
            detail="rows must be an array.",
        )

    try:
        return run_batch(method_id, rows)
    except BiochemistryBatchError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
