from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.18.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "aerospace-engineering-flight-systems-methods.json"
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


class AerospaceEngineeringFlightSystemsError(ValueError):
    """Raised for invalid aerospace-engineering and flight-system calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AerospaceEngineeringFlightSystemsError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise AerospaceEngineeringFlightSystemsError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(
    method_id: str,
    outputs: dict[str, float],
) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "af.coordinated_turn_load_factor"
        and outputs["loadFactor"] > 3
    ):
        warnings.append(
            "The calculated turn load factor exceeds 3 g; verify "
            "structural and operating limits."
        )

    if (
        method_id == "af.static_margin"
        and (
            outputs["staticMarginFraction"] <= 0
            or outputs["staticMarginFraction"] > 0.25
        )
    ):
        warnings.append(
            "The static margin is outside the usual positive screening "
            "range; review stability and controllability."
        )

    if (
        method_id == "af.short_period_damping_ratio"
        and outputs["dampingRatio"] < 0.3
    ):
        warnings.append(
            "Short-period damping is below a common preliminary "
            "handling-quality screening value."
        )

    if (
        method_id == "af.electric_endurance"
        and outputs["enduranceMargin"] < 1.2
    ):
        warnings.append(
            "Battery endurance margin is below 20% for the stated "
            "mission duration."
        )

    if (
        method_id == "af.propeller_tip_mach"
        and outputs["tipMachNumber"] > 0.85
    ):
        warnings.append(
            "Propeller helical tip Mach exceeds 0.85; compressibility "
            "and acoustic effects require review."
        )

    if (
        method_id == "af.torsional_divergence_speed"
        and outputs["divergenceSpeedMargin"] < 1.2
    ):
        warnings.append(
            "The screening divergence-speed margin is below 20% above "
            "the reference flight speed."
        )

    if (
        method_id == "af.series_system_reliability"
        and outputs["seriesReliability"] < 0.9
    ):
        warnings.append(
            "Series flight-system reliability is below 0.90 for the "
            "stated mission interval."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise AerospaceEngineeringFlightSystemsError(
            f"Unknown aerospace-flight method: {method_id}"
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
            raise AerospaceEngineeringFlightSystemsError(
                "The method expression contains unsupported characters."
            )

        try:
            value = float(
                eval(expression, {"__builtins__": {}}, scope)
            )
        except Exception as exc:
            raise AerospaceEngineeringFlightSystemsError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise AerospaceEngineeringFlightSystemsError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]
        expressions[key] = expression

    warnings = _warnings(method_id, outputs)

    return {
        "schema":
            "sc-lab-aerospace-engineering-flight-analysis/1.0",
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
                "sc-lab-aerospace-engineering-flight-systems-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine":
                "sc-lab-aerospace-engineering-flight-systems-python",
            "release": VERSION,
        },
    }
