from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.14.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "urban-planning-spatial-methods.json"
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
}


class UrbanPlanningSpatialError(ValueError):
    """Raised for invalid urban-planning or spatial calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise UrbanPlanningSpatialError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise UrbanPlanningSpatialError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(
    method_id: str,
    outputs: dict[str, float],
) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "up.land_use_mix"
        and abs(outputs["shareTotal"] - 1) > 0.02
    ):
        warnings.append(
            "Land-use shares do not sum to approximately 1.0."
        )

    if (
        method_id == "up.spatial_entropy"
        and abs(outputs["shareTotal"] - 1) > 0.02
    ):
        warnings.append(
            "Zone shares do not sum to approximately 1.0."
        )

    if (
        method_id == "up.housing_cost_burden"
        and outputs["costBurdenFraction"] > 0.3
    ):
        warnings.append(
            "Housing costs exceed 30% of the stated monthly household income."
        )

    if (
        method_id == "up.flood_exposure"
        and outputs["exposureFraction"] > 0.2
    ):
        warnings.append(
            "More than 20% of the stated population is exposed "
            "in this hazard scenario."
        )

    if (
        method_id == "up.facility_utilization"
        and outputs["utilizationFraction"] > 0.9
    ):
        warnings.append(
            "Facility utilization exceeds 90%; evaluate peak demand "
            "and resilience capacity."
        )

    if (
        method_id == "up.school_capacity_gap"
        and outputs["seatGap"] > 0
    ):
        warnings.append(
            "Projected enrollment exceeds the stated available school capacity."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise UrbanPlanningSpatialError(
            f"Unknown urban planning method: {method_id}"
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
            raise UrbanPlanningSpatialError(
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
            raise UrbanPlanningSpatialError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise UrbanPlanningSpatialError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]

    warnings = _warnings(method_id, outputs)

    return {
        "schema": "sc-lab-urban-planning-spatial-analysis/1.0",
        "version": VERSION,
        "methodId": method["id"],
        "methodVersion": VERSION,
        "category": method["category"],
        "title": method["title"],
        "equation": method["equation"],
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
                "sc-lab-urban-planning-spatial-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine": "sc-lab-urban-planning-spatial-python",
            "release": VERSION,
        },
    }
