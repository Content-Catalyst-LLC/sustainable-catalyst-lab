from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.15.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "sustainable-cities-resilience-methods.json"
)

SAFE = {
    "pi": math.pi,
    "g": 9.80665,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "min": min,
    "max": max,
    "pow": pow,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
}


class SustainableCitiesResilienceError(ValueError):
    """Raised for invalid sustainable-city or resilience calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise SustainableCitiesResilienceError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise SustainableCitiesResilienceError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(
    method_id: str,
    outputs: dict[str, float],
) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "sc.drought_supply_ratio"
        and outputs["supplyDemandRatio"] < 1
    ):
        warnings.append(
            "Reliable drought supply is below stated drought demand."
        )

    if (
        method_id == "sc.critical_service_reliability"
        and outputs["serviceReliability"] < 1
    ):
        warnings.append(
            "Critical service delivery is below the stated requirement."
        )

    if (
        method_id == "sc.energy_burden"
        and outputs["energyBurdenFraction"] > 0.06
    ):
        warnings.append(
            "The stated household energy burden exceeds 6%."
        )

    if (
        method_id == "sc.transit_access_equity"
        and outputs["accessEquityRatio"] < 0.8
    ):
        warnings.append(
            "Priority-population transit access is below 80% "
            "of the citywide level."
        )

    if (
        method_id == "sc.emissions_target_gap"
        and outputs["targetGapTonnes"] > 0
    ):
        warnings.append(
            "Projected emissions remain above the stated target."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise SustainableCitiesResilienceError(
            f"Unknown sustainable-cities method: {method_id}"
        )

    inputs = {
        item["key"]: _finite(
            raw_inputs.get(item["key"]),
            item["label"],
        )
        for item in method["inputs"]
    }

    scope = dict(SAFE)
    scope.update(inputs)
    outputs: dict[str, float] = {}
    output_units: dict[str, str] = {}

    for key, specification in method["outputs"].items():
        expression = specification["expression"]

        if not all(
            character.isalnum()
            or character in "_+-*/().,<>=!? : "
            for character in expression
        ):
            raise SustainableCitiesResilienceError(
                "The method expression contains unsupported characters."
            )

        try:
            value = float(
                eval(
                    expression,
                    {"__builtins__": {}},
                    scope,
                )
            )
        except Exception as exc:
            raise SustainableCitiesResilienceError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise SustainableCitiesResilienceError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]

    warnings = _warnings(method_id, outputs)

    return {
        "schema":
            "sc-lab-sustainable-cities-resilience-analysis/1.0",
        "version": VERSION,
        "methodId": method["id"],
        "methodVersion": method["version"],
        "category": method["category"],
        "title": method["title"],
        "equation": method["equation"],
        "expressions": {
            key: specification["expression"]
            for key, specification in method["outputs"].items()
        },
        "inputs": inputs,
        "inputUnits": {
            item["key"]: item["unit"]
            for item in method["inputs"]
        },
        "outputs": outputs,
        "outputUnits": output_units,
        "assumptions": method["assumptions"],
        "notes": method.get("notes", []),
        "warnings": warnings,
        "validation": {
            "status": "review" if warnings else "screened",
            "benchmarkSuite":
                "sc-lab-sustainable-cities-resilience-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine":
                "sc-lab-sustainable-cities-resilience-python",
            "release": VERSION,
        },
    }
