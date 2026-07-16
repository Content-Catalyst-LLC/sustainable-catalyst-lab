from __future__ import annotations

import importlib.metadata
import platform
import sys
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from math import isfinite
from typing import Any

from .config import settings
from .provenance import digest
from .registry import catalog

VERSION = "0.28.2"
SCHEMA = "sc-lab-reproducible-run/0.28.2"
BUNDLE_SCHEMA = "sc-lab-reproducibility-bundle/0.28.2"
MAX_COMPARE_NODES = 20000

class ReproducibilityError(ValueError):
    pass

def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def _packages() -> dict[str, str]:
    names = ["fastapi", "pydantic", "numpy", "scipy", "pandas", "sympy", "reportlab"]
    out: dict[str, str] = {}
    for name in names:
        try: out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: out[name] = "unavailable"
    return out

def environment_fingerprint() -> dict[str, Any]:
    methods = [{"id": row["id"], "version": row["version"]} for row in catalog()]
    payload = {
        "serviceVersion": settings.version,
        "pythonVersion": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": _packages(),
        "registeredMethodsSha256": digest(methods),
    }
    return {**payload, "sha256": digest(payload)}

def _request_view(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "method": str(request.get("method") or ""),
        "version": request.get("version"),
        "inputs": request.get("inputs") or {},
        "parameters": request.get("parameters") or {},
        "units": request.get("units") or {},
        "project_id": request.get("project_id") or request.get("projectId"),
        "requested_outputs": request.get("requested_outputs") or request.get("requestedOutputs") or ["summary", "values"],
        "random_seed": request.get("random_seed") if request.get("random_seed") is not None else request.get("randomSeed"),
        "execution_target": request.get("execution_target") or "automatic",
        "governance": request.get("governance") or {},
    }

def _response_view(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": bool(response.get("ok", True)),
        "method": response.get("method"),
        "method_version": response.get("method_version") or response.get("methodVersion"),
        "outputs": response.get("outputs") or response.get("result") or {},
        "summary": response.get("summary") or "",
        "warnings": response.get("warnings") or [],
        "validation": response.get("validation") or {},
        "governance": response.get("governance") or {},
        "provenance": response.get("provenance") or {},
    }

def build_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    request = deepcopy(_request_view(payload.get("request") or {}))
    response = deepcopy(_response_view(payload.get("response") or {}))
    if not request["method"]:
        raise ReproducibilityError("A registered method identifier is required.")
    if not response["outputs"] and not response["provenance"]:
        raise ReproducibilityError("A completed compute response is required.")
    env = environment_fingerprint()
    checksums = {
        "requestSha256": digest(request),
        "outputsSha256": digest(response["outputs"]),
        "responseSha256": digest(response),
        "environmentSha256": env["sha256"],
    }
    provenance = response.get("provenance") or {}
    warnings = list(dict.fromkeys([str(x) for x in (response.get("warnings") or [])]))
    manifest = {
        "schema": SCHEMA,
        "version": VERSION,
        "recordType": "reproducible-run",
        "collection": "reproducibleRuns",
        "id": str(payload.get("id") or uuid.uuid4()),
        "title": str(payload.get("title") or f"{request['method']} reproducible run")[:200],
        "status": "completed" if response.get("ok", True) else "failed",
        "createdAt": str(payload.get("createdAt") or _utc()),
        "projectId": payload.get("projectId") or request.get("project_id"),
        "method": request["method"],
        "methodVersion": response.get("method_version") or request.get("version") or provenance.get("method_version"),
        "serviceVersion": provenance.get("service_version") or settings.version,
        "request": request,
        "response": response,
        "environment": env,
        "checksums": checksums,
        "warnings": warnings,
        "errors": list(payload.get("errors") or []),
        "history": list(payload.get("history") or []),
        "parentRunId": payload.get("parentRunId"),
        "notes": str(payload.get("notes") or "")[:4000],
    }
    manifest["manifestSha256"] = digest({k:v for k,v in manifest.items() if k != "manifestSha256"})
    return {"ok": True, "version": VERSION, "manifest": manifest}

def verify_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    manifest = payload.get("manifest") if isinstance(payload.get("manifest"), dict) else payload
    if manifest.get("schema") != SCHEMA:
        raise ReproducibilityError("Unsupported reproducible-run schema.")
    request = manifest.get("request") or {}
    response = manifest.get("response") or {}
    env = manifest.get("environment") or {}
    expected = manifest.get("checksums") or {}
    actual = {
        "requestSha256": digest(request),
        "outputsSha256": digest(response.get("outputs") or {}),
        "responseSha256": digest(response),
        "environmentSha256": digest({k:v for k,v in env.items() if k != "sha256"}),
    }
    checks = {key: {"expected": expected.get(key), "actual": value, "ok": expected.get(key) == value} for key,value in actual.items()}
    body_without = {k:v for k,v in manifest.items() if k != "manifestSha256"}
    manifest_actual = digest(body_without)
    checks["manifestSha256"] = {"expected": manifest.get("manifestSha256"), "actual": manifest_actual, "ok": manifest.get("manifestSha256") == manifest_actual}
    provenance = response.get("provenance") or {}
    provenance_checks = {
        "inputSha256": {"expected": provenance.get("input_sha256") or provenance.get("inputSha256"), "actual": digest(request.get("inputs") or {}), "informational": True},
        "resultSha256": {"expected": provenance.get("result_sha256") or provenance.get("resultSha256"), "actual": digest(response.get("outputs") or {}), "informational": True},
    }
    return {"ok": all(row["ok"] for row in checks.values()), "version": VERSION, "checks": checks, "provenanceChecks": provenance_checks}

def _flatten(value: Any, prefix: str = "", out: dict[str, Any] | None = None, counter: list[int] | None = None) -> dict[str, Any]:
    if out is None: out = {}
    if counter is None: counter = [0]
    counter[0] += 1
    if counter[0] > MAX_COMPARE_NODES: raise ReproducibilityError("Run comparison exceeds the node limit.")
    if isinstance(value, dict):
        for key in sorted(value): _flatten(value[key], f"{prefix}.{key}" if prefix else str(key), out, counter)
    elif isinstance(value, list):
        for i,item in enumerate(value): _flatten(item, f"{prefix}[{i}]", out, counter)
    else: out[prefix or "$"] = value
    return out

def compare_manifests(payload: dict[str, Any]) -> dict[str, Any]:
    left = payload.get("left") or {}
    right = payload.get("right") or {}
    abs_tol = max(0.0, float(payload.get("absoluteTolerance", 1e-9)))
    rel_tol = max(0.0, float(payload.get("relativeTolerance", 1e-7)))
    left_flat = _flatten((left.get("response") or {}).get("outputs") or {})
    right_flat = _flatten((right.get("response") or {}).get("outputs") or {})
    paths = sorted(set(left_flat) | set(right_flat))
    differences=[]; numeric_count=0; within_count=0
    for path in paths:
        a=left_flat.get(path); b=right_flat.get(path)
        row={"path":path,"left":a,"right":b,"equal":a==b}
        if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool) and isfinite(float(a)) and isfinite(float(b)):
            numeric_count += 1
            delta=abs(float(a)-float(b)); allowed=max(abs_tol,rel_tol*max(abs(float(a)),abs(float(b)),1.0)); ok=delta<=allowed
            row.update({"absoluteDifference":delta,"allowedDifference":allowed,"withinTolerance":ok})
            if ok: within_count += 1
        else: row["withinTolerance"] = row["equal"]
        if not row["withinTolerance"]: differences.append(row)
    same_request = digest(left.get("request") or {}) == digest(right.get("request") or {})
    same_environment = (left.get("environment") or {}).get("sha256") == (right.get("environment") or {}).get("sha256")
    comparison={
        "schema":"sc-lab-run-comparison/0.28.2","version":VERSION,"recordType":"run-comparison","collection":"runComparisons","id":str(uuid.uuid4()),"createdAt":_utc(),
        "leftRunId":left.get("id"),"rightRunId":right.get("id"),"sameMethod":left.get("method")==right.get("method"),
        "sameRequest":same_request,"sameEnvironment":same_environment,"numericValueCount":numeric_count,"numericWithinTolerance":within_count,
        "differenceCount":len(differences),"differences":differences[:500],"absoluteTolerance":abs_tol,"relativeTolerance":rel_tol,
    }
    comparison["status"] = "reproduced" if comparison["sameMethod"] and same_request and not differences else "changed"
    comparison["sha256"] = digest(comparison)
    return {"ok": True, "version": VERSION, "comparison": comparison}

def health() -> dict[str, Any]:
    return {"ok":True,"status":"ready","version":VERSION,"schema":SCHEMA,"bundleSchema":BUNDLE_SCHEMA,"environmentFingerprint":True,"manifestVerification":True,"runComparison":True,"arbitraryCode":False}
