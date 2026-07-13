from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.13.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "architecture-building-methods.json"
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
}


class ArchitectureBuildingError(ValueError):
    """Raised for invalid architecture and building-performance calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ArchitectureBuildingError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise ArchitectureBuildingError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(
    method_id: str,
    inputs: dict[str, float],
    outputs: dict[str, float],
) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "ab.condensation_margin"
        and outputs["condensationMarginK"] < 2
    ):
        warnings.append(
            "The surface condensation margin is below 2 K and "
            "requires hygrothermal review."
        )

    if (
        method_id == "ab.window_wall_ratio"
        and outputs["windowWallRatio"] > 0.5
    ):
        warnings.append(
            "The window-to-wall ratio exceeds 0.50; evaluate solar, "
            "thermal, glare, and envelope tradeoffs."
        )

    if method_id == "ab.steady_co2" and outputs["indoorCo2Ppm"] > 1200:
        warnings.append(
            "The steady-state CO2 screening result exceeds 1200 ppm."
        )

    if (
        method_id == "ab.passive_survivability"
        and outputs["autonomyFraction"] < 0.8
    ):
        warnings.append(
            "Passive survivability autonomy is below 80% of the "
            "stated outage period."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise ArchitectureBuildingError(
            f"Unknown architecture/building method: {method_id}"
        )

    inputs = {
        field["key"]: _finite(
            raw_inputs.get(field["key"]),
            field["label"],
        )
        for field in method["inputs"]
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
            raise ArchitectureBuildingError(
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
            raise ArchitectureBuildingError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise ArchitectureBuildingError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]

    warnings = _warnings(method_id, inputs, outputs)

    return {
        "schema": "sc-lab-architecture-building-analysis/1.0",
        "version": VERSION,
        "methodId": method["id"],
        "methodVersion": VERSION,
        "category": method["category"],
        "title": method["title"],
        "equation": method["equation"],
        "inputs": inputs,
        "inputUnits": {
            field["key"]: field["unit"]
            for field in method["inputs"]
        },
        "outputs": outputs,
        "outputUnits": output_units,
        "assumptions": method["assumptions"],
        "notes": method.get("notes", []),
        "warnings": warnings,
        "validation": {
            "status": "review" if warnings else "screened",
            "benchmarkSuite":
                "sc-lab-architecture-building-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine": "sc-lab-architecture-building-python",
            "release": VERSION,
        },
    }
