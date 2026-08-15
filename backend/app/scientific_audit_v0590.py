from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re
from typing import Any

from .reproducible_model_package import verify_package as verify_model_package
from .security_privacy_hardening import privacy_scan

VERSION = "0.59.0"
AUDIT_SCHEMA = "sc-lab-scientific-audit-report/0.59.0"
REDACTED_EXPORT_SCHEMA = "sc-lab-redacted-research-export/0.59.0"
MINIMIZATION_SCHEMA = "sc-lab-data-minimization-review/0.59.0"
MAX_AUDIT_BYTES = 16 * 1024 * 1024
MAX_ROWS_PROFILED = 5000
MAX_FINDINGS = 2000

EXECUTABLE_KEYS = {
    "code", "script", "command", "shell", "python", "javascript", "callback", "callbackurl",
    "callback_url", "webhook", "webhookurl", "webhook_url", "subprocess", "eval", "exec", "import",
    "binary", "executable", "remote_shell", "remotecommand", "remote_command",
}
SECRET_KEYS = {
    "password", "passwd", "secret", "token", "api_key", "apikey", "credential", "private_key",
    "access_token", "refresh_token", "authorization", "cookie", "client_secret", "master_key",
}
DIRECT_IDENTIFIER_KEYS = {
    "email", "email_address", "phone", "phone_number", "full_name", "fullname", "name", "address",
    "street_address", "ssn", "social_security_number", "medical_record", "medical_record_number", "mrn",
    "biometric", "passport", "passport_number", "driver_license", "driver_licence", "student_id",
    "employee_id", "ip_address", "precise_location", "latitude", "longitude",
}
HIGH_STAKES_KEYS = {
    "diagnosis", "treatment", "patient", "clinical", "credit", "loan", "eligibility", "sentence",
    "parole", "hiring_decision", "termination_decision", "benefits_decision", "safety_critical",
}
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


class ScientificAuditError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ScientificAuditError("Scientific audit input must be finite JSON data.") from exc
    if len(text.encode("utf-8")) > MAX_AUDIT_BYTES:
        raise ScientificAuditError("Scientific audit input exceeds the 16 MiB bounded audit envelope.")
    return text


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _norm_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "auditSchema": AUDIT_SCHEMA,
        "redactedExportSchema": REDACTED_EXPORT_SCHEMA,
        "dataMinimizationSchema": MINIMIZATION_SCHEMA,
        "capabilities": {
            "recursiveThreatSurfaceScan": True,
            "secretLeakageDetection": True,
            "privacyFindingPathsWithoutValues": True,
            "dataMinimizationReview": True,
            "deterministicRedactedExport": True,
            "reproducibilityVerification": True,
            "modelPackageHashVerification": True,
            "workflowRunEvidenceReview": True,
            "tamperEvidentAuditHash": True,
        },
        "boundaries": {
            "automaticCertificationAuthorized": False,
            "automaticPublicationAuthorized": False,
            "automaticDeletionAuthorized": False,
            "automaticHighStakesDecisionAuthorized": False,
            "arbitraryCodeExecutionAuthorized": False,
            "rawSensitiveValuesInFindings": False,
        },
        "limits": {"maximumAuditBytes": MAX_AUDIT_BYTES, "maximumRowsProfiled": MAX_ROWS_PROFILED, "maximumFindings": MAX_FINDINGS},
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "security-privacy-reproducibility-scientific-audit-ready",
        "version": VERSION,
        "auditSchema": AUDIT_SCHEMA,
        "sensitiveValuesEchoed": False,
        "automaticCertification": False,
        "automaticPublication": False,
        "automaticHighStakesDecision": False,
        "arbitraryCode": False,
    }


def scan_surface(value: Any) -> dict[str, Any]:
    _canonical(value)
    findings: list[dict[str, Any]] = []

    def add(path: str, category: str, severity: str, control: str) -> None:
        if len(findings) >= MAX_FINDINGS:
            return
        findings.append({"path": path or "$", "category": category, "severity": severity, "control": control})

    def walk(item: Any, path: str = "$") -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                nk = _norm_key(key)
                child_path = f"{path}.{key}"
                if nk in EXECUTABLE_KEYS:
                    add(child_path, "executable-or-callback-field", "block", "remove-executable-field")
                if nk in SECRET_KEYS or any(part in nk for part in ("password", "secret", "credential", "private_key", "access_token", "refresh_token")):
                    add(child_path, "secret-or-credential", "block", "remove-secret-from-research-payload")
                if nk in DIRECT_IDENTIFIER_KEYS:
                    add(child_path, "direct-identifier", "review", "minimize-mask-or-document-necessity")
                if nk in HIGH_STAKES_KEYS:
                    add(child_path, "high-stakes-context", "review", "require-accountable-human-review")
                walk(child, child_path)
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{path}[{index}]")
        elif isinstance(item, str):
            if EMAIL_RE.search(item):
                add(path, "email", "review", "minimize-or-redact")
            if PHONE_RE.search(item):
                add(path, "phone", "review", "minimize-or-redact")
            if IP_RE.search(item):
                add(path, "ip-address", "review", "minimize-or-generalize")
        elif isinstance(item, float) and not math.isfinite(item):
            add(path, "non-finite-number", "block", "replace-with-finite-json-value")

    walk(value)
    dedup = {(f["path"], f["category"], f["severity"]): f for f in findings}
    ordered = sorted(dedup.values(), key=lambda row: (row["severity"], row["path"], row["category"]))
    counts = {"block": 0, "review": 0, "info": 0}
    for finding in ordered:
        counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
    return {
        "ok": counts["block"] == 0,
        "version": VERSION,
        "findingCount": len(ordered),
        "counts": counts,
        "findings": ordered,
        "valuesDisclosed": False,
        "inputHash": _digest(value),
    }


def _column_risk(column: str, samples: list[Any]) -> tuple[str, str]:
    nk = _norm_key(column)
    if nk in SECRET_KEYS or any(part in nk for part in ("secret", "password", "token", "credential")):
        return "secret-or-credential", "block"
    if nk in DIRECT_IDENTIFIER_KEYS:
        return "direct-identifier", "review"
    joined = "\n".join(str(v) for v in samples if v is not None)[:20000]
    if EMAIL_RE.search(joined):
        return "email", "review"
    if PHONE_RE.search(joined):
        return "phone", "review"
    if IP_RE.search(joined):
        return "ip-address", "review"
    return "ordinary-research-variable", "low"


def data_minimization_review(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificAuditError("Data minimization request must be an object.")
    rows = payload.get("rows") or payload.get("dataset") or []
    if isinstance(rows, dict):
        rows = rows.get("rows") or []
    if not isinstance(rows, list):
        raise ScientificAuditError("rows must be an array.")
    if len(rows) > MAX_ROWS_PROFILED:
        rows = rows[:MAX_ROWS_PROFILED]
        truncated = True
    else:
        truncated = False
    required = {_norm_key(v) for v in (payload.get("requiredColumns") or [])}
    purpose = str(payload.get("purposeNote") or "").strip()
    columns: list[str] = sorted({str(k) for row in rows if isinstance(row, dict) for k in row.keys()})
    decisions = []
    for column in columns:
        samples = [row.get(column) for row in rows[:200] if isinstance(row, dict)]
        category, risk = _column_risk(column, samples)
        needed = _norm_key(column) in required
        if category == "secret-or-credential":
            action = "remove"
        elif category != "ordinary-research-variable" and not needed:
            action = "drop-or-mask"
        elif category != "ordinary-research-variable" and needed:
            action = "retain-only-with-documented-necessity-and-access-controls"
        else:
            action = "retain" if needed else "review-necessity"
        decisions.append({"column": column, "category": category, "risk": risk, "required": needed, "recommendedAction": action})
    review_required = any(row["category"] != "ordinary-research-variable" for row in decisions) or not purpose
    basis = {
        "schema": MINIMIZATION_SCHEMA,
        "rowCountProfiled": len(rows),
        "profileTruncated": truncated,
        "columnCount": len(columns),
        "requiredColumns": sorted(required),
        "purposeNotePresent": bool(purpose),
        "decisions": decisions,
        "humanReviewRequired": review_required,
        "rawValuesReturned": False,
    }
    basis["reviewHash"] = _digest(basis)
    return {"ok": True, "version": VERSION, **basis}


def _redact(value: Any, path: str, manifest: list[dict[str, str]]) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, child in value.items():
            nk = _norm_key(key)
            child_path = f"{path}.{key}"
            if nk in EXECUTABLE_KEYS:
                manifest.append({"path": child_path, "category": "executable-or-callback-field", "action": "removed"})
                continue
            if nk in SECRET_KEYS or any(part in nk for part in ("password", "secret", "credential", "private_key", "access_token", "refresh_token")):
                out[str(key)] = "[REDACTED]"
                manifest.append({"path": child_path, "category": "secret-or-credential", "action": "redacted"})
                continue
            if nk in DIRECT_IDENTIFIER_KEYS:
                out[str(key)] = "[REDACTED]"
                manifest.append({"path": child_path, "category": "direct-identifier", "action": "redacted"})
                continue
            out[str(key)] = _redact(child, child_path, manifest)
        return out
    if isinstance(value, list):
        return [_redact(child, f"{path}[{index}]", manifest) for index, child in enumerate(value)]
    if isinstance(value, str):
        text = value
        if EMAIL_RE.search(text):
            text = EMAIL_RE.sub("[EMAIL]", text)
            manifest.append({"path": path, "category": "email", "action": "redacted"})
        if PHONE_RE.search(text):
            text = PHONE_RE.sub("[PHONE]", text)
            manifest.append({"path": path, "category": "phone", "action": "redacted"})
        if IP_RE.search(text):
            text = IP_RE.sub("[IP]", text)
            manifest.append({"path": path, "category": "ip-address", "action": "redacted"})
        return text
    return value


def build_redacted_export(payload: Any) -> dict[str, Any]:
    _canonical(payload)
    manifest: list[dict[str, str]] = []
    redacted = _redact(deepcopy(payload), "$", manifest)
    manifest = sorted({(m["path"], m["category"], m["action"]): m for m in manifest}.values(), key=lambda row: (row["path"], row["category"]))
    basis = {
        "schema": REDACTED_EXPORT_SCHEMA,
        "sourceHash": _digest(payload),
        "redactedHash": _digest(redacted),
        "redactionCount": len(manifest),
        "redactions": manifest,
        "payload": redacted,
        "rawSensitiveValuesInManifest": False,
    }
    basis["exportHash"] = _digest(basis)
    return {"ok": True, "version": VERSION, **basis}


def _workflow_reproducibility(run: dict[str, Any]) -> dict[str, Any]:
    stages = run.get("stages") or run.get("stageRuns") or run.get("timeline") or []
    if not isinstance(stages, list):
        stages = []
    stage_hash_count = sum(1 for row in stages if isinstance(row, dict) and (row.get("outputHash") or row.get("resultHash")))
    checks = {
        "workflowHashPresent": bool(run.get("workflowHash") or run.get("definitionHash")),
        "runHashPresent": bool(run.get("runHash") or run.get("workflowRunHash") or run.get("semanticRunHash")),
        "stageEvidencePresent": bool(stages),
        "stageOutputHashesPresent": bool(stages) and stage_hash_count == len(stages),
    }
    return {"ok": all(checks.values()), "kind": "scientific-workflow-run", "checks": checks, "stageCount": len(stages), "hashedStageCount": stage_hash_count}


def reproducibility_audit(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificAuditError("Reproducibility audit request must be an object.")
    package = payload.get("package") or payload.get("modelPackage")
    workflow = payload.get("workflowRun") or payload.get("run")
    evidence: list[dict[str, Any]] = []
    if isinstance(package, dict):
        checked = verify_model_package(package)
        evidence.append({"kind": "reproducible-model-package", "ok": bool(checked.get("ok")), "checks": checked.get("checks") or {}, "packageHash": package.get("packageHash")})
    if isinstance(workflow, dict):
        evidence.append(_workflow_reproducibility(workflow))
    if not evidence:
        generic_checks = {
            "sourceOrDatasetHashPresent": bool(payload.get("sourceHash") or payload.get("datasetHash") or payload.get("inputHash")),
            "modelOrMethodHashPresent": bool(payload.get("modelHash") or payload.get("methodHash") or payload.get("workflowHash")),
            "environmentEvidencePresent": bool(payload.get("environment") or payload.get("environmentHash") or payload.get("platformVersion")),
        }
        evidence.append({"kind": "generic-research-record", "ok": all(generic_checks.values()), "checks": generic_checks})
    ok = all(row.get("ok") is True for row in evidence)
    result = {"ok": ok, "version": VERSION, "evidence": evidence, "evidenceCount": len(evidence), "humanReviewRequired": not ok}
    result["auditHash"] = _digest(result)
    return result


def scientific_audit(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScientificAuditError("Scientific audit request must be an object.")
    target = payload.get("target") if isinstance(payload.get("target"), (dict, list)) else payload
    surface = scan_surface(target)
    privacy = privacy_scan(target)
    repro_payload = payload.get("reproducibility") if isinstance(payload.get("reproducibility"), dict) else payload
    repro = reproducibility_audit(repro_payload)
    block_count = surface["counts"].get("block", 0)
    review_count = surface["counts"].get("review", 0) + int(bool(privacy.get("containsSensitiveData"))) + int(not repro.get("ok"))
    gate = "blocked" if block_count else ("human-review-required" if review_count else "audit-ready")
    basis = {
        "schema": AUDIT_SCHEMA,
        "version": VERSION,
        "targetHash": _digest(target),
        "securityPrivacy": {
            "findingCount": surface["findingCount"],
            "counts": surface["counts"],
            "findings": surface["findings"],
            "legacyPrivacyFindingCount": privacy.get("findingCount", 0),
            "containsSensitiveData": bool(privacy.get("containsSensitiveData")),
            "valuesDisclosed": False,
        },
        "reproducibility": repro,
        "gate": gate,
        "humanReviewRequired": gate != "audit-ready",
        "automaticCertificationAuthorized": False,
        "automaticPublicationAuthorized": False,
        "automaticHighStakesDecisionAuthorized": False,
    }
    basis["auditHash"] = _digest(basis)
    return {"ok": gate != "blocked", "generatedAt": _now(), **basis}


def verify_audit(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ScientificAuditError("Audit report must be an object.")
    expected = str(report.get("auditHash") or "")
    basis = deepcopy(report)
    basis.pop("ok", None)
    basis.pop("generatedAt", None)
    basis.pop("auditHash", None)
    actual = _digest(basis)
    return {"ok": bool(expected) and expected == actual, "version": VERSION, "expectedAuditHash": expected, "actualAuditHash": actual}
