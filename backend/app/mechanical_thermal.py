from __future__ import annotations
import json, math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

VERSION = "0.11.0"
router = APIRouter(prefix="/v1/mechanical", tags=["mechanical-thermal"])
CATALOG_PATH = Path(__file__).resolve().parents[2] / "contracts" / "mechanical-thermal-methods.json"
def _lmtd(a: float, b: float) -> float:
    return a if abs(a-b) < 1e-12 else (a-b)/math.log(a/b)
SAFE = {
    "pi": math.pi, "g": 9.80665, "sigma": 5.670374419e-8,
    "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
    "abs": abs, "hypot": math.hypot, "min": min, "max": max, "pow": pow, "lmtd": _lmtd
}
class MechanicalThermalError(ValueError): pass
def _load() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
CATALOG = _load()
METHODS = {item["id"]: item for item in CATALOG["methods"]}
def public_catalog() -> dict[str, Any]:
    return CATALOG
def _finite(value: Any, name: str) -> float:
    try: number=float(value)
    except (TypeError,ValueError) as exc: raise MechanicalThermalError(f"{name} must be finite.") from exc
    if not math.isfinite(number): raise MechanicalThermalError(f"{name} must be finite.")
    return number
def run_method(method_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    method=METHODS.get(method_id)
    if not method: raise MechanicalThermalError(f"Unknown method: {method_id}")
    clean={field["key"]:_finite(inputs.get(field["key"]),field["label"]) for field in method["inputs"]}
    outputs={}; units={}
    scope=dict(SAFE); scope.update(clean)
    for key,spec in method["outputs"].items():
        expression=spec["expression"]
        if not all(ch.isalnum() or ch in "_+-*/().,<>=!? : " for ch in expression):
            raise MechanicalThermalError("Catalog expression contains unsupported characters.")
        try: value=float(eval(expression,{"__builtins__":{}},scope))
        except Exception as exc: raise MechanicalThermalError(f"Could not evaluate {key}: {exc}") from exc
        if not math.isfinite(value): raise MechanicalThermalError(f"{key} is not finite.")
        outputs[key]=value; units[key]=spec["unit"]
    return {
        "schema":"sc-lab-mechanical-thermal-analysis/1.0","version":VERSION,
        "methodId":method_id,"methodVersion":VERSION,"category":method["category"],
        "title":method["title"],"equation":method["equation"],"inputs":clean,
        "outputs":outputs,"outputUnits":units,"assumptions":method["assumptions"],
        "warnings":[],"validation":{"status":"screened"},
        "audit":{"createdAt":datetime.now(timezone.utc).isoformat(),
                 "engine":"sc-lab-mechanical-thermal-python","release":VERSION}
    }


@router.get("/methods")
def list_methods() -> dict[str, Any]:
    return public_catalog()


@router.post("/run")
def run(payload: dict[str, Any]) -> dict[str, Any]:
    method_id = str(payload.get("methodId") or "")
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict):
        raise HTTPException(status_code=422, detail="inputs must be an object")
    try:
        return run_method(method_id, inputs)
    except MechanicalThermalError as exc:
        status = 404 if "Unknown method" in str(exc) else 422
        raise HTTPException(status_code=status, detail=str(exc)) from exc
