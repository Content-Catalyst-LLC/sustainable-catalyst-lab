from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.19.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "rocket-propulsion-spaceflight-methods.json"
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


class RocketPropulsionSpaceflightError(ValueError):
    """Raised for invalid rocket-propulsion and spaceflight calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise RocketPropulsionSpaceflightError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise RocketPropulsionSpaceflightError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(
    method_id: str,
    outputs: dict[str, float],
) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "rp.required_mass_ratio"
        and outputs["requiredMassRatio"] > 10
    ):
        warnings.append(
            "The ideal required mass ratio exceeds 10; staging or a "
            "different mission architecture should be examined."
        )

    if (
        method_id == "rp.liftoff_thrust_to_weight"
        and outputs["thrustToWeightRatio"] <= 1
    ):
        warnings.append(
            "Liftoff thrust-to-weight is not greater than one in the "
            "stated condition."
        )

    if (
        method_id == "rp.ascent_dynamic_pressure"
        and outputs["dynamicPressurePa"] > 50000
    ):
        warnings.append(
            "Dynamic pressure exceeds 50 kPa; structural and trajectory "
            "constraints require review."
        )

    if (
        method_id == "rp.burnout_acceleration"
        and outputs["netAccelerationG"] > 5
    ):
        warnings.append(
            "Net burnout acceleration exceeds 5 g in this screening "
            "calculation."
        )

    if (
        method_id == "rp.plane_change_delta_v"
        and outputs["planeChangeDeltaVMps"] > 1000
    ):
        warnings.append(
            "The impulsive plane change requires more than 1 km/s; "
            "alternate maneuver geometry should be considered."
        )

    if (
        method_id == "rp.propellant_reserve_fraction"
        and outputs["propellantReserveFraction"] < 0.1
    ):
        warnings.append(
            "Propellant reserve is below 10% of loaded propellant."
        )

    if (
        method_id == "rp.series_mission_reliability"
        and outputs["missionReliability"] < 0.95
    ):
        warnings.append(
            "Series mission reliability is below 0.95 for the stated "
            "independent-element model."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise RocketPropulsionSpaceflightError(
            f"Unknown rocket-propulsion method: {method_id}"
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
            raise RocketPropulsionSpaceflightError(
                "The method expression contains unsupported characters."
            )

        try:
            value = float(
                eval(expression, {"__builtins__": {}}, scope)
            )
        except Exception as exc:
            raise RocketPropulsionSpaceflightError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise RocketPropulsionSpaceflightError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]
        expressions[key] = expression

    warnings = _warnings(method_id, outputs)

    return {
        "schema":
            "sc-lab-rocket-propulsion-spaceflight-analysis/1.0",
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
                "sc-lab-rocket-propulsion-spaceflight-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine":
                "sc-lab-rocket-propulsion-spaceflight-python",
            "release": VERSION,
        },
    }
