from __future__ import annotations

import base64
import io
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas

from .compute import ComputeExecutionError, run_compute
from .config import settings
from .extensions import load_legacy_extensions
from .jobs import InvalidJobStateError, PersistentJobQueue, QueueCapacityError
from .registry import catalog, resolve
from .schemas import ComputeRequest, ComputeResponse
from .security import require_compute_auth


jobs = PersistentJobQueue()


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.extensions = (
        load_legacy_extensions(application)
        if settings.extension_loading
        else {"loaded": [], "failed": {}}
    )
    jobs.start()
    yield
    jobs.stop()


app = FastAPI(
    title=settings.service_name,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_limits(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH"}:
        body = await request.body()
        if len(body) > settings.max_request_bytes:
            return JSONResponse(
                status_code=413,
                content={"detail": "Compute request exceeds the configured size limit."},
            )
    return await call_next(request)


def execute_or_http(payload: ComputeRequest, auth: dict[str, str]) -> ComputeResponse:
    try:
        return run_compute(payload, auth)
    except ComputeExecutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


def job_payload(source: dict[str, Any]) -> ComputeRequest:
    return ComputeRequest(
        method=str(source.get("methodId") or source.get("method") or ""),
        version=source.get("version"),
        inputs=source.get("inputs") or {},
        parameters=source.get("parameters") or {},
        units=source.get("units") or {},
        project_id=source.get("project_id") or source.get("projectId"),
        requested_outputs=source.get("requested_outputs") or source.get("requestedOutputs") or ["summary", "values"],
        random_seed=source.get("random_seed") if source.get("random_seed") is not None else source.get("randomSeed"),
    )


@app.get("/health")
def health():
    queue_state = jobs.queue_status()
    return {
        "ok": True,
        "status": "ready",
        "service": settings.service_name,
        "version": settings.version,
        "architecture": "python-compute-core",
        "authMode": settings.auth_mode,
        "methodCount": len(catalog()),
        "extensionLoading": settings.extension_loading,
        "extensions": getattr(app.state, "extensions", {"loaded": [], "failed": {}}),
        "queue": {
            "persistent": queue_state["persistent"],
            "storage": queue_state["storage"],
            "activeWorkers": queue_state["activeWorkers"],
            "workerCapacity": queue_state["workerCapacity"],
            "queued": queue_state["counts"]["queued"] + queue_state["counts"]["retrying"],
        },
    }


@app.get("/version")
def version():
    return {"version": settings.version, "service": settings.service_name}


@app.get("/v1/capabilities", dependencies=[Depends(require_compute_auth)])
def capabilities():
    return {
        "schema": "sc-lab-compute-capabilities/1.1",
        "version": settings.version,
        "executionTargets": ["python-core-cpu", "isolated-process-worker"],
        "modes": ["synchronous", "persistent-queued"],
        "packages": ["numpy", "scipy", "pandas", "sympy", "reportlab"],
        "security": {
            "authMode": settings.auth_mode,
            "arbitraryCode": False,
            "registeredMethodsOnly": True,
            "requestLimitBytes": settings.max_request_bytes,
            "hardWorkerTermination": True,
        },
        "jobs": {
            "persistent": True,
            "storage": "sqlite-wal",
            "states": ["queued", "running", "completed", "failed", "cancelled", "timed_out", "retrying"],
            "workerCount": settings.job_workers,
            "maxQueuedJobs": settings.max_queued_jobs,
            "defaultTimeoutSeconds": settings.default_job_timeout_seconds,
            "maxTimeoutSeconds": settings.max_job_timeout_seconds,
            "defaultAttempts": settings.default_job_attempts,
            "maxAttempts": settings.max_job_attempts,
            "deduplication": True,
            "restartRecovery": True,
        },
        "provenanceSchema": "sc-lab-compute-provenance/1.0",
        "methodCount": len(catalog()),
        "legacyExtensions": getattr(app.state, "extensions", {"loaded": [], "failed": {}}),
    }


@app.get("/v1/methods", dependencies=[Depends(require_compute_auth)])
def methods():
    return {"schema": "sc-lab-method-registry/1.0", "version": settings.version, "methods": catalog()}


@app.get("/v1/methods/{method_id}", dependencies=[Depends(require_compute_auth)])
def method(method_id: str):
    try:
        return resolve(method_id).public()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/v1/compute/run", response_model=ComputeResponse)
def compute_run(payload: ComputeRequest, auth: dict[str, str] = Depends(require_compute_auth)):
    return execute_or_http(payload, auth)


@app.get("/v1/languages", dependencies=[Depends(require_compute_auth)])
def languages():
    return {
        "languages": [
            {"id": "python", "status": "native", "version": "3"},
            {"id": "javascript", "status": "browser-fallback"},
            {"id": "typescript", "status": "source-only"},
            {"id": "r", "status": "source-only"},
            {"id": "julia", "status": "source-only"},
            {"id": "rust", "status": "source-only"},
            {"id": "go", "status": "source-only"},
            {"id": "c", "status": "source-only"},
            {"id": "cpp", "status": "source-only"},
            {"id": "fortran", "status": "source-only"},
            {"id": "sql", "status": "source-only"},
            {"id": "haskell", "status": "source-only"},
        ]
    }


@app.post("/v1/validate")
def validate(payload: ComputeRequest, auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    try:
        method_record = resolve(payload.method)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "method": method_record.public(), "request": payload.model_dump()}


@app.post("/v1/execute")
def execute_compat(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    language = str(payload.get("language") or "python").lower()
    if language != "python":
        raise HTTPException(
            status_code=422,
            detail=f"v0.26.1 executes Python natively; {language} remains a browser/source fallback.",
        )
    request = job_payload(payload)
    result = execute_or_http(request, auth)
    return {
        "ok": True,
        "methodId": payload.get("methodId") or request.method,
        "language": "python",
        "outputs": result.outputs,
        "result": result.model_dump(mode="json", by_alias=True),
        "provenance": result.provenance.model_dump(mode="json", by_alias=True),
    }


@app.post("/v1/compare")
def compare_compat(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    languages_requested = [str(v).lower() for v in payload.get("languages") or []]
    request = job_payload(payload)
    result = execute_or_http(request, auth)
    return {
        "ok": True,
        "methodId": payload.get("methodId"),
        "referenceLanguage": "python",
        "reference": result.outputs,
        "runs": [{"language": "python", "status": "completed", "outputs": result.outputs}]
        if "python" in languages_requested
        else [],
        "unsupported": [lang for lang in languages_requested if lang != "python"],
        "provenance": result.provenance.model_dump(mode="json", by_alias=True),
    }


@app.post("/v1/jobs", status_code=202)
def create_job(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    operation = str(payload.get("operation") or "core_run")
    if operation in {"execute", "core_run"}:
        source = payload.get("execute") or payload.get("request") or payload
    elif operation == "compare":
        source = payload.get("compare") or {}
    else:
        raise HTTPException(status_code=422, detail="Job operation must be execute, core_run, or compare.")

    try:
        request = job_payload(source)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    idempotency_key = str(payload.get("idempotencyKey") or payload.get("idempotency_key") or "") or None
    timeout_seconds = payload.get("timeoutSeconds") or payload.get("timeout_seconds") or source.get("timeoutSeconds")
    max_attempts = payload.get("maxAttempts") or payload.get("max_attempts")
    try:
        record, deduplicated = jobs.submit(
            operation=operation,
            payload=request.model_dump(mode="json"),
            auth=auth,
            timeout_seconds=int(timeout_seconds) if timeout_seconds is not None else None,
            max_attempts=int(max_attempts) if max_attempts is not None else None,
            idempotency_key=idempotency_key,
        )
    except QueueCapacityError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    record["deduplicated"] = deduplicated
    return record


@app.get("/v1/jobs", dependencies=[Depends(require_compute_auth)])
def list_jobs(
    status: str | None = Query(default=None),
    project_id: str | None = Query(default=None, max_length=128),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        result = jobs.list(status=status, project_id=project_id, limit=limit, offset=offset)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"schema": "sc-lab-compute-job-list/1.0", **result}


@app.get("/v1/jobs/{job_id}", dependencies=[Depends(require_compute_auth)])
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.delete("/v1/jobs/{job_id}", dependencies=[Depends(require_compute_auth)])
def cancel_job_delete(job_id: str):
    job = jobs.cancel(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.post("/v1/jobs/{job_id}/cancel", dependencies=[Depends(require_compute_auth)])
def cancel_job(job_id: str):
    job = jobs.cancel(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.post("/v1/jobs/{job_id}/retry", dependencies=[Depends(require_compute_auth)])
def retry_job(job_id: str):
    try:
        job = jobs.retry(job_id)
    except InvalidJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not job:
        raise HTTPException(status_code=404, detail="Compute job not found.")
    return job


@app.get("/v1/workers", dependencies=[Depends(require_compute_auth)])
def workers():
    return jobs.workers_status()


@app.get("/v1/queue/status", dependencies=[Depends(require_compute_auth)])
def queue_status():
    return jobs.queue_status()


@app.post("/v1/reports/validate")
def report_validate(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    errors = []
    if not str(payload.get("title") or "").strip():
        errors.append("title is required")
    analyses = payload.get("analyses")
    if not isinstance(analyses, list) or not analyses:
        errors.append("at least one analysis is required")
    return {"ok": not errors, "valid": not errors, "errors": errors, "schema": "sc-lab-report-validation/1.0"}


@app.post("/v1/reports/pdf")
def report_pdf(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    validation = report_validate(payload, auth)
    if not validation["valid"]:
        raise HTTPException(status_code=422, detail=validation["errors"])
    buffer = io.BytesIO()
    pagesize = A4 if payload.get("pageSize") == "A4" else letter
    pdf = canvas.Canvas(buffer, pagesize=pagesize)
    _, height = pagesize
    pdf.setTitle(str(payload.get("title")))
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(54, height - 54, str(payload.get("title"))[:100])
    y = height - 86
    pdf.setFont("Helvetica", 10)
    for index, analysis in enumerate(payload.get("analyses") or [], 1):
        line = f"{index}. {analysis.get('title') or analysis.get('method') or 'Analysis'}"
        pdf.drawString(54, y, line[:120])
        y -= 16
        if y < 54:
            pdf.showPage()
            y = height - 54
            pdf.setFont("Helvetica", 10)
    pdf.save()
    raw = buffer.getvalue()
    return {
        "ok": True,
        "mimeType": "application/pdf",
        "filename": "sustainable-catalyst-lab-report.pdf",
        "base64": base64.b64encode(raw).decode("ascii"),
        "sizeBytes": len(raw),
    }


@app.post("/v1/handoffs/decision-studio/validate")
def handoff_validate(payload: dict[str, Any], auth: dict[str, str] = Depends(require_compute_auth)):
    del auth
    packet = payload.get("packet")
    valid = isinstance(packet, dict) and bool(packet)
    return {
        "ok": valid,
        "valid": valid,
        "errors": [] if valid else ["packet must be a non-empty object"],
        "schema": "sc-lab-decision-handoff-validation/1.0",
    }
