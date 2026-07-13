from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.16.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "circular-economy-industrial-ecology-methods.json"
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


class CircularEconomyIndustrialEcologyError(ValueError):
    """Raised for invalid circular-economy calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise CircularEconomyIndustrialEcologyError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise CircularEconomyIndustrialEcologyError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(method_id: str, outputs: dict[str, float]) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "ce.circular_material_use_rate"
        and outputs["circularMaterialUseFraction"] < 0.2
    ):
        warnings.append(
            "Circular material use is below 20% in the stated scenario."
        )

    if (
        method_id == "ce.mass_balance_gap"
        and outputs["massBalanceGapTonnes"] > 0
    ):
        warnings.append(
            "The material-flow account does not close; review boundaries "
            "and measurement uncertainty."
        )

    if (
        method_id == "ce.landfill_rate"
        and outputs["landfillFraction"] > 0.5
    ):
        warnings.append(
            "More than half of generated waste is landfilled "
            "in the stated scenario."
        )

    if (
        method_id == "ce.symbiosis_network_redundancy"
        and outputs["networkRedundancy"] < 1
    ):
        warnings.append(
            "Critical industrial exchanges have fewer than one "
            "alternate path on average."
        )

    if (
        method_id == "ce.transition_gap"
        and outputs["transitionGapPoints"] > 0
    ):
        warnings.append(
            "The current circularity score remains below the stated target."
        )

    if (
        method_id == "ce.scenario_npv"
        and outputs["netPresentValueUsd"] < 0
    ):
        warnings.append(
            "The circular transition scenario has a negative net present "
            "value under the stated assumptions."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise CircularEconomyIndustrialEcologyError(
            f"Unknown circular-economy method: {method_id}"
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
            raise CircularEconomyIndustrialEcologyError(
                "The method expression contains unsupported characters."
            )

        try:
            value = float(
                eval(expression, {"__builtins__": {}}, scope)
            )
        except Exception as exc:
            raise CircularEconomyIndustrialEcologyError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise CircularEconomyIndustrialEcologyError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]
        expressions[key] = expression

    warnings = _warnings(method_id, outputs)

    return {
        "schema":
            "sc-lab-circular-economy-industrial-ecology-analysis/1.0",
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
                "sc-lab-circular-economy-industrial-ecology-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine":
                "sc-lab-circular-economy-industrial-ecology-python",
            "release": VERSION,
        },
    }
