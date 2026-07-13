from __future__ import annotations

import hashlib
import json
import math
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.21.3"

PROFILES_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "molecular-analysis-validation-profiles-v0213.json"
)


class MolecularValidationError(ValueError):
    """Raised when molecular validation input is invalid."""


def profiles_contract() -> dict[str, Any]:
    return json.loads(
        PROFILES_PATH.read_text(encoding="utf-8")
    )


def _profile(profile_id: str) -> dict[str, Any]:
    for profile in profiles_contract()["profiles"]:
        if profile["id"] == profile_id:
            return profile

    raise MolecularValidationError(
        f"Unknown validation profile: {profile_id}"
    )


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise MolecularValidationError(
            f"{label} must be numerical."
        ) from exc

    if not math.isfinite(number):
        raise MolecularValidationError(
            f"{label} must be finite."
        )

    return number


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _standard_deviation(values: list[float]) -> float:
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


def _regression(
    points: list[dict[str, float]],
) -> dict[str, float]:
    if len(points) < 2:
        raise MolecularValidationError(
            "At least two calibration points are required."
        )

    x_mean = _mean([point["x"] for point in points])
    y_mean = _mean([point["y"] for point in points])
    numerator = sum(
        (point["x"] - x_mean)
        * (point["y"] - y_mean)
        for point in points
    )
    denominator = sum(
        (point["x"] - x_mean) ** 2
        for point in points
    )

    if denominator == 0:
        raise MolecularValidationError(
            "Calibration concentrations must vary."
        )

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    total = sum(
        (point["y"] - y_mean) ** 2
        for point in points
    )
    residual = sum(
        (
            point["y"]
            - (slope * point["x"] + intercept)
        )
        ** 2
        for point in points
    )

    return {
        "slope": slope,
        "intercept": intercept,
        "rSquared": (
            1.0
            if total == 0
            else 1.0 - residual / total
        ),
    }


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


def _resolved_thresholds(
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


def _required_columns(
    profile: dict[str, Any],
    rows: list[dict[str, Any]],
) -> None:
    if not rows:
        raise MolecularValidationError(
            "Validation requires at least one data row."
        )

    for column in profile["requiredColumns"]:
        if column not in rows[0]:
            raise MolecularValidationError(
                f"Required data column is missing: {column}"
            )


def _numeric_column(
    rows: list[dict[str, Any]],
    key: str,
) -> list[float]:
    return [
        _finite(
            row.get(key),
            f"{key} on data row {index + 1}",
        )
        for index, row in enumerate(rows)
    ]


def _grouped_values(
    rows: list[dict[str, Any]],
    group_key: str,
) -> dict[str, list[float]]:
    groups: dict[str, list[float]] = {}

    for index, row in enumerate(rows):
        group = str(row.get(group_key) or "").strip()

        if not group:
            raise MolecularValidationError(
                f"{group_key} is required on data row "
                f"{index + 1}."
            )

        value = _finite(
            row.get("value"),
            f"value on data row {index + 1}",
        )
        groups.setdefault(group, []).append(value)

    return groups


def validate_profile(
    profile_id: str,
    rows: list[dict[str, Any]],
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = _profile(profile_id)
    _required_columns(profile, rows)
    resolved = _resolved_thresholds(
        profile,
        thresholds or {},
    )
    metrics: dict[str, Any] = {}
    checks: list[dict[str, Any]] = []

    if profile_id == "precision-repeatability":
        values = _numeric_column(rows, "value")
        average = _mean(values)
        deviation = _standard_deviation(values)
        cv = (
            None
            if average == 0
            else abs(deviation / average) * 100
        )
        metrics = {
            "n": len(values),
            "mean": average,
            "standardDeviation": deviation,
            "coefficientOfVariationPercent": cv,
            "minimum": min(values),
            "maximum": max(values),
        }
        checks = [
            _check(
                "minimum-replicates",
                "Replicate count",
                len(values),
                ">=",
                resolved["minimumReplicates"],
                len(values)
                >= resolved["minimumReplicates"],
            ),
            _check(
                "maximum-cv",
                "Coefficient of variation",
                cv,
                "<=",
                resolved["maximumCvPercent"],
                cv is not None
                and cv <= resolved["maximumCvPercent"],
                "%",
            ),
        ]

    elif profile_id == "accuracy-recovery":
        recoveries: list[float] = []
        biases: list[float] = []

        for index, row in enumerate(rows):
            expected = _finite(
                row.get("expected"),
                f"expected on data row {index + 1}",
            )
            measured = _finite(
                row.get("measured"),
                f"measured on data row {index + 1}",
            )

            if expected == 0:
                raise MolecularValidationError(
                    "expected cannot be zero on data row "
                    f"{index + 1}."
                )

            recovery = measured / expected * 100
            recoveries.append(recovery)
            biases.append(recovery - 100)

        mean_recovery = _mean(recoveries)
        maximum_bias = max(abs(value) for value in biases)
        metrics = {
            "n": len(recoveries),
            "meanRecoveryPercent": mean_recovery,
            "meanBiasPercent": _mean(biases),
            "maximumAbsoluteBiasPercent": maximum_bias,
            "recoveryStandardDeviation":
                _standard_deviation(recoveries),
        }
        checks = [
            _check(
                "minimum-recovery",
                "Mean recovery lower bound",
                mean_recovery,
                ">=",
                resolved["minimumRecoveryPercent"],
                mean_recovery
                >= resolved["minimumRecoveryPercent"],
                "%",
            ),
            _check(
                "maximum-recovery",
                "Mean recovery upper bound",
                mean_recovery,
                "<=",
                resolved["maximumRecoveryPercent"],
                mean_recovery
                <= resolved["maximumRecoveryPercent"],
                "%",
            ),
            _check(
                "maximum-absolute-bias",
                "Maximum absolute row bias",
                maximum_bias,
                "<=",
                resolved["maximumAbsoluteBiasPercent"],
                maximum_bias
                <= resolved["maximumAbsoluteBiasPercent"],
                "%",
            ),
        ]

    elif profile_id == "calibration-linearity":
        points = [
            {
                "x": _finite(
                    row.get("concentration"),
                    f"concentration on data row {index + 1}",
                ),
                "y": _finite(
                    row.get("signal"),
                    f"signal on data row {index + 1}",
                ),
            }
            for index, row in enumerate(rows)
        ]
        fit = _regression(points)
        metrics = {
            "levelCount": len(points),
            **fit,
        }
        checks = [
            _check(
                "minimum-levels",
                "Calibration level count",
                len(points),
                ">=",
                resolved["minimumLevels"],
                len(points) >= resolved["minimumLevels"],
            ),
            _check(
                "minimum-r-squared",
                "Coefficient of determination",
                fit["rSquared"],
                ">=",
                resolved["minimumRSquared"],
                fit["rSquared"]
                >= resolved["minimumRSquared"],
            ),
            _check(
                "positive-slope",
                "Positive calibration slope",
                fit["slope"],
                ">",
                0,
                resolved["requirePositiveSlope"] < 0.5
                or fit["slope"] > 0,
            ),
        ]

    elif profile_id == "detection-quantitation":
        blanks = _numeric_column(rows, "blank")
        slopes = _numeric_column(rows, "slope")
        blank_sd = _standard_deviation(blanks)
        mean_slope = _mean(slopes)

        if mean_slope <= 0:
            raise MolecularValidationError(
                "Mean calibration slope must be positive."
            )

        lod = 3.3 * blank_sd / mean_slope
        loq = 10 * blank_sd / mean_slope
        metrics = {
            "blankReplicates": len(blanks),
            "blankMean": _mean(blanks),
            "blankStandardDeviation": blank_sd,
            "meanSlope": mean_slope,
            "lod": lod,
            "loq": loq,
        }
        checks = [
            _check(
                "minimum-blank-replicates",
                "Blank replicate count",
                len(blanks),
                ">=",
                resolved["minimumBlankReplicates"],
                len(blanks)
                >= resolved["minimumBlankReplicates"],
            ),
            _check(
                "maximum-lod",
                "Estimated LOD",
                lod,
                "<=",
                resolved["maximumLod"],
                lod <= resolved["maximumLod"],
            ),
            _check(
                "maximum-loq",
                "Estimated LOQ",
                loq,
                "<=",
                resolved["maximumLoq"],
                loq <= resolved["maximumLoq"],
            ),
        ]

    elif profile_id == "blank-background":
        values = _numeric_column(rows, "value")
        average = _mean(values)
        maximum = max(values)
        metrics = {
            "n": len(values),
            "meanBlank": average,
            "maximumBlank": maximum,
            "standardDeviation":
                _standard_deviation(values),
        }
        checks = [
            _check(
                "minimum-blanks",
                "Blank count",
                len(values),
                ">=",
                resolved["minimumBlanks"],
                len(values) >= resolved["minimumBlanks"],
            ),
            _check(
                "maximum-mean",
                "Mean blank response",
                average,
                "<=",
                resolved["maximumMean"],
                average <= resolved["maximumMean"],
            ),
            _check(
                "maximum-single",
                "Maximum single blank",
                maximum,
                "<=",
                resolved["maximumSingle"],
                maximum <= resolved["maximumSingle"],
            ),
        ]

    elif profile_id == "control-performance":
        z_scores: list[float] = []

        for index, row in enumerate(rows):
            value = _finite(
                row.get("value"),
                f"value on data row {index + 1}",
            )
            target = _finite(
                row.get("target"),
                f"target on data row {index + 1}",
            )
            sd = _finite(
                row.get("sd"),
                f"sd on data row {index + 1}",
            )

            if sd <= 0:
                raise MolecularValidationError(
                    "sd must be positive on data row "
                    f"{index + 1}."
                )

            z_scores.append((value - target) / sd)

        warning_count = sum(
            1
            for value in z_scores
            if (
                abs(value) >= resolved["warningZ"]
                and abs(value) < resolved["actionZ"]
            )
        )
        action_count = sum(
            1
            for value in z_scores
            if abs(value) >= resolved["actionZ"]
        )
        maximum_z = max(abs(value) for value in z_scores)
        metrics = {
            "n": len(z_scores),
            "meanZ": _mean(z_scores),
            "maximumAbsoluteZ": maximum_z,
            "warningCount": warning_count,
            "actionCount": action_count,
        }
        checks = [
            _check(
                "action-limit",
                "Control action-limit events",
                action_count,
                "=",
                0,
                action_count == 0,
            ),
            _check(
                "maximum-z",
                "Maximum absolute z-score",
                maximum_z,
                "<",
                resolved["actionZ"],
                maximum_z < resolved["actionZ"],
            ),
        ]

    elif profile_id == "robustness":
        groups = _grouped_values(rows, "condition")
        group_means = {
            name: _mean(values)
            for name, values in groups.items()
        }
        means = list(group_means.values())
        center = _mean(means)
        difference = max(means) - min(means)
        relative = (
            None
            if center == 0
            else abs(difference / center) * 100
        )
        metrics = {
            "conditionCount": len(groups),
            "conditionMeans": group_means,
            "relativeDifferencePercent": relative,
        }
        checks = [
            _check(
                "minimum-conditions",
                "Condition count",
                len(groups),
                ">=",
                resolved["minimumConditions"],
                len(groups)
                >= resolved["minimumConditions"],
            ),
            _check(
                "maximum-relative-difference",
                "Maximum relative condition difference",
                relative,
                "<=",
                resolved[
                    "maximumRelativeDifferencePercent"
                ],
                relative is not None
                and relative
                <= resolved[
                    "maximumRelativeDifferencePercent"
                ],
                "%",
            ),
        ]

    elif profile_id == "inter-run-comparability":
        groups = _grouped_values(rows, "run")
        run_means = {
            name: _mean(values)
            for name, values in groups.items()
        }
        values = [
            value
            for group_values in groups.values()
            for value in group_values
        ]
        means = list(run_means.values())
        center = _mean(means)
        bias = (
            None
            if center == 0
            else (max(means) - min(means)) / center * 100
        )
        pooled_mean = _mean(values)
        pooled_sd = _standard_deviation(values)
        pooled_cv = (
            None
            if pooled_mean == 0
            else abs(pooled_sd / pooled_mean) * 100
        )
        metrics = {
            "runCount": len(groups),
            "runMeans": run_means,
            "relativeRunBiasPercent": bias,
            "pooledMean": pooled_mean,
            "pooledStandardDeviation": pooled_sd,
            "pooledCvPercent": pooled_cv,
        }
        checks = [
            _check(
                "minimum-runs",
                "Run count",
                len(groups),
                ">=",
                resolved["minimumRuns"],
                len(groups) >= resolved["minimumRuns"],
            ),
            _check(
                "maximum-run-bias",
                "Relative run bias",
                bias,
                "<=",
                resolved["maximumBiasPercent"],
                bias is not None
                and bias <= resolved["maximumBiasPercent"],
                "%",
            ),
            _check(
                "maximum-pooled-cv",
                "Pooled coefficient of variation",
                pooled_cv,
                "<=",
                resolved["maximumPooledCvPercent"],
                pooled_cv is not None
                and pooled_cv
                <= resolved["maximumPooledCvPercent"],
                "%",
            ),
        ]

    else:
        raise MolecularValidationError(
            f"Unsupported validation profile: {profile_id}"
        )

    failed = [
        item
        for item in checks
        if not item["passed"]
    ]

    return {
        "profile": profile,
        "thresholds": resolved,
        "metrics": metrics,
        "checks": checks,
        "decision": "fail" if failed else "pass",
        "failedCheckCount": len(failed),
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


def create_provenance_record(
    payload: Any,
    metadata: dict[str, Any] | None = None,
    previous_hash: str | None = None,
) -> dict[str, Any]:
    metadata = dict(metadata or {})
    record = {
        "schema": (
            "sc-lab-molecular-analysis-provenance/1.0"
        ),
        "version": VERSION,
        "recordId": metadata.get("recordId")
        or (
            f"scprov-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-"
            f"{secrets.token_hex(5)}"
        ),
        "eventType": metadata.get(
            "eventType",
            "validation-dossier",
        ),
        "timestamp": metadata.get("timestamp")
        or datetime.now(timezone.utc).isoformat(),
        "methodId": metadata.get("methodId"),
        "profileId": metadata.get("profileId"),
        "analyst": metadata.get("analyst"),
        "organization": metadata.get("organization"),
        "instrument": metadata.get("instrument"),
        "sampleSet": metadata.get("sampleSet"),
        "sourceIdentifiers": list(
            metadata.get("sourceIdentifiers") or []
        ),
        "evidenceLinks": list(
            metadata.get("evidenceLinks") or []
        ),
        "notes": metadata.get("notes"),
        "previousHash": previous_hash,
        "payloadHash": fingerprint(payload),
        "payload": payload,
        "engine": {
            "validationRelease": VERSION,
            "analysisEngineVersion": "0.21.0",
            "visualizationBatchVersion": "0.21.2",
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
        stored_hash = str(copy.pop("recordHash", ""))
        calculated_hash = fingerprint(copy)
        hash_valid = secrets.compare_digest(
            stored_hash,
            calculated_hash,
        )
        chain_valid = (
            record.get("previousHash") == previous_hash
        )
        results.append(
            {
                "recordId": record.get("recordId"),
                "hashValid": hash_valid,
                "chainValid": chain_valid,
                "valid": hash_valid and chain_valid,
                "storedHash": stored_hash,
                "calculatedHash": calculated_hash,
            }
        )
        previous_hash = stored_hash

    return {
        "valid": all(
            result["valid"]
            for result in results
        ),
        "recordCount": len(records),
        "results": results,
    }
