from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.20.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "microbiology-laboratory-methods.json"
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


class MicrobiologyLaboratoryError(ValueError):
    """Raised for invalid microbiology laboratory calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise MicrobiologyLaboratoryError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise MicrobiologyLaboratoryError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(
    method_id: str,
    outputs: dict[str, float],
) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "mb.chemostat_steady_substrate"
        and outputs["steadyStateSubstrateMgL"] < 0
    ):
        warnings.append(
            "The steady-state substrate result is negative; verify "
            "that dilution rate remains below maximum growth rate."
        )

    if (
        method_id == "mb.washout_margin"
        and outputs["washoutMarginPerHour"] <= 0
    ):
        warnings.append(
            "The dilution rate meets or exceeds maximum growth rate, "
            "indicating washout risk."
        )

    if (
        method_id == "mb.viable_fraction"
        and (
            outputs["viableFraction"] < 0
            or outputs["viableFraction"] > 1
        )
    ):
        warnings.append(
            "The viable fraction lies outside 0 to 1; review counts "
            "and background correction."
        )

    if (
        method_id == "mb.assay_recovery"
        and (
            outputs["recoveryFraction"] < 0.7
            or outputs["recoveryFraction"] > 1.3
        )
    ):
        warnings.append(
            "Assay recovery is outside the 70% to 130% "
            "screening interval."
        )

    if (
        method_id == "mb.z_prime_factor"
        and outputs["zPrimeFactor"] < 0.5
    ):
        warnings.append(
            "The assay Z-prime factor is below 0.5 and may not support "
            "robust screening."
        )

    if (
        method_id == "mb.replicate_coefficient_variation"
        and outputs["coefficientOfVariation"] > 0.2
    ):
        warnings.append(
            "Replicate coefficient of variation exceeds 20%."
        )

    if (
        method_id == "mb.contamination_rate"
        and outputs["contaminationFraction"] > 0.05
    ):
        warnings.append(
            "Negative-control contamination exceeds 5% in the "
            "stated record."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise MicrobiologyLaboratoryError(
            f"Unknown microbiology method: {method_id}"
        )

    inputs = {
        item["key"]: _finite(raw_inputs.get(item["key"]), item["label"])
        for item in method["inputs"]
    }

    scope = dict(SAFE)
    scope.update(inputs)
    outputs: dict[str, float] = {}
    output_units: dict[str, str] = {}
    expressions: dict[str, str] = {}

    for key, specification in method["outputs"].items():
        expression = specification["expression"]

        if not all(
            character.isalnum()
            or character in "_+-*/().,<>=!? : "
            for character in expression
        ):
            raise MicrobiologyLaboratoryError(
                "The method expression contains unsupported characters."
            )

        try:
            value = float(
                eval(expression, {"__builtins__": {}}, scope)
            )
        except Exception as exc:
            raise MicrobiologyLaboratoryError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise MicrobiologyLaboratoryError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]
        expressions[key] = expression

    warnings = _warnings(method_id, outputs)

    return {
        "schema":
            "sc-lab-microbiology-analysis/1.0",
        "version": VERSION,
        "methodId": method["id"],
        "methodVersion": method["version"],
        "category": method["category"],
        "title": method["title"],
        "equation": method["equation"],
        "expressions": expressions,
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
                "sc-lab-microbiology-laboratory-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine":
                "sc-lab-microbiology-laboratory-python",
            "release": VERSION,
        },
    }
