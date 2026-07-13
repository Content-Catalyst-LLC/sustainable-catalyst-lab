from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.21.0"

CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "biochemistry-molecular-analysis-methods.json"
)

SAFE = {
    "pow": pow,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "min": min,
    "max": max,
}


class BiochemistryMolecularAnalysisError(ValueError):
    """Raised for invalid biochemical calculations."""


CATALOG = json.loads(
    CATALOG_PATH.read_text(encoding="utf-8")
)
METHODS = {
    item["id"]: item
    for item in CATALOG["methods"]
}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BiochemistryMolecularAnalysisError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise BiochemistryMolecularAnalysisError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(
    method_id: str,
    outputs: dict[str, float],
    inputs: dict[str, float],
) -> list[str]:
    warnings: list[str] = []

    for key, value in outputs.items():
        lowered = key.lower()

        if "percent" in lowered and not 0 <= value <= 100:
            warnings.append(
                f"{key} lies outside the expected 0–100% "
                "interval."
            )

        if "fraction" in lowered and not 0 <= value <= 1:
            warnings.append(
                f"{key} lies outside the expected 0–1 interval."
            )

    if "pH" in inputs and not 0 <= inputs["pH"] <= 14:
        warnings.append(
            "The stated pH is outside the conventional aqueous "
            "0–14 range."
        )

    if (
        method_id == "bc.chromatography_resolution"
        and outputs["resolution"] < 1.5
    ):
        warnings.append(
            "Resolution is below 1.5; baseline separation may not "
            "be achieved."
        )

    if (
        method_id == "bc.coefficient_of_variation"
        and outputs["coefficientOfVariationPercent"] > 20
    ):
        warnings.append(
            "Coefficient of variation exceeds 20%; review assay "
            "precision."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise BiochemistryMolecularAnalysisError(
            f"Unknown biochemistry method: {method_id}"
        )

    inputs: dict[str, float] = {}

    for specification in method["inputs"]:
        value = _finite(
            raw_inputs.get(specification["key"]),
            specification["label"],
        )

        if (
            "min" in specification
            and value < float(specification["min"])
        ):
            raise BiochemistryMolecularAnalysisError(
                f"{specification['label']} is below its minimum."
            )

        if (
            "max" in specification
            and value > float(specification["max"])
        ):
            raise BiochemistryMolecularAnalysisError(
                f"{specification['label']} exceeds its maximum."
            )

        inputs[specification["key"]] = value

    scope = dict(SAFE)
    scope.update(inputs)

    outputs: dict[str, float] = {}
    output_units: dict[str, str] = {}
    expressions: dict[str, str] = {}

    for key, specification in method["outputs"].items():
        expression = specification["expression"]

        if not all(
            character.isalnum()
            or character in "_+-*/()., :"
            for character in expression
        ):
            raise BiochemistryMolecularAnalysisError(
                "The method expression contains unsupported "
                "characters."
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
            raise BiochemistryMolecularAnalysisError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise BiochemistryMolecularAnalysisError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]
        expressions[key] = expression

    warnings = _warnings(method_id, outputs, inputs)

    return {
        "schema": "sc-lab-biochemistry-analysis/1.0",
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
        "assumptions": method.get("assumptions", []),
        "notes": method.get("notes", []),
        "warnings": warnings,
        "validation": {
            "status": "review" if warnings else "screened",
            "benchmarkSuite": (
                "sc-lab-biochemistry-molecular-analysis-"
                "benchmarks/1.0"
            ),
        },
        "audit": {
            "createdAt": datetime.now(
                timezone.utc
            ).isoformat(),
            "engine": (
                "sc-lab-biochemistry-molecular-analysis-python"
            ),
            "release": VERSION,
        },
    }
