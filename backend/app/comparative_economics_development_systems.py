from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.17.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "comparative-economics-development-systems-methods.json"
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


class ComparativeEconomicsDevelopmentSystemsError(ValueError):
    """Raised for invalid comparative-economics and development-system calculations."""


CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
METHODS = {item["id"]: item for item in CATALOG["methods"]}


def public_catalog() -> dict[str, Any]:
    return CATALOG


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ComparativeEconomicsDevelopmentSystemsError(
            f"{label} must be a finite number."
        ) from exc

    if not math.isfinite(number):
        raise ComparativeEconomicsDevelopmentSystemsError(
            f"{label} must be a finite number."
        )

    return number


def _warnings(method_id: str, outputs: dict[str, float]) -> list[str]:
    warnings: list[str] = []

    if (
        method_id == "de.current_account_balance"
        and outputs["currentAccountFractionOfGdp"] < -0.05
    ):
        warnings.append(
            "The current-account deficit exceeds 5% of GDP in the stated scenario."
        )

    if (
        method_id == "de.fiscal_balance"
        and outputs["fiscalBalanceFractionOfGdp"] < -0.03
    ):
        warnings.append(
            "The fiscal deficit exceeds 3% of GDP in the stated scenario."
        )

    if (
        method_id == "de.export_concentration"
        and outputs["exportConcentrationHhi"] > 0.25
    ):
        warnings.append(
            "The export basket is highly concentrated under this screening threshold."
        )

    if (
        method_id == "de.grouped_gini"
        and (
            abs(outputs["populationShareTotal"] - 1) > 0.02
            or abs(outputs["incomeShareTotal"] - 1) > 0.02
        )
    ):
        warnings.append(
            "Grouped population and income shares should each sum to approximately 1.0."
        )

    if (
        method_id == "de.debt_service_burden"
        and outputs["debtServiceBurdenFraction"] > 0.2
    ):
        warnings.append(
            "External debt service exceeds 20% of export earnings."
        )

    if (
        method_id == "de.development_scenario_robustness"
        and outputs["robustnessFraction"] < 0.8
    ):
        warnings.append(
            "Worst-case development performance is below 80% of the stated target."
        )

    return warnings


def run_method(
    method_id: str,
    raw_inputs: dict[str, Any],
) -> dict[str, Any]:
    method = METHODS.get(method_id)

    if method is None:
        raise ComparativeEconomicsDevelopmentSystemsError(
            f"Unknown development-economics method: {method_id}"
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
            raise ComparativeEconomicsDevelopmentSystemsError(
                "The method expression contains unsupported characters."
            )

        try:
            value = float(
                eval(expression, {"__builtins__": {}}, scope)
            )
        except Exception as exc:
            raise ComparativeEconomicsDevelopmentSystemsError(
                f"Could not evaluate {key}: {exc}"
            ) from exc

        if not math.isfinite(value):
            raise ComparativeEconomicsDevelopmentSystemsError(
                f"{key} did not produce a finite result."
            )

        outputs[key] = value
        output_units[key] = specification["unit"]
        expressions[key] = expression

    warnings = _warnings(method_id, outputs)

    return {
        "schema":
            "sc-lab-comparative-economics-development-analysis/1.0",
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
                "sc-lab-comparative-economics-development-systems-benchmarks/1.0",
        },
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine":
                "sc-lab-comparative-economics-development-systems-python",
            "release": VERSION,
        },
    }
