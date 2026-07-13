from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import VERSION
from .catalog import CatalogError, get_method, public_catalog
from .executor import ExecutionError, compare_languages, execute_method, language_registry
from .expressions import ContractValidationError, evaluate_contract
from .jobs import jobs
from .models import CompareRequest, ExecuteRequest, HandoffValidateRequest, JobRequest, ReportRequest, ValidateRequest
from .reporting import ReportValidationError, report_pdf_response, validate_handoff, validate_report
from .electrical_embedded import router as electrical_router
from .mechanical_thermal import router as mechanical_router
from .security import rate_limit, require_api_key

app = FastAPI(
    title="Sustainable Catalyst Lab Compute API",
    version=VERSION,
    description="Curated multi-language execution for versioned Sustainable Catalyst Lab method contracts.",
    docs_url="/docs" if os.getenv("SC_LAB_ENABLE_DOCS", "true").lower() in {"1", "true", "yes"} else None,
    redoc_url=None,
)

origins = [item.strip() for item in os.getenv("SC_LAB_CORS_ORIGINS", "https://sustainablecatalyst.com").split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-SC-Lab-Key"],
)


@app.middleware("http")
async def body_and_rate_limits(request: Request, call_next: Any) -> Any:
    if request.method in {"POST", "PUT", "PATCH"}:
        length = int(request.headers.get("content-length") or 0)
        limit = 2_000_000 if request.url.path.startswith(("/v1/reports", "/v1/handoffs")) else 65536
        if length > limit:
            return JSONResponse(status_code=413, content={"detail": f"Request body exceeds {limit} bytes."})
    if request.url.path.startswith("/v1/"):
        rate_limit(request)
    return await call_next(request)


@app.exception_handler(ExecutionError)
async def execution_error_handler(_: Request, exc: ExecutionError) -> JSONResponse:
    status_code = {
        "invalid_input": 422,
        "unsupported_language": 400,
        "runtime_unavailable": 503,
        "timeout": 408,
        "compile_error": 500,
        "runtime_error": 500,
        "output_limit": 500,
    }.get(exc.code, 500)
    return JSONResponse(status_code=status_code, content={"error": {"code": exc.code, "message": str(exc), "details": exc.details}})




@app.exception_handler(ReportValidationError)
async def report_validation_error_handler(_: Request, exc: ReportValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": {"code": "invalid_report", "message": str(exc)}})

@app.exception_handler(CatalogError)
async def catalog_error_handler(_: Request, exc: CatalogError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": {"code": "unknown_method", "message": str(exc)}})


@app.get("/")
def root() -> dict[str, Any]:
    return {"service": "Sustainable Catalyst Lab Compute API", "version": VERSION, "health": "/health", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, Any]:
    languages = language_registry()
    return {
        "ok": True,
        "service": "sustainable-catalyst-lab-compute-api",
        "version": VERSION,
        "queueMode": jobs.mode,
        "availableLanguages": [language for language, details in languages.items() if details["available"]],
        "curatedExecutionOnly": True,
        "arbitrarySourceAccepted": False,
    }


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": VERSION, "contractSchema": "sc-lab-method/1.0", "executionSchema": "sc-lab-execution/1.0"}


@app.get("/v1/methods", dependencies=[Depends(require_api_key)])
def methods() -> dict[str, Any]:
    return public_catalog()


@app.get("/v1/languages", dependencies=[Depends(require_api_key)])
def languages() -> dict[str, Any]:
    return {"version": VERSION, "languages": language_registry()}


@app.post("/v1/validate", dependencies=[Depends(require_api_key)])
def validate(payload: ValidateRequest) -> dict[str, Any]:
    contract = get_method(payload.methodId)
    try:
        inputs, outputs = evaluate_contract(contract, payload.inputs)
    except ContractValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {
        "schema": "sc-lab-contract-validation/1.0",
        "methodId": payload.methodId,
        "methodVersion": contract.get("version"),
        "inputs": inputs,
        "outputs": outputs,
        "status": "VALIDATED",
    }


@app.post("/v1/execute", dependencies=[Depends(require_api_key)])
def execute(payload: ExecuteRequest) -> dict[str, Any]:
    return execute_method(payload.methodId, payload.language, payload.inputs, payload.timeoutSeconds, payload.includeSource)


@app.post("/v1/compare", dependencies=[Depends(require_api_key)])
def compare(payload: CompareRequest) -> dict[str, Any]:
    return compare_languages(
        payload.methodId,
        list(payload.languages),
        payload.inputs,
        payload.timeoutSeconds,
        payload.includeSource,
        payload.absoluteTolerance,
        payload.relativeTolerance,
    )


@app.post("/v1/jobs", status_code=202, dependencies=[Depends(require_api_key)])
def create_job(payload: JobRequest) -> dict[str, Any]:
    try:
        selected = payload.selected_payload()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return jobs.submit(payload.operation, selected)


@app.get("/v1/jobs/{job_id}", dependencies=[Depends(require_api_key)])
def job_status(job_id: str) -> dict[str, Any]:
    record = jobs.status(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Unknown execution job.")
    return record


@app.delete("/v1/jobs/{job_id}", dependencies=[Depends(require_api_key)])
def cancel_job(job_id: str) -> dict[str, Any]:
    record = jobs.cancel(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Unknown execution job.")
    return record


@app.post("/v1/reports/validate", dependencies=[Depends(require_api_key)])
def report_validate(payload: ReportRequest) -> dict[str, Any]:
    report = validate_report(payload.model_dump())
    return {
        "schema": "sc-lab-report-validation/1.0",
        "status": "VALIDATED",
        "reportType": report["reportType"],
        "analysisCount": len(report["analyses"]),
        "reportFingerprint": report["audit"]["reportFingerprint"],
        "engine": "reportlab-vector-pdf",
    }


@app.post("/v1/reports/pdf", dependencies=[Depends(require_api_key)])
def report_pdf(payload: ReportRequest) -> dict[str, Any]:
    return report_pdf_response(payload.model_dump())


@app.post("/v1/handoffs/decision-studio/validate", dependencies=[Depends(require_api_key)])
def handoff_validate(payload: HandoffValidateRequest) -> dict[str, Any]:
    return validate_handoff(payload.packet)

# Lab v0.10.0 curated electrical and embedded routes.
app.include_router(electrical_router, dependencies=[Depends(require_api_key)])
app.include_router(mechanical_router, dependencies=[Depends(require_api_key)])
