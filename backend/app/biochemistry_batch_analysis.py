from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from .biochemistry_molecular_analysis import (
    VERSION as ANALYSIS_ENGINE_VERSION,
    BiochemistryMolecularAnalysisError,
    run_method,
)

VERSION = "0.21.2"


class BiochemistryBatchError(ValueError):
    """Raised when a batch analysis request is invalid."""


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _standard_deviation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    average = _mean(values)
    variance = sum(
        (value - average) ** 2
        for value in values
    ) / (len(values) - 1)

    return math.sqrt(variance)


def _summary(values: list[float]) -> dict[str, Any]:
    clean = [
        float(value)
        for value in values
        if math.isfinite(float(value))
    ]

    if not clean:
        return {
            "n": 0,
            "mean": None,
            "standardDeviation": None,
            "coefficientOfVariationPercent": None,
            "minimum": None,
            "maximum": None,
            "status": "unavailable",
        }

    average = _mean(clean)
    deviation = _standard_deviation(clean)
    cv = (
        None
        if average == 0
        else abs(deviation / average) * 100
    )

    return {
        "n": len(clean),
        "mean": average,
        "standardDeviation": deviation,
        "coefficientOfVariationPercent": cv,
        "minimum": min(clean),
        "maximum": max(clean),
        "status": (
            "review"
            if cv is not None and cv > 20
            else "screened"
        ),
    }


def run_batch(
    method_id: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not method_id:
        raise BiochemistryBatchError(
            "methodId is required."
        )

    if not rows:
        raise BiochemistryBatchError(
            "At least one batch row is required."
        )

    results: list[dict[str, Any]] = []

    for index, raw_row in enumerate(rows):
        row = dict(raw_row or {})
        sample = str(
            row.pop("sample", None)
            or row.pop("sampleId", None)
            or f"sample-{index + 1}"
        )
        nested = row.pop("inputs", None)
        inputs = (
            dict(nested)
            if isinstance(nested, dict)
            else row
        )

        try:
            analysis = run_method(
                method_id,
                inputs,
            )
            results.append(
                {
                    "sample": sample,
                    "row": index + 1,
                    "ok": True,
                    "inputs": analysis["inputs"],
                    "outputs": analysis["outputs"],
                    "warnings": analysis["warnings"],
                    "analysis": analysis,
                }
            )
        except (
            BiochemistryMolecularAnalysisError,
            TypeError,
            ValueError,
        ) as exc:
            results.append(
                {
                    "sample": sample,
                    "row": index + 1,
                    "ok": False,
                    "inputs": inputs,
                    "outputs": {},
                    "warnings": [],
                    "error": str(exc),
                }
            )

    output_keys: list[str] = []

    for result in results:
        if result["ok"]:
            output_keys = list(
                result["outputs"].keys()
            )
            break

    statistics = {
        key: _summary(
            [
                result["outputs"][key]
                for result in results
                if result["ok"]
                and key in result["outputs"]
            ]
        )
        for key in output_keys
    }

    flags = [
        f"{key} has CV above 20%."
        for key, summary in statistics.items()
        if summary["status"] == "review"
    ]

    error_count = sum(
        1
        for result in results
        if not result["ok"]
    )

    if error_count:
        flags.append(
            f"{error_count} batch row(s) "
            "could not be calculated."
        )

    return {
        "schema": (
            "sc-lab-biochemistry-batch-analysis/1.0"
        ),
        "version": VERSION,
        "analysisEngineVersion": ANALYSIS_ENGINE_VERSION,
        "methodId": method_id,
        "rowCount": len(results),
        "successCount": len(results) - error_count,
        "errorCount": error_count,
        "results": results,
        "statistics": statistics,
        "flags": flags,
        "status": "review" if flags else "screened",
        "audit": {
            "createdAt": datetime.now(
                timezone.utc
            ).isoformat(),
            "engine": (
                "sc-lab-biochemistry-batch-python"
            ),
            "release": VERSION,
        },
    }
