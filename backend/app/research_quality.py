from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any

VERSION = "0.29.1"
REVIEW_SCHEMA = "sc-lab-method-review/0.29.1"
DECISION_SCHEMA = "sc-lab-method-review-decision/0.29.1"
COMPARISON_SCHEMA = "sc-lab-method-review-comparison/0.29.1"

STATUSES = [
    "draft", "under-review", "changes-requested", "conditionally-approved",
    "approved", "rejected", "deprecated"
]
RISK_TIERS = ["exploratory", "standard", "high-consequence"]
CALIBRATION_STATUSES = ["not-required", "uncalibrated", "calibrated", "due", "expired"]
DECISIONS = ["no-decision", "approve", "conditional-approval", "request-changes", "reject", "deprecate"]

POLICIES: dict[str, dict[str, Any]] = {
    "exploratory": {
        "minimumBenchmarks": 0,
        "minimumValidationEvidence": 0,
        "requireLimitations": False,
        "requireReproducibleRun": False,
        "requireProvenance": False,
        "requireIndependentReviewer": False,
        "minimumScore": 45,
    },
    "standard": {
        "minimumBenchmarks": 1,
        "minimumValidationEvidence": 1,
        "requireLimitations": True,
        "requireReproducibleRun": True,
        "requireProvenance": True,
        "requireIndependentReviewer": False,
        "minimumScore": 70,
    },
    "high-consequence": {
        "minimumBenchmarks": 2,
        "minimumValidationEvidence": 2,
        "requireLimitations": True,
        "requireReproducibleRun": True,
        "requireProvenance": True,
        "requireIndependentReviewer": True,
        "minimumScore": 85,
    },
}

class QualityReviewError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _strings(value: Any, limit: int = 200) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip()[:2000] for item in value[:limit] if str(item).strip()]


def _coverage(payload: dict[str, Any]) -> dict[str, Any]:
    coverage = payload.get("benchmarkCoverage") or {}
    passed = max(0, int(coverage.get("passed") or payload.get("benchmarksPassed") or 0))
    total = max(passed, int(coverage.get("total") or payload.get("benchmarksTotal") or len(payload.get("benchmarkIds") or [])))
    percent = round((passed / total) * 100.0, 2) if total else 0.0
    return {"passed": passed, "total": total, "percent": percent, "complete": bool(total and passed == total)}


def policies() -> dict[str, Any]:
    return {
        "ok": True,
        "version": VERSION,
        "schema": "sc-lab-method-review-policy/0.29.1",
        "statuses": STATUSES,
        "riskTiers": RISK_TIERS,
        "calibrationStatuses": CALIBRATION_STATUSES,
        "decisions": DECISIONS,
        "requirements": POLICIES,
        "arbitraryMethodExecution": False,
        "serverBackedRegistry": False,
    }


def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "ready",
        "version": VERSION,
        "schemas": [REVIEW_SCHEMA, DECISION_SCHEMA, COMPARISON_SCHEMA],
        "riskTierCount": len(RISK_TIERS),
        "approvalWorkflow": True,
        "benchmarkCoverage": True,
        "calibrationTracking": True,
        "deprecationHistory": True,
        "hashVerification": True,
        "serverBackedRegistry": False,
    }


def normalize_review(payload: dict[str, Any]) -> dict[str, Any]:
    method_id = str(payload.get("methodId") or payload.get("method") or "").strip()
    title = str(payload.get("title") or payload.get("methodTitle") or method_id).strip()
    if not method_id:
        raise QualityReviewError("methodId is required.")
    risk = str(payload.get("riskTier") or "standard").strip().lower()
    if risk not in RISK_TIERS:
        raise QualityReviewError(f"Unsupported riskTier: {risk}")
    status = str(payload.get("status") or "draft").strip().lower()
    if status not in STATUSES:
        raise QualityReviewError(f"Unsupported status: {status}")
    calibration = payload.get("calibration") or {}
    calibration_status = str(calibration.get("status") or payload.get("calibrationStatus") or "not-required").strip().lower()
    if calibration_status not in CALIBRATION_STATUSES:
        raise QualityReviewError(f"Unsupported calibration status: {calibration_status}")
    reviewer = payload.get("reviewer") or {}
    review = {
        "schema": REVIEW_SCHEMA,
        "version": VERSION,
        "recordType": "method-review",
        "collection": "methodReviewRecords",
        "id": str(payload.get("id") or f"review-{_hash(payload)[:16]}"),
        "projectId": payload.get("projectId"),
        "methodId": method_id[:256],
        "title": title[:500],
        "methodVersion": str(payload.get("methodVersion") or "")[:128],
        "domain": str(payload.get("domain") or "")[:256],
        "owner": str(payload.get("owner") or "")[:256],
        "riskTier": risk,
        "status": status,
        "benchmarkIds": _strings(payload.get("benchmarkIds")),
        "benchmarkCoverage": _coverage(payload),
        "validationEvidenceIds": _strings(payload.get("validationEvidenceIds")),
        "sourceIds": _strings(payload.get("sourceIds")),
        "evidenceIds": _strings(payload.get("evidenceIds")),
        "reproducibleRunIds": _strings(payload.get("reproducibleRunIds")),
        "provenanceIds": _strings(payload.get("provenanceIds")),
        "assumptions": _strings(payload.get("assumptions")),
        "limitations": _strings(payload.get("limitations")),
        "knownIssues": _strings(payload.get("knownIssues")),
        "calibration": {
            "status": calibration_status,
            "lastCalibratedAt": calibration.get("lastCalibratedAt"),
            "dueAt": calibration.get("dueAt"),
            "reference": str(calibration.get("reference") or "")[:1000],
        },
        "reviewer": {
            "name": str(reviewer.get("name") or payload.get("reviewerName") or "")[:256],
            "role": str(reviewer.get("role") or payload.get("reviewerRole") or "")[:256],
            "independent": bool(reviewer.get("independent") or payload.get("independentReviewer")),
        },
        "reviewerNotes": str(payload.get("reviewerNotes") or "")[:12000],
        "decision": str(payload.get("decision") or "no-decision").strip().lower(),
        "decisionRationale": str(payload.get("decisionRationale") or "")[:12000],
        "createdAt": payload.get("createdAt") or _now(),
        "updatedAt": payload.get("updatedAt") or _now(),
        "history": (payload.get("history") or [])[:200],
    }
    if review["decision"] not in DECISIONS:
        raise QualityReviewError(f"Unsupported decision: {review['decision']}")
    review["sha256"] = _hash({k: v for k, v in review.items() if k != "sha256"})
    return review


def evaluate_review(payload: dict[str, Any]) -> dict[str, Any]:
    review = normalize_review(payload.get("review") or payload)
    policy = POLICIES[review["riskTier"]]
    issues: list[str] = []
    warnings: list[str] = []
    score = 20

    coverage = review["benchmarkCoverage"]
    if coverage["passed"] < policy["minimumBenchmarks"]:
        issues.append(f"At least {policy['minimumBenchmarks']} passed benchmark(s) are required.")
    else:
        score += min(20, coverage["passed"] * 10)
    if coverage["total"] and coverage["passed"] < coverage["total"]:
        warnings.append("One or more registered benchmarks are not passing.")

    evidence_count = len(review["validationEvidenceIds"])
    if evidence_count < policy["minimumValidationEvidence"]:
        issues.append(f"At least {policy['minimumValidationEvidence']} validation-evidence record(s) are required.")
    else:
        score += min(15, evidence_count * 7)

    if policy["requireLimitations"] and not review["limitations"]:
        issues.append("Known limitations must be documented.")
    elif review["limitations"]:
        score += 10

    if policy["requireReproducibleRun"] and not review["reproducibleRunIds"]:
        issues.append("A reproducible computational run is required.")
    elif review["reproducibleRunIds"]:
        score += 10

    if policy["requireProvenance"] and not (review["provenanceIds"] or review["evidenceIds"] or review["sourceIds"]):
        issues.append("Research provenance or linked evidence is required.")
    elif review["provenanceIds"] or review["evidenceIds"] or review["sourceIds"]:
        score += 10

    if policy["requireIndependentReviewer"] and not review["reviewer"]["independent"]:
        issues.append("An independent reviewer is required for high-consequence methods.")
    elif review["reviewer"]["name"]:
        score += 5

    if review["calibration"]["status"] in {"uncalibrated", "due", "expired"}:
        issues.append(f"Calibration status is {review['calibration']['status']}.")
    elif review["calibration"]["status"] in {"calibrated", "not-required"}:
        score += 5

    if review["knownIssues"]:
        warnings.append(f"{len(review['knownIssues'])} known issue(s) remain documented.")
    if not review["reviewerNotes"]:
        warnings.append("Reviewer notes are empty.")

    score = min(100, score)
    ready = not issues and score >= policy["minimumScore"]
    if ready:
        recommendation = "approved" if review["riskTier"] != "high-consequence" else "conditionally-approved"
    elif score >= max(40, policy["minimumScore"] - 15):
        recommendation = "changes-requested"
    else:
        recommendation = "draft"
    return {
        "ok": True,
        "version": VERSION,
        "review": review,
        "evaluation": {
            "readyForApproval": ready,
            "score": score,
            "minimumScore": policy["minimumScore"],
            "recommendation": recommendation,
            "issues": issues,
            "warnings": warnings,
            "policy": policy,
        },
    }


def verify_review(payload: dict[str, Any]) -> dict[str, Any]:
    record = payload.get("review") or payload.get("record") or payload
    expected = str(record.get("sha256") or "")
    actual = _hash({k: v for k, v in record.items() if k != "sha256"})
    return {"ok": bool(expected) and expected == actual, "expected": expected, "actual": actual, "recordType": record.get("recordType")}


def compare_reviews(payload: dict[str, Any]) -> dict[str, Any]:
    left = normalize_review(payload.get("left") or {})
    right = normalize_review(payload.get("right") or {})
    fields = ["status", "riskTier", "benchmarkCoverage", "validationEvidenceIds", "limitations", "knownIssues", "calibration", "reviewer", "decision"]
    differences = []
    for field in fields:
        if left.get(field) != right.get(field):
            differences.append({"field": field, "left": left.get(field), "right": right.get(field)})
    comparison = {
        "schema": COMPARISON_SCHEMA,
        "version": VERSION,
        "recordType": "method-review-comparison",
        "leftId": left["id"],
        "rightId": right["id"],
        "sameMethod": left["methodId"] == right["methodId"],
        "status": "unchanged" if not differences else "changed",
        "differences": differences,
        "createdAt": _now(),
    }
    comparison["sha256"] = _hash({k: v for k, v in comparison.items() if k != "sha256"})
    return {"ok": True, "version": VERSION, "comparison": comparison}
