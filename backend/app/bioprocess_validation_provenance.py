from __future__ import annotations

import hashlib
import json
import math
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.22.3"
CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "contracts"
    / "bioprocess-validation-provenance-v0223.json"
)


class BioprocessValidationError(ValueError):
    """Raised when bioprocess validation input is invalid."""


def contract() -> dict[str, Any]:
    return json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8")
    )


def _profile(profile_id: str) -> dict[str, Any]:
    for profile in contract()["profiles"]:
        if profile["id"] == profile_id:
            return profile

    raise BioprocessValidationError(
        f"Unknown validation profile: {profile_id}"
    )


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BioprocessValidationError(
            f"{label} must be numerical."
        ) from exc

    if not math.isfinite(number):
        raise BioprocessValidationError(
            f"{label} must be finite."
        )

    return number


def _mean(values: list[float]) -> float:
    if not values:
        raise BioprocessValidationError(
            "At least one value is required."
        )

    return sum(values) / len(values)


def _sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    average = _mean(values)
    return math.sqrt(
        sum(
            (value - average) ** 2
            for value in values
        )
        / (len(values) - 1)
    )


def _cv(values: list[float]) -> float | None:
    average = _mean(values)

    if average == 0:
        return None

    return abs(_sd(values) / average) * 100


def _check(
    identifier: str,
    label: str,
    value: Any,
    operator: str,
    limit: Any,
    passed: bool,
    unit: str = "",
) -> dict[str, Any]:
    return {
        "id": identifier,
        "label": label,
        "value": value,
        "operator": operator,
        "limit": limit,
        "unit": unit,
        "passed": bool(passed),
        "status": "pass" if passed else "fail",
    }


def _thresholds(
    profile: dict[str, Any],
    supplied: dict[str, Any],
) -> dict[str, float]:
    return {
        definition["key"]: _finite(
            supplied.get(
                definition["key"],
                definition["default"],
            ),
            definition["label"],
        )
        for definition in profile["thresholds"]
    }


def _required_rows(
    profile: dict[str, Any],
    rows: list[dict[str, Any]],
) -> None:
    if not rows:
        raise BioprocessValidationError(
            "Validation requires at least one data row."
        )

    for index, row in enumerate(rows):
        for column in profile["requiredColumns"]:
            if column not in row:
                raise BioprocessValidationError(
                    f"Required column {column} is missing "
                    f"from row {index + 1}."
                )


def _linear_regression(
    points: list[tuple[float, float]],
) -> dict[str, float]:
    if len(points) < 2:
        raise BioprocessValidationError(
            "At least two points are required."
        )

    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]
    x_mean = _mean(x_values)
    y_mean = _mean(y_values)
    denominator = sum(
        (value - x_mean) ** 2
        for value in x_values
    )

    if denominator == 0:
        raise BioprocessValidationError(
            "Hold-time observations must use distinct times."
        )

    slope = (
        sum(
            (x - x_mean) * (y - y_mean)
            for x, y in points
        )
        / denominator
    )
    intercept = y_mean - slope * x_mean

    return {
        "slope": slope,
        "intercept": intercept,
    }


def evaluate(
    profile_id: str,
    rows: list[dict[str, Any]],
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = _profile(profile_id)
    _required_rows(profile, rows)
    limits = _thresholds(profile, thresholds or {})
    metrics: dict[str, Any] = {}
    checks: list[dict[str, Any]] = []

    if profile_id == "batch-record-completeness":
        required = profile["requiredColumns"]
        missing = 0
        evidence_counts: list[int] = []
        batch_results: list[dict[str, Any]] = []

        for row in rows:
            missing_fields = [
                key
                for key in required
                if key != "evidenceLinks"
                and not str(row.get(key) or "").strip()
            ]
            evidence = row.get("evidenceLinks") or []

            if isinstance(evidence, str):
                evidence = [
                    item.strip()
                    for item in evidence.split("|")
                    if item.strip()
                ]

            evidence_count = len(evidence)
            evidence_counts.append(evidence_count)
            missing += len(missing_fields)
            batch_results.append(
                {
                    "batchId": row.get("batchId"),
                    "missingFields": missing_fields,
                    "evidenceCount": evidence_count,
                }
            )

        minimum_evidence = min(evidence_counts)
        metrics = {
            "batchCount": len(rows),
            "missingFieldCount": missing,
            "minimumEvidenceLinks": minimum_evidence,
            "batches": batch_results,
        }
        checks = [
            _check(
                "maximum-missing-fields",
                "Missing required fields",
                missing,
                "<=",
                limits["maximumMissingFields"],
                missing <= limits["maximumMissingFields"],
            ),
            _check(
                "minimum-evidence-links",
                "Minimum evidence links",
                minimum_evidence,
                ">=",
                limits["minimumEvidenceLinks"],
                minimum_evidence
                >= limits["minimumEvidenceLinks"],
            ),
        ]

    elif profile_id == "cpp-conformance":
        action_count = 0
        warning_count = 0
        observations: list[dict[str, Any]] = []

        for index, row in enumerate(rows):
            value = _finite(
                row.get("value"),
                f"value on row {index + 1}",
            )
            low = _finite(
                row.get("low"),
                f"low on row {index + 1}",
            )
            high = _finite(
                row.get("high"),
                f"high on row {index + 1}",
            )

            if low > high:
                raise BioprocessValidationError(
                    f"low exceeds high on row {index + 1}."
                )

            status = "pass"

            if value < low or value > high:
                status = "action"
                action_count += 1
            else:
                span = high - low
                warning_band = span * 0.1

                if (
                    value < low + warning_band
                    or value > high - warning_band
                ):
                    status = "warning"
                    warning_count += 1

            observations.append(
                {
                    "parameter": row.get("parameter"),
                    "value": value,
                    "low": low,
                    "high": high,
                    "status": status,
                }
            )

        warning_percent = warning_count / len(rows) * 100
        metrics = {
            "observationCount": len(rows),
            "actionExcursionCount": action_count,
            "warningCount": warning_count,
            "warningPercent": warning_percent,
            "observations": observations,
        }
        checks = [
            _check(
                "maximum-action-excursions",
                "Action-limit excursions",
                action_count,
                "<=",
                limits["maximumActionExcursions"],
                action_count
                <= limits["maximumActionExcursions"],
            ),
            _check(
                "maximum-warning-percent",
                "Warning observations",
                warning_percent,
                "<=",
                limits["maximumWarningPercent"],
                warning_percent
                <= limits["maximumWarningPercent"],
                "%",
            ),
        ]

    elif profile_id == "cqa-conformance":
        failures = 0
        observations = []

        for index, row in enumerate(rows):
            value = _finite(
                row.get("value"),
                f"value on row {index + 1}",
            )
            low = _finite(
                row.get("low"),
                f"low on row {index + 1}",
            )
            high = _finite(
                row.get("high"),
                f"high on row {index + 1}",
            )
            passed = low <= value <= high
            failures += 0 if passed else 1
            observations.append(
                {
                    "attribute": row.get("attribute"),
                    "value": value,
                    "low": low,
                    "high": high,
                    "status": "pass" if passed else "fail",
                }
            )

        pass_percent = (
            (len(rows) - failures)
            / len(rows)
            * 100
        )
        metrics = {
            "observationCount": len(rows),
            "failureCount": failures,
            "passPercent": pass_percent,
            "observations": observations,
        }
        checks = [
            _check(
                "maximum-failures",
                "Failed CQA observations",
                failures,
                "<=",
                limits["maximumFailures"],
                failures <= limits["maximumFailures"],
            ),
            _check(
                "minimum-pass-percent",
                "CQA pass rate",
                pass_percent,
                ">=",
                limits["minimumPassPercent"],
                pass_percent
                >= limits["minimumPassPercent"],
                "%",
            ),
        ]

    elif profile_id == "cross-batch-consistency":
        yields = [
            _finite(row.get("yield"), "yield")
            for row in rows
        ]
        titers = [
            _finite(row.get("titer"), "titer")
            for row in rows
        ]
        cycle_times = [
            _finite(row.get("cycleTime"), "cycleTime")
            for row in rows
        ]
        yield_cv = _cv(yields)
        titer_cv = _cv(titers)
        cycle_cv = _cv(cycle_times)
        metrics = {
            "batchCount": len(rows),
            "yield": {
                "mean": _mean(yields),
                "standardDeviation": _sd(yields),
                "coefficientOfVariationPercent": yield_cv,
            },
            "titer": {
                "mean": _mean(titers),
                "standardDeviation": _sd(titers),
                "coefficientOfVariationPercent": titer_cv,
            },
            "cycleTime": {
                "mean": _mean(cycle_times),
                "standardDeviation": _sd(cycle_times),
                "coefficientOfVariationPercent": cycle_cv,
            },
        }
        checks = [
            _check(
                "minimum-batches",
                "Comparable batches",
                len(rows),
                ">=",
                limits["minimumBatches"],
                len(rows) >= limits["minimumBatches"],
            ),
            _check(
                "maximum-yield-cv",
                "Yield CV",
                yield_cv,
                "<=",
                limits["maximumYieldCvPercent"],
                yield_cv is not None
                and yield_cv
                <= limits["maximumYieldCvPercent"],
                "%",
            ),
            _check(
                "maximum-titer-cv",
                "Titer CV",
                titer_cv,
                "<=",
                limits["maximumTiterCvPercent"],
                titer_cv is not None
                and titer_cv
                <= limits["maximumTiterCvPercent"],
                "%",
            ),
            _check(
                "maximum-cycle-time-cv",
                "Cycle-time CV",
                cycle_cv,
                "<=",
                limits["maximumCycleTimeCvPercent"],
                cycle_cv is not None
                and cycle_cv
                <= limits["maximumCycleTimeCvPercent"],
                "%",
            ),
        ]

    elif profile_id == "monitoring-control-performance":
        actions = sum(
            int(_finite(row.get("actionCount"), "actionCount"))
            for row in rows
        )
        warnings = sum(
            int(_finite(row.get("warningCount"), "warningCount"))
            for row in rows
        )
        final_errors = [
            abs(_finite(row.get("finalError"), "finalError"))
            for row in rows
        ]
        iae_values = [
            _finite(
                row.get("integralAbsoluteError"),
                "integralAbsoluteError",
            )
            for row in rows
        ]
        maximum_final_error = max(final_errors)
        maximum_iae = max(iae_values)
        metrics = {
            "runCount": len(rows),
            "actionCount": actions,
            "warningCount": warnings,
            "maximumAbsoluteFinalError": maximum_final_error,
            "meanAbsoluteFinalError": _mean(final_errors),
            "maximumIntegralAbsoluteError": maximum_iae,
            "meanIntegralAbsoluteError": _mean(iae_values),
        }
        checks = [
            _check(
                "maximum-actions",
                "Action excursions",
                actions,
                "<=",
                limits["maximumActionCount"],
                actions <= limits["maximumActionCount"],
            ),
            _check(
                "maximum-warnings",
                "Warnings",
                warnings,
                "<=",
                limits["maximumWarningCount"],
                warnings <= limits["maximumWarningCount"],
            ),
            _check(
                "maximum-final-error",
                "Maximum absolute final error",
                maximum_final_error,
                "<=",
                limits["maximumAbsoluteFinalError"],
                maximum_final_error
                <= limits["maximumAbsoluteFinalError"],
            ),
            _check(
                "maximum-iae",
                "Maximum integral absolute error",
                maximum_iae,
                "<=",
                limits["maximumIntegralAbsoluteError"],
                maximum_iae
                <= limits["maximumIntegralAbsoluteError"],
            ),
        ]

    elif profile_id == "excursion-disposition":
        open_actions = 0
        undocumented = 0

        for row in rows:
            severity = str(
                row.get("severity") or ""
            ).strip().lower()
            status = str(
                row.get("status") or ""
            ).strip().lower()
            investigation = str(
                row.get("investigationId") or ""
            ).strip()
            evidence = str(
                row.get("evidenceLink") or ""
            ).strip()

            if severity == "action" and status not in {
                "closed",
                "resolved",
                "accepted",
            }:
                open_actions += 1

            if not investigation or not evidence:
                undocumented += 1

        metrics = {
            "excursionCount": len(rows),
            "openActionExcursionCount": open_actions,
            "undocumentedExcursionCount": undocumented,
        }
        checks = [
            _check(
                "maximum-open-actions",
                "Open action excursions",
                open_actions,
                "<=",
                limits["maximumOpenActionExcursions"],
                open_actions
                <= limits["maximumOpenActionExcursions"],
            ),
            _check(
                "maximum-undocumented",
                "Undocumented excursions",
                undocumented,
                "<=",
                limits["maximumUndocumentedExcursions"],
                undocumented
                <= limits["maximumUndocumentedExcursions"],
            ),
        ]

    elif profile_id == "hold-time-stability":
        points = [
            (
                _finite(row.get("time"), "time"),
                _finite(row.get("value"), "value"),
            )
            for row in rows
        ]
        points.sort(key=lambda point: point[0])
        baseline = points[0][1]

        if baseline == 0:
            raise BioprocessValidationError(
                "The initial hold-time value cannot be zero."
            )

        final_change = (
            (points[-1][1] - baseline)
            / baseline
            * 100
        )
        regression = _linear_regression(points)
        slope_percent = (
            regression["slope"]
            / baseline
            * 100
        )
        metrics = {
            "pointCount": len(points),
            "initialValue": baseline,
            "finalValue": points[-1][1],
            "absoluteChangePercent": abs(final_change),
            "signedChangePercent": final_change,
            "slope": regression["slope"],
            "slopePercentPerHour": slope_percent,
        }
        checks = [
            _check(
                "minimum-points",
                "Hold-time observations",
                len(points),
                ">=",
                limits["minimumPoints"],
                len(points) >= limits["minimumPoints"],
            ),
            _check(
                "maximum-change",
                "Absolute hold-time change",
                abs(final_change),
                "<=",
                limits["maximumAbsoluteChangePercent"],
                abs(final_change)
                <= limits["maximumAbsoluteChangePercent"],
                "%",
            ),
            _check(
                "maximum-slope",
                "Absolute hold-time slope",
                abs(slope_percent),
                "<=",
                limits["maximumSlopePercentPerHour"],
                abs(slope_percent)
                <= limits["maximumSlopePercentPerHour"],
                "%/h",
            ),
        ]

    elif profile_id == "release-readiness":
        failed_critical = 0
        open_major = 0
        evidence_count = 0

        for row in rows:
            status = str(
                row.get("status") or ""
            ).strip().lower()
            category = str(
                row.get("category") or ""
            ).strip().lower()
            critical = str(
                row.get("critical") or ""
            ).strip().lower() in {
                "1",
                "true",
                "yes",
                "critical",
            }
            evidence = str(
                row.get("evidence") or ""
            ).strip()

            if critical and status not in {
                "pass",
                "passed",
                "closed",
                "complete",
            }:
                failed_critical += 1

            if (
                category == "major"
                and status not in {
                    "pass",
                    "passed",
                    "closed",
                    "complete",
                }
            ):
                open_major += 1

            if evidence:
                evidence_count += 1

        evidence_percent = (
            evidence_count
            / len(rows)
            * 100
        )
        metrics = {
            "checkCount": len(rows),
            "failedCriticalCheckCount": failed_critical,
            "openMajorCheckCount": open_major,
            "evidenceCoveragePercent": evidence_percent,
        }
        checks = [
            _check(
                "maximum-failed-critical",
                "Failed critical checks",
                failed_critical,
                "<=",
                limits["maximumFailedCriticalChecks"],
                failed_critical
                <= limits["maximumFailedCriticalChecks"],
            ),
            _check(
                "maximum-open-major",
                "Open major checks",
                open_major,
                "<=",
                limits["maximumOpenMajorChecks"],
                open_major
                <= limits["maximumOpenMajorChecks"],
            ),
            _check(
                "minimum-evidence-coverage",
                "Evidence coverage",
                evidence_percent,
                ">=",
                limits["minimumEvidenceCoveragePercent"],
                evidence_percent
                >= limits["minimumEvidenceCoveragePercent"],
                "%",
            ),
        ]

    else:
        raise BioprocessValidationError(
            f"Unsupported validation profile: {profile_id}"
        )

    failed = [
        check
        for check in checks
        if not check["passed"]
    ]
    decision = "fail" if failed else "pass"

    return {
        "schema": "sc-lab-bioprocess-validation-result/1.0",
        "version": VERSION,
        "profile": profile,
        "thresholds": limits,
        "metrics": metrics,
        "checks": checks,
        "decision": decision,
        "failedCheckCount": len(failed),
        "releaseRecommendation": (
            "hold"
            if failed
            else "release"
        ),
    }


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def fingerprint(value: Any) -> str:
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def create_record(
    payload: Any,
    metadata: dict[str, Any] | None = None,
    previous_hash: str | None = None,
) -> dict[str, Any]:
    metadata = dict(metadata or {})
    allowed_event_types = {
        item["id"]
        for item in contract()["eventTypes"]
    }
    event_type = str(
        metadata.get("eventType")
        or contract()["defaults"]["eventType"]
    )

    if event_type not in allowed_event_types:
        raise BioprocessValidationError(
            f"Unknown provenance event type: {event_type}"
        )

    record = {
        "schema": "sc-lab-bioprocess-batch-provenance/1.0",
        "version": VERSION,
        "recordId": (
            metadata.get("recordId")
            or (
                "scbatch-"
                + datetime.now(timezone.utc).strftime(
                    "%Y%m%d%H%M%S"
                )
                + "-"
                + secrets.token_hex(5)
            )
        ),
        "eventType": event_type,
        "timestamp": (
            metadata.get("timestamp")
            or datetime.now(timezone.utc).isoformat()
        ),
        "batchId": metadata.get("batchId"),
        "lotId": metadata.get("lotId"),
        "runId": metadata.get("runId"),
        "profileId": metadata.get("profileId"),
        "analyst": metadata.get("analyst"),
        "reviewer": metadata.get("reviewer"),
        "organization": (
            metadata.get("organization")
            or contract()["defaults"]["organization"]
        ),
        "instrument": metadata.get("instrument"),
        "sourceRecordIds": list(
            metadata.get("sourceRecordIds") or []
        ),
        "evidenceLinks": list(
            metadata.get("evidenceLinks") or []
        ),
        "disposition": (
            metadata.get("disposition")
            or contract()["defaults"]["disposition"]
        ),
        "notes": metadata.get("notes"),
        "previousHash": previous_hash,
        "payloadHash": fingerprint(payload),
        "payload": payload,
        "engine": {
            "validationRelease": VERSION,
            "bioprocessEngineVersion": "0.22.0",
            "productionReliabilityVersion": "0.22.1",
            "monitoringControlVersion": "0.22.2",
        },
    }
    record["recordHash"] = fingerprint(record)
    return record


def verify_ledger(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    previous_hash: str | None = None

    for record in records:
        copy = dict(record)
        stored_hash = str(
            copy.pop("recordHash", "")
        )
        calculated_hash = fingerprint(copy)
        payload_valid = (
            record.get("payloadHash")
            == fingerprint(record.get("payload"))
        )
        hash_valid = secrets.compare_digest(
            stored_hash,
            calculated_hash,
        )
        chain_valid = (
            record.get("previousHash")
            == previous_hash
        )
        results.append(
            {
                "recordId": record.get("recordId"),
                "payloadValid": payload_valid,
                "hashValid": hash_valid,
                "chainValid": chain_valid,
                "valid": (
                    payload_valid
                    and hash_valid
                    and chain_valid
                ),
                "storedHash": stored_hash,
                "calculatedHash": calculated_hash,
            }
        )
        previous_hash = stored_hash

    return {
        "schema": "sc-lab-bioprocess-ledger-verification/1.0",
        "version": VERSION,
        "valid": all(
            result["valid"]
            for result in results
        ),
        "recordCount": len(records),
        "results": results,
    }


def create_dossier(
    validation_results: list[dict[str, Any]],
    batch: dict[str, Any] | None = None,
    records: list[dict[str, Any]] | None = None,
    disposition: str | None = None,
) -> dict[str, Any]:
    batch = dict(batch or {})
    records = list(records or [])
    failed_results = [
        result
        for result in validation_results
        if result.get("decision") != "pass"
    ]
    ledger = verify_ledger(records)
    resolved_disposition = (
        disposition
        or (
            "hold"
            if failed_results or not ledger["valid"]
            else "release"
        )
    )
    dossier = {
        "schema": "sc-lab-bioprocess-validation-dossier/1.0",
        "version": VERSION,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "batch": batch,
        "summary": {
            "validationResultCount": len(validation_results),
            "failedValidationCount": len(failed_results),
            "recordCount": len(records),
            "ledgerValid": ledger["valid"],
            "disposition": resolved_disposition,
            "releaseReady": (
                not failed_results
                and ledger["valid"]
                and resolved_disposition == "release"
            ),
        },
        "validationResults": validation_results,
        "provenanceLedger": records,
        "ledgerVerification": ledger,
        "responsibleUse": contract()["responsibleUse"],
    }
    dossier["dossierHash"] = fingerprint(dossier)
    return dossier
