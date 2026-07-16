from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

VERSION = "0.31.4"
FAILURE_SCHEMA = "sc-lab-dispatch-failure/0.31.4"
DEAD_LETTER_SCHEMA = "sc-lab-dispatch-dead-letter/0.31.4"
OPERATIONS_SCHEMA = "sc-lab-dispatch-operations/0.31.4"

FAILURE_CLASSES: dict[str, dict[str, Any]] = {
    "worker-transient": {"retryable": True, "severity": "warning", "description": "Temporary worker runtime or dependency failure."},
    "lease-timeout": {"retryable": True, "severity": "warning", "description": "Worker lease expired before completion."},
    "capacity": {"retryable": True, "severity": "warning", "description": "Worker or coordinator capacity was temporarily unavailable."},
    "artifact-transport": {"retryable": True, "severity": "warning", "description": "Artifact upload, download, or integrity transport failed."},
    "coordinator-transient": {"retryable": True, "severity": "warning", "description": "Temporary coordinator or storage failure."},
    "input-validation": {"retryable": False, "severity": "error", "description": "Workload input did not satisfy the registered method contract."},
    "method-not-found": {"retryable": False, "severity": "error", "description": "The requested method is not registered on the worker or coordinator."},
    "security-policy": {"retryable": False, "severity": "critical", "description": "The workload or receipt violated a security or signature policy."},
    "worker-quarantined": {"retryable": False, "severity": "critical", "description": "The assigned worker has been quarantined or revoked."},
    "operator-cancelled": {"retryable": False, "severity": "info", "description": "An operator intentionally cancelled the workload."},
    "unknown": {"retryable": True, "severity": "error", "description": "Failure could not be classified automatically."},
}


def _text(value: Any, limit: int = 2000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def classify_failure(payload: dict[str, Any] | None = None, fallback: str = "") -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    explicit = _text(source.get("failureClass") or source.get("classification"), 80).lower()
    error = _text(source.get("error") or source.get("message") or fallback, 2000)
    code = _text(source.get("failureCode") or source.get("errorCode"), 120).lower()
    if explicit in FAILURE_CLASSES:
        failure_class = explicit
    else:
        haystack = f"{code} {error}".lower()
        if any(token in haystack for token in ("signature", "credential", "unauthorized", "forbidden", "unsafe", "security")):
            failure_class = "security-policy"
        elif any(token in haystack for token in ("quarantin", "revoked worker")):
            failure_class = "worker-quarantined"
        elif any(token in haystack for token in ("method not found", "unknown method", "not registered", "unsupported method")):
            failure_class = "method-not-found"
        elif any(token in haystack for token in ("validation", "invalid input", "schema", "required field", "unprocessable")):
            failure_class = "input-validation"
        elif any(token in haystack for token in ("artifact", "checksum", "sha-256", "upload", "download", "blob", "chunk")):
            failure_class = "artifact-transport"
        elif any(token in haystack for token in ("timeout", "timed out", "lease expired", "deadline")):
            failure_class = "lease-timeout"
        elif any(token in haystack for token in ("capacity", "busy", "overloaded", "rate limit", "too many")):
            failure_class = "capacity"
        elif any(token in haystack for token in ("worker", "dependency", "package", "runtime", "process exited")):
            failure_class = "worker-transient"
        elif any(token in haystack for token in ("database locked", "temporar", "connection reset", "unavailable", "coordinator")):
            failure_class = "coordinator-transient"
        else:
            failure_class = "unknown"
    policy = FAILURE_CLASSES[failure_class]
    retryable = bool(source.get("retryable", policy["retryable"]))
    return {
        "schema": FAILURE_SCHEMA,
        "version": VERSION,
        "failureClass": failure_class,
        "failureCode": code or failure_class.replace("-", "_"),
        "retryable": retryable,
        "severity": policy["severity"],
        "description": policy["description"],
        "error": error or "unspecified dispatcher failure",
        "classifiedAt": datetime.now(timezone.utc).isoformat(),
        "classificationSource": "explicit" if explicit in FAILURE_CLASSES else "automatic",
    }


def retry_delay_seconds(attempts: int, base_seconds: int = 15, maximum_seconds: int = 900) -> int:
    attempts = max(1, int(attempts))
    base_seconds = max(1, int(base_seconds))
    maximum_seconds = max(base_seconds, int(maximum_seconds))
    return min(maximum_seconds, base_seconds * (2 ** max(0, attempts - 1)))


def policies(base_seconds: int = 15, maximum_seconds: int = 900) -> dict[str, Any]:
    return {
        "ok": True,
        "schema": OPERATIONS_SCHEMA,
        "version": VERSION,
        "failureClasses": FAILURE_CLASSES,
        "retry": {
            "strategy": "bounded-exponential-backoff",
            "baseDelaySeconds": max(1, int(base_seconds)),
            "maximumDelaySeconds": max(max(1, int(base_seconds)), int(maximum_seconds)),
            "attemptLimitPerQueueItem": True,
            "operatorReplay": True,
            "replayResetsAttemptsByDefault": True,
        },
        "deadLetters": {
            "terminalState": "dead-lettered",
            "inspection": True,
            "timeline": True,
            "singleReplay": True,
            "bulkReplay": True,
            "operatorCancellation": True,
            "hardDelete": False,
        },
        "observability": {
            "queueMetrics": True,
            "failureClassification": True,
            "oldestQueueAge": True,
            "leaseExpiryWindow": True,
            "throughputWindows": ["1h", "24h"],
            "sqliteIntegrity": True,
            "eventTimeline": True,
        },
    }
