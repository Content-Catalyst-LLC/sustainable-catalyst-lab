"""Electrical, electronics, and embedded-systems methods for Lab v0.10.0.

The router accepts only curated method identifiers.  It does not execute arbitrary
source code, flash hardware, or certify safety-critical designs.
"""
from __future__ import annotations

import math
from typing import Any, Callable

from fastapi import APIRouter, HTTPException

VERSION = "0.10.0"
SCHEMA = "sc-lab-electrical-analysis/1.0"
router = APIRouter(prefix="/v1/electrical", tags=["electrical-embedded"])


def _num(data: dict[str, Any], key: str, *, positive: bool = False, nonnegative: bool = False) -> float:
    try:
        value = float(data[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be numeric") from exc
    if not math.isfinite(value):
        raise ValueError(f"{key} must be finite")
    if positive and value <= 0:
        raise ValueError(f"{key} must be positive")
    if nonnegative and value < 0:
        raise ValueError(f"{key} must be nonnegative")
    return value


def _round(value: float, digits: int = 12) -> float:
    return float(f"{value:.{digits}g}") if math.isfinite(value) else value


def ohms_law(data: dict[str, Any]) -> dict[str, float]:
    voltage = _num(data, "voltage")
    resistance = _num(data, "resistance", positive=True)
    current = voltage / resistance
    return {"current": _round(current), "power": _round(voltage * current)}


def resistor_parallel(data: dict[str, Any]) -> dict[str, float]:
    raw = data.get("resistances")
    values = raw if isinstance(raw, list) else str(raw or "").split(",")
    resistances = [float(item) for item in values]
    if not resistances or any((not math.isfinite(item) or item <= 0) for item in resistances):
        raise ValueError("resistances must contain positive finite values")
    equivalent = 1.0 / sum(1.0 / item for item in resistances)
    return {"equivalentResistance": _round(equivalent), "branchCount": len(resistances)}


def voltage_divider_loaded(data: dict[str, Any]) -> dict[str, float]:
    vin = _num(data, "vin")
    r1 = _num(data, "r1", positive=True)
    r2 = _num(data, "r2", positive=True)
    load = _num(data, "load", positive=True)
    lower = 1.0 / (1.0 / r2 + 1.0 / load)
    output = vin * lower / (r1 + lower)
    return {"outputVoltage": _round(output), "loadedLowerResistance": _round(lower)}


def rc_time_constant(data: dict[str, Any]) -> dict[str, float]:
    resistance = _num(data, "resistance", positive=True)
    capacitance = _num(data, "capacitance", positive=True)
    tau = resistance * capacitance
    return {"timeConstant": _round(tau), "fiveTau": _round(5.0 * tau), "cutoffFrequency": _round(1.0 / (2.0 * math.pi * tau))}


def rlc_series(data: dict[str, Any]) -> dict[str, float]:
    resistance = _num(data, "resistance", nonnegative=True)
    inductance = _num(data, "inductance", positive=True)
    capacitance = _num(data, "capacitance", positive=True)
    frequency = _num(data, "frequency", positive=True)
    voltage = _num(data, "voltage", nonnegative=True)
    omega = 2.0 * math.pi * frequency
    xl = omega * inductance
    xc = 1.0 / (omega * capacitance)
    magnitude = math.hypot(resistance, xl - xc)
    current = voltage / magnitude if magnitude else math.inf
    phase = math.degrees(math.atan2(xl - xc, resistance))
    return {"inductiveReactance": _round(xl), "capacitiveReactance": _round(xc), "impedanceMagnitude": _round(magnitude), "currentRms": _round(current), "phaseDegrees": _round(phase)}


def resonance(data: dict[str, Any]) -> dict[str, float]:
    inductance = _num(data, "inductance", positive=True)
    capacitance = _num(data, "capacitance", positive=True)
    resistance = _num(data, "resistance", positive=True)
    f0 = 1.0 / (2.0 * math.pi * math.sqrt(inductance * capacitance))
    q = math.sqrt(inductance / capacitance) / resistance
    return {"resonantFrequency": _round(f0), "qualityFactor": _round(q), "bandwidth": _round(f0 / q)}


def opamp_inverting(data: dict[str, Any]) -> dict[str, float]:
    rin = _num(data, "rin", positive=True)
    rf = _num(data, "rf", positive=True)
    vin = _num(data, "vin")
    supply = _num(data, "supply", positive=True)
    ideal = -rf / rin * vin
    output = max(-supply, min(supply, ideal))
    return {"gain": _round(-rf / rin), "idealOutput": _round(ideal), "limitedOutput": _round(output), "saturated": abs(ideal) > supply}


def adc_quantization(data: dict[str, Any]) -> dict[str, float]:
    bits = int(_num(data, "bits", positive=True))
    reference = _num(data, "reference", positive=True)
    input_voltage = _num(data, "inputVoltage", nonnegative=True)
    if bits > 32:
        raise ValueError("bits must be 32 or less")
    levels = 2**bits
    lsb = reference / levels
    code = min(levels - 1, max(0, int(round(input_voltage / lsb))))
    quantized = code * lsb
    return {"levels": levels, "lsbVoltage": _round(lsb), "code": code, "quantizedVoltage": _round(quantized), "quantizationError": _round(quantized - input_voltage)}


def pwm_average(data: dict[str, Any]) -> dict[str, float]:
    supply = _num(data, "supply", nonnegative=True)
    duty = _num(data, "duty", nonnegative=True)
    if duty > 100:
        raise ValueError("duty must not exceed 100 percent")
    fraction = duty / 100.0
    return {"averageVoltage": _round(supply * fraction), "rmsVoltage": _round(supply * math.sqrt(fraction)), "dutyFraction": _round(fraction)}


def uart_baud(data: dict[str, Any]) -> dict[str, float]:
    clock = _num(data, "clock", positive=True)
    target = _num(data, "targetBaud", positive=True)
    oversampling = _num(data, "oversampling", positive=True)
    divisor = max(1, round(clock / (oversampling * target)))
    actual = clock / (oversampling * divisor)
    error = 100.0 * (actual - target) / target
    return {"divisor": divisor, "actualBaud": _round(actual), "errorPercent": _round(error), "withinTwoPercent": abs(error) <= 2.0}


def i2c_pullup(data: dict[str, Any]) -> dict[str, float]:
    voltage = _num(data, "voltage", positive=True)
    sink_current = _num(data, "sinkCurrent", positive=True)
    bus_capacitance = _num(data, "busCapacitance", positive=True)
    rise_time = _num(data, "riseTime", positive=True)
    r_min = voltage / sink_current
    r_max = rise_time / (0.8473 * bus_capacitance)
    return {"minimumResistance": _round(r_min), "maximumResistance": _round(r_max), "feasible": r_min <= r_max}


def thermal_junction(data: dict[str, Any]) -> dict[str, float]:
    ambient = _num(data, "ambient")
    power = _num(data, "power", nonnegative=True)
    theta_ja = _num(data, "thetaJA", positive=True)
    limit = _num(data, "junctionLimit")
    junction = ambient + power * theta_ja
    return {"junctionTemperature": _round(junction), "margin": _round(limit - junction), "withinLimit": junction <= limit}


METHODS: dict[str, tuple[str, Callable[[dict[str, Any]], dict[str, Any]]]] = {
    "electrical.ohms-law": ("Ohm's law and DC power", ohms_law),
    "electrical.resistors-parallel": ("Parallel resistor equivalent", resistor_parallel),
    "electrical.loaded-divider": ("Loaded voltage divider", voltage_divider_loaded),
    "electrical.rc-time-constant": ("RC time constant", rc_time_constant),
    "electrical.series-rlc": ("Series RLC impedance", rlc_series),
    "electrical.resonance": ("RLC resonance", resonance),
    "electronics.opamp-inverting": ("Inverting op-amp", opamp_inverting),
    "embedded.adc-quantization": ("ADC quantization", adc_quantization),
    "embedded.pwm-average": ("PWM average and RMS", pwm_average),
    "embedded.uart-baud": ("UART baud-rate error", uart_baud),
    "embedded.i2c-pullup": ("I2C pull-up bounds", i2c_pullup),
    "electronics.thermal-junction": ("Junction temperature", thermal_junction),
}


def public_methods() -> dict[str, Any]:
    return {
        "schema": "sc-lab-electrical-method-catalog/1.0",
        "version": VERSION,
        "curatedOnly": True,
        "methods": [{"id": key, "name": value[0], "engine": "python-curated"} for key, value in METHODS.items()],
    }


def run_method(method_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    selected = METHODS.get(method_id)
    if selected is None:
        raise KeyError(method_id)
    name, function = selected
    outputs = function(inputs)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "methodId": method_id,
        "name": name,
        "inputs": inputs,
        "outputs": outputs,
        "validation": {
            "status": "SCREENING_ONLY",
            "warnings": [
                "Verify component tolerances, temperature coefficients, parasitics, transients, layout, and manufacturer limits.",
                "Safety-critical and regulated designs require qualified engineering review and physical validation.",
            ],
        },
    }


@router.get("/methods")
def list_methods() -> dict[str, Any]:
    return public_methods()


@router.post("/run")
def run(payload: dict[str, Any]) -> dict[str, Any]:
    method_id = str(payload.get("methodId") or "")
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict):
        raise HTTPException(status_code=422, detail="inputs must be an object")
    try:
        return run_method(method_id, inputs)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown curated electrical method") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
