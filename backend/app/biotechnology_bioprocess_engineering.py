from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

VERSION = "0.22.0"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "biotechnology-bioprocess-methods-v0220.json"
)


class BioprocessEngineeringError(ValueError):
    """Raised when a bioprocess request is invalid."""


def catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _method(method_id: str) -> dict[str, Any]:
    for method in catalog()["methods"]:
        if method["id"] == method_id:
            return method
    raise BioprocessEngineeringError(
        f"Unknown bioprocess method: {method_id}"
    )


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BioprocessEngineeringError(
            f"{label} must be numerical."
        ) from exc
    if not math.isfinite(number):
        raise BioprocessEngineeringError(
            f"{label} must be finite."
        )
    return number


def _normalize_inputs(
    method: dict[str, Any],
    supplied: dict[str, Any] | None,
) -> dict[str, float]:
    supplied = dict(supplied or {})
    values: dict[str, float] = {}
    for definition in method["inputs"]:
        number = _finite(
            supplied.get(
                definition["key"],
                definition["default"],
            ),
            definition["label"],
        )
        if "min" in definition and number < definition["min"]:
            raise BioprocessEngineeringError(
                f"{definition['label']} must be at least "
                f"{definition['min']}."
            )
        if "max" in definition and number > definition["max"]:
            raise BioprocessEngineeringError(
                f"{definition['label']} must be at most "
                f"{definition['max']}."
            )
        values[definition["key"]] = number
    return values


OPERATIONS: dict[str, Callable[[dict[str, float]], float]] = {
    "exponential_biomass": lambda a: a["x0"] * math.exp(a["mu"] * a["time"]),
    "specific_growth_rate": lambda a: math.log(a["x2"] / a["x1"]) / (a["t2"] - a["t1"]),
    "doubling_time": lambda a: math.log(2.0) / a["mu"],
    "monod_growth_rate": lambda a: a["mu_max"] * a["substrate"] / (a["ks"] + a["substrate"]),
    "logistic_biomass": lambda a: a["carrying_capacity"] / (1.0 + ((a["carrying_capacity"] - a["x0"]) / a["x0"]) * math.exp(-a["mu"] * a["time"])),
    "viable_cell_density": lambda a: a["total_cells"] * a["viability_percent"] / 100.0,
    "substrate_consumed": lambda a: a["initial_substrate"] - a["final_substrate"],
    "biomass_yield": lambda a: a["biomass_increase"] / a["substrate_consumed"],
    "product_yield": lambda a: a["product_formed"] / a["substrate_consumed"],
    "batch_productivity": lambda a: a["product_concentration"] / a["batch_time"],
    "maintenance_substrate": lambda a: a["maintenance_coefficient"] * a["biomass"] * a["time"],
    "carbon_recovery": lambda a: a["carbon_outputs"] / a["carbon_inputs"] * 100.0,
    "feed_volume": lambda a: a["feed_rate"] * a["time"],
    "fed_batch_final_volume": lambda a: a["initial_volume"] + a["feed_rate"] * a["time"],
    "substrate_mass_fed": lambda a: a["feed_rate"] * a["feed_concentration"] * a["time"],
    "exponential_feed_rate": lambda a: a["initial_feed_rate"] * math.exp(a["mu_set"] * a["time"]),
    "apparent_dilution_rate": lambda a: a["feed_rate"] / a["reactor_volume"],
    "fed_batch_substrate_balance": lambda a: a["initial_substrate_mass"] + a["substrate_fed"] - a["substrate_consumed"],
    "dilution_rate": lambda a: a["flow_rate"] / a["reactor_volume"],
    "residence_time": lambda a: a["reactor_volume"] / a["flow_rate"],
    "chemostat_biomass": lambda a: a["yield_coefficient"] * (a["feed_substrate"] - a["residual_substrate"]),
    "washout_margin": lambda a: a["mu_max"] - a["dilution_rate"],
    "continuous_productivity": lambda a: a["dilution_rate"] * a["product_concentration"],
    "critical_dilution_monod": lambda a: a["mu_max"] * a["feed_substrate"] / (a["ks"] + a["feed_substrate"]),
    "oxygen_transfer_rate": lambda a: a["kla"] * (a["saturation_concentration"] - a["liquid_concentration"]),
    "oxygen_uptake_rate": lambda a: a["specific_oxygen_uptake"] * a["biomass"],
    "kla_from_otr": lambda a: a["otr"] / (a["saturation_concentration"] - a["liquid_concentration"]),
    "oxygen_balance_margin": lambda a: a["otr"] - a["our"],
    "aeration_vvm": lambda a: a["gas_flow"] / a["reactor_volume"],
    "gas_molar_flow": lambda a: a["volumetric_flow"] * a["pressure"] / (0.082057 * a["temperature"]),
    "metabolic_heat": lambda a: a["heat_per_biomass"] * a["biomass_rate"],
    "cooling_water_flow": lambda a: a["heat_duty"] / (a["heat_capacity"] * a["temperature_rise"]),
    "impeller_tip_speed": lambda a: math.pi * a["impeller_diameter"] * a["rotation_speed"] / 60.0,
    "power_per_volume": lambda a: a["power"] / a["volume"],
    "reynolds_mixing": lambda a: a["density"] * a["rotation_speed"] * a["impeller_diameter"] ** 2 / a["dynamic_viscosity"],
    "mixing_time_correlation": lambda a: a["coefficient"] * (a["volume"] / a["power"]) ** a["exponent"],
    "geometric_scale_factor": lambda a: a["target_volume"] / a["base_volume"],
    "linear_scale_factor": lambda a: (a["target_volume"] / a["base_volume"]) ** (1.0 / 3.0),
    "constant_tip_speed_rpm": lambda a: a["base_rpm"] * a["base_diameter"] / a["target_diameter"],
    "constant_power_volume": lambda a: a["base_power"] * a["target_volume"] / a["base_volume"],
    "cylinder_area_volume": lambda a: (math.pi * a["diameter"] * a["height"] + 2.0 * math.pi * (a["diameter"] / 2.0) ** 2) / (math.pi * (a["diameter"] / 2.0) ** 2 * a["height"]),
    "superficial_gas_velocity": lambda a: a["gas_flow"] / a["cross_section_area"],
    "luedeking_piret_product": lambda a: (a["alpha"] * a["mu"] + a["beta"]) * a["biomass"] * a["time"],
    "specific_productivity": lambda a: a["product_rate"] / a["biomass"],
    "harvest_titer": lambda a: a["product_mass"] / a["harvest_volume"],
    "downstream_recovery": lambda a: a["recovered_mass"] / a["feed_mass"] * 100.0,
    "volumetric_productivity": lambda a: a["product_mass"] / (a["reactor_volume"] * a["process_time"]),
    "overall_process_yield": lambda a: a["final_product_mass"] / a["theoretical_product_mass"] * 100.0,
}


def run_method(
    method_id: str,
    inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    method = _method(method_id)
    values = _normalize_inputs(method, inputs)
    operation = method["operation"]

    if operation == "specific_growth_rate" and values["t2"] == values["t1"]:
        raise BioprocessEngineeringError(
            "Final time must differ from initial time."
        )
    if (
        operation == "substrate_consumed"
        and values["final_substrate"] > values["initial_substrate"]
    ):
        raise BioprocessEngineeringError(
            "Final substrate cannot exceed initial substrate."
        )
    if (
        operation == "kla_from_otr"
        and values["saturation_concentration"]
        == values["liquid_concentration"]
    ):
        raise BioprocessEngineeringError(
            "Oxygen driving force must be non-zero."
        )

    try:
        result = OPERATIONS[operation](values)
    except KeyError as exc:
        raise BioprocessEngineeringError(
            f"Unsupported bioprocess operation: {operation}"
        ) from exc

    if not math.isfinite(result):
        raise BioprocessEngineeringError(
            "Calculation produced a non-finite result."
        )

    return {
        "schema": "sc-lab-biotechnology-bioprocess-result/1.0",
        "version": VERSION,
        "methodId": method["id"],
        "title": method["title"],
        "category": method["category"],
        "formula": method["formula"],
        "inputs": values,
        "outputs": {"result": result},
        "outputDefinition": method["outputs"]["result"],
        "warnings": [],
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine": "sc-lab-bioprocess-python",
            "release": VERSION,
        },
    }


def _summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "standardDeviation": None,
            "coefficientOfVariationPercent": None,
            "minimum": None,
            "maximum": None,
        }
    average = sum(values) / len(values)
    deviation = 0.0
    if len(values) > 1:
        deviation = math.sqrt(
            sum((value - average) ** 2 for value in values)
            / (len(values) - 1)
        )
    return {
        "n": len(values),
        "mean": average,
        "standardDeviation": deviation,
        "coefficientOfVariationPercent": (
            None if average == 0 else abs(deviation / average) * 100
        ),
        "minimum": min(values),
        "maximum": max(values),
    }


def run_batch(
    method_id: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not rows:
        raise BioprocessEngineeringError(
            "At least one batch row is required."
        )
    results: list[dict[str, Any]] = []
    values: list[float] = []
    for index, raw in enumerate(rows):
        row = dict(raw or {})
        sample = str(
            row.pop("sample", None)
            or f"sample-{index + 1}"
        )
        nested = row.pop("inputs", None)
        inputs = dict(nested) if isinstance(nested, dict) else row
        try:
            analysis = run_method(method_id, inputs)
            values.append(analysis["outputs"]["result"])
            results.append(
                {"sample": sample, "ok": True, "analysis": analysis}
            )
        except BioprocessEngineeringError as exc:
            results.append(
                {"sample": sample, "ok": False, "error": str(exc)}
            )
    statistics = _summary(values)
    flags: list[str] = []
    cv = statistics["coefficientOfVariationPercent"]
    if cv is not None and cv > 20:
        flags.append("Coefficient of variation exceeds 20%.")
    error_count = len(results) - len(values)
    if error_count:
        flags.append(f"{error_count} row(s) failed.")
    return {
        "schema": "sc-lab-bioprocess-batch/1.0",
        "version": VERSION,
        "methodId": method_id,
        "rowCount": len(results),
        "successCount": len(values),
        "errorCount": error_count,
        "results": results,
        "statistics": statistics,
        "flags": flags,
        "audit": {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "engine": "sc-lab-bioprocess-batch-python",
            "release": VERSION,
        },
    }


def simulate(mode: str, parameters: dict[str, Any] | None = None) -> dict[str, Any]:
    p = dict(parameters or {})
    if mode == "batch":
        x0 = _finite(p.get("x0", 1), "Initial biomass")
        mu = _finite(p.get("mu", 0.3), "Growth rate")
        time = _finite(p.get("time", 24), "Time")
        substrate0 = _finite(p.get("substrate0", 40), "Initial substrate")
        yield_xs = _finite(p.get("yieldXs", 0.5), "Biomass yield")
        yield_ps = _finite(p.get("yieldPs", 0.2), "Product yield")
        points = []
        for index in range(41):
            t = time * index / 40
            ideal = x0 * math.exp(mu * t)
            biomass = min(ideal, x0 + substrate0 * yield_xs)
            substrate = max(0.0, substrate0 - (biomass - x0) / yield_xs)
            product = (substrate0 - substrate) * yield_ps
            points.append(
                {"time": t, "biomass": biomass, "substrate": substrate, "product": product}
            )
        return {"mode": mode, "points": points, "summary": points[-1]}
    if mode == "fed-batch":
        v0 = _finite(p.get("initialVolume", 5), "Initial volume")
        f0 = _finite(p.get("initialFeedRate", 0.05), "Initial feed rate")
        mu = _finite(p.get("muSet", 0.15), "Target growth rate")
        concentration = _finite(p.get("feedConcentration", 500), "Feed concentration")
        x0 = _finite(p.get("x0", 2), "Initial biomass")
        time = _finite(p.get("time", 24), "Time")
        points = []
        for index in range(41):
            t = time * index / 40
            feed_rate = f0 * math.exp(mu * t)
            cumulative = 0.0 if index == 0 else f0 / mu * (math.exp(mu * t) - 1)
            volume = v0 + cumulative
            biomass = x0 * math.exp(mu * t) * v0 / volume
            points.append(
                {
                    "time": t,
                    "feedRate": feed_rate,
                    "volume": volume,
                    "biomass": biomass,
                    "substrateFed": cumulative * concentration,
                }
            )
        return {"mode": mode, "points": points, "summary": points[-1]}
    if mode == "continuous":
        volume = _finite(p.get("volume", 10), "Volume")
        flow = _finite(p.get("flowRate", 1.5), "Flow rate")
        mu_max = _finite(p.get("muMax", 0.5), "Maximum growth rate")
        ks = _finite(p.get("ks", 0.5), "Ks")
        feed = _finite(p.get("feedSubstrate", 20), "Feed substrate")
        yield_xs = _finite(p.get("yieldXs", 0.5), "Yield")
        product = _finite(p.get("productConcentration", 12), "Product concentration")
        dilution = flow / volume
        washout = dilution >= mu_max
        residual = feed if washout else min(feed, ks * dilution / (mu_max - dilution))
        biomass = 0.0 if washout else yield_xs * (feed - residual)
        summary = {
            "dilutionRate": dilution,
            "residualSubstrate": residual,
            "biomass": biomass,
            "productivity": dilution * product,
            "washoutMargin": mu_max - dilution,
            "washout": washout,
        }
        return {"mode": mode, "points": [summary], "summary": summary}
    raise BioprocessEngineeringError(f"Unknown simulation mode: {mode}")
