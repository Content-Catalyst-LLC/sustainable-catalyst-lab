from __future__ import annotations
import json, math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
VERSION="0.12.0"
CATALOG_PATH=Path(__file__).resolve().parents[2]/"contracts"/"civil-infrastructure-methods.json"
SAFE={"pi":math.pi,"g":9.80665,"sqrt":math.sqrt,"log":math.log,"log10":math.log10,"exp":math.exp,"abs":abs,"min":min,"max":max,"pow":pow,"sin":math.sin,"cos":math.cos,"tan":math.tan}
class CivilInfrastructureError(ValueError): pass
CATALOG=json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS={item["id"]:item for item in CATALOG["methods"]}
def public_catalog()->dict[str,Any]: return CATALOG
def _finite(value:Any,name:str)->float:
    try: number=float(value)
    except (TypeError,ValueError) as exc: raise CivilInfrastructureError(f"{name} must be finite.") from exc
    if not math.isfinite(number): raise CivilInfrastructureError(f"{name} must be finite.")
    return number
def run_method(method_id:str,inputs:dict[str,Any])->dict[str,Any]:
    method=METHODS.get(method_id)
    if method is None: raise CivilInfrastructureError(f"Unknown civil method: {method_id}")
    clean={field["key"]:_finite(inputs.get(field["key"]),field["label"]) for field in method["inputs"]}
    scope=dict(SAFE);scope.update(clean);outputs={};units={}
    for key,spec in method["outputs"].items():
        expression=spec["expression"]
        if not all(ch.isalnum() or ch in "_+-*/().,<>=!? : " for ch in expression): raise CivilInfrastructureError("Catalog expression contains unsupported characters.")
        try: value=float(eval(expression,{"__builtins__":{}},scope))
        except Exception as exc: raise CivilInfrastructureError(f"Could not evaluate {key}: {exc}") from exc
        if not math.isfinite(value): raise CivilInfrastructureError(f"{key} is not finite.")
        outputs[key]=value;units[key]=spec["unit"]
    return {"schema":"sc-lab-civil-infrastructure-analysis/1.0","version":VERSION,"methodId":method_id,"methodVersion":VERSION,"category":method["category"],"title":method["title"],"equation":method["equation"],"inputs":clean,"outputs":outputs,"outputUnits":units,"assumptions":method["assumptions"],"warnings":[],"validation":{"status":"screened"},"audit":{"createdAt":datetime.now(timezone.utc).isoformat(),"engine":"sc-lab-civil-infrastructure-python","release":VERSION}}
