from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import hmac
import json
import platform
import time
from typing import Any

from .compute import run_compute
from .distributed_dispatcher import CONTRACT_SCHEMA, DispatcherError, _hash, _stable, _text
from .schemas import ComputeRequest, ComputeResponse

VERSION = "0.31.3"
AGENT_CONFIG_SCHEMA = "sc-lab-worker-agent-config/0.31.3"
ENROLLMENT_SCHEMA = "sc-lab-worker-enrollment/0.31.3"
RECEIPT_SCHEMA = "sc-lab-worker-execution-receipt/0.31.3"
ALLOWED_REQUEST_KEYS = {
    "version", "inputs", "units", "parameters", "project_id", "projectId",
    "requested_outputs", "requestedOutputs", "random_seed", "randomSeed", "governance",
}
FORBIDDEN_KEYS = {
    "code", "sourceCode", "source_code", "script", "command", "shell", "callback",
    "callbackUrl", "callback_url", "webhook", "executable", "binary", "modulePath",
    "module_path", "pickle", "serializedObject", "serialized_object",
}


class WorkerAgentError(DispatcherError):
    pass


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_time(value: Any) -> datetime:
    try:
        return datetime.fromisoformat(str(value)).astimezone(timezone.utc)
    except Exception as exc:
        raise WorkerAgentError("Dispatch contract expiration is invalid.") from exc


def policies(enrollment_required: bool = True, contract_secret_configured: bool = True) -> dict[str, Any]:
    return {
        "version": VERSION,
        "architecture": "secure-pull-based-worker-agent-runtime",
        "enrollment": {
            "schema": ENROLLMENT_SCHEMA,
            "required": enrollment_required,
            "oneTimeCredentialReturn": True,
            "credentialStorage": "sha256-digest-only",
            "rotation": True,
            "revocation": True,
        },
        "contracts": {
            "signed": True,
            "secretConfigured": contract_secret_configured,
            "workerBinding": True,
            "expirationRequired": True,
            "methodBinding": True,
        },
        "execution": {
            "pullBased": True,
            "registeredMethodsOnly": True,
            "arbitraryCode": False,
            "arbitraryCommands": False,
            "arbitraryCallbackUrls": False,
            "leaseRenewal": True,
            "idempotentCompletion": True,
        },
        "receipts": {"schema": RECEIPT_SCHEMA, "provenance": True, "resultHash": True, "externalResultArtifacts": True},
        "artifactTransport": {"version": VERSION, "inputMaterialization": True, "resultExternalization": True, "checkpointTransport": True, "sha256Verification": True},
    }


def verify_contract(contract: dict[str, Any], worker_id: str, secret: str, allow_insecure: bool = False) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise WorkerAgentError("A dispatch contract object is required.")
    if contract.get("schema") != CONTRACT_SCHEMA:
        raise WorkerAgentError("Unsupported dispatch contract schema.")
    if _text(contract.get("workerId"), 180) != _text(worker_id, 180):
        raise WorkerAgentError("Dispatch contract is assigned to a different worker.")
    expires = _parse_time(contract.get("expiresAt"))
    if expires <= datetime.now(timezone.utc):
        raise WorkerAgentError("Dispatch contract has expired.")
    signature = _text(contract.get("signature"), 128)
    unsigned = {key: value for key, value in contract.items() if key != "signature"}
    if secret:
        expected = hmac.new(secret.encode("utf-8"), _stable(unsigned).encode("utf-8"), sha256).hexdigest()
        signature_valid = bool(signature) and hmac.compare_digest(signature, expected)
        if not signature_valid:
            raise WorkerAgentError("Dispatch contract signature verification failed.")
    elif not allow_insecure:
        raise WorkerAgentError("A worker contract verification secret is required.")
    else:
        signature_valid = False
    workload = contract.get("workload") if isinstance(contract.get("workload"), dict) else {}
    method = _text(workload.get("method"), 128)
    if not method:
        raise WorkerAgentError("Dispatch contract does not identify a registered method.")
    return {
        "ok": True,
        "valid": True,
        "signatureValid": signature_valid,
        "insecureDevelopmentMode": not bool(secret),
        "workerId": worker_id,
        "contractId": contract.get("id"),
        "leaseId": contract.get("leaseId"),
        "method": method,
        "expiresAt": expires.isoformat(),
    }


def _reject_unsafe_tree(value: Any, path: str = "request") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in FORBIDDEN_KEYS:
                raise WorkerAgentError(f"Unsafe worker request field is not permitted: {path}.{key}")
            _reject_unsafe_tree(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_tree(child, f"{path}[{index}]")


def compute_request_from_contract(contract: dict[str, Any], worker_id: str, secret: str, allow_insecure: bool = False, materialized_inputs: dict[str, Any] | None = None) -> ComputeRequest:
    verified = verify_contract(contract, worker_id, secret, allow_insecure)
    workload = contract["workload"]
    raw = workload.get("request") if isinstance(workload.get("request"), dict) else {}
    unknown = sorted(set(raw) - ALLOWED_REQUEST_KEYS)
    if unknown:
        raise WorkerAgentError("Unsupported worker request fields: " + ", ".join(unknown))
    _reject_unsafe_tree(raw)
    payload = {
        "method": verified["method"],
        "version": raw.get("version"),
        "inputs": {**(raw.get("inputs") or {}), **(materialized_inputs or {})},
        "units": raw.get("units") or {},
        "parameters": raw.get("parameters") or {},
        "project_id": raw.get("project_id") or raw.get("projectId") or workload.get("projectId") or None,
        "requested_outputs": raw.get("requested_outputs") or raw.get("requestedOutputs") or ["summary", "values"],
        "random_seed": raw.get("random_seed") if raw.get("random_seed") is not None else raw.get("randomSeed"),
        "governance": raw.get("governance") or {},
    }
    try:
        return ComputeRequest(**payload)
    except Exception as exc:
        raise WorkerAgentError(f"Worker request validation failed: {exc}") from exc


def build_receipt(contract: dict[str, Any], worker_id: str, response: ComputeResponse, started_at: str, duration_ms: float) -> dict[str, Any]:
    result = response.model_dump(by_alias=True)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "recordType": "worker-execution-receipt",
        "id": f"worker-receipt-{_hash({'contract': contract.get('id'), 'worker': worker_id, 'result': result})[:24]}",
        "workerId": worker_id,
        "contractId": contract.get("id"),
        "leaseId": contract.get("leaseId"),
        "queueId": contract.get("queueId"),
        "workloadHash": (contract.get("workload") or {}).get("workloadHash"),
        "method": response.method,
        "methodVersion": response.method_version,
        "startedAt": started_at,
        "completedAt": _utcnow(),
        "durationMs": round(duration_ms, 4),
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "resultHash": _hash(result),
        "result": result,
    }
    receipt["receiptHash"] = _hash({key: value for key, value in receipt.items() if key != "receiptHash"})
    return receipt


def materialize_artifact_inputs(contract: dict[str, Any], downloader) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    workload = contract.get("workload") if isinstance(contract.get("workload"), dict) else {}
    references = workload.get("artifactInputs") if isinstance(workload.get("artifactInputs"), list) else []
    inputs: dict[str, Any] = {}
    materialized: list[dict[str, Any]] = []
    for index, reference in enumerate(references):
        if not isinstance(reference, dict):
            raise WorkerAgentError(f"Artifact input {index} is invalid.")
        artifact_id = _text(reference.get("artifactId"), 220)
        input_key = _text(reference.get("inputKey"), 128)
        fmt = _text(reference.get("format"), 40).lower() or "json"
        if not artifact_id or not input_key:
            raise WorkerAgentError("Artifact inputs require artifactId and inputKey.")
        payload, metadata = downloader(artifact_id)
        expected = _text(reference.get("sha256"), 64).lower()
        actual = sha256(payload).hexdigest()
        if expected and not hmac.compare_digest(expected, actual):
            raise WorkerAgentError(f"Artifact input SHA-256 verification failed: {artifact_id}")
        if metadata.get("sha256") and not hmac.compare_digest(str(metadata["sha256"]), actual):
            raise WorkerAgentError(f"Coordinator artifact metadata hash mismatch: {artifact_id}")
        try:
            if fmt == "json":
                value = json.loads(payload.decode("utf-8"))
            elif fmt == "text":
                value = payload.decode("utf-8")
            elif fmt == "binary-base64":
                import base64
                value = base64.b64encode(payload).decode("ascii")
            else:
                raise WorkerAgentError(f"Unsupported artifact input format: {fmt}")
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise WorkerAgentError(f"Artifact input decoding failed: {artifact_id}") from exc
        inputs[input_key] = value
        materialized.append({"artifactId": artifact_id, "inputKey": input_key, "format": fmt, "sha256": actual, "sizeBytes": len(payload)})
    return inputs, materialized


def externalize_receipt_result(receipt: dict[str, Any], uploader, threshold_bytes: int) -> dict[str, Any]:
    result = receipt.get("result")
    encoded = _stable(result).encode("utf-8")
    if len(encoded) < max(1024, int(threshold_bytes)):
        receipt["artifactTransport"] = {"externalized": False, "inlineBytes": len(encoded), "version": VERSION}
        return receipt
    artifact = uploader(
        encoded,
        {
            "kind": "result",
            "filename": f"{receipt.get('contractId') or 'worker-result'}.json",
            "mediaType": "application/json",
            "sha256": sha256(encoded).hexdigest(),
            "sizeBytes": len(encoded),
            "queueId": receipt.get("queueId"),
            "contractId": receipt.get("contractId"),
            "metadata": {"receiptId": receipt.get("id"), "method": receipt.get("method"), "resultHash": receipt.get("resultHash")},
        },
    )
    receipt["resultArtifact"] = artifact
    receipt["result"] = {
        "externalized": True,
        "artifactId": artifact.get("id"),
        "sha256": artifact.get("sha256"),
        "sizeBytes": artifact.get("sizeBytes"),
        "mediaType": artifact.get("mediaType"),
    }
    receipt["artifactTransport"] = {"externalized": True, "inlineBytes": 0, "version": VERSION}
    receipt["receiptHash"] = _hash({key: value for key, value in receipt.items() if key != "receiptHash"})
    return receipt


def execute_contract(contract: dict[str, Any], worker_id: str, secret: str, auth: dict[str, str], allow_insecure: bool = False, materialized_inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    request = compute_request_from_contract(contract, worker_id, secret, allow_insecure, materialized_inputs)
    started = _utcnow()
    clock = time.perf_counter()
    response = run_compute(request, auth)
    return build_receipt(contract, worker_id, response, started, (time.perf_counter() - clock) * 1000)
