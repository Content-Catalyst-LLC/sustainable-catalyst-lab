from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

VERSION = "0.25.3"
ENGINE_VERSION = "0.25.0"
PRODUCTION_VERSION = "0.25.1"
LIVE_VERSION = "0.25.2"
CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "contracts"
    / "instrumentation-validation-custody-v0253.json"
)


class InstrumentationValidationError(ValueError):
    """Raised when instrumentation validation input is invalid."""


def contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise InstrumentationValidationError(f"{label} must be numerical.") from exc
    if not math.isfinite(number):
        raise InstrumentationValidationError(f"{label} must be finite.")
    return number


def _positive(value: Any, label: str) -> float:
    number = _finite(value, label)
    if number <= 0:
        raise InstrumentationValidationError(f"{label} must be greater than zero.")
    return number


def _values(value: Any, label: str, minimum: int = 1) -> list[float]:
    if not isinstance(value, list) or len(value) < minimum:
        raise InstrumentationValidationError(
            f"{label} must contain at least {minimum} values."
        )
    return [_finite(item, f"{label}[{index}]") for index, item in enumerate(value)]


def _paired(left: Any, right: Any) -> tuple[list[float], list[float]]:
    a = _values(left, "measuredValues")
    b = _values(right, "referenceValues")
    if len(a) != len(b):
        raise InstrumentationValidationError(
            "measuredValues and referenceValues must have equal length."
        )
    return a, b


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    average = _mean(values)
    return math.sqrt(
        sum((value - average) ** 2 for value in values)
        / (len(values) - 1)
    )


def calibration_absolute_error(measured: Any, reference: Any) -> float:
    return abs(_finite(measured, "measured") - _finite(reference, "reference"))


def calibration_percent_error(measured: Any, reference: Any) -> float:
    return calibration_absolute_error(measured, reference) / abs(
        _positive(reference, "reference")
    ) * 100


def calibration_bias(measured_values: Any, reference_values: Any) -> float:
    measured, reference = _paired(measured_values, reference_values)
    return _mean([m - r for m, r in zip(measured, reference)])


def calibration_rmse(measured_values: Any, reference_values: Any) -> float:
    measured, reference = _paired(measured_values, reference_values)
    return math.sqrt(
        _mean([(m - r) ** 2 for m, r in zip(measured, reference)])
    )


def calibration_linearity_r2(reference_values: Any, measured_values: Any) -> float:
    reference, measured = _paired(reference_values, measured_values)
    x_mean = _mean(reference)
    y_mean = _mean(measured)
    numerator = sum(
        (x - x_mean) * (y - y_mean)
        for x, y in zip(reference, measured)
    )
    x_square = sum((x - x_mean) ** 2 for x in reference)
    y_square = sum((y - y_mean) ** 2 for y in measured)
    if x_square == 0 or y_square == 0:
        raise InstrumentationValidationError(
            "Linearity requires non-constant measured and reference values."
        )
    correlation = numerator / math.sqrt(x_square * y_square)
    return correlation * correlation


def repeatability_cv(values: Any) -> float:
    numbers = _values(values, "values", 2)
    average = _mean(numbers)
    if average == 0:
        raise InstrumentationValidationError(
            "repeatability CV requires a non-zero mean."
        )
    return _sd(numbers) / abs(average) * 100


def acceptance_window_status(
    value: Any,
    target: Any,
    warning_tolerance: Any,
    action_tolerance: Any,
) -> str:
    delta = abs(_finite(value, "value") - _finite(target, "target"))
    warning = _positive(warning_tolerance, "warningTolerance")
    action = _positive(action_tolerance, "actionTolerance")
    if action < warning:
        raise InstrumentationValidationError(
            "actionTolerance must be at least warningTolerance."
        )
    if delta > action:
        return "action"
    if delta > warning:
        return "warning"
    return "accepted"


def due_state(
    elapsed: Any,
    interval: Any,
    warning_lead: Any,
) -> str:
    days = _finite(elapsed, "elapsedDays")
    limit = _positive(interval, "intervalDays")
    lead = max(0.0, _finite(warning_lead, "warningLeadDays"))
    if days > limit:
        return "overdue"
    if days >= max(0.0, limit - lead):
        return "due-soon"
    return "current"


def measurement_completeness(present_count: Any, expected_count: Any) -> float:
    return max(
        0.0,
        min(
            100.0,
            _finite(present_count, "presentCount")
            / _positive(expected_count, "expectedCount")
            * 100,
        ),
    )


def quality_flag_rate(flagged_count: Any, total_count: Any) -> float:
    return max(
        0.0,
        min(
            100.0,
            _finite(flagged_count, "flaggedCount")
            / _positive(total_count, "totalCount")
            * 100,
        ),
    )


def custody_completeness(complete_event_count: Any, total_event_count: Any) -> float:
    return measurement_completeness(
        complete_event_count,
        total_event_count,
    )


def custody_sequence_status(events: Any) -> dict[str, Any]:
    if not isinstance(events, list):
        raise InstrumentationValidationError("events must be an array.")
    previous_hash = ""
    previous_timestamp: float | None = None
    problems: list[str] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            problems.append(f"event-{index + 1}-not-object")
            continue
        timestamp = _finite(event.get("timestamp"), f"events[{index}].timestamp")
        if previous_timestamp is not None and timestamp < previous_timestamp:
            problems.append(f"event-{index + 1}-timestamp-order")
        if str(event.get("previousHash") or "") != previous_hash:
            problems.append(f"event-{index + 1}-parent-hash")
        event_hash = str(event.get("eventHash") or "")
        if not event_hash:
            problems.append(f"event-{index + 1}-missing-hash")
        previous_hash = event_hash
        previous_timestamp = timestamp
    return {
        "valid": len(problems) == 0,
        "eventCount": len(events),
        "problems": problems,
        "headHash": previous_hash,
    }


def deviation_rate(deviation_count: Any, reviewed_item_count: Any) -> float:
    return _finite(deviation_count, "deviationCount") / _positive(
        reviewed_item_count,
        "reviewedItemCount",
    ) * 100


def validation_score(profile_scores: Any, weights: Any) -> float:
    if not isinstance(profile_scores, dict) or not profile_scores:
        raise InstrumentationValidationError(
            "profileScores must be a non-empty object."
        )
    if not isinstance(weights, dict):
        weights = {}
    numerator = 0.0
    denominator = 0.0
    for profile_id, raw_score in profile_scores.items():
        score = max(0.0, min(100.0, _finite(raw_score, profile_id)))
        weight = max(0.0, _finite(weights.get(profile_id, 1), f"weight:{profile_id}"))
        numerator += score * weight
        denominator += weight
    if denominator == 0:
        raise InstrumentationValidationError("At least one validation weight must be positive.")
    return numerator / denominator


def validation_disposition(
    score: Any,
    critical_failure_count: Any,
    open_deviation_count: Any,
    expired_record_count: Any,
) -> str:
    value = _finite(score, "score")
    critical = int(_finite(critical_failure_count, "criticalFailureCount"))
    deviations = int(_finite(open_deviation_count, "openDeviationCount"))
    expired = int(_finite(expired_record_count, "expiredRecordCount"))
    if critical > 0:
        return "rejected"
    if expired > 0 or value < 70:
        return "hold"
    if value < 85 or deviations > 0:
        return "conditionally-accepted"
    return "accepted"


def execute(method_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    i = inputs or {}
    dispatch = {
        "calibration-absolute-error": lambda: calibration_absolute_error(i.get("measured"), i.get("reference")),
        "calibration-percent-error": lambda: calibration_percent_error(i.get("measured"), i.get("reference")),
        "calibration-bias": lambda: calibration_bias(i.get("measuredValues"), i.get("referenceValues")),
        "calibration-rmse": lambda: calibration_rmse(i.get("measuredValues"), i.get("referenceValues")),
        "calibration-linearity-r2": lambda: calibration_linearity_r2(i.get("referenceValues"), i.get("measuredValues")),
        "repeatability-cv": lambda: repeatability_cv(i.get("values")),
        "acceptance-window-status": lambda: acceptance_window_status(i.get("value"), i.get("target"), i.get("warningTolerance"), i.get("actionTolerance")),
        "calibration-due-state": lambda: due_state(i.get("daysSinceCalibration"), i.get("calibrationIntervalDays"), i.get("warningLeadDays")),
        "maintenance-due-state": lambda: due_state(i.get("daysSinceMaintenance"), i.get("maintenanceIntervalDays"), i.get("warningLeadDays")),
        "measurement-completeness": lambda: measurement_completeness(i.get("presentCount"), i.get("expectedCount")),
        "quality-flag-rate": lambda: quality_flag_rate(i.get("flaggedCount"), i.get("totalCount")),
        "custody-completeness": lambda: custody_completeness(i.get("completeEventCount"), i.get("totalEventCount")),
        "custody-sequence-status": lambda: custody_sequence_status(i.get("events")),
        "deviation-rate": lambda: deviation_rate(i.get("deviationCount"), i.get("reviewedItemCount")),
        "validation-score": lambda: validation_score(i.get("profileScores"), i.get("weights")),
        "validation-disposition": lambda: validation_disposition(i.get("score"), i.get("criticalFailureCount"), i.get("openDeviationCount"), i.get("expiredRecordCount")),
    }
    if method_id not in dispatch:
        raise InstrumentationValidationError(
            f"Unknown instrumentation validation method: {method_id}"
        )
    return {
        "schema": "sc-lab-instrumentation-validation-result/1.0",
        "version": VERSION,
        "methodId": method_id,
        "inputs": inputs,
        "value": dispatch[method_id](),
    }


def create_manifest(components: dict[str, Any], metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(components, dict) or not components:
        raise InstrumentationValidationError(
            "components must be a non-empty object."
        )
    component_hashes = {
        key: sha256_text(canonical_json(value))
        for key, value in sorted(components.items())
    }
    payload = {
        "schema": "sc-lab-instrumentation-validation-manifest/1.0",
        "version": VERSION,
        "components": components,
        "componentHashes": component_hashes,
        "metadata": metadata or {},
    }
    payload["manifestHash"] = sha256_text(canonical_json(payload))
    return payload


def create_custody_event(
    sample_id: str,
    action: str,
    actor: str,
    location: str,
    timestamp: Any,
    previous_hash: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schema": "sc-lab-instrumentation-custody-event/1.0",
        "version": VERSION,
        "sampleId": str(sample_id),
        "action": str(action),
        "actor": str(actor),
        "location": str(location),
        "timestamp": _finite(timestamp, "timestamp"),
        "previousHash": str(previous_hash or ""),
        "metadata": metadata or {},
    }
    payload["eventHash"] = sha256_text(canonical_json(payload))
    return payload


def verify_custody_chain(events: Any) -> dict[str, Any]:
    if not isinstance(events, list):
        raise InstrumentationValidationError("events must be an array.")
    previous_hash = ""
    problems: list[str] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            problems.append(f"event-{index + 1}-not-object")
            continue
        stored_hash = str(event.get("eventHash") or "")
        payload = dict(event)
        payload.pop("eventHash", None)
        calculated_hash = sha256_text(canonical_json(payload))
        if stored_hash != calculated_hash:
            problems.append(f"event-{index + 1}-hash")
        if str(event.get("previousHash") or "") != previous_hash:
            problems.append(f"event-{index + 1}-chain")
        previous_hash = stored_hash
    return {
        "valid": len(problems) == 0,
        "eventCount": len(events),
        "headHash": previous_hash,
        "problems": problems,
    }


def create_dossier(
    profile_results: dict[str, Any],
    manifest: dict[str, Any],
    custody_events: list[dict[str, Any]],
    deviations: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scores = {
        profile_id: float(result.get("score", 0))
        for profile_id, result in profile_results.items()
    }
    score = validation_score(scores, {})
    critical = sum(
        1
        for result in profile_results.values()
        if result.get("criticalFailure")
    )
    expired = sum(
        1
        for result in profile_results.values()
        if result.get("expired")
    )
    disposition = validation_disposition(
        score,
        critical,
        len([item for item in deviations if not item.get("closed")]),
        expired,
    )
    custody = verify_custody_chain(custody_events)
    dossier = {
        "schema": "sc-lab-instrumentation-validation-dossier/1.0",
        "version": VERSION,
        "profileResults": profile_results,
        "validationScore": score,
        "disposition": disposition,
        "manifest": manifest,
        "custodyVerification": custody,
        "deviations": deviations,
        "metadata": metadata or {},
    }
    dossier["dossierHash"] = sha256_text(canonical_json(dossier))
    return dossier
